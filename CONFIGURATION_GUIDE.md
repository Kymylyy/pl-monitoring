# Przewodnik konfiguracji

## Przegląd plików konfiguracyjnych

System używa **3 plików konfiguracyjnych JSON**, każdy służy do innego celu:

| Plik | Przeznaczenie | Gdzie używany | Format |
|------|---------------|---------------|--------|
| `projects.json` | Konkretne projekty RCL i Sejm do monitorowania | `monitor_rcl_projects.py`, `monitor_sejm_projects.py` | Lista projektów z ID i `source` |
| `kprm_keywords.json` | Słowa kluczowe do wyszukiwania w tekście KPRM | `analyze_kprm_register.py` | Kategorie → słowa (stringi) |
| `rcl_subject_tags.json` | Hasła przedmiotowe RCL (wordkeyId) | `monitor_rcl_tags.py` | Lista tagów z ID (numeryczne) |

---

## 1. `config/projects.json` - Projekty RCL i Sejm

**Cel:** Monitoring konkretnych projektów ustaw z RCL lub Sejmu.

**Kiedy używać:**
- Masz konkretne projekty ustaw, które chcesz monitorować
- Chcesz śledzić zmiany w znanych projektach
- Chcesz monitorować projekty zarówno z RCL jak i Sejmu w jednym pliku

**Format dla projektów RCL:**
```json
{
  "projects": [
    {
      "id": 12382311,
      "title": "Projekt ustawy o rynku kryptoaktywów",
      "number": "UC2",
      "source": "rcl"
    }
  ]
}
```

**Format dla projektów Sejm:**
```json
{
  "projects": [
    {
      "id": "1424",
      "title": "Projekt ustawy o rynku kryptoaktywów",
      "source": "sejm",
      "term": 10,
      "last_hit": "2025-12-04",
      "referred_to": [
        {
          "date": "2025-12-04",
          "stage_type": "Sprawozdanie Komisji Finansów Publicznych o wniosku Prezydenta RP...",
          "print_number": "2059",
          "description": "..."
        },
        {
          "date": "2025-06-25",
          "stage_type": "III czytanie na posiedzeniu Sejmu",
          "sitting_number": "37",
          "voting_result": "231 za, 193 przeciw, 5 wstrzymało się",
          "decision": "uchwalono"
        }
      ]
    }
  ]
}
```

**Uwagi:**
- `id` dla RCL: integer (ID projektu z RCL)
- `id` dla Sejm: string (numer druku, np. "1424")
- `source`: `"rcl"` lub `"sejm"` (wymagane)
- `term`: tylko dla Sejm (kadencja, np. 10)
- `number`: opcjonalne, tylko dla RCL
- `referred_to`: tylko dla Sejm - lista wszystkich etapów procesu legislacyjnego w ostatnim zakresie dat. Zawiera:
  - `date`: data etapu (format: YYYY-MM-DD)
  - `stage_type`: typ etapu (np. "III czytanie na posiedzeniu Sejmu", "Sprawozdanie komisji")
  - `print_number`: numer druku (jeśli dotyczy)
  - `sitting_number`: numer posiedzenia Sejmu (jeśli dotyczy)
  - `voting_result`: wynik głosowania (jeśli dotyczy)
  - `decision`: decyzja (jeśli dotyczy)
  - `description`: pełny opis etapu
- Pole `referred_to` jest automatycznie czyszczone i wypełniane przy każdym uruchomieniu monitora
- System scrapuje stronę HTML przebiegu procesu: `https://www.sejm.gov.pl/Sejm10.nsf/PrzebiegProc.xsp?nr={id}`

**Jak znaleźć ID projektu RCL:**
1. Wejdź na stronę projektu w RCL: `https://legislacja.rcl.gov.pl/projekt/12345678`
2. ID znajduje się w URL: `/projekt/12345678` → ID = `12345678`

**Jak znaleźć ID projektu Sejm:**
1. ID to numer druku z pola `processPrint` w API Sejmu
2. Sprawdź w drukach Sejmu: `https://api.sejm.gov.pl/sejm/term10/prints`
3. Szukaj druku gdzie `processPrint` zawiera numer projektu RCL

