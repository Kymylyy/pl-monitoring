"""Narzędzia do dopasowywania słów kluczowych w tekście."""

from typing import List, Set


class KeywordMatcher:
    """Klasa do wyszukiwania słów kluczowych w tekście."""
    
    @staticmethod
    def contains_keywords(
        text: str, 
        keywords: List[str], 
        case_sensitive: bool = False
    ) -> Set[str]:
        """
        Sprawdza czy tekst zawiera którekolwiek ze słów kluczowych.
        
        Args:
            text: Tekst do przeszukania
            keywords: Lista słów kluczowych
            case_sensitive: Czy wyszukiwanie ma być wrażliwe na wielkość liter
            
        Returns:
            Zbiór dopasowanych słów kluczowych
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

