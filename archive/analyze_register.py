#!/usr/bin/env python3
"""
Skrypt do analizy pliku CSV rejestru prac legislacyjnych
Filtruje po zakresie dat i wyszukuje słowa kluczowe w opisach projektów
Słowa kluczowe są wczytywane z pliku JSON z kategoriami
"""

import csv
import json
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Optional, Set


# Konfiguracja
REGISTER_FILE = Path("data/Rejestr_20874195.csv")
KEYWORDS_FILE = Path("config/keywords.json")
OUTPUT_FILE = Path("data/register_results.json")


def parse_date(date_str: str) -> Optional[datetime]:
    """
    Parsuje datę z formatu "YYYY-MM-DD HH:MM" lub "YYYY-MM-DD"
    """
    if not date_str or not date_str.strip():
        return None
    
    date_str = date_str.strip()
    
    # Spróbuj format z czasem
    try:
        return datetime.strptime(date_str, "%Y-%m-%d %H:%M")
    except ValueError:
        pass
    
    # Spróbuj format bez czasu
    try:
        return datetime.strptime(date_str, "%Y-%m-%d")
    except ValueError:
        pass
    
    return None


def load_keywords(keywords_file: Path) -> Dict[str, List[str]]:
    """
    Wczytuje kategorie i słowa kluczowe z pliku JSON
    Zwraca słownik: {kategoria: [słowa_kluczowe]}
    """
    try:
        with open(keywords_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            kategorie = data.get('kategorie', {})
            return kategorie
    except FileNotFoundError:
        print(f"Błąd: Nie znaleziono pliku {keywords_file}")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Błąd parsowania JSON: {e}")
        sys.exit(1)


def contains_keywords(text: str, keywords: List[str], case_sensitive: bool = False) -> Set[str]:
    """
    Sprawdza czy tekst zawiera którekolwiek ze słów kluczowych
    Zwraca zbiór dopasowanych słów kluczowych
    """
    matched = set()
    
    if not text:
        return matched
    
    if not case_sensitive:
        text_lower = text.lower()
        for keyword in keywords:
            if keyword.lower() in text_lower:
                matched.add(keyword)
    else:
        for keyword in keywords:
            if keyword in text:
                matched.add(keyword)
    
    return matched


def analyze_register(
    start_date: datetime,
    end_date: datetime,
    keywords_by_category: Dict[str, List[str]] = None,
    selected_categories: List[str] = None,
    search_columns: List[str] = None
) -> List[Dict]:
    """
    Analizuje plik CSV rejestru:
    - Filtruje po zakresie dat
    - Szuka słów kluczowych z wybranych kategorii w określonych kolumnach
    """
    if keywords_by_category is None:
        keywords_by_category = {}
    
    if selected_categories is None:
        # Jeśli nie wybrano kategorii, użyj wszystkich
        selected_categories = list(keywords_by_category.keys())
    
    if search_columns is None:
        # Domyślnie szukaj w kolumnach z opisami
        search_columns = [
            "Cele projektu oraz informacja o przyczynach i potrzebie rozwiązań planowanych w projekcie",
            "Istota rozwiązań planowanych w projekcie, w tym proponowane środki realizacji",
            "Oddziaływanie na życie społeczne nowych regulacji prawnych",
            "Spodziewane skutki i następstwa projektowanych regulacji prawnych",
            "Tytuł"
        ]
    
    # Zbierz wszystkie słowa kluczowe z wybranych kategorii
    all_keywords = []
    for category in selected_categories:
        if category in keywords_by_category:
            all_keywords.extend(keywords_by_category[category])
    
    results = []
    
    print(f"Wczytywanie pliku: {REGISTER_FILE}")
    print(f"Zakres dat: {start_date.strftime('%Y-%m-%d')} - {end_date.strftime('%Y-%m-%d')}")
    print(f"Wybrane kategorie: {', '.join(selected_categories)}")
    print(f"Łącznie słów kluczowych: {len(all_keywords)}")
    
    if not REGISTER_FILE.exists():
        print(f"Błąd: Nie znaleziono pliku {REGISTER_FILE}")
        return results
    
    try:
        with open(REGISTER_FILE, 'r', encoding='utf-8') as f:
            # CSV z separatorem średnikowym
            reader = csv.DictReader(f, delimiter=';', quotechar='"')
            
            total_rows = 0
            date_filtered = 0
            keyword_filtered = 0
            
            for row in reader:
                total_rows += 1
                
                # Parsuj datę publikacji
                date_str = row.get("Data publikacji", "")
                pub_date = parse_date(date_str)
                
                if not pub_date:
                    continue
                
                # Filtruj po zakresie dat
                # end_date jest ustawione na początek dnia, więc dodajemy 1 dzień żeby uwzględnić cały dzień końcowy
                end_date_inclusive = end_date + timedelta(days=1)
                if not (start_date <= pub_date < end_date_inclusive):
                    continue
                
                date_filtered += 1
                
                # Jeśli nie ma słów kluczowych, dodaj wszystkie wiersze z zakresu dat
                if not all_keywords:
                    results.append(row)
                    continue
                
                # Szukaj słów kluczowych w określonych kolumnach
                all_matched_keywords = set()
                matched_columns = {}
                
                for col_name in search_columns:
                    col_value = row.get(col_name, "")
                    matched = contains_keywords(col_value, all_keywords)
                    if matched:
                        all_matched_keywords.update(matched)
                        matched_columns[col_name] = list(matched)
                
                if all_matched_keywords:
                    keyword_filtered += 1
                    # Określ które kategorie zostały dopasowane
                    matched_categories = []
                    for category in selected_categories:
                        category_keywords = keywords_by_category.get(category, [])
                        if any(kw in all_matched_keywords for kw in category_keywords):
                            matched_categories.append(category)
                    
                    # Dodaj informację o dopasowaniach
                    result_row = dict(row)
                    result_row["_matched_keywords"] = sorted(list(all_matched_keywords))
                    result_row["_matched_categories"] = matched_categories
                    result_row["_matched_columns"] = matched_columns
                    results.append(result_row)
            
            print(f"\nStatystyki:")
            print(f"  Łącznie wierszy: {total_rows}")
            print(f"  W zakresie dat: {date_filtered}")
            if all_keywords:
                print(f"  Z dopasowanymi słowami kluczowymi: {keyword_filtered}")
            print(f"  Wyników: {len(results)}")
    
    except Exception as e:
        print(f"Błąd podczas wczytywania pliku: {e}")
        import traceback
        traceback.print_exc()
    
    return results


def save_results(
    results: List[Dict],
    start_date: datetime,
    end_date: datetime,
    selected_categories: List[str],
    keywords_by_category: Dict[str, List[str]]
):
    """
    Zapisuje wyniki do pliku JSON
    """
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
    
    OUTPUT_FILE.parent.mkdir(exist_ok=True)
    
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)
    
    print(f"\nZapisano wyniki do: {OUTPUT_FILE}")


