# Instrukcja użycia - Horizon Monitoring

## Szybki start

System monitoruje projekty legislacyjne w Polsce na trzech poziomach:

1. **RCL** - Rządowy Proces Legislacyjny (przygotowanie projektu)
2. **Sejm** - Proces legislacyjny w Sejmie (czytania, głosowania, decyzje Senatu/Prezydenta)
3. **KPRM** - Rejestr prac legislacyjnych (analiza tekstowa)

## Dlaczego trzy źródła?

- **RCL** - śledzimy projekty od początku, zanim trafią do Sejmu
- **Sejm** - pełny przebieg procesu (nie tylko druki, ale wszystkie etapy: głosowania, decyzje)
- **KPRM** - wyszukiwanie projektów po słowach kluczowych w opisach (gdy nie znamy konkretnego projektu)

## Podstawowe użycie

### 1. Monitoring konkretnych projektów RCL

```bash
python scripts/monitor_rcl_projects.py 2025-01-01 2025-12-31
```

**Kiedy używać:** Masz konkretne projekty RCL (znasz ID) i chcesz śledzić ich zmiany.

**Konfiguracja:** `config/projects.json` - dodaj projekty z `source: "rcl"`

### 2. Monitoring konkretnych projektów Sejm

```bash
python scripts/monitor_sejm_projects.py 2025-01-01 2025-12-31
```

**Kiedy używać:** Masz konkretne projekty Sejm (znasz numer druku) i chcesz śledzić pełny przebieg procesu.

**Konfiguracja:** `config/projects.json` - dodaj projekty z `source: "sejm"`

**Dlaczego scraping HTML?** API Sejmu (`/processes`) nie jest aktualizowane, a `/prints` pokazuje tylko druki, nie pełny przebieg. Strona HTML zawiera wszystkie etapy: głosowania, decyzje Senatu, Prezydenta.

### 3. Monitoring aktów RCL po hasłach przedmiotowych

```bash
python scripts/monitor_rcl_tags.py 2025-01-01 2025-12-31
```

**Kiedy używać:** Chcesz znaleźć wszystkie akty prawne z określonym hasłem przedmiotowym (np. "BANKOWE PRAWO").

**Konfiguracja:** `config/rcl_subject_tags.json` - dodaj hasła przedmiotowe (wordkeyId)

**Dlaczego hasła przedmiotowe?** Oficjalna kategoryzacja RCL - precyzyjne wyniki, nie zależne od słów w tekście.

### 4. Analiza rejestru KPRM

```bash
# Pobierz aktualny rejestr
python scripts/fetch_kprm_register.py

# Przeanalizuj po słowach kluczowych
python scripts/analyze_kprm_register.py 2025-01-01 2025-12-31
```

**Kiedy używać:** Chcesz znaleźć projekty zawierające określone słowa w opisach (np. "budżet", "podatek").

**Konfiguracja:** `config/kprm_keywords.json` - dodaj kategorie i słowa kluczowe

**Dlaczego słowa kluczowe?** Wyszukiwanie semantyczne - znajdziesz projekty związane z tematem, nawet jeśli nie są oficjalnie skategoryzowane.

## Format dat

Wszystkie skrypty używają formatu: **YYYY-MM-DD**

Przykład: `2025-01-01`

## Wyniki

- **Projekty RCL/Sejm:** Automatyczna aktualizacja `config/projects.json` z polem `last_hit`
- **Projekty Sejm:** Dodatkowo pole `referred_to` z pełnym przebiegiem procesu
- **Tagi RCL:** Zapis do `data/financial_results.json`
- **KPRM:** Zapis do `data/register_results.json`

## Typowy workflow

1. **Znajdź projekty** - użyj monitoringu tagów RCL lub analizy KPRM
2. **Dodaj do konfiguracji** - skopiuj ID/numer do `config/projects.json`
3. **Monitoruj zmiany** - uruchamiaj regularnie monitoring projektów
4. **Śledź przebieg** - dla projektów Sejm sprawdzaj `referred_to` z pełnym przebiegiem

