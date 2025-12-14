"""Zarządzanie konfiguracją aplikacji."""

import json
from pathlib import Path
from typing import Dict, List, Any, Optional

# Ścieżki do plików konfiguracyjnych
CONFIG_DIR = Path(__file__).parent.parent / "config"
DATA_DIR = Path(__file__).parent.parent / "data"

# Pliki konfiguracyjne
PROJECTS_CONFIG = CONFIG_DIR / "projects.json"
KPRM_KEYWORDS_CONFIG = CONFIG_DIR / "kprm_keywords.json"
RCL_SUBJECT_TAGS_CONFIG = CONFIG_DIR / "rcl_subject_tags.json"
RCL_SEARCH_QUERIES_CONFIG = CONFIG_DIR / "rcl_search_queries.json"

# Backward compatibility - stare nazwy (deprecated)
RCL_PROJECTS_CONFIG = PROJECTS_CONFIG
KEYWORDS_CONFIG = KPRM_KEYWORDS_CONFIG
FINANCIAL_TAGS_CONFIG = RCL_SUBJECT_TAGS_CONFIG

# Pliki danych
REGISTER_CSV = DATA_DIR / "Rejestr_20874195.csv"
REGISTER_RESULTS = DATA_DIR / "register_results.json"
FINANCIAL_RESULTS = DATA_DIR / "financial_results.json"


def load_config(file_path: Path) -> Dict[str, Any]:
    """
    Wczytuje plik konfiguracyjny JSON.
    
    Args:
        file_path: Ścieżka do pliku JSON
        
    Returns:
        Słownik z danymi konfiguracyjnymi
        
    Raises:
        FileNotFoundError: Jeśli plik nie istnieje
        json.JSONDecodeError: Jeśli plik nie jest poprawnym JSON
    """
    if not file_path.exists():
        raise FileNotFoundError(f"Plik konfiguracyjny nie istnieje: {file_path}")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_config(file_path: Path, data: Dict[str, Any]) -> None:
    """
    Zapisuje dane konfiguracyjne do pliku JSON.
    
    Args:
        file_path: Ścieżka do pliku JSON
        data: Dane do zapisania
    """
    file_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def load_projects() -> List[Dict[str, Any]]:
    """
    Wczytuje listę wszystkich projektów (RCL + Sejm) do monitorowania.
    
    Returns:
        Lista projektów (każdy projekt to dict z 'id', 'source' i opcjonalnie 'title', 'number', 'term')
    """
    config = load_config(PROJECTS_CONFIG)
    return config.get('projects', [])


def save_projects(projects: List[Dict[str, Any]]) -> None:
    """
    Zapisuje listę wszystkich projektów (RCL + Sejm).
    
    Args:
        projects: Lista projektów do zapisania
    """
    data = {'projects': projects}
    save_config(PROJECTS_CONFIG, data)


def load_rcl_projects() -> List[Dict[str, Any]]:
    """
    Wczytuje listę projektów RCL do monitorowania (filtruje tylko projekty z source='rcl').
    
    Returns:
        Lista projektów RCL (każdy projekt to dict z 'id' i opcjonalnie 'title', 'number')
    """
    from .utils.project_utils import filter_projects_by_source
    
    all_projects = load_projects()
    return filter_projects_by_source(all_projects, 'rcl')


def save_rcl_projects(projects: List[Dict[str, Any]]) -> None:
    """
    Zapisuje listę projektów RCL (zachowuje inne projekty w pliku).
    
    Args:
        projects: Lista projektów RCL do zapisania
    """
    from .utils.project_utils import filter_projects_by_source, ensure_source_field
    
    # Wczytaj wszystkie projekty
    all_projects = load_projects()
    
    # Filtruj projekty nie-RCL
    non_rcl_projects = [p for p in all_projects if p.get('source') != 'rcl']
    
    # Upewnij się że wszystkie projekty RCL mają source='rcl'
    rcl_projects = [ensure_source_field(p, 'rcl') for p in projects]
    
    # Połącz i zapisz
    all_projects = rcl_projects + non_rcl_projects
    save_projects(all_projects)


def load_sejm_projects() -> List[Dict[str, Any]]:
    """
    Wczytuje listę projektów Sejm do monitorowania (filtruje tylko projekty z source='sejm').
    
    Returns:
        Lista projektów Sejm (każdy projekt to dict z 'id', 'source', 'term' i opcjonalnie 'title')
    """
    from .utils.project_utils import filter_projects_by_source
    
    all_projects = load_projects()
    return filter_projects_by_source(all_projects, 'sejm')


def load_kprm_keywords() -> Dict[str, List[str]]:
    """
    Wczytuje kategorie i słowa kluczowe do wyszukiwania w rejestrze KPRM.
    
    Returns:
        Słownik: {kategoria: [słowa_kluczowe]}
    """
    config = load_config(KPRM_KEYWORDS_CONFIG)
    return config.get('kategorie', {})


def load_rcl_subject_tags() -> List[Dict[str, Any]]:
    """
    Wczytuje hasła przedmiotowe (tagi) RCL do wyszukiwania aktów prawnych.
    
    Returns:
        Lista tagów, każdy to dict z 'id' i opcjonalnie 'name'
    """
    config = load_config(RCL_SUBJECT_TAGS_CONFIG)
    tags = config.get('tags', [])
    
    # Normalizuj format - obsługuj zarówno obiekty jak i proste ID
    tag_list = []
    for tag in tags:
        if isinstance(tag, dict):
            tag_id = tag.get('id')
            tag_name = tag.get('name', '')
            if tag_id is not None:
                tag_list.append({
                    'id': int(tag_id),
                    'name': tag_name
                })
        elif isinstance(tag, (int, str)):
            tag_list.append({
                'id': int(tag),
                'name': ''
            })
    
    return tag_list


# Backward compatibility - stare nazwy funkcji (deprecated)
# Uwaga: load_projects() i save_projects() są teraz głównymi funkcjami
# Stare wrappery zostały usunięte, ponieważ nowe funkcje są bardziej uniwersalne


def load_keywords() -> Dict[str, List[str]]:
    """Deprecated: Użyj load_kprm_keywords()"""
    return load_kprm_keywords()


def load_financial_tags() -> List[Dict[str, Any]]:
    """Deprecated: Użyj load_rcl_subject_tags()"""
    return load_rcl_subject_tags()


def load_rcl_search_queries() -> List[Dict[str, Any]]:
    """
    Wczytuje zapytania wyszukiwawcze RCL (po numerze aktu UE lub numerze KPRM).
    
    Returns:
        Lista zapytań, każdy to dict z 'ue_act_number', 'ue_act_title', 'kprm_number'
        (wartości mogą być None)
    """
    config = load_config(RCL_SEARCH_QUERIES_CONFIG)
    return config.get('search_queries', [])

