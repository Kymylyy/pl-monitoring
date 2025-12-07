# Horizon Monitoring

System monitoringu projektów legislacyjnych w Polsce - śledzenie zmian w projektach ustaw od etapu KPRM, przez RCL, aż do Sejmu i decyzji Prezydenta.

## Co monitorujemy?

1. **KPRM** - Rejestr prac legislacyjnych (identyfikacja projektów implementujących akty UE)
2. **RCL** - Rządowy Proces Legislacyjny (identyfikacja po hasłach przedmiotowych, monitoring konkretnych projektów)
3. **Sejm** - Pełny przebieg procesu legislacyjnego (czytania, głosowania, decyzje Senatu/Prezydenta)

## Szybki start

### Instalacja

```bash
# Instalacja pakietu
pip install -e .

# Instalacja przeglądarki Playwright (wymagana)
playwright install chromium
```

### Podstawowe użycie

```bash
# 1. Analiza rejestru KPRM (identyfikacja projektów UE)
python scripts/fetch_kprm_register.py
python scripts/analyze_kprm_register.py 2025-01-01 2025-12-31

# 2. Monitoring aktów RCL po hasłach przedmiotowych (identyfikacja)
python scripts/monitor_rcl_tags.py 2025-01-01 2025-12-31

# 3. Monitoring konkretnych projektów RCL (monitoring)
python scripts/monitor_rcl_projects.py 2025-01-01 2025-12-31

# 4. Monitoring konkretnych projektów Sejm
python scripts/monitor_sejm_projects.py 2025-01-01 2025-12-31
```

📖 **Szczegółowa instrukcja:** Zobacz [USAGE.md](USAGE.md)

## Struktura projektu

```
horizon-monitoring/
├── horizon_monitoring/    # Główny pakiet Python
│   ├── monitors/          # Moduły monitoringu (RCL, Sejm)
│   ├── fetchers/          # Pobieranie danych (KPRM)
│   ├── analyzers/         # Analiza danych
│   └── utils/             # Narzędzia pomocnicze
├── scripts/               # Skrypty uruchomieniowe
├── config/                # Pliki konfiguracyjne JSON
└── data/                  # Wyniki i dane
```

## Konfiguracja

System używa 3 plików konfiguracyjnych JSON:

- `config/kprm_keywords.json` - Numery aktów UE i słowa kluczowe do wyszukiwania w KPRM
- `config/rcl_subject_tags.json` - Hasła przedmiotowe RCL (identyfikacja)
- `config/projects.json` - Lista projektów do monitorowania (RCL + Sejm)

📖 **Szczegółowy przewodnik:** Zobacz [CONFIGURATION_GUIDE.md](CONFIGURATION_GUIDE.md)

## Dokumentacja

- **[USAGE.md](USAGE.md)** - Instrukcja użycia z wyjaśnieniem dlaczego tak a nie inaczej
- **[CONFIGURATION_GUIDE.md](CONFIGURATION_GUIDE.md)** - Szczegółowy przewodnik konfiguracji
- **[TODO.md](TODO.md)** - Plan rozwoju systemu

## Wymagania

- Python 3.8+
- Zobacz `pyproject.toml` lub `requirements.txt` dla pełnej listy zależności

## Testy

```bash
pytest
pytest --cov=horizon_monitoring --cov-report=html
```

## Licencja

MIT
