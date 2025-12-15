# PL Monitoring

System monitoringu projektów legislacyjnych w Polsce - śledzenie zmian w projektach ustaw od etapu KPRM, przez RCL, aż do Sejmu i decyzji Prezydenta.

## 📋 Opis

PL Monitoring to kompleksowe narzędzie do automatycznego monitorowania procesu legislacyjnego w Polsce. System umożliwia:

- **Identyfikację projektów** implementujących konkretne akty prawne UE
- **Wyszukiwanie projektów** w RCL po hasłach przedmiotowych lub identyfikatorach zewnętrznych
- **Monitoring zmian** w konkretnych projektach ustaw
- **Śledzenie pełnego przebiegu** procesu legislacyjnego w Sejmie (czytania, głosowania, decyzje Senatu i Prezydenta)

## ✨ Funkcjonalności

### 🔍 Identyfikacja projektów

- **KPRM** - Analiza rejestru prac legislacyjnych po numerach aktów UE i słowach kluczowych
- **RCL - Hasła przedmiotowe** - Wyszukiwanie projektów po oficjalnych hasłach przedmiotowych RCL
- **RCL - Identyfikatory zewnętrzne** - Wyszukiwanie po numerze aktu UE lub numerze z wykazu KPRM

### 📊 Monitoring projektów

- **RCL** - Wykrywanie zmian w projektach w określonym zakresie dat
- **Sejm** - Scrapowanie pełnego przebiegu procesu legislacyjnego (czytania, głosowania, decyzje Senatu/Prezydenta)

## 🚀 Szybki start

### Wymagania

- Python 3.8+
- Chromium (instalowany przez Playwright)

### Instalacja

```bash
# Sklonuj repozytorium
git clone <repository-url>
cd pl-monitoring

# Zainstaluj zależności
pip install -e .

# Zainstaluj przeglądarkę Chromium
playwright install chromium
```

### Podstawowe użycie

```bash
# 1. Analiza rejestru KPRM (identyfikacja projektów UE)
python scripts/fetch_kprm_register.py
python scripts/analyze_kprm_register.py 2025-01-01 2025-12-31

# 2. Monitoring aktów RCL po hasłach przedmiotowych (identyfikacja)
python scripts/monitor_rcl_tags.py 2025-01-01 2025-12-31

# 2b. Wyszukiwanie projektów RCL po identyfikatorach zewnętrznych (identyfikacja)
python scripts/search_rcl_projects.py 2025-01-01 2025-12-31

# 3. Monitoring konkretnych projektów RCL (monitoring)
python scripts/monitor_rcl_projects.py 2025-01-01 2025-12-31

# 4. Monitoring konkretnych projektów Sejm
python scripts/monitor_sejm_projects.py 2025-01-01 2025-12-31
```

## 📖 Dokumentacja

- **[USAGE.md](USAGE.md)** - Szczegółowa instrukcja użycia wszystkich funkcjonalności
- **[CONFIGURATION_GUIDE.md](CONFIGURATION_GUIDE.md)** - Przewodnik konfiguracji plików JSON

## 🏗️ Struktura projektu

```
pl-monitoring/
├── config/                 # Pliki konfiguracyjne JSON
│   ├── projects.json       # Lista projektów do monitorowania
│   ├── kprm_keywords.json  # Numery aktów UE i słowa kluczowe
│   ├── rcl_subject_tags.json  # Hasła przedmiotowe RCL
│   └── rcl_search_queries.json  # Zapytania wyszukiwawcze RCL
├── data/                   # Wyniki i dane (gitignored)
├── scripts/                # Skrypty CLI
│   ├── fetch_kprm_register.py
│   ├── analyze_kprm_register.py
│   ├── monitor_rcl_tags.py
│   ├── search_rcl_projects.py
│   ├── monitor_rcl_projects.py
│   └── monitor_sejm_projects.py
├── pl_monitoring/     # Główny pakiet
│   ├── monitors/           # Klasy monitorujące różne źródła
│   ├── fetchers/           # Pobieranie danych
│   ├── analyzers/          # Analiza tekstowa
│   └── utils/              # Narzędzia pomocnicze
└── tests/                  # Testy jednostkowe
```

## ⚙️ Konfiguracja

System używa plików JSON do konfiguracji:

- **`config/kprm_keywords.json`** - Numery aktów UE i słowa kluczowe do wyszukiwania w rejestrze KPRM
- **`config/rcl_subject_tags.json`** - Hasła przedmiotowe RCL (wordkeyId) do identyfikacji projektów
- **`config/rcl_search_queries.json`** - Zapytania wyszukiwawcze po numerze aktu UE lub numerze KPRM
- **`config/projects.json`** - Lista konkretnych projektów RCL i Sejm do monitorowania

Szczegółowy opis każdego pliku znajdziesz w [CONFIGURATION_GUIDE.md](CONFIGURATION_GUIDE.md).

## 🔄 Typowy workflow

1. **Identyfikacja w KPRM** - Znajdź projekty implementujące konkretne akty UE
2. **Identyfikacja w RCL** - Użyj haseł przedmiotowych lub identyfikatorów zewnętrznych
3. **Dodaj do konfiguracji** - Skopiuj ID projektów do `config/projects.json`
4. **Monitoruj zmiany** - Uruchamiaj regularnie monitoring projektów RCL i Sejm
5. **Śledź przebieg** - Dla projektów Sejm sprawdzaj `referred_to` z pełnym przebiegiem procesu

## 📦 Zależności

Główne zależności:
- `requests` - Pobieranie danych HTTP
- `beautifulsoup4` - Parsowanie HTML
- `playwright` - Automatyzacja przeglądarki (scrapowanie RCL)
- `python-dateutil` - Obsługa dat
- `lxml` - Parser XML/HTML

Pełna lista w `pyproject.toml` lub `requirements.txt`.

## 🧪 Testy

```bash
# Uruchom testy
pytest

# Z pokryciem kodu
pytest --cov=pl_monitoring --cov-report=html
```

## 📝 Format dat

Wszystkie skrypty używają formatu: **YYYY-MM-DD** (np. `2025-01-01`)

## 📊 Wyniki

- **KPRM:** `data/register_results.json` - Lista projektów zawierających numery aktów UE/słowa kluczowe
- **Tagi RCL:** `data/financial_results.json` - Lista aktów z określonym hasłem przedmiotowym
- **Wyszukiwanie RCL:** `data/rcl_search_results_YYYY-MM-DD.json` - Lista projektów znalezionych po identyfikatorach zewnętrznych (format gotowy do wklejenia do `config/projects.json`)
- **Projekty RCL/Sejm:** Automatyczna aktualizacja `config/projects.json` z polem `last_hit` i `referred_to`

## 🔧 Rozwój

### Instalacja środowiska deweloperskiego

```bash
pip install -e ".[dev]"
```

### Narzędzia deweloperskie

- `black` - Formatowanie kodu
- `mypy` - Sprawdzanie typów
- `ruff` - Linter
- `pytest` - Testy

## 📄 Licencja

Proprietary - All Rights Reserved

## 👥 Autorzy

Kamil Mosoń
