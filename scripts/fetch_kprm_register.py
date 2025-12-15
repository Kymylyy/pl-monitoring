#!/usr/bin/env python3
"""
Entry point do pobierania rejestru prac legislacyjnych z KPRM.

Użycie:
    python scripts/fetch_kprm_register.py
"""

import sys
from pathlib import Path

# Dodaj główny katalog projektu do ścieżki
sys.path.insert(0, str(Path(__file__).parent.parent))

from pl_monitoring.fetchers.kprm_register import KPRMRegisterFetcher


def main():
    """Główna funkcja."""
    fetcher = KPRMRegisterFetcher()
    success = fetcher.download()
    
    if success:
        print(f"\nPlik zapisany w: {fetcher.output_file}")
    else:
        print("\nNie udało się pobrać pliku")
        sys.exit(1)


if __name__ == "__main__":
    main()

