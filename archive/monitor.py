#!/usr/bin/env python3
"""
Skrypt monitoringu projektów RCL
Sprawdza czy w określonym okresie wystąpiły zmiany w projektach ustaw.
"""

import json
import re
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional

import requests
from bs4 import BeautifulSoup
from dateutil import parser as date_parser


# Konfiguracja
BASE_URL = "https://legislacja.rcl.gov.pl"
PROJECTS_FILE = Path("config/projects.json")
OUTPUT_FILE = Path("config/projects.json")  # Zapisujemy z powrotem do tego samego pliku


def parse_polish_date(date_str: str) -> Optional[datetime]:
    """
    Parsuje polską datę w formacie DD-MM-YYYY
    """
    try:
        # Usuwamy ewentualne białe znaki
        date_str = date_str.strip()
        # Format: DD-MM-YYYY
        return datetime.strptime(date_str, "%d-%m-%Y")
    except ValueError:
        return None


def fetch_project_page(project_id: int) -> Optional[BeautifulSoup]:
    """
    Pobiera stronę projektu z RCL
    """
    url = f"{BASE_URL}/projekt/{project_id}"
    
    # Nagłówki HTTP symulujące przeglądarkę
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'pl-PL,pl;q=0.9,en-US;q=0.8,en;q=0.7',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        return BeautifulSoup(response.content, 'html.parser')
    except requests.RequestException as e:
        print(f"Błąd przy pobieraniu projektu {project_id}: {e}")
        return None


def extract_modification_dates(soup: BeautifulSoup) -> List[datetime]:
    """
    Wyciąga wszystkie daty modyfikacji z etapów projektu
    """
    dates = []
    
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
    
    return dates


def check_date_in_range(dates: List[datetime], start_date: datetime, end_date: datetime) -> Optional[datetime]:
    """
    Sprawdza czy któraś z dat mieści się w zakresie [start_date, end_date]
    Zwraca najnowszą datę z zakresu lub None
    """
    dates_in_range = [d for d in dates if start_date <= d <= end_date]
    if dates_in_range:
        return max(dates_in_range)
    return None


def monitor_projects(start_date_str: str, end_date_str: str):
    """
    Główna funkcja monitoringu
    """
    # Parsowanie dat
    try:
        start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
        end_date = datetime.strptime(end_date_str, "%Y-%m-%d")
    except ValueError as e:
        print(f"Błąd parsowania dat: {e}")
        print("Użyj formatu: YYYY-MM-DD")
        return
    
    # Wczytanie listy projektów
    if not PROJECTS_FILE.exists():
        print(f"Plik {PROJECTS_FILE} nie istnieje!")
        return
    
    with open(PROJECTS_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    projects = data.get('projects', [])
    if not projects:
        print("Brak projektów do monitorowania!")
        return
    
    print(f"Monitoring projektów od {start_date_str} do {end_date_str}")
    print(f"Znaleziono {len(projects)} projektów do sprawdzenia\n")
    
    # Iteracja przez projekty
    for project in projects:
        # Obsługa zarówno formatu z obiektem jak i tylko ID
        if isinstance(project, dict):
            project_id = project.get('id')
            project_title = project.get('title', f'Projekt {project_id}')
        else:
            project_id = project
            project_title = f'Projekt {project_id}'
        
        print(f"Sprawdzam: {project_title} (ID: {project_id})...")
        
        # Pobranie strony projektu
        soup = fetch_project_page(project_id)
        if not soup:
            continue
        
        # Wyciągnięcie dat modyfikacji
        modification_dates = extract_modification_dates(soup)
        
        if not modification_dates:
            print(f"  Brak dat modyfikacji")
            continue
        
        print(f"  Znaleziono {len(modification_dates)} dat modyfikacji")
        
        # Sprawdzenie czy któraś data mieści się w zakresie
        last_hit = check_date_in_range(modification_dates, start_date, end_date)
        
        if last_hit:
            # Zapisanie wyniku
            if isinstance(project, dict):
                project['last_hit'] = last_hit.strftime("%d-%m-%Y")
            else:
                # Konwersja na dict jeśli było tylko ID
                project_dict = {
                    'id': project_id,
                    'last_hit': last_hit.strftime("%d-%m-%Y")
                }
                # Znajdź indeks i zamień
                idx = projects.index(project)
                projects[idx] = project_dict
            
            print(f"  ✓ Ostatnia zmiana: {last_hit.strftime('%d-%m-%Y')}")
        else:
            print(f"  Brak zmian w okresie")
        
        print()
    
    # Zapisanie zaktualizowanych danych
    data['projects'] = projects
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"Wyniki zapisane do {OUTPUT_FILE}")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) != 3:
        print("Użycie: python monitor.py <data_początkowa> <data_końcowa>")
        print("Format dat: YYYY-MM-DD")
        print("\nPrzykład:")
        print("  python monitor.py 2025-01-01 2025-12-31")
        sys.exit(1)
    
    start_date = sys.argv[1]
    end_date = sys.argv[2]
    
    monitor_projects(start_date, end_date)

