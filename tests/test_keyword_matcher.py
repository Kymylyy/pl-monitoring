"""Testy dla modułu keyword_matcher."""

import pytest

from horizon_monitoring.analyzers.keyword_matcher import KeywordMatcher


class TestKeywordMatcher:
    """Testy dla klasy KeywordMatcher."""
    
    def test_contains_keywords_case_insensitive(self):
        """Test wyszukiwania bez rozróżniania wielkości liter."""
        matcher = KeywordMatcher()
        keywords = ["finansowy", "budżet", "podatek"]
        text = "Projekt dotyczy spraw FINANSOWYCH i budżetu"
        
        result = matcher.contains_keywords(text, keywords, case_sensitive=False)
        
        assert "finansowy" in result
        assert "budżet" in result
        assert "podatek" not in result
    
    def test_contains_keywords_case_sensitive(self):
        """Test wyszukiwania z rozróżnianiem wielkości liter."""
        matcher = KeywordMatcher()
        keywords = ["Finansowy", "budżet"]
        text = "Projekt dotyczy spraw finansowych i budżetu"
        
        result = matcher.contains_keywords(text, keywords, case_sensitive=True)
        
        assert "Finansowy" not in result
        assert "budżet" in result
    
    def test_no_keywords_found(self):
        """Test gdy nie znaleziono słów kluczowych."""
        matcher = KeywordMatcher()
        keywords = ["podatek"]
        text = "Projekt dotyczy spraw finansowych"
        
        result = matcher.contains_keywords(text, keywords)
        
        assert len(result) == 0
    
    def test_empty_text(self):
        """Test z pustym tekstem."""
        matcher = KeywordMatcher()
        keywords = ["finansowy"]
        text = ""
        
        result = matcher.contains_keywords(text, keywords)
        
        assert len(result) == 0
    
    def test_empty_keywords(self):
        """Test z pustą listą słów kluczowych."""
        matcher = KeywordMatcher()
        keywords = []
        text = "Projekt dotyczy spraw finansowych"
        
        result = matcher.contains_keywords(text, keywords)
        
        assert len(result) == 0

