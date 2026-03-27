import os
from dotenv import load_dotenv

# Load explicitly to ensure it's picked up
load_dotenv()

class SecretsManager:
    """Gestionnaire centralisé pour la récupération sécurisée des secrets d'environnement."""
    
    @staticmethod
    def get_mistral_api_key() -> str:
        key = os.environ.get("MISTRAL_API_KEY")
        if not key or key == "your_mistral_api_key_here":
            raise ValueError("MISTRAL_API_KEY n'est pas définie correctement dans l'environnement.")
        return key

    @staticmethod
    def get_chat_model() -> str:
        return os.environ.get("MISTRAL_CHAT_MODEL", "mistral-large-latest")

    @staticmethod
    def get_ocr_model() -> str:
        return os.environ.get("MISTRAL_OCR_MODEL", "mistral-ocr-latest")
        
    @staticmethod
    def get_log_level() -> str:
        return os.environ.get("LOG_LEVEL", "INFO")
