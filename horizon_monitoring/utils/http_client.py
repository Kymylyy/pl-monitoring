"""Narzędzia do obsługi żądań HTTP i przeglądarki."""

from typing import Dict, Tuple
from playwright.sync_api import BrowserContext, sync_playwright, Browser

from ..constants import DEFAULT_USER_AGENT


def get_http_headers() -> Dict[str, str]:
    """
    Zwraca standardowe nagłówki HTTP symulujące przeglądarkę.
    
    Returns:
        Słownik z nagłówkami HTTP
    """
    return {
        'User-Agent': DEFAULT_USER_AGENT,
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'pl-PL,pl;q=0.9,en-US;q=0.8,en;q=0.7',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
    }


def get_browser_context(headless: bool = False) -> Tuple[Browser, BrowserContext]:
    """
    Tworzy kontekst przeglądarki Playwright z domyślnymi ustawieniami.
    
    Args:
        headless: Czy przeglądarka ma działać w trybie headless
        
    Returns:
        Tuple (browser, context)
    """
    playwright = sync_playwright().start()
    browser = playwright.chromium.launch(headless=headless)
    context = browser.new_context(
        user_agent=DEFAULT_USER_AGENT,
        viewport={'width': 1280, 'height': 720},
        extra_http_headers=get_http_headers()
    )
    return browser, context