**Użycie:**
```bash
# Monitoring projektów RCL
python scripts/monitor_rcl_projects.py 2025-01-01 2025-12-31

# Monitoring projektów Sejm
python scripts/monitor_sejm_projects.py 2025-01-01 2025-12-31
```

**Wynik:** Plik jest automatycznie aktualizowany:
- Dodaje pole `last_hit` (format: `YYYY-MM-DD`) do projektów ze zmianami
- Dla projektów Sejm: aktualizuje pole `referred_to` z listą wszystkich etapów procesu legislacyjnego (głosowania, decyzje Senatu, Prezydenta) - czyszczone i wypełniane przy każdym uruchomieniu

---

## 2. `config/kprm_keywords.json` - Słowa kluczowe KPRM

**Cel:** Wyszukiwanie projektów w rejestrze KPRM po słowach kluczowych w tekście.

**Kiedy używać:**
- Chcesz znaleźć projekty zawierające określone słowa w opisach
- Szukasz projektów związanych z konkretnymi tematami
- Analizujesz rejestr KPRM po kategoriach tematycznych

**Format:**
```json
{
  "kategorie": {
    "finansowe": [
      "finansowy",
      "budżet",
      "podatek",
      "opłata",
      "składka",
      "dotacja",
      "subwencja",
      "dofinansowanie",
      "pomoc finansowa",
      "środki finansowe",
      "fundusz",
      "kredyt",
      "pożyczka"
    ],
    "budżetowe": [
      "budżet",
      "budżet państwa",
      "budżet samorządowy",
      "wydatek budżetowy",
      "przychód budżetowy",
      "deficyt budżetowy",
      "nadwyżka budżetowa"
    ],
    "twoja_kategoria": [
      "słowo1",
      "słowo2",
      "słowo3"
    ]
  }
}
```

**Jak działa:**
- System przeszukuje kolumny w pliku CSV rejestru KPRM:
  - "Tytuł"
  - "Cele projektu oraz informacja o przyczynach..."
  - "Istota rozwiązań planowanych..."
  - "Oddziaływanie na życie społeczne..."
  - "Spodziewane skutki i następstwa..."
- Szuka wystąpień słów kluczowych (bez rozróżniania wielkości liter)
- Zwraca projekty zawierające którekolwiek ze słów z wybranej kategorii

**Użycie:**
```bash
# Wszystkie kategorie
python scripts/analyze_kprm_register.py 2025-01-01 2025-12-31

# Tylko wybrane kategorie
python scripts/analyze_kprm_register.py 2025-01-01 2025-12-31 finansowe budżetowe
```

**Wynik:** `data/register_results.json` z projektami zawierającymi dopasowane słowa.

---

## 3. `config/rcl_subject_tags.json` - Hasła przedmiotowe RCL

**Cel:** Wyszukiwanie aktów prawnych w RCL po hasłach przedmiotowych (wordkeyId).

**Kiedy używać:**
- Chcesz znaleźć wszystkie akty prawne z określonym hasłem przedmiotowym
- Szukasz aktów w konkretnej dziedzinie prawa
- Chcesz monitorować zmiany w aktach z określonej kategorii

**Format:**
```json
{
  "tags": [
    {
      "id": 29,
      "name": "BANKOWE PRAWO"
    },
    {
      "id": 365,
      "name": "BUDŻET PAŃSTWA"
    },
    {
      "id": 276,
      "name": "FINANSE PUBLICZNE"
    }
  ]
}
```

**Jak znaleźć ID hasła przedmiotowego:**
1. Lista wszystkich haseł znajduje się w pliku `data/hasla_przedmiotowe.json`
2. Możesz też sprawdzić na stronie RCL w wyszukiwarce (dropdown "Hasło przedmiotowe")
3. ID to numeryczna wartość przypisana do każdego hasła w systemie RCL

**Użycie:**
```bash
python scripts/monitor_rcl_tags.py 2025-01-01 2025-12-31
```

