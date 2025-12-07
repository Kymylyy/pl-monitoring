"""Monitoring aktów prawnych w RCL na podstawie haseł przedmiotowych (tagów)."""

import json
import re
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional, Callable
from urllib.parse import urlencode

from bs4 import BeautifulSoup
from playwright.sync_api import Page

from ..constants import RCL_BASE_URL, PLAYWRIGHT_TIMEOUT, PLAYWRIGHT_WAIT_TIMEOUT
from ..config import FINANCIAL_RESULTS, DATA_DIR
from ..exceptions import RCLConnectionError, DataParseError
from ..utils.date_utils import parse_polish_date
from ..utils.http_client import get_browser_context
from ..utils.logger import get_logger

logger = get_logger(__name__)


class RCLTagMonitor:
    """Klasa do monitorowania aktów prawnych w RCL na podstawie haseł przedmiotowych."""
    
    def __init__(
        self,
        load_tags_fn: Optional[Callable[[], List[Dict]]] = None,
        output_file: Optional[Path] = None,
        base_url: str = RCL_BASE_URL
    ):
        """
        Inicjalizuje monitor tagów.
        
        Args:
            load_tags_fn: Funkcja do wczytania tagów (dependency injection)
            output_file: Plik wyjściowy dla wyników
            base_url: Bazowy URL RCL
        """
        from ..config import load_rcl_subject_tags
        
        self.load_tags = load_tags_fn or load_rcl_subject_tags
        self.output_file = output_file or FINANCIAL_RESULTS
        self.base_url = base_url
        DATA_DIR.mkdir(exist_ok=True)
    
    def monitor(self, start_date: datetime, end_date: datetime) -> List[Dict]:
        """
        Monitoruje akty prawne z tagami w podanym zakresie dat.
        
        Args:
            start_date: Data początkowa zakresu
            end_date: Data końcowa zakresu
            
        Returns:
            Lista znalezionych aktów prawnych
        """
        tags = self.load_tags()
        
        logger.info("Monitoring aktów prawnych z tagami finansowymi")
        logger.info(f"Zakres dat: {start_date.strftime('%Y-%m-%d')} - {end_date.strftime('%Y-%m-%d')}")
        logger.info(f"Znaleziono {len(tags)} tag(ów) do monitorowania:")
        for tag in tags:
            if tag['name']:
                logger.debug(f"  - ID: {tag['id']}, Nazwa: {tag['name']}")
            else:
                logger.debug(f"  - ID: {tag['id']}")
        
        # Wyszukaj dla każdego tagu
        all_results = []
        for tag in tags:
            tag_id = tag['id']
            try:
                results = self._search_by_tag(tag_id, start_date, end_date)
                all_results.extend(results)
            except RCLConnectionError as e:
                logger.error(f"Błąd podczas wyszukiwania dla tagu {tag_id}: {e}")
                continue
        
        # Zapisz wyniki
        if all_results:
            self._save_results(all_results, start_date, end_date)
        else:
            logger.info("Nie znaleziono żadnych aktów w podanym zakresie dat")
        
        return all_results
    
    def _search_by_tag(
        self, 
        tag_id: int, 
        start_date: datetime, 
        end_date: datetime
    ) -> List[Dict]:
        """
        Wykonuje wyszukiwanie dla danego tagu i zwraca listę aktów.
        
        Args:
            tag_id: ID hasła przedmiotowego
            start_date: Data początkowa zakresu
            end_date: Data końcowa zakresu
            
        Returns:
            Lista znalezionych aktów
            
        Raises:
            RCLConnectionError: Jeśli wystąpi błąd połączenia
        """
        logger.debug(f"Wyszukiwanie dla tagu ID: {tag_id}")
        
        # Zbuduj URL bezpośrednio z parametrem wordkeyId
        base_url = f"{self.base_url}/szukaj"
        params = {
            '_typeId': '1',
            'progress': '',
            'status': '',
            'tenure': '',
            'createDateFrom': '',
            'createDateTo': '',
            'title': '',
            '_keywordId': '1',
            'applicantId': '',
            'periodId': '',
            '_deptId': '1',
            'wordkeyId': str(tag_id),
            '_wordkeyId': '1',
            'amended': '',
            'repealed': '',
            'topic': '',
            'number': '',
            '_isUEAct': 'on',
            '_isActEstablishingNumber': 'on',
            '_isTKAct': 'on',
            '_isSeparateMode': 'on',
            '_isDU': 'on',
            '_isNumerSejm': 'on',
            'activeTab': 'tab1',
            'sKey': 'modifiedDate',
            'sOrder': 'desc'
        }
        
        search_url = f"{base_url}?{urlencode(params)}#list"
        
        logger.debug(f"Otwieranie URL z hasłem przedmiotowym ID: {tag_id}")
        
        browser, context = get_browser_context(headless=False)
        page = context.new_page()
        
        try:
            logger.debug("Ładowanie strony z wynikami...")
            page.goto(search_url, wait_until="networkidle", timeout=PLAYWRIGHT_TIMEOUT)
            
            logger.debug("Oczekiwanie na załadowanie wyników...")
            page.wait_for_timeout(PLAYWRIGHT_WAIT_TIMEOUT)
            
            # Parsuj wyniki
            results = self._parse_search_results(page, start_date, end_date)
            
            browser.close()
            return results
            
        except Exception as e:
            browser.close()
            raise RCLConnectionError(f"Błąd podczas wyszukiwania dla tagu {tag_id}: {e}") from e
    
    def _parse_search_results(
        self, 
        page: Page, 
        start_date: datetime, 
        end_date: datetime
    ) -> List[Dict]:
        """
        Parsuje tabelę wyników z HTML i filtruje według zakresu dat.
        
        Args:
            page: Playwright Page obiekt
            start_date: Data początkowa zakresu
            end_date: Data końcowa zakresu
            
        Returns:
            Lista znalezionych aktów
            
        Raises:
            DataParseError: Jeśli wystąpi błąd podczas parsowania
        """
        try:
            html = page.content()
            soup = BeautifulSoup(html, 'html.parser')
            
            # Znajdź tabelę z wynikami
            tables = soup.find_all('table')
            table = None
            
            for t in tables:
                rows = t.find_all('tr')
                if len(rows) > 1:
                    first_data_row = rows[1] if len(rows) > 1 else None
                    if first_data_row and first_data_row.find('a', href=re.compile(r'/projekt/\d+')):
                        table = t
                        break
            
            if not table:
                logger.warning("Nie znaleziono tabeli z wynikami")
                return []
            
            results = []
            rows = table.find_all('tr')[1:]  # Pomijamy nagłówek
            
            logger.debug(f"Znaleziono {len(rows)} wierszy w tabeli")
            
            for row_idx, row in enumerate(rows):
                cells = row.find_all(['td', 'th'])
                
                # Sprawdź czy pierwsza kolumna to checkbox
                has_checkbox = False
                if len(cells) > 0:
                    first_cell = cells[0]
                    if first_cell.find('a', href=re.compile(r'/zapisz/projekt')):
                        has_checkbox = True
                
                # Dostosuj indeksy kolumn
                if has_checkbox:
                    if len(cells) < 6:
                        continue
                    title_cell_idx = 1
                    number_cell_idx = 3
                    updated_date_cell_idx = 5
                else:
                    if len(cells) < 5:
                        continue
                    title_cell_idx = 0
                    number_cell_idx = 2
                    updated_date_cell_idx = 4
                
                try:
                    # Tytuł (z linkiem)
                    title_cell = cells[title_cell_idx]
                    title_link = title_cell.find('a', href=re.compile(r'/projekt/\d+'))
                    if not title_link:
                        continue
                    
                    title = title_link.get_text(strip=True)
                    href = title_link.get('href', '')
                    
                    # Wyciągnij ID z URL
                    project_id = None
                    if href:
                        match = re.search(r'/projekt/(\d+)', href)
                        if match:
                            project_id = int(match.group(1))
                    
                    # Numer
                    number = cells[number_cell_idx].get_text(strip=True) if len(cells) > number_cell_idx else ""
                    
                    # Data zaktualizowania
                    updated_date_str = cells[updated_date_cell_idx].get_text(strip=True) if len(cells) > updated_date_cell_idx else ""
                    
                    if not updated_date_str:
                        continue
                    
                    # Parsuj datę
                    updated_date = parse_polish_date(updated_date_str)
                    if not updated_date:
                        logger.warning(f"Nie można sparsować daty: {updated_date_str}")
                        continue
                    
                    # Filtruj według zakresu dat
                    if start_date <= updated_date <= end_date:
                        results.append({
                            "title": title,
                            "id": project_id,
                            "updated_date": updated_date_str,
                            "number": number
                        })
                        logger.info(f"  ✓ Znaleziono: {title[:50]}... (zaktualizowany: {updated_date_str})")
                
                except Exception as e:
                    logger.warning(f"Błąd parsowania wiersza {row_idx}: {e}")
                    continue
            
            return results
            
        except Exception as e:
            raise DataParseError(f"Błąd podczas parsowania wyników: {e}") from e
    
    def _save_results(
        self, 
        all_results: List[Dict], 
        start_date: datetime, 
        end_date: datetime
    ) -> None:
        """
        Zapisuje wyniki do pliku JSON.
        
        Args:
            all_results: Lista wyników
            start_date: Data początkowa zakresu
            end_date: Data końcowa zakresu
        """
        output_data = {
            "search_date": datetime.now().strftime("%Y-%m-%d"),
            "date_range": {
                "start": start_date.strftime("%Y-%m-%d"),
                "end": end_date.strftime("%Y-%m-%d")
            },
            "results": all_results
        }
        
        try:
            with open(self.output_file, 'w', encoding='utf-8') as f:
                json.dump(output_data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"Zapisano {len(all_results)} wyników do pliku: {self.output_file}")
        except Exception as e:
            logger.error(f"Błąd podczas zapisywania wyników: {e}")
            raise