def main():
    """
    Główna funkcja
    """
    if len(sys.argv) < 3:
        print("Użycie: python analyze_register.py <data_początkowa> <data_końcowa> [kategoria1] [kategoria2] ...")
        print("Format dat: YYYY-MM-DD")
        print("\nDostępne kategorie (jeśli nie podano, używa wszystkich):")
        
        # Wczytaj kategorie żeby je pokazać
        if KEYWORDS_FILE.exists():
            keywords_by_category = load_keywords(KEYWORDS_FILE)
            for category in keywords_by_category.keys():
                print(f"  - {category} ({len(keywords_by_category[category])} słów)")
        
        print("\nPrzykłady:")
        print("  python analyze_register.py 2025-01-01 2025-12-31")
        print("  python analyze_register.py 2025-01-01 2025-12-31 finansowe podatkowe")
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
    keywords_by_category = load_keywords(KEYWORDS_FILE)
    
    # Parsuj wybrane kategorie (opcjonalne)
    selected_categories = sys.argv[3:] if len(sys.argv) > 3 else list(keywords_by_category.keys())
    
    # Sprawdź czy wszystkie wybrane kategorie istnieją
    invalid_categories = [cat for cat in selected_categories if cat not in keywords_by_category]
    if invalid_categories:
        print(f"Błąd: Nieznane kategorie: {', '.join(invalid_categories)}")
        print(f"Dostępne kategorie: {', '.join(keywords_by_category.keys())}")
        sys.exit(1)
    
    # Analizuj
    results = analyze_register(
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
                matched_kw = result['_matched_keywords'][:5]  # Pokaż pierwsze 5
                print(f"   Dopasowane słowa: {', '.join(matched_kw)}")
                if len(result['_matched_keywords']) > 5:
                    print(f"   ... i {len(result['_matched_keywords']) - 5} więcej")
    else:
        print("\nNie znaleziono żadnych wyników")


if __name__ == "__main__":
    main()