**Wynik:** `data/financial_results.json` z aktami prawnymi zaktualizowanymi w podanym zakresie dat.

---

## Różnice między plikami

### `kprm_keywords.json` vs `rcl_subject_tags.json`

| Aspekt | `kprm_keywords.json` | `rcl_subject_tags.json` |
|--------|---------------------|------------------------|
| **Źródło** | Rejestr KPRM (CSV) | RCL (wyszukiwarka) |
| **Typ wyszukiwania** | Tekst w opisach projektów | Hasła przedmiotowe (wordkeyId) |
| **Format wartości** | Stringi (słowa) | Numeryczne ID |
| **Przykład** | `"budżet"`, `"podatek"` | `29` (BANKOWE PRAWO) |
| **Gdzie szuka** | W tekście kolumn CSV | W systemie RCL po tagu |
| **Precyzja** | Może znaleźć wiele niepowiązanych projektów | Bardzo precyzyjne (oficjalne hasła RCL) |

### Kiedy użyć którego?

**Użyj `kprm_keywords.json` gdy:**
- ✅ Chcesz znaleźć projekty zawierające określone słowa w opisach
- ✅ Szukasz projektów związanych z tematem (niekoniecznie oficjalnie skategoryzowanych)
- ✅ Analizujesz rejestr KPRM

**Użyj `rcl_subject_tags.json` gdy:**
- ✅ Chcesz znaleźć wszystkie akty prawne z oficjalnym hasłem przedmiotowym
- ✅ Szukasz aktów w konkretnej dziedzinie prawa
- ✅ Potrzebujesz precyzyjnych wyników z systemu RCL

---

## Przykład wdrożenia w firmie

### Scenariusz: Firma finansowa chce monitorować projekty związane z finansami

**Krok 1:** Skonfiguruj `kprm_keywords.json`
```json
{
  "kategorie": {
    "finansowe": ["budżet", "podatek", "finansowanie", "kredyt"],
    "bankowe": ["bank", "bankowy", "kredyt", "depozyt"]
  }
}
```

**Krok 2:** Skonfiguruj `rcl_subject_tags.json`
```json
{
  "tags": [
    {"id": 29, "name": "BANKOWE PRAWO"},
    {"id": 365, "name": "BUDŻET PAŃSTWA"},
    {"id": 276, "name": "FINANSE PUBLICZNE"}
  ]
}
```

**Krok 3:** (Opcjonalnie) Skonfiguruj `projects.json` dla konkretnych projektów
```json
{
  "projects": [
    {"id": 12382311, "title": "Projekt ustawy o rynku kryptoaktywów", "source": "rcl"},
    {"id": "1424", "title": "Projekt ustawy o rynku kryptoaktywów", "source": "sejm", "term": 10}
  ]
}
```

**Użycie:**
```bash
# 1. Pobierz aktualny rejestr KPRM
python scripts/fetch_kprm_register.py

# 2. Przeanalizuj rejestr po słowach kluczowych
python scripts/analyze_kprm_register.py 2025-01-01 2025-12-31 finansowe bankowe

# 3. Monitoruj akty w RCL po hasłach przedmiotowych
python scripts/monitor_rcl_tags.py 2025-01-01 2025-12-31

# 4. Monitoruj konkretne projekty RCL
python scripts/monitor_rcl_projects.py 2025-01-01 2025-12-31

# 5. Monitoruj konkretne projekty Sejm
python scripts/monitor_sejm_projects.py 2025-01-01 2025-12-31
```

---

## Backward Compatibility

Stare nazwy plików i funkcji są nadal obsługiwane (deprecated):
- `rcl_projects.json` → `projects.json` ✅ (stary plik jest mapowany na nowy)
- `keywords.json` → `kprm_keywords.json` ✅
- `financial.json` → `rcl_subject_tags.json` ✅

Stare funkcje w `config.py` nadal działają, ale zalecane jest używanie nowych nazw. Projekty bez pola `source` są automatycznie traktowane jako RCL (backward compatibility).

