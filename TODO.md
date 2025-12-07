# TODO - Plan rozwoju systemu Horizon Monitoring

## Przegląd

System Horizon Monitoring to kompleksowe narzędzie do monitorowania procesu legislacyjnego w Polsce. Obecnie pokrywa monitoring projektów ustaw od etapu RCL, przez Sejm, aż do decyzji Prezydenta.

## Zrealizowane funkcjonalności ✅

### 1. Monitoring RCL (Rządowy Proces Legislacyjny)
- ✅ Monitoring konkretnych projektów po ID
- ✅ Monitoring aktów prawnych po hasłach przedmiotowych (tagi)
- ✅ Wykrywanie zmian w projektach w określonym zakresie dat

### 2. Monitoring Sejm
- ✅ Monitoring konkretnych projektów po numerze druku
- ✅ Scrapowanie pełnego przebiegu procesu legislacyjnego
- ✅ Wyciąganie wszystkich etapów: czytania, głosowania, decyzje Senatu i Prezydenta

### 3. Analiza KPRM (Kancelaria Prezesa Rady Ministrów)
- ✅ Pobieranie rejestru prac legislacyjnych (CSV)
- ✅ Analiza po słowach kluczowych w kategoriach tematycznych
- ✅ Wyszukiwanie projektów w tekście rejestru

## Planowane rozszerzenia 🚀

### 1. Wyszukiwanie projektów RCL po identyfikatorach zewnętrznych
**Priorytet: Wysoki**  
**Status: W trakcie implementacji**

**Cel:** Umożliwienie wyszukiwania projektów w RCL po identyfikatorach zewnętrznych:
- **Numer i tytuł aktu prawnego Unii Europejskiej** - znajdowanie projektów implementujących konkretne dyrektywy/rozporządzenia UE
- **Numer z wykazu prac legislacyjnych** - łączenie projektów RCL z numerami z rejestru KPRM

**Implementacja:**
- Scrapowanie strony wyszukiwania RCL: `https://legislacja.rcl.gov.pl/szukaj?typeId=1&typeId=2&activeTab=tab2`
- Wypełnianie formularza wyszukiwania przy użyciu Playwright:
  - Pole "Numer i tytuł aktu prawnego Unii Europejskiej" (np. "2021/0241", "Dyrektywa 2021/0241")
  - Pole "Numer z wykazu prac legislacyjnych" (np. "UD260", "UC2")
- Parsowanie wyników wyszukiwania z tabeli HTML
- Wyciąganie ID projektów z linków do szczegółów
- Integracja z istniejącym systemem monitoringu projektów RCL
- Automatyczne dodawanie znalezionych projektów do `config/projects.json`

**Korzyści:**
- Automatyczne znajdowanie projektów implementujących dyrektywy UE po numerze aktu
- Łączenie projektów RCL z rejestrem KPRM poprzez numer z wykazu
- Pełniejszy obraz procesu legislacyjnego - możliwość śledzenia projektów od identyfikatora UE lub numeru KPRM
- Ułatwienie identyfikacji projektów dla osób znających tylko numer UE lub KPRM

**Struktura konfiguracji:**
```json
{
  "search_queries": [
    {
      "ue_act_number": "2021/0241",
      "ue_act_title": "Dyrektywa w sprawie rynku kryptoaktywów",
      "kprm_number": null
    },
    {
      "ue_act_number": null,
      "ue_act_title": null,
      "kprm_number": "UD260"
    }
  ]
}
```


## Status

**Aktualna wersja:** 1.0.0  
**Ostatnia aktualizacja:** 2025-12-07

