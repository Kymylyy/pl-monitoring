"""Narzędzia do parsowania i obsługi dat."""

from datetime import datetime
from typing import Optional


def parse_polish_date(date_str: str) -> Optional[datetime]:
    """
    Parsuje polską datę w formacie DD-MM-YYYY.
    
    Args:
        date_str: String z datą w formacie DD-MM-YYYY
        
    Returns:
        Obiekt datetime lub None jeśli parsowanie się nie powiodło
    """
    if not date_str or not date_str.strip():
        return None
    
    try:
        date_str = date_str.strip()
        return datetime.strptime(date_str, "%d-%m-%Y")
    except ValueError:
        return None


def parse_date(date_str: str) -> Optional[datetime]:
    """
    Parsuje datę z różnych formatów: "YYYY-MM-DD HH:MM" lub "YYYY-MM-DD".
    
    Args:
        date_str: String z datą
        
    Returns:
        Obiekt datetime lub None jeśli parsowanie się nie powiodło
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


def parse_polish_date_full(date_str: str) -> Optional[datetime]:
    """
    Parsuje polską datę w pełnym formacie tekstowym (np. "12 maja 2025", "3 czerwca 2025").
    
    Args:
        date_str: String z datą w formacie "DD miesiąc YYYY" (np. "12 maja 2025")
        
    Returns:
        Obiekt datetime lub None jeśli parsowanie się nie powiodło
    """
    if not date_str or not date_str.strip():
        return None
    
    date_str = date_str.strip()
    
    # Mapowanie polskich nazw miesięcy
    months = {
        'stycznia': 1, 'lutego': 2, 'marca': 3, 'kwietnia': 4,
        'maja': 5, 'czerwca': 6, 'lipca': 7, 'sierpnia': 8,
        'września': 9, 'października': 10, 'listopada': 11, 'grudnia': 12
    }
    
    # Wzorzec: "12 maja 2025" lub "3 czerwca 2025"
    parts = date_str.split()
    if len(parts) == 3:
        try:
            day = int(parts[0])
            month_name = parts[1].lower()
            year = int(parts[2])
            
            if month_name in months:
                month = months[month_name]
                return datetime(year, month, day)
        except (ValueError, KeyError):
            pass
    
    return None

