"""Monitoring projektów RCL po identyfikatorach zewnętrznych (numer aktu UE, numer KPRM)."""

import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional, Callable

from playwright.sync_api import Page

from ..constants import RCL_BASE_URL, PLAYWRIGHT_TIMEOUT, PLAYWRIGHT_WAIT_TIMEOUT
from ..config import DATA_DIR
from ..exceptions import RCLConnectionError, DataParseError
from ..utils.rcl_browser_manager import RCLBrowserManager
from ..utils.logger import get_logger
from .rcl_tag_monitor import RCLTagMonitor

logger = get_logger(__name__)


class RCLSearchMonitor(RCLTagMonitor):
    """Klasa do monitorowania projektów RCL po identyfikatorach zewnętrznych."""
    
    def __init__(
        self,
        load_queries_fn: Optional[Callable[[], List[Dict]]] = None,
        output_file: Optional[Path] = None,
        base_url: str = RCL_BASE_URL
    ):
        """
        Inicjalizuje monitor wyszukiwania.
        
        Args:
            load_queries_fn: Funkcja do wczytania zapytań (dependency injection)
            output_file: Plik wyjściowy dla wyników (domyślnie data/rcl_search_results_YYYY-MM-DD.json)
            base_url: Bazowy URL RCL
        """
        from ..config import load_rcl_search_queries
        
        # Wywołaj __init__ z klasy bazowej, ale nie używamy load_tags
        super().__init__(load_tags_fn=None, output_file=None, base_url=base_url)
        
        self.load_queries = load_queries_fn or load_rcl_search_queries
        
        # Domyślny plik wyjściowy z datą
        if output_file is None:
            date_str = datetime.now().strftime("%Y-%m-%d")
            output_file = DATA_DIR / f"rcl_search_results_{date_str}.json"
        
        self.output_file = output_file
        DATA_DIR.mkdir(exist_ok=True)
    
    def monitor(self, start_date: datetime, end_date: datetime) -> List[Dict]:
        """
        Monitoruje projekty w podanym zakresie dat na podstawie zapytań wyszukiwawczych.
        
        Args:
            start_date: Data początkowa zakresu
            end_date: Data końcowa zakresu
            
        Returns:
            Lista znalezionych projektów w formacie gotowym do projects.json
        """
        queries = self.load_queries()
        
        logger.info("Wyszukiwanie projektów RCL po identyfikatorach zewnętrznych")
        logger.info(f"Zakres dat: {start_date.strftime('%Y-%m-%d')} - {end_date.strftime('%Y-%m-%d')}")
        logger.info(f"Znaleziono {len(queries)} zapytanie(ń) do wykonania")
        
        all_results = []
        seen_ids = set()  # Do usuwania duplikatów
        
        # Użyj jednej przeglądarki dla wszystkich wyszukiwań
        with RCLBrowserManager(active_tab='tab2', headless=False) as browser:
            for query_idx, query in enumerate(queries, 1):
                ue_act_number = query.get('ue_act_number')
                title = query.get('title')
                kprm_number = query.get('kprm_number')
                
                try:
                    # Wyszukiwanie tylko po numerze aktu UE (title jest ignorowany)
                    has_ue_act = bool(ue_act_number)
                    has_kprm = bool(kprm_number)
                    
                    query_results = []  # Zbierz wyniki z wszystkich wyszukiwań dla tego zapytania
                    
                    if has_ue_act and has_kprm:
                        # Wykonaj oba wyszukiwania osobno i połącz wyniki (OR)
                        search_value = self._build_ue_act_value(ue_act_number, title)
                        logger.info(f"Zapytanie {query_idx}/{len(queries)}: Wyszukiwanie po akcie UE: {search_value}")
                        try:
                            ue_results = self._search_by_ue_act(browser.page, search_value, start_date, end_date)
                            query_results.extend(ue_results)
                        except RCLConnectionError as e:
                            logger.warning(f"Błąd podczas wyszukiwania po akcie UE: {e}")
                        
                        # Wyczyść formularz przed następnym wyszukiwaniem
                        browser.clear_search_form()
                        
                        logger.info(f"Zapytanie {query_idx}/{len(queries)}: Wyszukiwanie po numerze KPRM: {kprm_number}")
                        try:
                            kprm_results = self._search_by_kprm_number(browser.page, kprm_number, start_date, end_date)
                            query_results.extend(kprm_results)
                        except RCLConnectionError as e:
                            logger.warning(f"Błąd podczas wyszukiwania po numerze KPRM: {e}")
                        
                        results = query_results
                    elif has_ue_act:
                        # Wyszukiwanie po akcie UE (tylko numer)
                        search_value = self._build_ue_act_value(ue_act_number, title)
                        logger.info(f"Zapytanie {query_idx}/{len(queries)}: Wyszukiwanie po akcie UE: {search_value}")
                        results = self._search_by_ue_act(browser.page, search_value, start_date, end_date)
                    elif has_kprm:
                        # Wyszukiwanie po numerze KPRM
                        logger.info(f"Zapytanie {query_idx}/{len(queries)}: Wyszukiwanie po numerze KPRM: {kprm_number}")
                        results = self._search_by_kprm_number(browser.page, kprm_number, start_date, end_date)
                    else:
                        logger.warning(f"Zapytanie {query_idx}/{len(queries)}: Brak wartości do wyszukania, pomijam")
                        continue
                    
                    # Dodaj wyniki, unikając duplikatów
                    for result in results:
                        project_id = result.get('id')
                        if project_id and project_id not in seen_ids:
                            seen_ids.add(project_id)
                            # Konwertuj do formatu projects.json
                            project = {
                                "id": project_id,
                                "title": result.get('title', ''),
                                "number": result.get('number', ''),
                                "source": "rcl"
                            }
                            all_results.append(project)
                    
                    # Wyczyść formularz przed następnym zapytaniem (oprócz ostatniego)
                    if query_idx < len(queries):
                        browser.clear_search_form()
                
                except RCLConnectionError as e:
                    logger.error(f"Błąd podczas wyszukiwania dla zapytania {query_idx}: {e}")
                    # Wyczyść formularz nawet po błędzie, jeśli to nie ostatnie zapytanie
                    if query_idx < len(queries):
                        try:
                            browser.clear_search_form()
                        except Exception:
                            pass
                    continue
                except Exception as e:
                    logger.error(f"Nieoczekiwany błąd dla zapytania {query_idx}: {e}")
                    # Wyczyść formularz nawet po błędzie, jeśli to nie ostatnie zapytanie
                    if query_idx < len(queries):
                        try:
                            browser.clear_search_form()
                        except Exception:
                            pass
                    continue
        
        # Zapisz wyniki
        if all_results:
            self._save_results(all_results, start_date, end_date)
        else:
            logger.info("Nie znaleziono żadnych projektów w podanym zakresie dat")
        
        return all_results
    
    def _build_ue_act_value(self, ue_act_number: Optional[str], title: Optional[str]) -> str:
        """
        Buduje wartość do wyszukiwania po akcie UE (tylko numer).
        
        Args:
            ue_act_number: Numer aktu UE (np. "2021/0241")
            title: Tytuł (ignorowany - używany tylko numer)
            
        Returns:
            Numer aktu UE do wyszukiwania
        """
        # Używamy tylko numeru - title jest ignorowany
        return ue_act_number if ue_act_number else ""
    
    def _search_by_ue_act(
        self,
        page: Page,
        ue_act_value: str,
        start_date: datetime,
        end_date: datetime
    ) -> List[Dict]:
        """
        Wykonuje wyszukiwanie po numerze i tytule aktu prawnego UE.
        
        Args:
            page: Playwright Page obiekt (już otwarta przeglądarka)
            ue_act_value: Wartość do wyszukania (numer i/lub tytuł)
            start_date: Data początkowa zakresu
            end_date: Data końcowa zakresu
            
        Returns:
            Lista znalezionych projektów
            
        Raises:
            RCLConnectionError: Jeśli wystąpi błąd połączenia
        """
        logger.debug(f"Wyszukiwanie po akcie UE: {ue_act_value}")
        
        try:
            # Zakładamy, że formularz jest już czysty (po clear_search_form() lub start_browser())
            # Sprawdź czy jesteśmy na właściwej stronie, jeśli nie - przeładuj
            current_url = page.url
            if 'szukaj' not in current_url or 'tab2' not in current_url:
                # Tylko wtedy przeładuj jeśli nie jesteśmy na stronie wyszukiwania
                search_url = f"{self.base_url}/szukaj?typeId=1&typeId=2&activeTab=tab2#list"
                logger.debug("Przechodzenie do strony wyszukiwania...")
                page.goto(search_url, wait_until="networkidle", timeout=PLAYWRIGHT_TIMEOUT)
                page.wait_for_timeout(PLAYWRIGHT_WAIT_TIMEOUT)
            
            # Poczekaj aż pole UEActValue będzie widoczne i gotowe do użycia
            logger.debug("Oczekiwanie na pole UEActValue...")
            ue_act_input = page.locator('input#UEActValue').first
            ue_act_input.wait_for(state='visible', timeout=PLAYWRIGHT_TIMEOUT)
            page.wait_for_timeout(PLAYWRIGHT_WAIT_TIMEOUT)  # Dodatkowe oczekiwanie na stabilizację
            
            # Wypełnij pole UEActValue
            logger.debug(f"Wypełnianie pola UEActValue wartością: {ue_act_value}")
            ue_act_input.fill(ue_act_value)
            
            # Kliknij przycisk "Szukaj" - próbuj różnych selektorów
            logger.debug("Klikanie przycisku Szukaj...")
            try:
                # Spróbuj najpierw button z tekstem "Szukaj"
                page.click('button:has-text("Szukaj")', timeout=5000)
            except:
                try:
                    # Spróbuj input submit
                    page.click('input[type="submit"]', timeout=5000)
                except:
                    # Spróbuj submit formularza przez Enter
                    page.press('input#UEActValue', 'Enter')
            
            # Poczekaj na wyniki
            logger.debug("Oczekiwanie na wyniki wyszukiwania...")
            page.wait_for_timeout(PLAYWRIGHT_WAIT_TIMEOUT * 2)  # Dłuższe oczekiwanie na wyniki
            
            # Parsuj wyniki używając metody z klasy bazowej
            results = self._parse_search_results(page, start_date, end_date)
            
            return results
                
        except Exception as e:
            raise RCLConnectionError(f"Błąd podczas wyszukiwania po akcie UE '{ue_act_value}': {e}") from e
    
    def _search_by_kprm_number(
        self,
        page: Page,
        kprm_number: str,
        start_date: datetime,
        end_date: datetime
    ) -> List[Dict]:
        """
        Wykonuje wyszukiwanie po numerze z wykazu prac legislacyjnych KPRM.
        
        Args:
            page: Playwright Page obiekt (już otwarta przeglądarka)
            kprm_number: Numer z wykazu KPRM (np. "UD260", "UC2")
            start_date: Data początkowa zakresu
            end_date: Data końcowa zakresu
            
        Returns:
            Lista znalezionych projektów
            
        Raises:
            RCLConnectionError: Jeśli wystąpi błąd połączenia
        """
        logger.debug(f"Wyszukiwanie po numerze KPRM: {kprm_number}")
        
        try:
            # Zakładamy, że formularz jest już czysty (po clear_search_form() lub start_browser())
            # Sprawdź czy jesteśmy na właściwej stronie, jeśli nie - przeładuj
            current_url = page.url
            if 'szukaj' not in current_url or 'tab2' not in current_url:
                # Tylko wtedy przeładuj jeśli nie jesteśmy na stronie wyszukiwania
                search_url = f"{self.base_url}/szukaj?typeId=1&typeId=2&activeTab=tab2#list"
                logger.debug("Przechodzenie do strony wyszukiwania...")
                page.goto(search_url, wait_until="networkidle", timeout=PLAYWRIGHT_TIMEOUT)
                page.wait_for_timeout(PLAYWRIGHT_WAIT_TIMEOUT)
            
            # Pole number może być ukryte w sekcji "dodatkowe kryteria"
            # Spróbuj znaleźć widoczne pole, jeśli nie ma, użyj force
            logger.debug("Oczekiwanie na pole number...")
            
            # Spróbuj znaleźć widoczne pole
            number_input_visible = page.locator('input#number:visible').first
            number_input_all = page.locator('input#number').first
            
            # Poczekaj chwilę na załadowanie
            page.wait_for_timeout(PLAYWRIGHT_WAIT_TIMEOUT)
            
            # Wypełnij pole number
            logger.debug(f"Wypełnianie pola number wartością: {kprm_number}")
            try:
                # Spróbuj najpierw widoczne pole
                if number_input_visible.count() > 0:
                    number_input_visible.fill(kprm_number)
                else:
                    # Jeśli nie ma widocznego, użyj force
                    logger.debug("Pole number nie jest widoczne, używam force fill...")
                    number_input_all.fill(kprm_number, force=True)
            except Exception as e:
                # Ostatecznie użyj force na pierwszym znalezionym
                logger.debug(f"Błąd podczas wypełniania, próba force fill: {e}")
                number_input_all.fill(kprm_number, force=True)
            
            # Kliknij przycisk "Szukaj" - próbuj różnych selektorów
            logger.debug("Klikanie przycisku Szukaj...")
            try:
                # Spróbuj najpierw button z tekstem "Szukaj"
                page.click('button:has-text("Szukaj")', timeout=5000)
            except:
                try:
                    # Spróbuj input submit
                    page.click('input[type="submit"]', timeout=5000)
                except:
                    # Spróbuj submit formularza przez Enter
                    page.press('input#number', 'Enter')
            
            # Poczekaj na wyniki
            logger.debug("Oczekiwanie na wyniki wyszukiwania...")
            page.wait_for_timeout(PLAYWRIGHT_WAIT_TIMEOUT * 2)  # Dłuższe oczekiwanie na wyniki
            
            # Parsuj wyniki używając metody z klasy bazowej
            results = self._parse_search_results(page, start_date, end_date)
            
            return results
                
        except Exception as e:
            raise RCLConnectionError(f"Błąd podczas wyszukiwania po numerze KPRM '{kprm_number}': {e}") from e
    
    def _save_results(
        self,
        all_results: List[Dict],
        start_date: datetime,
        end_date: datetime
    ) -> None:
        """
        Zapisuje wyniki do pliku JSON w formacie gotowym do wklejenia do projects.json.
        
        Args:
            all_results: Lista projektów w formacie projects.json
            start_date: Data początkowa zakresu
            end_date: Data końcowa zakresu
        """
        # Format identyczny z projects.json
        output_data = {
            "projects": all_results
        }
        
        try:
            with open(self.output_file, 'w', encoding='utf-8') as f:
                json.dump(output_data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"Zapisano {len(all_results)} projektów do pliku: {self.output_file}")
            logger.info(f"Format gotowy do wklejenia do config/projects.json")
        except Exception as e:
            logger.error(f"Błąd podczas zapisywania wyników: {e}")
            raise
