#!/usr/bin/env python3
"""
Entry point do analizy rejestru prac legislacyjnych KPRM.

Użycie:
    python scripts/analyze_kprm_register.py <data_początkowa> <data_końcowa> [kategoria1] [kategoria2] ...

Format dat: YYYY-MM-DD

Przykłady:
    python scripts/analyze_kprm_register.py 2025-01-01 2025-12-31
    python scripts/analyze_kprm_register.py 2025-01-01 2025-12-31 finansowe budżetowe
"""

import json
import sys
from datetime import datetime
from pathlib import Path

# Dodaj główny katalog projektu do ścieżki
sys.path.insert(0, str(Path(__file__).parent.parent))

from horizon_monitoring.analyzers.register_analyzer import RegisterAnalyzer
from horizon_monitoring.config import load_kprm_keywords, REGISTER_RESULTS, KPRM_KEYWORDS_CONFIG


def save_results(
    results: list,
    start_date: datetime,
    end_date: datetime,
    selected_categories: list,
    keywords_by_category: dict
):
    """Zapisuje wyniki do pliku JSON."""
    output_data = {
        "search_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "date_range": {
            "start": start_date.strftime("%Y-%m-%d"),
            "end": end_date.strftime("%Y-%m-%d")
        },
        "selected_categories": selected_categories,
        "keywords_by_category": {
            cat: keywords_by_category.get(cat, [])
            for cat in selected_categories
        },
        "total_results": len(results),
        "results": results
    }
    
    REGISTER_RESULTS.parent.mkdir(exist_ok=True)
    
    with open(REGISTER_RESULTS, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)
    
    print(f"\nZapisano wyniki do: {REGISTER_RESULTS}")


def main():
    """Główna funkcja."""
    if len(sys.argv) < 3:
        print("Użycie: python scripts/analyze_kprm_register.py <data_początkowa> <data_końcowa> [kategoria1] [kategoria2] ...")
        print("Format dat: YYYY-MM-DD")
        print("\nDostępne kategorie (jeśli nie podano, używa wszystkich):")
        
        # Wczytaj kategorie żeby je pokazać
        if KPRM_KEYWORDS_CONFIG.exists():
            keywords_by_category = load_kprm_keywords()
            for category in keywords_by_category.keys():
                print(f"  - {category} ({len(keywords_by_category[category])} słów)")
        
        print("\nPrzykłady:")
        print("  python scripts/analyze_kprm_register.py 2025-01-01 2025-12-31")
        print("  python scripts/analyze_kprm_register.py 2025-01-01 2025-12-31 finansowe budżetowe")
        sys.exit(1)
    
    # Parsuj daty
    try:
        start_date = datetime.strptime(sys.argv[1], "%Y-%m-%d")
        end_date = datetime.strptime(sys.argv[2], "%Y-%m-%d")
    except ValueError as e:
        print(f"Błąd parsowania dat: {e}")
        print("Format dat: YYYY-MM-DD")
        sys.exit(1)
    
    # Wczytaj kategorie i słowa kluczowe
    keywords_by_category = load_kprm_keywords()
    
    # Parsuj wybrane kategorie (opcjonalne)
    selected_categories = sys.argv[3:] if len(sys.argv) > 3 else list(keywords_by_category.keys())
    
    # Sprawdź czy wszystkie wybrane kategorie istnieją
    invalid_categories = [cat for cat in selected_categories if cat not in keywords_by_category]
    if invalid_categories:
        print(f"Błąd: Nieznane kategorie: {', '.join(invalid_categories)}")
        print(f"Dostępne kategorie: {', '.join(keywords_by_category.keys())}")
        sys.exit(1)
    
    # Analizuj
    analyzer = RegisterAnalyzer()
    results = analyzer.analyze(
        start_date,
        end_date,
        keywords_by_category,
        selected_categories
    )
    
    # Zapisz wyniki
    if results:
        save_results(results, start_date, end_date, selected_categories, keywords_by_category)
        
        # Pokaż przykładowe wyniki
        print(f"\nPrzykładowe wyniki (pierwsze 5):")
        for i, result in enumerate(results[:5], 1):
            print(f"\n{i}. {result.get('Tytuł', 'Brak tytułu')[:80]}...")
            print(f"   Numer: {result.get('Numer projektu', 'N/A')}")
            print(f"   Data publikacji: {result.get('Data publikacji', 'N/A')}")
            if '_matched_categories' in result:
                print(f"   Dopasowane kategorie: {', '.join(result['_matched_categories'])}")
            if '_matched_keywords' in result:
                matched_kw = result['_matched_keywords'][:5]
                print(f"   Dopasowane słowa: {', '.join(matched_kw)}")
                if len(result['_matched_keywords']) > 5:
                    print(f"   ... i {len(result['_matched_keywords']) - 5} więcej")
    else:
        print("\nNie znaleziono żadnych wyników")


if __name__ == "__main__":
    main()

