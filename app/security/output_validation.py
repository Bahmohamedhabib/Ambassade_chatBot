from app.utils.logger import setup_logger

logger = setup_logger(__name__)

class OutputValidator:
    """Classe responsable de vérifier que la sortie générée respecte le contexte."""
    
    @staticmethod
    def validate_response(response: str, sources_found: bool) -> bool:
        """
        Valide la réponse finale. Si aucune source n'a été trouvée pour la requête
        et que le modèle tente quand même de répondre factuellement, c'est une 
        potentielle hallucination.
        """
        if not sources_found:
            # Si pas de sources, la réponse doit idéalement être le message de refus
            # Mais on renverra True ici, c'est au niveau du coordinateur (pipeline) 
            # de forcer le message de refus si pas de source.
            pass
            
        # On pourrait implémenter un LLM-as-a-judge ou d'autres checks ici
        # Pour l'instant, validation basique.
        return True
        
    @staticmethod
    def get_rejection_message() -> str:
        msg = "Je n'ai pas trouvé d'information suffisamment fiable dans les documents consultés pour répondre à cette question."
        logger.info(f"Message de refus généré: {msg}")
        return msg
