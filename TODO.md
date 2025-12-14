# TODO - Plan rozwoju systemu Horizon Monitoring

## Przegląd

System Horizon Monitoring to kompleksowe narzędzie do monitorowania procesu legislacyjnego w Polsce. Obecnie pokrywa monitoring projektów ustaw od etapu RCL, przez Sejm, aż do decyzji Prezydenta.

## Zrealizowane funkcjonalności ✅

### 1. Monitoring RCL (Rządowy Proces Legislacyjny)
- ✅ Monitoring konkretnych projektów po ID
- ✅ Monitoring aktów prawnych po hasłach przedmiotowych (tagi)
- ✅ Wykrywanie zmian w projektach w określonym zakresie dat
- ✅ Wyszukiwanie projektów po identyfikatorach zewnętrznych (numer aktu UE, numer KPRM)

### 2. Monitoring Sejm
- ✅ Monitoring konkretnych projektów po numerze druku
- ✅ Scrapowanie pełnego przebiegu procesu legislacyjnego
- ✅ Wyciąganie wszystkich etapów: czytania, głosowania, decyzje Senatu i Prezydenta

### 3. Analiza KPRM (Kancelaria Prezesa Rady Ministrów)
- ✅ Pobieranie rejestru prac legislacyjnych (CSV)
- ✅ Analiza po słowach kluczowych w kategoriach tematycznych
- ✅ Wyszukiwanie projektów w tekście rejestru

## Planowane rozszerzenia 🚀

### 1. Wyszukiwanie projektów RCL po identyfikatorach zewnętrznych ✅
**Priorytet: Wysoki**  
**Status: Zrealizowane**

**Cel:** Umożliwienie wyszukiwania projektów w RCL po identyfikatorach zewnętrznych:
- **Numer aktu prawnego Unii Europejskiej** - znajdowanie projektów implementujących konkretne dyrektywy/rozporządzenia UE
- **Numer z wykazu prac legislacyjnych** - łączenie projektów RCL z numerami z rejestru KPRM

**Zaimplementowane:**
- ✅ Scrapowanie strony wyszukiwania RCL: `https://legislacja.rcl.gov.pl/szukaj?typeId=1&typeId=2&activeTab=tab2`
- ✅ Wypełnianie formularza wyszukiwania przy użyciu Playwright z optymalizacją (jedna przeglądarka dla wszystkich wyszukiwań)
- ✅ Wyszukiwanie po numerze aktu UE (pole `UEActValue`)
- ✅ Wyszukiwanie po numerze z wykazu KPRM (pole `number`)
- ✅ Parsowanie wyników wyszukiwania z tabeli HTML
- ✅ Wyciąganie ID projektów z linków do szczegółów
- ✅ Zapis wyników w formacie gotowym do wklejenia do `config/projects.json`
- ✅ Integracja z istniejącym systemem monitoringu projektów RCL

**Użycie:**
```bash
python scripts/search_rcl_projects.py 2025-01-01 2025-12-31
```

**Konfiguracja:** `config/rcl_search_queries.json`

**Korzyści:**
- ✅ Automatyczne znajdowanie projektów implementujących dyrektywy UE po numerze aktu
- ✅ Łączenie projektów RCL z rejestrem KPRM poprzez numer z wykazu
- ✅ Pełniejszy obraz procesu legislacyjnego - możliwość śledzenia projektów od identyfikatora UE lub numeru KPRM
- ✅ Ułatwienie identyfikacji projektów dla osób znających tylko numer UE lub KPRM
- ✅ Optymalizacja wydajności - jedna przeglądarka dla wszystkich wyszukiwań


## Status

**Aktualna wersja:** 1.1.0  
**Ostatnia aktualizacja:** 2025-12-14

