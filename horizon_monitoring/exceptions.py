"""Własne wyjątki dla aplikacji PL Monitoring."""


class PLMonitoringError(Exception):
    """Bazowy wyjątek dla wszystkich błędów aplikacji."""
    pass


class ConfigurationError(PLMonitoringError):
    """Błąd konfiguracji - brak pliku, nieprawidłowy format, etc."""
    pass


class DataFetchError(PLMonitoringError):
    """Błąd podczas pobierania danych z zewnętrznego źródła."""
    pass


class DataParseError(PLMonitoringError):
    """Błąd podczas parsowania danych."""
    pass


class ValidationError(PLMonitoringError):
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

