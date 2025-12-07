#!/usr/bin/env python3
"""
Skrypt monitoringu aktów prawnych z tagami finansowymi na RCL
Wyszukuje akty prawne z określonymi hasłami przedmiotowymi zaktualizowane w danym zakresie dat.
"""

import json
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional
from urllib.parse import urlencode

from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright


# Konfiguracja
BASE_URL = "https://legislacja.rcl.gov.pl"
SEARCH_URL = "https://legislacja.rcl.gov.pl/szukaj?_typeId=1&progress=&status=&tenure=&createDateFrom=&createDateTo=&title=&_keywordId=1&applicantId=&periodId=&_deptId=1&_wordkeyId=1&amended=&repealed=&topic=&number=&_isUEAct=on&_isActEstablishingNumber=on&_isTKAct=on&_isSeparateMode=on&_isDU=on&_isNumerSejm=on&activeTab=tab1&sKey=modifiedDate&sOrder=desc#list"
FINANCIAL_TAGS_FILE = Path("config/financial.json")
OUTPUT_FILE = Path("financial_results.json")


def parse_polish_date(date_str: str) -> Optional[datetime]:
    """
    Parsuje polską datę w formacie DD-MM-YYYY
    """
    try:
        date_str = date_str.strip()
        return datetime.strptime(date_str, "%d-%m-%Y")
    except ValueError:
        return None


def load_financial_tags() -> List[Dict]:
    """
    Wczytuje tagi z pliku konfiguracyjnego
    Zwraca listę obiektów z id i name
    Obsługuje zarówno format z obiektami {id, name} jak i prostą listę ID
    """
    try:
        with open(FINANCIAL_TAGS_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            tags = data.get('tags', [])
            
            # Obsługa różnych formatów
            tag_list = []
            for tag in tags:
                if isinstance(tag, dict):
                    # Format z obiektem {id, name}
                    tag_id = tag.get('id')
                    tag_name = tag.get('name', '')
                    if tag_id is not None:
                        tag_list.append({
                            'id': int(tag_id),
                            'name': tag_name
                        })
                elif isinstance(tag, (int, str)):
                    # Prosty format z samym ID - nie mamy nazwy
                    tag_list.append({
                        'id': int(tag),
                        'name': ''
                    })
            
            return tag_list
    except FileNotFoundError:
        print(f"Błąd: Nie znaleziono pliku {FINANCIAL_TAGS_FILE}")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Błąd parsowania JSON: {e}")
        sys.exit(1)


def search_by_tag(tag_id: int, start_date: datetime, end_date: datetime) -> List[Dict]:
    """
    Wykonuje wyszukiwanie dla danego tagu i zwraca listę aktów
    Buduje URL bezpośrednio z parametrem wordkeyId zamiast klikać w formularz
    """
    print(f"\nWyszukiwanie dla tagu ID: {tag_id}...")
    
    # Zbuduj URL bezpośrednio z parametrem wordkeyId
    # Bazowy URL z parametrami
    base_url = "https://legislacja.rcl.gov.pl/szukaj"
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
        'wordkeyId': str(tag_id),  # Dodajemy ID hasła przedmiotowego
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
    
    # Zbuduj URL z parametrami
    search_url = f"{base_url}?{urlencode(params)}#list"
    
    print(f"Otwieranie URL z hasłem przedmiotowym ID: {tag_id}...")
    
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
            # Otwórz stronę z wynikami bezpośrednio
            print("Ładowanie strony z wynikami...")
            page.goto(search_url, wait_until="networkidle", timeout=30000)
            
            # Poczekaj na załadowanie strony z wynikami
            print("Oczekiwanie na załadowanie wyników...")
            page.wait_for_timeout(2000)  # Dodatkowe oczekiwanie na renderowanie
            
            # Parsuj wyniki
            results = parse_search_results(page, start_date, end_date)
            
            browser.close()
            return results
            
        except Exception as e:
            print(f"Błąd podczas wyszukiwania: {e}")
            browser.close()
            return []


def parse_search_results(page, start_date: datetime, end_date: datetime) -> List[Dict]:
    """
    Parsuje tabelę wyników z HTML i filtruje według zakresu dat
    """
    # Pobierz HTML strony
    html = page.content()
    soup = BeautifulSoup(html, 'html.parser')
    
    # Znajdź tabelę z wynikami
    # Może być kilka tabel, szukamy tej z wynikami wyszukiwania
    tables = soup.find_all('table')
    table = None
    
    for t in tables:
        # Szukamy tabeli, która ma wiersze z linkami do projektów
        rows = t.find_all('tr')
        if len(rows) > 1:  # Ma więcej niż nagłówek
            first_data_row = rows[1] if len(rows) > 1 else None
            if first_data_row and first_data_row.find('a', href=re.compile(r'/projekt/\d+')):
                table = t
                break
    
    if not table:
        print("Nie znaleziono tabeli z wynikami")
        return []
    
    results = []
    rows = table.find_all('tr')[1:]  # Pomijamy nagłówek
    
    print(f"Znaleziono {len(rows)} wierszy w tabeli")
    
    for row_idx, row in enumerate(rows):
        cells = row.find_all(['td', 'th'])
        
        # Sprawdź czy pierwsza kolumna to checkbox (zawiera link do /zapisz/projekt)
        has_checkbox = False
        if len(cells) > 0:
            first_cell = cells[0]
            if first_cell.find('a', href=re.compile(r'/zapisz/projekt')):
                has_checkbox = True
        
        # Dostosuj indeksy kolumn w zależności od obecności checkboxa
        if has_checkbox:
            # Struktura: checkbox, tytuł, wnioskodawca, numer, data_utworzenia, data_modyfikacji
            if len(cells) < 6:
                continue
            title_cell_idx = 1
            number_cell_idx = 3
            updated_date_cell_idx = 5
        else:
            # Struktura: tytuł, wnioskodawca, numer, data_utworzenia, data_modyfikacji
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
                if row_idx < 3:  # Debug dla pierwszych 3 wierszy
                    print(f"  DEBUG wiersz {row_idx}: Nie znaleziono linku do projektu w kolumnie {title_cell_idx}")
                continue
            
            title = title_link.get_text(strip=True)
            href = title_link.get('href', '')
            
            # Wyciągnij ID z URL (np. /projekt/12345)
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
                if row_idx < 3:  # Debug dla pierwszych 3 wierszy
                    print(f"  DEBUG wiersz {row_idx}: Brak daty modyfikacji")
                continue
            
            # Parsuj datę
            updated_date = parse_polish_date(updated_date_str)
            if not updated_date:
                if row_idx < 3:  # Debug dla pierwszych 3 wierszy
                    print(f"  DEBUG wiersz {row_idx}: Nie można sparsować daty: '{updated_date_str}'")
                continue
            
            # Debug dla pierwszych wierszy
            if row_idx < 3:
                print(f"  DEBUG wiersz {row_idx}: Data modyfikacji: {updated_date_str} -> {updated_date}, zakres: {start_date} - {end_date}")
            
            # Filtruj według zakresu dat
            if start_date <= updated_date <= end_date:
                results.append({
                    "title": title,
                    "id": project_id,
                    "updated_date": updated_date_str,
                    "number": number
                })
                print(f"  ✓ Znaleziono: {title[:50]}... (zaktualizowany: {updated_date_str})")
        
        except Exception as e:
            print(f"Błąd parsowania wiersza: {e}")
            continue
    
    return results


def save_results(all_results: List[Dict], start_date: datetime, end_date: datetime, output_file: Path):
    """
    Zapisuje wyniki do pliku JSON
    """
    output_data = {
        "search_date": datetime.now().strftime("%Y-%m-%d"),
        "date_range": {
            "start": start_date.strftime("%Y-%m-%d"),
            "end": end_date.strftime("%Y-%m-%d")
        },
        "results": all_results
    }
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)
    
    print(f"\nZapisano {len(all_results)} wyników do pliku: {output_file}")


