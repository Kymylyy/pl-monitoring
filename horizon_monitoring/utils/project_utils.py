"""Funkcje pomocnicze do pracy z projektami."""

from typing import List, Dict, Any, Optional


def filter_projects_by_source(projects: List[Dict[str, Any]], source: str) -> List[Dict[str, Any]]:
    """
    Filtruje projekty po źródle.
    
    Args:
        projects: Lista wszystkich projektów
        source: Źródło do filtrowania ('rcl' lub 'sejm')
        
    Returns:
        Lista projektów z określonego źródła
    """
    return [p for p in projects if p.get('source') == source]


def ensure_source_field(project: Dict[str, Any], default_source: str) -> Dict[str, Any]:
    """
    Upewnia się że projekt ma pole 'source'.
    
    Args:
        project: Słownik projektu
        default_source: Domyślne źródło jeśli brak pola 'source'
        
    Returns:
        Projekt z upewnionym polem 'source'
    """
    if 'source' not in project:
        project = project.copy()
        project['source'] = default_source
    return project


def normalize_project_id(project_id: Any) -> str:
    """
    Normalizuje ID projektu do stringa dla porównań.
    
    Args:
        project_id: ID projektu (może być int lub str)
        
    Returns:
        ID jako string
    """
    return str(project_id)

