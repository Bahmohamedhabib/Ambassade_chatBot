import os
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

# Obtenir le chemin absolu du projet
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
LOG_DIR = PROJECT_ROOT / "data" / "raw" / "private" / "logs"

# Ensure the log directory exists, but don't track it in git
LOG_DIR.mkdir(parents=True, exist_ok=True)

def setup_logger(name: str) -> logging.Logger:
    """
    Configure un logger sécurisé (log local, pas de console pour secrets, etc.)
    """
    logger = logging.getLogger(name)
    logger.setLevel(os.environ.get("LOG_LEVEL", "INFO").upper())
    
    if logger.hasHandlers():
        logger.handlers.clear()

    # Format de log sécurisé : on exclut les données personnelles complexes, 
    # mais on garde l'horodatage et le niveau.
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Fichier tournant de 5 MB, max 3 fichiers (pour limiter la taille)
    file_path = LOG_DIR / "chatbot.log"
    file_handler = RotatingFileHandler(
        file_path, 
        maxBytes=5*1024*1024, 
        backupCount=3,
        encoding="utf-8"
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # Handler console, avec moins de détails pour ne pas exposer de prompt dans les logs console
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    return logger
