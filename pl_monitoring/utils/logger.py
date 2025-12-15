"""Konfiguracja systemu logowania dla aplikacji."""

import logging
import sys
from pathlib import Path
from typing import Optional


def setup_logger(
    name: str = "pl_monitoring",
    level: int = logging.INFO,
    log_file: Optional[Path] = None,
    format_string: Optional[str] = None
) -> logging.Logger:
    """
    Konfiguruje i zwraca logger dla aplikacji.
    
    Args:
        name: Nazwa loggera
        level: Poziom logowania (logging.DEBUG, INFO, WARNING, ERROR)
        log_file: Opcjonalna ścieżka do pliku logów
        format_string: Opcjonalny format logów
        
    Returns:
        Skonfigurowany logger
    """
    logger = logging.getLogger(name)
    
    # Nie dodawaj handlerów jeśli już istnieją (zapobiega duplikacji)
    if logger.handlers:
        return logger
    
    logger.setLevel(level)
    
    # Format domyślny
    if format_string is None:
        format_string = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    formatter = logging.Formatter(format_string, datefmt='%Y-%m-%d %H:%M:%S')
    
    # Handler dla konsoli
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # Handler dla pliku (jeśli podano)
    if log_file:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger


def get_logger(name: Optional[str] = None) -> logging.Logger:
    """
    Zwraca logger dla danego modułu.
    
    Args:
        name: Nazwa modułu (domyślnie używa nazwy wywołującego modułu)
        
    Returns:
        Logger
    """
    if name is None:
        # Automatycznie wykryj nazwę modułu wywołującego
        import inspect
        frame = inspect.currentframe().f_back
        module_name = frame.f_globals.get('__name__', 'pl_monitoring')
        name = module_name
    
    return logging.getLogger(name)

