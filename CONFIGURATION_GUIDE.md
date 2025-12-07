# Przewodnik konfiguracji

## Przegląd plików konfiguracyjnych

System używa **3 plików konfiguracyjnych JSON**, każdy służy do innego celu:

| Plik | Przeznaczenie | Gdzie używany | Format |
|------|---------------|---------------|--------|
| `kprm_keywords.json` | Numery aktów UE i słowa kluczowe do wyszukiwania w KPRM | `analyze_kprm_register.py` | Kategorie → numery aktów UE i słowa (stringi) |
| `rcl_subject_tags.json` | Hasła przedmiotowe RCL (wordkeyId) - identyfikacja | `monitor_rcl_tags.py` | Lista tagów z ID (numeryczne) |
| `projects.json` | Konkretne projekty RCL i Sejm do monitorowania | `monitor_rcl_projects.py`, `monitor_sejm_projects.py` | Lista projektów z ID i `source` |

---

## 1. `config/kprm_keywords.json` - Numery aktów UE i słowa kluczowe KPRM

**Cel:** Wyszukiwanie projektów w rejestrze KPRM implementujących konkretne akty prawne UE.

**Kiedy używać:**
- Chcesz znaleźć projekty implementujące konkretne dyrektywy/rozporządzenia UE (np. "2023/2225")
- Szukasz projektów wdrożeniowych po numerze aktu UE
- Chcesz monitorować implementację konkretnych aktów prawnych UE

**Format:**
```json
{
  "kategorie": {
    "implementacja_ue": [
      "2023/2225",
      "dyrektywa 2023/2225",
      "dyrektywa Parlamentu Europejskiego i Rady (UE) 2023/2225",
      "umów o kredyt konsumencki",
      "kredyt konsumencki",
      "implementacja dyrektywy 2023/2225",
      "2023/2673",
      "dyrektywa 2023/2673",
      "dyrektywa Parlamentu Europejskiego i Rady (UE) 2023/2673",
      "usługi finansowe zawierane na odległość",
      "implementacja dyrektywy 2023/2673"
    ]
  }
}
```

**Dlaczego konkretne numery aktów UE?**
Projekty implementujące dyrektywy UE zawierają w opisach konkretne numery aktów (np. "2023/2225", "dyrektywa 2023/2225"). To najpewniejszy sposób na znalezienie projektów wdrożeniowych. Numery aktów UE są unikalne i precyzyjne - nie ma ryzyka pomylenia z innymi projektami.

**Przykład:** Aby znaleźć projekty implementujące dyrektywy o kredycie konsumenckim:
- Dodaj numer dyrektywy: `"2023/2225"`
- Dodaj pełną nazwę: `"dyrektywa 2023/2225"` lub `"dyrektywa Parlamentu Europejskiego i Rady (UE) 2023/2225"`
- Dodaj temat projektu: `"kredyt konsumencki"`, `"umów o kredyt konsumencki"`
- Jeśli projekt implementuje kilka aktów, dodaj wszystkie numery (np. `"2023/2673"`)

**Użycie:**
```bash
# Pobierz aktualny rejestr
python scripts/fetch_kprm_register.py

# Przeanalizuj po numerach aktów UE
python scripts/analyze_kprm_register.py 2025-01-01 2025-12-31
```

**Wynik:** Zapisuje do `data/register_results.json` - lista projektów zawierających numery aktów UE/słowa kluczowe

---

## 2. `config/rcl_subject_tags.json` - Hasła przedmiotowe RCL (identyfikacja)

**Cel:** Wyszukiwanie aktów prawnych w RCL na podstawie haseł przedmiotowych (wordkeyId).

**Kiedy używać:**
- Chcesz znaleźć wszystkie akty prawne z określonym hasłem przedmiotowym (np. "BANKOWE PRAWO")
- Szukasz projektów związanych z konkretną kategorią tematyczną
- To pierwszy poziom identyfikacji w RCL - znajdź projekty, potem dodaj do `projects.json` do monitoringu

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
    }
  ]
}
```

**Uwagi:**
- `id`: ID hasła przedmiotowego (wordkeyId) - numeryczne
- `name`: Nazwa hasła przedmiotowego (opcjonalne, dla czytelności)
- Lista wszystkich haseł znajduje się w pliku `data/hasla_przedmiotowe.json`

**Dlaczego hasła przedmiotowe?**
Oficjalna kategoryzacja RCL - precyzyjne wyniki, nie zależne od słów w tekście. Hasła przedmiotowe są przypisywane przez RCL do każdego projektu, więc wyszukiwanie po nich daje pewne wyniki.

**Użycie:**
```bash
python scripts/monitor_rcl_tags.py 2025-01-01 2025-12-31
```

**Wynik:** Zapisuje do `data/financial_results.json` - lista aktów z określonym hasłem przedmiotowym

**Workflow:** Po znalezieniu projektów w wynikach, dodaj ich ID do `config/projects.json` i użyj `monitor_rcl_projects.py` do monitoringu.

---

## 3. `config/projects.json` - Projekty RCL i Sejm (monitoring)

**Cel:** Monitoring konkretnych projektów ustaw z RCL lub Sejmu.

**Kiedy używać:**
- Masz konkretne projekty ustaw, które chcesz monitorować (znasz ID/numer)
- Projekty zostały zidentyfikowane wcześniej (przez KPRM lub RCL tags)
- Chcesz śledzić zmiany w znanych projektach

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
- `term`: tylko dla Sejm (kadencja, np. 10) - opcjonalne, domyślnie 10
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
3. Lub użyj `monitor_rcl_tags.py` do identyfikacji projektów

**Jak znaleźć ID projektu Sejm:**
1. ID to numer druku
2. Możesz znaleźć go w wynikach monitoringu RCL (gdy projekt trafi do Sejmu)
3. Lub sprawdź w drukach Sejmu: `https://api.sejm.gov.pl/sejm/term10/prints`

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

## Typowy workflow konfiguracji

1. **KPRM - identyfikacja projektów UE:**
   - Dodaj numery aktów UE do `config/kprm_keywords.json`
   - Uruchom `analyze_kprm_register.py`
   - Znajdź projekty implementujące konkretne akty UE

2. **RCL - identyfikacja po hasłach przedmiotowych:**
   - Dodaj hasła przedmiotowe do `config/rcl_subject_tags.json`
   - Uruchom `monitor_rcl_tags.py`
   - Znajdź projekty związane z tematem

3. **Dodaj do monitoringu:**
   - Skopiuj ID projektów z wyników do `config/projects.json`
   - Ustaw odpowiedni `source` ("rcl" lub "sejm")

4. **Monitoruj zmiany:**
   - Uruchamiaj regularnie `monitor_rcl_projects.py` i `monitor_sejm_projects.py`
   - Sprawdzaj `last_hit` i `referred_to` w `config/projects.json`
