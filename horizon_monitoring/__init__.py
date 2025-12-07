"""
Horizon Monitoring - System monitoringu projektów legislacyjnych

System do monitorowania zmian w projektach ustaw z RCL (Rządowy Proces Legislacyjny)
oraz analizy rejestru prac legislacyjnych KPRM.
"""

__version__ = "1.0.0"

# Inicjalizacja logowania przy imporcie pakietu
from .utils.logger import setup_logger

# Konfiguruj domyślny logger
setup_logger()

