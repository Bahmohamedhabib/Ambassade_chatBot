from typing import List, Dict, Any, Tuple
from app.rag.vector_store import VectorStore
from app.utils.logger import setup_logger

logger = setup_logger(__name__)

class Retriever:
    """Moteur de recherche documentaire contrôlé."""
    
    def __init__(self, vector_store: VectorStore):
        self.store = vector_store
        # Paramètres très stricts pour une institution
        self.top_k = 4
        # Le modèle d'embedding Mistral distribue le Cosine Similarity souvent entre 0.3 et 0.8
        # Un seuil à 0.5 était trop élevé et bloquait les réponses, on le baisse à 0.25
        self.similarity_threshold = 0.25

    def retrieve_context(self, query: str) -> Tuple[str, List[Dict[str, Any]]]:
        """
        Récupère les documents pertinents et formate le contexte.
        Retourne (texte_contexte_formaté, list_des_sources_brutes)
        """
        logger.info("Exécution de la recherche RAG...")
        results = self.store.search(query, top_k=self.top_k, threshold=self.similarity_threshold)
        
        if not results:
            logger.warning("Aucun document pertinent trouvé.")
            return "", []
            
        context_parts = []
        for res in results:
            metadata = res.get('metadata', {})
            source_name = metadata.get('source', 'Document Inconnu')
            page = metadata.get('page', '?')
            content = res.get('content', '')
            
            part = f"[Source: {source_name}, Page: {page}]\n{content}"
            context_parts.append(part)
            
        formatted_context = "\n\n---\n\n".join(context_parts)
        return formatted_context, results
