"""Monitoring konkretnych projektów ustaw w Sejmie."""

import re
from datetime import datetime
from typing import List, Dict, Optional, Callable

import requests
from bs4 import BeautifulSoup

from ..constants import SEJM_WWW_BASE_URL, SEJM_PROCESS_URL_TEMPLATE, HTTP_TIMEOUT
from ..exceptions import SejmConnectionError, DataParseError
from ..utils.project_utils import filter_projects_by_source
from ..utils.date_utils import parse_polish_date_full
from ..utils.http_client import get_http_headers, retry_request
from ..utils.logger import get_logger

logger = get_logger(__name__)


class SejmProjectMonitor:
    """Klasa do monitorowania zmian w konkretnych projektach ustaw w Sejmie."""
    
    def __init__(
        self,
        load_projects_fn: Optional[Callable[[], List[Dict]]] = None,
        save_projects_fn: Optional[Callable[[List[Dict]], None]] = None,
        base_url: str = SEJM_WWW_BASE_URL
    ):
        """
        Inicjalizuje monitor projektów Sejm.
        
        Args:
            load_projects_fn: Funkcja do wczytania projektów (dependency injection)
            save_projects_fn: Funkcja do zapisania projektów (dependency injection)
            base_url: Bazowy URL strony Sejmu
        """
        from ..config import load_projects, save_projects
        
        self.load_projects = load_projects_fn or load_projects
        self.save_projects = save_projects_fn or save_projects
        self.base_url = base_url
    
    def monitor(self, start_date: datetime, end_date: datetime) -> List[Dict]:
        """
        Monitoruje projekty Sejm w podanym zakresie dat.
        
        Args:
            start_date: Data początkowa zakresu
            end_date: Data końcowa zakresu
            
        Returns:
            Lista projektów z informacją o zmianach
        """
        all_projects = self.load_projects()
        sejm_projects = filter_projects_by_source(all_projects, 'sejm')
        
        if not sejm_projects:
            logger.warning("Brak projektów Sejm do monitorowania!")
            return []
        
        logger.info(f"Monitoring projektów Sejm od {start_date.strftime('%Y-%m-%d')} do {end_date.strftime('%Y-%m-%d')}")
        logger.info(f"Znaleziono {len(sejm_projects)} projektów do sprawdzenia")
        
        # Wyczyść referred_to dla wszystkich projektów Sejm (zaczynamy od nowa dla tego zakresu dat)
        for project in sejm_projects:
            project['referred_to'] = []
        
        updated_projects = []
        all_projects_dict = {p.get('id'): p for p in all_projects}
        
        for project in sejm_projects:
            project_id = str(project.get('id'))
            project_title = project.get('title', f'Projekt {project_id}')
            
            logger.debug(f"Sprawdzam: {project_title} (ID: {project_id})")
            
            try:
                soup = self._fetch_process_page(project_id)
            except SejmConnectionError as e:
                logger.error(f"Błąd połączenia dla projektu {project_id}: {e}")
                updated_projects.append(project)
                continue
            
            if not soup:
                logger.warning(f"Nie udało się pobrać strony dla projektu {project_id}")
                updated_projects.append(project)
                continue
            
            # Parsuj wszystkie etapy procesu
            try:
                all_stages = self._parse_process_stages(soup)
            except DataParseError as e:
                logger.error(f"Błąd parsowania etapów dla projektu {project_id}: {e}")
                updated_projects.append(project)
                continue
            
            if not all_stages:
                logger.debug(f"  Brak etapów dla projektu {project_id}")
                updated_projects.append(project)
                continue
            
            logger.debug(f"  Znaleziono {len(all_stages)} etapów procesu")
            
            # Filtruj etapy w zakresie dat
            stages_in_range = [
                stage for stage in all_stages
                if start_date <= stage['date'] <= end_date
            ]
            
            if stages_in_range:
                # Znajdź najnowszą datę
                latest_date = max(stage['date'] for stage in stages_in_range)
                project['last_hit'] = latest_date.strftime('%Y-%m-%d')
                
                # Zapisz wszystkie etapy z zakresu
                project['referred_to'] = [
                    self._format_stage_for_json(stage)
                    for stage in stages_in_range
                ]
                
                logger.info(f"  ✓ Projekt {project_id}: Ostatnia zmiana: {latest_date.strftime('%Y-%m-%d')} (znaleziono {len(stages_in_range)} etapów)")
            else:
                logger.debug(f"  Brak zmian w okresie dla projektu {project_id}")
                project['referred_to'] = []
            
            # Zaktualizuj projekt w słowniku wszystkich projektów
            all_projects_dict[project.get('id')] = project
            updated_projects.append(project)
        
        # Zapisanie zaktualizowanych danych (wszystkie projekty, nie tylko Sejm)
        try:
            all_projects_updated = list(all_projects_dict.values())
            self.save_projects(all_projects_updated)
            logger.info("Wyniki zapisane do pliku konfiguracyjnego")
        except Exception as e:
            logger.error(f"Błąd podczas zapisywania projektów: {e}")
            raise
        
        return updated_projects
    
    def _fetch_process_page(self, print_number: str) -> Optional[BeautifulSoup]:
        """
        Pobiera stronę HTML przebiegu procesu legislacyjnego.
        
        Args:
            print_number: Numer druku (ID projektu)
            
        Returns:
            BeautifulSoup obiekt lub None w przypadku błędu
            
        Raises:
            SejmConnectionError: Jeśli nie udało się pobrać strony
        """
        url = f"{self.base_url}{SEJM_PROCESS_URL_TEMPLATE.format(number=print_number)}"
        headers = get_http_headers()
        
        try:
            response = retry_request(
                lambda: requests.get(url, headers=headers, timeout=HTTP_TIMEOUT),
                max_retries=3,
                retry_delay=1.0
            )
            response.raise_for_status()
            return BeautifulSoup(response.content, 'html.parser')
        except requests.RequestException as e:
            raise SejmConnectionError(f"Błąd przy pobieraniu strony procesu dla druku {print_number}: {e}") from e
    
    def _parse_process_stages(self, soup: BeautifulSoup) -> List[Dict]:
        """
        Parsuje wszystkie etapy procesu legislacyjnego z HTML.
        
        Args:
            soup: BeautifulSoup obiekt strony procesu
            
        Returns:
            Lista słowników z etapami procesu
            
        Raises:
            DataParseError: Jeśli wystąpi błąd podczas parsowania
        """
        stages = []
        
        try:
            # Znajdź główną listę procesu
            process_list = soup.find('ul', class_=re.compile(r'proces'))
            if not process_list:
                logger.warning("Nie znaleziono listy procesu legislacyjnego")
                return []
            
            # Iteruj przez wszystkie <li> w liście procesu
            for li in process_list.find_all('li', recursive=False):
                # Pomiń elementy z klasą "rok"
                if 'rok' in li.get('class', []):
                    continue
                
                # Główne etapy (class="krok")
                if 'krok' in li.get('class', []):
                    stage = self._parse_main_stage(li)
                    if stage:
                        stages.append(stage)
                
                # Zagnieżdżone listy (praca w komisjach)
                nested_ul = li.find('ul')
                if nested_ul:
                    nested_stages = self._parse_nested_stages(nested_ul)
                    stages.extend(nested_stages)
        
        except Exception as e:
            raise DataParseError(f"Błąd podczas parsowania etapów procesu: {e}") from e
        
        return stages
    
    def _parse_main_stage(self, li_element) -> Optional[Dict]:
        """
        Parsuje główny etap procesu (class="krok").
        
        Args:
            li_element: Element <li class="krok">
            
        Returns:
            Słownik z danymi etapu lub None
        """
        # Wyciągnij datę
        date_span = li_element.find('span')
        if not date_span:
            return None
        
        date_str = date_span.get_text(strip=True)
        date = parse_polish_date_full(date_str)
        if not date:
            logger.debug(f"Nie udało się sparsować daty: {date_str}")
            return None
        
        # Wyciągnij typ etapu z <h3>
        h3 = li_element.find('h3')
        stage_type = h3.get_text(strip=True) if h3 else ""
        
        # Wyciągnij numer druku z linku jeśli jest
        print_number = None
        if h3:
            print_link = h3.find('a', href=re.compile(r'druk\.xsp\?nr='))
            if print_link:
                match = re.search(r'nr=(\d+)', print_link.get('href', ''))
                if match:
                    print_number = match.group(1)
        
        # Wyciągnij szczegóły z <div>
        details = {}
        details_div = li_element.find('div')
        if details_div:
            # Przejdź przez wszystkie <p> w div
            for p in details_div.find_all('p'):
                text = p.get_text(strip=True)
                if not text:
                    continue
                
                # Nr posiedzenia
                if 'Nr posiedzenia:' in text:
                    strong = p.find('strong')
                    if strong:
                        details['sitting_number'] = strong.get_text(strip=True)
                
                # Głosowanie
                elif text.startswith('Głosowanie:'):
                    details['voting'] = text.replace('Głosowanie:', '').strip()
                
                # Wynik głosowania
                elif text.startswith('Wynik:'):
                    details['voting_result'] = text.replace('Wynik:', '').strip()
                
                # Decyzja
                elif text.startswith('Decyzja:'):
                    details['decision'] = text.replace('Decyzja:', '').strip()
                
                # Komentarz
                elif text.startswith('Komentarz:'):
                    details['comment'] = text.replace('Komentarz:', '').strip()
            
            # Zbierz wszystkie teksty jako opis
            all_texts = [p.get_text(strip=True) for p in details_div.find_all('p') if p.get_text(strip=True)]
            details['description'] = ' | '.join(all_texts) if all_texts else ""
        
        return {
            'date': date,
            'stage_type': stage_type,
            'print_number': print_number,
            **details
        }
    
    def _parse_nested_stages(self, ul_element) -> List[Dict]:
        """
        Parsuje zagnieżdżone etapy (praca w komisjach).
        
        Args:
            ul_element: Element <ul> z zagnieżdżonymi etapami
            
        Returns:
            Lista słowników z etapami
        """
        stages = []
        
        for li in ul_element.find_all('li', recursive=False):
            # Etapy z datą (class="koniec" lub "poczatek")
            if 'koniec' in li.get('class', []) or 'poczatek' in li.get('class', []):
                stage = self._parse_nested_stage(li)
                if stage:
                    stages.append(stage)
        
        return stages
    
    def _parse_nested_stage(self, li_element) -> Optional[Dict]:
        """
        Parsuje zagnieżdżony etap (praca w komisjach).
        
        Args:
            li_element: Element <li> z zagnieżdżonym etapem
            
        Returns:
            Słownik z danymi etapu lub None
        """
        # Wyciągnij datę jeśli jest
        date_span = li_element.find('span')
        date = None
        if date_span:
            date_str = date_span.get_text(strip=True)
            date = parse_polish_date_full(date_str)
        
        # Wyciągnij typ etapu z <h3> lub <h4>
        h3 = li_element.find('h3')
        h4 = li_element.find('h4')
        stage_type = ""
        if h4:
            stage_type = h4.get_text(strip=True)
        elif h3:
            stage_type = h3.get_text(strip=True)
        
        # Wyciągnij numer druku z linku jeśli jest
        print_number = None
        element_with_link = h4 or h3
        if element_with_link:
            print_link = element_with_link.find('a', href=re.compile(r'druk\.xsp\?nr='))
            if print_link:
                match = re.search(r'nr=(\d+)', print_link.get('href', ''))
                if match:
                    print_number = match.group(1)
        
        # Wyciągnij szczegóły z <div>
        details = {}
        details_div = li_element.find('div')
        if details_div:
            # Zbierz wszystkie teksty jako opis
            all_texts = [p.get_text(strip=True) for p in details_div.find_all('p') if p.get_text(strip=True)]
            details['description'] = ' | '.join(all_texts) if all_texts else ""
        
        # Jeśli nie ma daty, pomiń etap
        if not date:
            return None
        
        return {
            'date': date,
            'stage_type': stage_type,
            'print_number': print_number,
            **details
        }
    
    def _format_stage_for_json(self, stage: Dict) -> Dict:
        """
        Formatuje etap do zapisu w JSON (konwertuje datetime na string).
        
        Args:
            stage: Słownik z danymi etapu
            
        Returns:
            Słownik gotowy do zapisu w JSON
        """
        formatted = {
            'date': stage['date'].strftime('%Y-%m-%d'),
            'stage_type': stage.get('stage_type', ''),
        }
        
        # Dodaj opcjonalne pola
        if stage.get('print_number'):
            formatted['print_number'] = stage['print_number']
        
        if stage.get('sitting_number'):
            formatted['sitting_number'] = stage['sitting_number']
        
        if stage.get('decision'):
            formatted['decision'] = stage['decision']
        
        if stage.get('voting_result'):
            formatted['voting_result'] = stage['voting_result']
        
        if stage.get('description'):
            formatted['description'] = stage['description']
        
        if stage.get('comment'):
            formatted['comment'] = stage['comment']
        
        return formatted
