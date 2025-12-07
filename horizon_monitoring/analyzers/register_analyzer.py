"""Analiza pliku CSV rejestru prac legislacyjnych KPRM."""

import csv
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Optional, Set

from ..config import REGISTER_CSV
from ..exceptions import DataParseError, ValidationError
from ..utils.date_utils import parse_date
from ..utils.logger import get_logger
from .keyword_matcher import KeywordMatcher

logger = get_logger(__name__)


class RegisterAnalyzer:
    """Klasa do analizy rejestru prac legislacyjnych."""
    
    DEFAULT_SEARCH_COLUMNS = [
        "Cele projektu oraz informacja o przyczynach i potrzebie rozwiązań planowanych w projekcie",
        "Istota rozwiązań planowanych w projekcie, w tym proponowane środki realizacji",
        "Oddziaływanie na życie społeczne nowych regulacji prawnych",
        "Spodziewane skutki i następstwa projektowanych regulacji prawnych",
        "Tytuł"
    ]
    
    def __init__(self, register_file: Path = None):
        """
        Inicjalizuje analyzer.
        
        Args:
            register_file: Ścieżka do pliku CSV rejestru (domyślnie z config.py)
        """
        self.register_file = register_file or REGISTER_CSV
        self.keyword_matcher = KeywordMatcher()
    
    def analyze(
        self,
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
        
        Args:
            start_date: Data początkowa zakresu
            end_date: Data końcowa zakresu
            keywords_by_category: Słownik kategorii i słów kluczowych
            selected_categories: Lista wybranych kategorii (None = wszystkie)
            search_columns: Lista kolumn do przeszukania (None = domyślne)
            
        Returns:
            Lista wyników (wierszy z dopasowaniami)
        """
        if keywords_by_category is None:
            keywords_by_category = {}
        
        if selected_categories is None:
            selected_categories = list(keywords_by_category.keys())
        
        if search_columns is None:
            search_columns = self.DEFAULT_SEARCH_COLUMNS
        
        # Zbierz wszystkie słowa kluczowe z wybranych kategorii
        all_keywords = []
        for category in selected_categories:
            if category in keywords_by_category:
                all_keywords.extend(keywords_by_category[category])
        
        results = []
        
        logger.info(f"Wczytywanie pliku: {self.register_file}")
        logger.info(f"Zakres dat: {start_date.strftime('%Y-%m-%d')} - {end_date.strftime('%Y-%m-%d')}")
        logger.info(f"Wybrane kategorie: {', '.join(selected_categories)}")
        logger.info(f"Łącznie słów kluczowych: {len(all_keywords)}")
        
        if not self.register_file.exists():
            raise ValidationError(f"Nie znaleziono pliku {self.register_file}")
        
        try:
            with open(self.register_file, 'r', encoding='utf-8') as f:
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
                        matched = self.keyword_matcher.contains_keywords(
                            col_value, all_keywords
                        )
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
                
                logger.info(f"Statystyki:")
                logger.info(f"  Łącznie wierszy: {total_rows}")
                logger.info(f"  W zakresie dat: {date_filtered}")
                if all_keywords:
                    logger.info(f"  Z dopasowanymi słowami kluczowymi: {keyword_filtered}")
                logger.info(f"  Wyników: {len(results)}")
        
        except ValidationError:
            raise
        except Exception as e:
            logger.exception("Błąd podczas wczytywania pliku")
            raise DataParseError(f"Błąd podczas wczytywania pliku: {e}") from e
        
        return results

