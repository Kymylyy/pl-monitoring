#!/usr/bin/env python3
"""
Entry point do wyszukiwania projektów RCL po identyfikatorach zewnętrznych.

Użycie:
    python scripts/search_rcl_projects.py <data_początkowa> <data_końcowa>

Format dat: YYYY-MM-DD

Przykład:
    python scripts/search_rcl_projects.py 2025-01-01 2025-12-31
"""

import sys
from datetime import datetime
from pathlib import Path

# Dodaj główny katalog projektu do ścieżki
sys.path.insert(0, str(Path(__file__).parent.parent))

from pl_monitoring.monitors.rcl_search_monitor import RCLSearchMonitor


def main():
    """Główna funkcja."""
    if len(sys.argv) != 3:
        print("Użycie: python scripts/search_rcl_projects.py <data_początkowa> <data_końcowa>")
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
    
    # Walidacja dat
    if start_date > end_date:
        print(f"Błąd: Data początkowa ({start_date.strftime('%Y-%m-%d')}) nie może być późniejsza niż data końcowa ({end_date.strftime('%Y-%m-%d')})")
        sys.exit(1)
    
    # Wyszukiwanie
    monitor = RCLSearchMonitor()
    results = monitor.monitor(start_date, end_date)
    
    # Podsumowanie
    print(f"\n{'='*60}")
    print(f"Podsumowanie wyszukiwania:")
    print(f"  Zakres dat: {start_date.strftime('%Y-%m-%d')} - {end_date.strftime('%Y-%m-%d')}")
    print(f"  Znaleziono projektów: {len(results)}")
    print(f"  Plik wyników: {monitor.output_file}")
    print(f"{'='*60}")
    
    if results:
        print(f"\nZnalezione projekty:")
        for project in results:
            print(f"  - ID: {project.get('id')}, Tytuł: {project.get('title', '')[:60]}...")
        print(f"\nWyniki zapisane w formacie gotowym do wklejenia do config/projects.json")


if __name__ == "__main__":
    main()
