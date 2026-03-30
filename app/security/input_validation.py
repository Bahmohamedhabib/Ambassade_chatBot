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
        """Détecte les requêtes conversationnelles simples (salutations, remerciements, small talk)."""
        clean_query = query.strip().lower().replace("?", "").replace("!", "").replace(".", "").strip()
        conversational_phrases = [
            "bonjour", "bonsoir", "salut", "hello", "coucou", 
            "merci", "merci beaucoup", "je vous remercie", "top", "super",
            "au revoir", "bonne journée", "bonne soirée", "a bientot",
            "comment ça va", "comment vas-tu", "ça va", 
            "qui es-tu", "qui es tu", "tu es qui", "que fais tu", "t'es qui"
        ]
        
        if clean_query in conversational_phrases:
            return True
            
        for phrase in conversational_phrases:
            if clean_query.startswith(phrase) and len(clean_query) < 35: 
                return True
                
        return False

    @staticmethod
    def get_conversational_response(query: str) -> str:
        """Retourne une réponse instantanée locale selon l'intention reconnue."""
        clean_query = query.strip().lower()
        if "merci" in clean_query or "super" in clean_query or "top" in clean_query:
            return "Je vous en prie. N'hésitez pas si vous avez d'autres questions pour l'Ambassade !"
        if "au revoir" in clean_query or "bonne " in clean_query:
            return "Au revoir et excellente journée. Les services consulaires restent à votre disposition."
        if "ça va" in clean_query or "vas-tu" in clean_query:
            return "Je suis un programme, je n'ai donc pas de sentiments, mais je suis parfaitement opérationnel pour répondre à vos questions administratives ! Que puis-je faire pour vous ?"
        if "qui es" in clean_query or "que fais" in clean_query:
            return "Je suis l'assistant virtuel de l'Ambassade de Côte d'Ivoire. Mon rôle est de vous guider instantanément dans vos démarches (Passeport, Visa, Légalisation, État Civil). Quelle est votre question ?"
            
        # Par défaut (salutations générales)
        return "Bonjour ! Je suis l'assistant virtuel de l'Ambassade de Côte d'Ivoire. Comment puis-je vous aider dans vos démarches aujourd'hui ?"
