import re
from app.utils.logger import setup_logger

logger = setup_logger(__name__)

class InputValidator:
    """Classe responsable de la validation stricte des entrées utilisateurs."""

    # Liste de mots-clés typiques de jailbreak / prompt injection
    FORBIDDEN_PATTERNS = [
        r"(?i)ignore\s+(toutes\s+)?les\s+instructions",
        r"(?i)oublie\s+(toutes\s+)?les\s+r[èe]gles",
        r"(?i)comporte[- ]?toi\s+comme",
        r"(?i)fais\s+comme\s+si",
        r"(?i)réponds\s+librement",
        r"(?i)r[éèe]v[èe]le\s+(ton\s+)?prompt",
        r"(?i)outre(?:\s+|-)passer",
        r"(?i)system\s+prompt",
    ]

    @staticmethod
    def validate_query(query: str) -> bool:
        """
        Vérifie si la requête est sécurisée.
        Retourne True si OK, False si suspecte.
        """
        if not query or len(query.strip()) == 0:
            logger.warning("Requête vide rejetée.")
            return False
            
        if len(query) > 500:
            logger.warning("Requête trop longue rejetée (max 500 caractères).")
            return False

        for pattern in InputValidator.FORBIDDEN_PATTERNS:
            if re.search(pattern, query):
                logger.warning(f"Tentative suspecte détectée avec le motif : {pattern}")
                return False

        return True

    @staticmethod
    def sanitize_query(query: str) -> str:
        """Nettoie la requête des caractères spéciaux dangereux si besoin."""
        # Dans sa forme la plus simple, on strip la chaîne.
        return query.strip()

    @staticmethod
    def is_conversational(query: str) -> bool:
        """Détecte les requêtes conversationnelles simples (salutations, remerciements)."""
        clean_query = query.strip().lower()
        conversational_phrases = [
            "bonjour", "bonsoir", "salut", "hello", "coucou", 
            "merci", "merci beaucoup", "je vous remercie",
            "au revoir", "bonne journée", "bonne soirée"
        ]
        
        if clean_query in conversational_phrases:
            return True
            
        for phrase in conversational_phrases:
            if clean_query.startswith(phrase) and len(clean_query) < 30: 
                return True
                
        return False
