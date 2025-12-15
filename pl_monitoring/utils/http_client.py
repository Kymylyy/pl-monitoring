"""Narzędzia do obsługi żądań HTTP i przeglądarki."""

import time
from typing import Dict, Tuple, Optional, Callable, TypeVar
from playwright.sync_api import BrowserContext, sync_playwright, Browser
import requests

from ..constants import DEFAULT_USER_AGENT, HTTP_TIMEOUT
from ..utils.logger import get_logger

logger = get_logger(__name__)

T = TypeVar('T')


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


def retry_request(
    request_fn: Callable[[], T],
    max_retries: int = 3,
    retry_delay: float = 1.0,
    backoff_factor: float = 2.0,
    retryable_exceptions: tuple = (requests.RequestException,)
) -> T:
    """
    Wykonuje żądanie HTTP z automatycznym ponawianiem przy błędach.
    
    Args:
        request_fn: Funkcja wykonująca żądanie HTTP (np. lambda: requests.get(url))
        max_retries: Maksymalna liczba ponownych prób (domyślnie 3)
        retry_delay: Początkowe opóźnienie między próbami w sekundach (domyślnie 1.0)
        backoff_factor: Mnożnik opóźnienia przy każdej kolejnej próbie (domyślnie 2.0)
        retryable_exceptions: Krotka wyjątków, które powinny być ponawiane
        
    Returns:
        Wynik funkcji request_fn
        
    Raises:
        Ostatni wyjątek jeśli wszystkie próby się nie powiodły
    """
    last_exception = None
    delay = retry_delay
    
    for attempt in range(max_retries + 1):
        try:
            return request_fn()
        except retryable_exceptions as e:
            last_exception = e
            if attempt < max_retries:
                logger.warning(f"Błąd żądania HTTP (próba {attempt + 1}/{max_retries + 1}): {e}. Ponawianie za {delay:.1f}s...")
                time.sleep(delay)
                delay *= backoff_factor
            else:
                logger.error(f"Wszystkie próby żądania HTTP nie powiodły się po {max_retries + 1} próbach")
    
    raise last_exception

