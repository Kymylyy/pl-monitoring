#!/usr/bin/env python3
"""
Entry point do monitoringu aktów prawnych w RCL na podstawie haseł przedmiotowych.

Użycie:
    python scripts/monitor_rcl_tags.py <data_początkowa> <data_końcowa>

Format dat: YYYY-MM-DD

Przykład:
    python scripts/monitor_rcl_tags.py 2025-01-01 2025-12-31
"""

import sys
from datetime import datetime
from pathlib import Path

# Dodaj główny katalog projektu do ścieżki
sys.path.insert(0, str(Path(__file__).parent.parent))

from pl_monitoring.monitors.rcl_tag_monitor import RCLTagMonitor


def main():
    """Główna funkcja."""
    if len(sys.argv) != 3:
        print("Użycie: python scripts/monitor_rcl_tags.py <data_początkowa> <data_końcowa>")
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
    
    # Monitoring
    monitor = RCLTagMonitor()
    monitor.monitor(start_date, end_date)


if __name__ == "__main__":
    main()

