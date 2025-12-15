"""Stałe używane w aplikacji."""

# URL-e zewnętrznych serwisów
RCL_BASE_URL = "https://legislacja.rcl.gov.pl"
KPRM_REGISTER_URL = "https://www.gov.pl/web/premier/wplip-rm"
KPRM_DIRECT_CSV_URL = "https://www.gov.pl/register-file/Rejestr_20874195.csv"
SEJM_WWW_BASE_URL = "https://www.sejm.gov.pl"
SEJM_PROCESS_URL_TEMPLATE = "/Sejm10.nsf/PrzebiegProc.xsp?nr={number}"

# Timeouty (w sekundach)
HTTP_TIMEOUT = 10
PLAYWRIGHT_TIMEOUT = 30000
PLAYWRIGHT_WAIT_TIMEOUT = 2000

# Domyślne wartości
DEFAULT_DATE_FORMAT = "%Y-%m-%d"
POLISH_DATE_FORMAT = "%d-%m-%Y"
DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"

# User Agent
DEFAULT_USER_AGENT = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'

