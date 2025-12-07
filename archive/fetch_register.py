#!/usr/bin/env python3
"""
Skrypt do pobierania pliku CSV z rejestru prac legislacyjnych i programowych Rady Ministrów
Pobiera plik z https://www.gov.pl/web/premier/wplip-rm
"""

import os
from pathlib import Path
from playwright.sync_api import sync_playwright


# Konfiguracja
REGISTER_URL = "https://www.gov.pl/web/premier/wplip-rm"
OUTPUT_DIR = Path("data")
OUTPUT_FILE = OUTPUT_DIR / "Rejestr_20874195.csv"


def download_register_csv():
    """
    Pobiera plik CSV z rejestru prac legislacyjnych
    """
    print("Pobieranie pliku CSV z rejestru prac legislacyjnych...")
    
    # Utwórz katalog na dane jeśli nie istnieje
    OUTPUT_DIR.mkdir(exist_ok=True)
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            viewport={'width': 1280, 'height': 720},
            extra_http_headers={
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'pl-PL,pl;q=0.9,en-US;q=0.8,en;q=0.7',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
            }
        )
        page = context.new_page()
        
        try:
            # Spróbuj najpierw pobrać plik bezpośrednio (znany URL)
            direct_url = "https://www.gov.pl/register-file/Rejestr_20874195.csv"
            print(f"Próba bezpośredniego pobrania z: {direct_url}...")
            
            try:
                response = context.request.get(direct_url)
                if response.status == 200:
                    # Zapisz plik
                    with open(OUTPUT_FILE, 'wb') as f:
                        f.write(response.body())
                    
                    file_size = os.path.getsize(OUTPUT_FILE)
                    file_size_mb = file_size / (1024 * 1024)
                    print(f"✓ Pobrano plik bezpośrednio: {OUTPUT_FILE}")
                    print(f"  Rozmiar: {file_size_mb:.2f} MB")
                    browser.close()
                    return True
            except Exception as e:
                print(f"Bezpośrednie pobranie nie powiodło się: {e}")
                print("Próba przez stronę...")
            
            # Jeśli bezpośrednie pobranie nie zadziałało, spróbuj przez stronę
            print(f"Ładowanie strony: {REGISTER_URL}...")
            page.goto(REGISTER_URL, wait_until="load", timeout=60000)
            
            # Poczekaj na załadowanie JavaScript
            print("Oczekiwanie na załadowanie JavaScript...")
            page.wait_for_timeout(5000)
            
            # Znajdź link do pobrania pliku CSV
            # Link ma href="/register-file/Rejestr_20874195.csv" i klasę "file-download"
            print("Szukanie linku do pobrania pliku CSV...")
            
            # Spróbuj różnych selektorów
            download_link = None
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
                            download_link = link
                            print(f"Znaleziono link: {href}")
                            break
                except Exception:
                    continue
            
            if not download_link:
                print("Błąd: Nie znaleziono linku do pobrania pliku CSV")
                # Spróbuj zapisać screenshot do debugowania
                try:
                    page.screenshot(path="debug_register.png")
                    print("Zapisano screenshot do debug_register.png")
                except Exception:
                    pass
                browser.close()
                return False
            
            # Pobierz pełny URL
            href = download_link.get_attribute('href')
            if href.startswith('/'):
                # Relatywny URL - dodaj domenę
                base_url = "https://www.gov.pl"
                file_url = base_url + href
            else:
                file_url = href
            
            print(f"Pobieranie pliku z: {file_url}")
            
            # Pobierz plik używając request context
            response = context.request.get(file_url)
            
            if response.status == 200:
                # Zapisz plik
                with open(OUTPUT_FILE, 'wb') as f:
                    f.write(response.body())
                
                file_size = os.path.getsize(OUTPUT_FILE)
                file_size_mb = file_size / (1024 * 1024)
                print(f"✓ Pobrano plik: {OUTPUT_FILE}")
                print(f"  Rozmiar: {file_size_mb:.2f} MB")
                return True
            else:
                print(f"Błąd: Nie udało się pobrać pliku. Status: {response.status}")
                browser.close()
                return False
            
        except Exception as e:
            print(f"Błąd podczas pobierania pliku: {e}")
            import traceback
            traceback.print_exc()
            browser.close()
            return False
        finally:
            browser.close()


if __name__ == "__main__":
    success = download_register_csv()
    if success:
        print(f"\nPlik zapisany w: {OUTPUT_FILE}")
    else:
        print("\nNie udało się pobrać pliku")

