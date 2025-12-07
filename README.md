# Horizon Monitoring

System monitoringu projektów legislacyjnych w Polsce - śledzenie zmian w projektach ustaw od etapu KPRM, przez RCL, aż do Sejmu i decyzji Prezydenta.

## Co monitorujemy?

1. **KPRM** - Rejestr prac legislacyjnych (analiza tekstowa, w szczególności identyfikacja projektów implementujących akty UE)
2. **RCL** - Rządowy Proces Legislacyjny (identyfikacja po hasłach przedmiotowych, monitoring konkretnych projektów)
3. **Sejm** - Pełny przebieg procesu legislacyjnego (czytania, głosowania, decyzje Senatu/Prezydenta)

## Szybki start

### Instalacja

```bash
pip install -e .
playwright install chromium
```

### Podstawowe użycie

```bash
# 1. Analiza rejestru KPRM (analiza tekstowa, identyfikacja projektów UE)
python scripts/fetch_kprm_register.py
python scripts/analyze_kprm_register.py 2025-01-01 2025-12-31

# 2. Monitoring aktów RCL po hasłach przedmiotowych (identyfikacja)
python scripts/monitor_rcl_tags.py 2025-01-01 2025-12-31

# 3. Monitoring konkretnych projektów RCL (monitoring)
python scripts/monitor_rcl_projects.py 2025-01-01 2025-12-31

# 4. Monitoring konkretnych projektów Sejm
python scripts/monitor_sejm_projects.py 2025-01-01 2025-12-31
```

📖 **Szczegółowa instrukcja:** [USAGE.md](USAGE.md)  
📖 **Przewodnik konfiguracji:** [CONFIGURATION_GUIDE.md](CONFIGURATION_GUIDE.md)

## Planowane funkcjonalności

### Wyszukiwanie projektów RCL po identyfikatorach zewnętrznych

**Status:** W planach (obecnie nieobsługiwane przez RCL)

**Cel:** Wyszukiwanie projektów w RCL po:
- Numerze i tytule aktu prawnego Unii Europejskiej (np. "2023/2225")
- Numerze z wykazu prac legislacyjnych KPRM (np. "UD260", "UC2")

**Uwaga:** Ta funkcjonalność nie jest jeszcze zaimplementowana, ponieważ strona RCL obecnie nie obsługuje wyszukiwania po identyfikatorach zewnętrznych (pola formularza istnieją, ale wyszukiwanie nie zwraca wyników).

**Planowana implementacja:**
- Scrapowanie strony wyszukiwania RCL: `https://legislacja.rcl.gov.pl/szukaj?typeId=1&typeId=2&activeTab=tab2`
- Wypełnianie formularza wyszukiwania przy użyciu Playwright
- Parsowanie wyników wyszukiwania z tabeli HTML
- Automatyczne dodawanie znalezionych projektów do `config/projects.json`

📖 **Szczegóły:** [TODO.md](TODO.md)

## Dokumentacja

- **[USAGE.md](USAGE.md)** - Instrukcja użycia
- **[CONFIGURATION_GUIDE.md](CONFIGURATION_GUIDE.md)** - Przewodnik konfiguracji
- **[TODO.md](TODO.md)** - Plan rozwoju systemu

## Wymagania

- Python 3.8+
- Zobacz `pyproject.toml` lub `requirements.txt` dla pełnej listy zależności

## Licencja

Proprietary - All Rights Reserved
