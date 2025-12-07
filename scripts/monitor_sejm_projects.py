#!/usr/bin/env python3
"""
Entry point do monitoringu konkretnych projektów Sejm.

Użycie:
    python scripts/monitor_sejm_projects.py <data_początkowa> <data_końcowa>

Format dat: YYYY-MM-DD

Przykład:
    python scripts/monitor_sejm_projects.py 2025-01-01 2025-12-31
"""

import sys
from datetime import datetime
from pathlib import Path

# Dodaj główny katalog projektu do ścieżki
sys.path.insert(0, str(Path(__file__).parent.parent))

from horizon_monitoring.monitors.sejm_project_monitor import SejmProjectMonitor


def main():
    """Główna funkcja."""
    if len(sys.argv) != 3:
        print("Użycie: python scripts/monitor_sejm_projects.py <data_początkowa> <data_końcowa>")
        print("Format dat: YYYY-MM-DD")
        print("\nPrzykład:")
        print("  python scripts/monitor_sejm_projects.py 2025-01-01 2025-12-31")
        sys.exit(1)
    
    # Parsowanie dat
    try:
        start_date = datetime.strptime(sys.argv[1], "%Y-%m-%d")
        end_date = datetime.strptime(sys.argv[2], "%Y-%m-%d")
    except ValueError as e:
        print(f"Błąd parsowania dat: {e}")
        print("Użyj formatu: YYYY-MM-DD")
        sys.exit(1)
    
    # Monitoring
    monitor = SejmProjectMonitor()
    monitor.monitor(start_date, end_date)


if __name__ == "__main__":
    main()

