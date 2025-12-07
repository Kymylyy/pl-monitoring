# Instrukcja użycia - Horizon Monitoring

## Szybki start

System monitoruje projekty legislacyjne w Polsce na trzech poziomach:

1. **KPRM** - Rejestr prac legislacyjnych (identyfikacja projektów implementujących akty UE)
2. **RCL** - Rządowy Proces Legislacyjny (identyfikacja po hasłach przedmiotowych, monitoring konkretnych projektów)
3. **Sejm** - Proces legislacyjny w Sejmie (monitoring pełnego przebiegu procesu)

## Dlaczego taka kolejność?

- **KPRM** - punkt startowy: znajdź projekty implementujące konkretne dyrektywy/rozporządzenia UE (np. "2023/2225")
- **RCL** - dwa poziomy: najpierw identyfikacja po hasłach przedmiotowych, potem monitoring konkretnych projektów
- **Sejm** - finalny etap: śledzenie pełnego przebiegu procesu legislacyjnego

## Podstawowe użycie

### 1. Analiza rejestru KPRM (identyfikacja projektów UE)

```bash
# Pobierz aktualny rejestr
python scripts/fetch_kprm_register.py

# Przeanalizuj po numerach aktów UE i słowach kluczowych
python scripts/analyze_kprm_register.py 2025-01-01 2025-12-31
```

**Kiedy używać:** Chcesz znaleźć projekty implementujące konkretne akty prawne UE (np. dyrektywa 2023/2225 o kredycie konsumenckim).

**Konfiguracja:** `config/kprm_keywords.json` - dodaj numery dyrektyw/rozporządzeń UE i kluczowe słowa

**Dlaczego konkretne numery aktów UE?** Projekty implementujące dyrektywy UE zawierają w opisach konkretne numery aktów (np. "2023/2225", "dyrektywa 2023/2225"). To najpewniejszy sposób na znalezienie projektów wdrożeniowych.

**Przykład:** Aby znaleźć projekty implementujące dyrektywę o kredycie konsumenckim, dodaj do konfiguracji:
- `"2023/2225"` - numer dyrektywy
- `"dyrektywa 2023/2225"` - pełna nazwa
- `"kredyt konsumencki"` - temat projektu

### 2. Monitoring aktów RCL po hasłach przedmiotowych (identyfikacja)

```bash
python scripts/monitor_rcl_tags.py 2025-01-01 2025-12-31
```

**Kiedy używać:** Chcesz znaleźć wszystkie akty prawne z określonym hasłem przedmiotowym (np. "BANKOWE PRAWO").

**Konfiguracja:** `config/rcl_subject_tags.json` - dodaj hasła przedmiotowe (wordkeyId)

**Dlaczego hasła przedmiotowe?** Oficjalna kategoryzacja RCL - precyzyjne wyniki, nie zależne od słów w tekście.

**To pierwszy poziom RCL** - identyfikacja projektów, które mogą być związane z tematem.

### 3. Monitoring konkretnych projektów RCL (monitoring)

```bash
python scripts/monitor_rcl_projects.py 2025-01-01 2025-12-31
```

**Kiedy używać:** Masz konkretne projekty RCL (znasz ID) i chcesz śledzić ich zmiany.

**Konfiguracja:** `config/projects.json` - dodaj projekty z `source: "rcl"`

**To drugi poziom RCL** - monitoring znalezionych projektów.

### 4. Monitoring konkretnych projektów Sejm

```bash
python scripts/monitor_sejm_projects.py 2025-01-01 2025-12-31
```

**Kiedy używać:** Masz konkretne projekty Sejm (znasz numer druku) i chcesz śledzić pełny przebieg procesu.

**Konfiguracja:** `config/projects.json` - dodaj projekty z `source: "sejm"`

**Dlaczego scraping HTML?** API Sejmu (`/processes`) nie jest aktualizowane, a `/prints` pokazuje tylko druki, nie pełny przebieg. Strona HTML zawiera wszystkie etapy: głosowania, decyzje Senatu, Prezydenta.

## Format dat

Wszystkie skrypty używają formatu: **YYYY-MM-DD**

Przykład: `2025-01-01`

## Wyniki

- **KPRM:** Zapis do `data/register_results.json` - lista projektów zawierających numery aktów UE/słowa kluczowe
- **Tagi RCL:** Zapis do `data/financial_results.json` - lista aktów z określonym hasłem przedmiotowym
- **Projekty RCL/Sejm:** Automatyczna aktualizacja `config/projects.json` z polem `last_hit`
- **Projekty Sejm:** Dodatkowo pole `referred_to` z pełnym przebiegiem procesu

## Typowy workflow

1. **Identyfikacja w KPRM** - znajdź projekty implementujące konkretne akty UE (np. "2023/2225")
2. **Identyfikacja w RCL** - użyj monitoringu tagów RCL, aby znaleźć projekty z określonym hasłem przedmiotowym
3. **Dodaj do konfiguracji** - skopiuj ID/numer do `config/projects.json`
4. **Monitoruj zmiany** - uruchamiaj regularnie monitoring projektów RCL i Sejm
5. **Śledź przebieg** - dla projektów Sejm sprawdzaj `referred_to` z pełnym przebiegiem procesu
