"""Monitoring konkretnych projektów ustaw w RCL."""

import re
from datetime import datetime
from typing import List, Dict, Optional, Callable

import requests
from bs4 import BeautifulSoup

from ..constants import RCL_BASE_URL, HTTP_TIMEOUT
from ..exceptions import RCLConnectionError, DataParseError
from ..utils.date_utils import parse_polish_date
from ..utils.http_client import get_http_headers
from ..utils.logger import get_logger
from ..utils.project_utils import filter_projects_by_source, ensure_source_field

logger = get_logger(__name__)


class RCLProjectMonitor:
    """Klasa do monitorowania zmian w konkretnych projektach ustaw w RCL."""
    
    def __init__(
        self,
        load_projects_fn: Optional[Callable[[], List[Dict]]] = None,
        save_projects_fn: Optional[Callable[[List[Dict]], None]] = None,
        base_url: str = RCL_BASE_URL
    ):
        """
        Inicjalizuje monitor projektów.
        
        Args:
            load_projects_fn: Funkcja do wczytania projektów (dependency injection)
            save_projects_fn: Funkcja do zapisania projektów (dependency injection)
            base_url: Bazowy URL RCL
        """
        from ..config import load_projects, save_projects
        
        # Domyślnie używamy uniwersalnych funkcji, ale filtrujemy tylko RCL
        self._load_all_projects = load_projects_fn or load_projects
        self._save_all_projects = save_projects_fn or save_projects
        self.base_url = base_url
    
    def monitor(self, start_date: datetime, end_date: datetime) -> List[Dict]:
        """
        Monitoruje projekty w podanym zakresie dat.
        
        Args:
            start_date: Data początkowa zakresu
            end_date: Data końcowa zakresu
            
        Returns:
            Lista projektów z informacją o zmianach
        """
        # Wczytaj wszystkie projekty i filtruj tylko RCL
        all_projects = self._load_all_projects()
        projects = filter_projects_by_source(all_projects, 'rcl')
        
        # Upewnij się że wszystkie projekty mają source='rcl' (backward compatibility)
        projects = [ensure_source_field(p, 'rcl') for p in projects]
        
        if not projects:
            logger.warning("Brak projektów RCL do monitorowania!")
            return []
        
        logger.info(f"Monitoring projektów RCL od {start_date.strftime('%Y-%m-%d')} do {end_date.strftime('%Y-%m-%d')}")
        logger.info(f"Znaleziono {len(projects)} projektów do sprawdzenia")
        
        updated_projects = []
        
        for project in projects:
            # Obsługa zarówno formatu z obiektem jak i tylko ID
            if isinstance(project, dict):
                project_id = project.get('id')
                project_title = project.get('title', f'Projekt {project_id}')
            else:
                project_id = project
                project_title = f'Projekt {project_id}'
            
            logger.debug(f"Sprawdzam: {project_title} (ID: {project_id})")
            
            # Pobranie strony projektu
            try:
                soup = self._fetch_project_page(project_id)
            except RCLConnectionError as e:
                logger.error(f"Błąd połączenia dla projektu {project_id}: {e}")
                updated_projects.append(project)
                continue
            
            if not soup:
                updated_projects.append(project)
                continue
            
            # Wyciągnięcie dat modyfikacji
            try:
                modification_dates = self._extract_modification_dates(soup)
            except DataParseError as e:
                logger.error(f"Błąd parsowania dat dla projektu {project_id}: {e}")
                updated_projects.append(project)
                continue
            
            if not modification_dates:
                logger.debug(f"  Brak dat modyfikacji dla projektu {project_id}")
                updated_projects.append(project)
                continue
            
            logger.debug(f"  Znaleziono {len(modification_dates)} dat modyfikacji")
            
            # Sprawdzenie czy któraś data mieści się w zakresie
            last_hit = self._check_date_in_range(modification_dates, start_date, end_date)
            
            if last_hit:
                # Zapisanie wyniku
                if isinstance(project, dict):
                    # Upewnij się że projekt ma source='rcl'
                    project = ensure_source_field(project, 'rcl')
                    project['last_hit'] = last_hit.strftime("%Y-%m-%d")
                else:
                    # Konwersja na dict jeśli było tylko ID
                    project = {
                        'id': project_id,
                        'source': 'rcl',
                        'last_hit': last_hit.strftime("%Y-%m-%d")
                    }
                
                logger.info(f"  ✓ Projekt {project_id}: Ostatnia zmiana: {last_hit.strftime('%Y-%m-%d')}")
            else:
                logger.debug(f"  Brak zmian w okresie dla projektu {project_id}")
            
            # Upewnij się że projekt ma source='rcl'
            if isinstance(project, dict):
                project = ensure_source_field(project, 'rcl')
            
            updated_projects.append(project)
        
        # Zapisanie zaktualizowanych danych (wszystkie projekty, nie tylko RCL)
        try:
            # Wczytaj wszystkie projekty i zaktualizuj tylko RCL
            all_projects = self._load_all_projects()
            all_projects_dict = {p.get('id'): p for p in all_projects}
            
            # Zaktualizuj projekty RCL
            for project in updated_projects:
                all_projects_dict[project.get('id')] = project
            
            # Zapisz wszystkie projekty
            self._save_all_projects(list(all_projects_dict.values()))
            logger.info("Wyniki zapisane do pliku konfiguracyjnego")
        except Exception as e:
            logger.error(f"Błąd podczas zapisywania projektów: {e}")
            raise
        
        return updated_projects
    
    def _fetch_project_page(self, project_id: int) -> Optional[BeautifulSoup]:
        """
        Pobiera stronę projektu z RCL.
        
        Args:
            project_id: ID projektu
            
        Returns:
            BeautifulSoup obiekt lub None w przypadku błędu
            
        Raises:
            RCLConnectionError: Jeśli nie udało się pobrać strony
        """
        url = f"{self.base_url}/projekt/{project_id}"
        headers = get_http_headers()
        
        try:
            response = requests.get(url, headers=headers, timeout=HTTP_TIMEOUT)
            response.raise_for_status()
            return BeautifulSoup(response.content, 'html.parser')
        except requests.RequestException as e:
            raise RCLConnectionError(f"Błąd przy pobieraniu projektu {project_id}: {e}") from e
    
    def _extract_modification_dates(self, soup: BeautifulSoup) -> List[datetime]:
        """
        Wyciąga wszystkie daty modyfikacji z etapów projektu.
        
        Args:
            soup: BeautifulSoup obiekt strony projektu
            
        Returns:
            Lista dat modyfikacji
            
        Raises:
            DataParseError: Jeśli wystąpi błąd podczas parsowania
        """
        dates = []
        
        try:
            # Szukamy wszystkich divów z klasą "small2" zawierających "Data ostatniej modyfikacji"
            modification_divs = soup.find_all('div', class_='small2')
            
            for div in modification_divs:
                text = div.get_text(strip=True)
                # Wzorzec: "Data ostatniej modyfikacji: DD-MM-YYYY"
                match = re.search(r'Data ostatniej modyfikacji:\s*(\d{2}-\d{2}-\d{4})', text)
                if match:
                    date_str = match.group(1)
                    parsed_date = parse_polish_date(date_str)
                    if parsed_date:
                        dates.append(parsed_date)
        except Exception as e:
            raise DataParseError(f"Błąd podczas wyciągania dat modyfikacji: {e}") from e
        
        return dates
    
    def _check_date_in_range(
        self, 
        dates: List[datetime], 
        start_date: datetime, 
        end_date: datetime
    ) -> Optional[datetime]:
        """
        Sprawdza czy któraś z dat mieści się w zakresie [start_date, end_date].
        
        Args:
            dates: Lista dat do sprawdzenia
            start_date: Data początkowa zakresu
            end_date: Data końcowa zakresu
            
        Returns:
            Najnowsza data z zakresu lub None
        """
        dates_in_range = [d for d in dates if start_date <= d <= end_date]
        if dates_in_range:
            return max(dates_in_range)
        return None
