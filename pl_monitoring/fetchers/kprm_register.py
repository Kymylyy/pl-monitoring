"""Pobieranie rejestru prac legislacyjnych z KPRM."""

import os
from pathlib import Path
from playwright.sync_api import BrowserContext

from ..constants import KPRM_REGISTER_URL, KPRM_DIRECT_CSV_URL
from ..config import REGISTER_CSV, DATA_DIR
from ..exceptions import KPRMConnectionError
from ..utils.http_client import get_browser_context
from ..utils.logger import get_logger

logger = get_logger(__name__)


class KPRMRegisterFetcher:
    """Klasa do pobierania pliku CSV z rejestru prac legislacyjnych KPRM."""
    
    def __init__(
        self,
        output_file: Path = None,
        register_url: str = KPRM_REGISTER_URL,
        direct_url: str = KPRM_DIRECT_CSV_URL
    ):
        """
        Inicjalizuje fetcher.
        
        Args:
            output_file: Ścieżka do pliku wyjściowego (domyślnie z config.py)
            register_url: URL strony rejestru KPRM
            direct_url: Bezpośredni URL do pliku CSV
        """
        self.output_file = output_file or REGISTER_CSV
        self.register_url = register_url
        self.direct_url = direct_url
        DATA_DIR.mkdir(exist_ok=True)
    
    def download(self) -> bool:
        """
        Pobiera plik CSV z rejestru prac legislacyjnych.
        
        Returns:
            True jeśli pobieranie się powiodło, False w przeciwnym razie
            
        Raises:
            KPRMConnectionError: Jeśli nie udało się pobrać pliku
        """
        logger.info("Pobieranie pliku CSV z rejestru prac legislacyjnych...")
        
        browser, context = get_browser_context(headless=False)
        
        try:
            # Spróbuj najpierw bezpośrednie pobranie
            if self._try_direct_download(context):
                return True
            
            # Jeśli bezpośrednie nie zadziałało, spróbuj przez stronę
            return self._download_via_page(context, browser)
            
        except KPRMConnectionError:
            raise
        except Exception as e:
            logger.exception("Nieoczekiwany błąd podczas pobierania pliku")
            raise KPRMConnectionError(f"Błąd podczas pobierania pliku: {e}") from e
        finally:
            browser.close()
    
    def _try_direct_download(self, context: BrowserContext) -> bool:
        """Próbuje pobrać plik bezpośrednio z URL."""
        try:
            logger.debug(f"Próba bezpośredniego pobrania z: {self.direct_url}")
            response = context.request.get(self.direct_url)
            
            if response.status == 200:
                with open(self.output_file, 'wb') as f:
                    f.write(response.body())
                
                file_size = os.path.getsize(self.output_file)
                file_size_mb = file_size / (1024 * 1024)
                logger.info(f"✓ Pobrano plik bezpośrednio: {self.output_file}")
                logger.info(f"  Rozmiar: {file_size_mb:.2f} MB")
                return True
        except Exception as e:
            logger.debug(f"Bezpośrednie pobranie nie powiodło się: {e}")
            logger.debug("Próba przez stronę...")
        
        return False
    
    def _download_via_page(self, context: BrowserContext, browser) -> bool:
        """Pobiera plik przez stronę WWW."""
        page = context.new_page()
        
        try:
            logger.debug(f"Ładowanie strony: {self.register_url}")
            page.goto(self.register_url, wait_until="load", timeout=60000)
            
            logger.debug("Oczekiwanie na załadowanie JavaScript...")
            page.wait_for_timeout(5000)
            
            logger.debug("Szukanie linku do pobrania pliku CSV...")
            download_link = self._find_download_link(page)
            
            if not download_link:
                logger.error("Nie znaleziono linku do pobrania pliku CSV")
                try:
                    page.screenshot(path="debug_register.png")
                    logger.debug("Zapisano screenshot do debug_register.png")
                except Exception:
                    pass
                raise KPRMConnectionError("Nie znaleziono linku do pobrania pliku CSV")
            
            # Pobierz pełny URL
            href = download_link.get_attribute('href')
            if href.startswith('/'):
                file_url = "https://www.gov.pl" + href
            else:
                file_url = href
            
            logger.debug(f"Pobieranie pliku z: {file_url}")
            response = context.request.get(file_url)
            
            if response.status == 200:
                with open(self.output_file, 'wb') as f:
                    f.write(response.body())
                
                file_size = os.path.getsize(self.output_file)
                file_size_mb = file_size / (1024 * 1024)
                logger.info(f"✓ Pobrano plik: {self.output_file}")
                logger.info(f"  Rozmiar: {file_size_mb:.2f} MB")
                return True
            else:
                raise KPRMConnectionError(f"Nie udało się pobrać pliku. Status: {response.status}")
    
    def _find_download_link(self, page) -> object:
        """Znajduje link do pobrania pliku CSV."""
        selectors = [
            'a[href*="Rejestr_20874195.csv"]',
            'a.file-download[href*="register-file"]',
            'a[href*="register-file"][href*=".csv"]',
            'a:has-text("Pobierz dane do pliku")',
            'a:has-text("csv")',
            'a[download]'
        ]
        
        for selector in selectors:
            try:
                link = page.locator(selector).first
                if link.count() > 0:
                    href = link.get_attribute('href')
                    if href and ('csv' in href.lower() or 'register-file' in href):
                        logger.debug(f"Znaleziono link: {href}")
                        return link
            except Exception:
                continue
        
        return None