def main():
    """
    Główna funkcja monitoringu
    """
    if len(sys.argv) != 3:
        print("Użycie: python monitor_financial.py <data_początkowa> <data_końcowa>")
        print("Format dat: YYYY-MM-DD")
        sys.exit(1)
    
    # Parsuj daty
    try:
        start_date = datetime.strptime(sys.argv[1], "%Y-%m-%d")
        end_date = datetime.strptime(sys.argv[2], "%Y-%m-%d")
    except ValueError as e:
        print(f"Błąd parsowania dat: {e}")
        print("Format dat: YYYY-MM-DD")
        sys.exit(1)
    
    print(f"Monitoring aktów prawnych z tagami finansowymi")
    print(f"Zakres dat: {start_date.strftime('%Y-%m-%d')} - {end_date.strftime('%Y-%m-%d')}")
    
    # Wczytaj tagi
    tags = load_financial_tags()
    print(f"Znaleziono {len(tags)} tag(ów) do monitorowania:")
    for tag in tags:
        if tag['name']:
            print(f"  - ID: {tag['id']}, Nazwa: {tag['name']}")
        else:
            print(f"  - ID: {tag['id']}")
    
    # Wyszukaj dla każdego tagu
    all_results = []
    for tag in tags:
        tag_id = tag['id']
        results = search_by_tag(tag_id, start_date, end_date)
        all_results.extend(results)
    
    # Zapisz wyniki
    if all_results:
        save_results(all_results, start_date, end_date, OUTPUT_FILE)
    else:
        print("\nNie znaleziono żadnych aktów w podanym zakresie dat")


if __name__ == "__main__":
    main()

