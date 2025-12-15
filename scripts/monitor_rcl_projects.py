#!/usr/bin/env python3
"""
Entry point do monitoringu konkretnych projektów RCL.

Użycie:
    python scripts/monitor_rcl_projects.py <data_początkowa> <data_końcowa>

Format dat: YYYY-MM-DD

Przykład:
    python scripts/monitor_rcl_projects.py 2025-01-01 2025-12-31
"""

import sys
from datetime import datetime
from pathlib import Path

# Dodaj główny katalog projektu do ścieżki
sys.path.insert(0, str(Path(__file__).parent.parent))

from pl_monitoring.monitors.rcl_project_monitor import RCLProjectMonitor
from pl_monitoring.utils.logger import get_logger

logger = get_logger(__name__)


def main():
    """Główna funkcja."""
    if len(sys.argv) != 3:
        print("Użycie: python scripts/monitor_rcl_projects.py <data_początkowa> <data_końcowa>")
        print("Format dat: YYYY-MM-DD")
        print("\nPrzykład:")
        print("  python scripts/monitor_rcl_projects.py 2025-01-01 2025-12-31")
        sys.exit(1)
    
    # Parsowanie dat
    try:
        start_date = datetime.strptime(sys.argv[1], "%Y-%m-%d")
        end_date = datetime.strptime(sys.argv[2], "%Y-%m-%d")
    except ValueError as e:
        logger.error(f"Błąd parsowania dat: {e}")
        print(f"Błąd parsowania dat: {e}")
        print("Użyj formatu: YYYY-MM-DD")
        sys.exit(1)
    
    # Walidacja dat
    if start_date > end_date:
        logger.error(f"Data początkowa ({start_date.strftime('%Y-%m-%d')}) jest późniejsza niż data końcowa ({end_date.strftime('%Y-%m-%d')})")
        print(f"Błąd: Data początkowa nie może być późniejsza niż data końcowa")
        sys.exit(1)
    
    # Monitoring
    try:
        monitor = RCLProjectMonitor()
        monitor.monitor(start_date, end_date)
    except Exception as e:
        logger.exception("Błąd podczas monitoringu projektów RCL")
        print(f"Błąd: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

