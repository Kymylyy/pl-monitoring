# TODO - Plan rozwoju systemu PL Monitoring

## Przegląd

System PL Monitoring to kompleksowe narzędzie do monitorowania procesu legislacyjnego w Polsce. Obecnie pokrywa monitoring projektów ustaw od etapu KPRM, przez RCL, aż do decyzji Prezydenta.

## Planowane rozszerzenia 🚀

### 1. Wyszukiwanie projektów Sejmowych poprzez API Sejmu

**Priorytet: Średni**

**Cel:** Implementacja wyszukiwania projektów ustaw w Sejmie poprzez oficjalne API Sejmu, co umożliwi bardziej precyzyjną i efektywną identyfikację projektów na podstawie różnych kryteriów.

**Szczegóły:**
- Wykorzystanie API Sejmu: `https://api.sejm.gov.pl/sejm.html#processes`
- Wyszukiwanie projektów po różnych kryteriach (tytuł, data, typ dokumentu, status)
- Integracja z istniejącym systemem monitoringu projektów Sejm
- Automatyczna identyfikacja projektów na podstawie kryteriów wyszukiwania
- Eksport znalezionych projektów w formacie gotowym do dodania do `config/projects.json`

**Korzyści:**
- Szybsza i bardziej niezawodna identyfikacja projektów Sejmowych
- Możliwość wyszukiwania po zaawansowanych kryteriach (tytuł, data, typ dokumentu)
- Oficjalne źródło danych - większa pewność co do aktualności i kompletności informacji
- Uzupełnienie istniejącego systemu scrapowania HTML o alternatywną metodę identyfikacji

**Dokumentacja API:**
- Endpoint: `/term{term}/processes`
- Parametry wyszukiwania: `sort_by`, `documentType`, `title`, `documentDate`, etc.
- Format odpowiedzi: JSON z listą procesów legislacyjnych

**Status:** Do zaimplementowania
