"""Własne wyjątki dla aplikacji Horizon Monitoring."""


class HorizonMonitoringError(Exception):
    """Bazowy wyjątek dla wszystkich błędów aplikacji."""
    pass


class ConfigurationError(HorizonMonitoringError):
    """Błąd konfiguracji - brak pliku, nieprawidłowy format, etc."""
    pass


class DataFetchError(HorizonMonitoringError):
    """Błąd podczas pobierania danych z zewnętrznego źródła."""
    pass


class DataParseError(HorizonMonitoringError):
    """Błąd podczas parsowania danych."""
    pass


class ValidationError(HorizonMonitoringError):
    """Błąd walidacji danych wejściowych."""
    pass


class RCLConnectionError(DataFetchError):
    """Błąd połączenia z RCL."""
    pass


class KPRMConnectionError(DataFetchError):
    """Błąd połączenia z KPRM."""
    pass


class SejmConnectionError(DataFetchError):
    """Błąd połączenia z API Sejmu."""
    pass

