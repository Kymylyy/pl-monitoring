"""Zarządzanie przeglądarką dla monitorów RCL."""

from playwright.sync_api import sync_playwright, Browser, BrowserContext, Page

from ..constants import RCL_BASE_URL, PLAYWRIGHT_TIMEOUT, PLAYWRIGHT_WAIT_TIMEOUT, DEFAULT_USER_AGENT
from ..utils.http_client import get_http_headers
from ..utils.logger import get_logger

logger = get_logger(__name__)


class RCLBrowserManager:
    """Klasa do zarządzania jedną przeglądarką dla wszystkich wyszukiwań RCL."""
    
    def __init__(self, active_tab: str = 'tab1', headless: bool = False):
        """
        Inicjalizuje manager przeglądarki.
        
        Args:
            active_tab: Aktywna zakładka ('tab1' dla tagów, 'tab2' dla wyszukiwania)
            headless: Czy przeglądarka ma działać w trybie headless
        """
        self.active_tab = active_tab
        self.headless = headless
        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None
    
    def __enter__(self):
        """Context manager entry - otwiera przeglądarkę."""
        self.start_browser()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - zamyka przeglądarkę."""
        self.close_browser()
    
    def start_browser(self):
        """Otwiera przeglądarkę i ładuje stronę wyszukiwania."""
        logger.debug(f"Otwieranie przeglądarki z activeTab={self.active_tab}")
        
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(headless=self.headless)
        self.context = self.browser.new_context(
            user_agent=DEFAULT_USER_AGENT,
            viewport={'width': 1280, 'height': 720},
            extra_http_headers=get_http_headers()
        )
        self.page = self.context.new_page()
        
        # Załaduj stronę wyszukiwania z odpowiednią zakładką
        search_url = f"{RCL_BASE_URL}/szukaj?activeTab={self.active_tab}"
        logger.debug(f"Ładowanie strony wyszukiwania: {search_url}")
        self.page.goto(search_url, wait_until="networkidle", timeout=PLAYWRIGHT_TIMEOUT)
        
        # Poczekaj na załadowanie formularza
        logger.debug("Oczekiwanie na załadowanie formularza...")
        self.page.wait_for_timeout(PLAYWRIGHT_WAIT_TIMEOUT)
    
    def clear_search_form(self):
        """
        Czyści formularz wyszukiwania przechodząc do URL z czystym formularzem.
        
        Raises:
            Exception: Jeśli nie udało się wyczyścić formularza
        """
        if not self.page:
            raise RuntimeError("Przeglądarka nie jest otwarta. Wywołaj start_browser() najpierw.")
        
        logger.debug("Czyszczenie formularza wyszukiwania...")
        
        # Zawsze przejdź do URL z czystym formularzem - to jest bardziej niezawodne
        # niż próba kliknięcia linku "Wyczyść", który może być niewidoczny
        search_url = f"{RCL_BASE_URL}/szukaj?activeTab={self.active_tab}#list"
        logger.debug(f"Przechodzenie do czystego formularza: {search_url}")
        self.page.goto(search_url, wait_until="networkidle", timeout=PLAYWRIGHT_TIMEOUT)
        self.page.wait_for_timeout(PLAYWRIGHT_WAIT_TIMEOUT)
        logger.debug("Formularz wyczyszczony")
    
    def close_browser(self):
        """Zamyka przeglądarkę i zwalnia zasoby."""
        if self.browser:
            logger.debug("Zamykanie przeglądarki...")
            self.browser.close()
            self.browser = None
            self.context = None
            self.page = None
        
        if self.playwright:
            self.playwright.stop()
            self.playwright = None
