import pickle
import numpy as np
from pathlib import Path
from typing import Optional, Dict

from app.utils.logger import setup_logger

logger = setup_logger(__name__)

class SemanticCache:
    """
    Système de Cache Sémantique Local.
    Stocke les paires (Question, Réponse) avec leur embedding pour éviter d'appeler l'IA
    sur des questions extrêmement similaires (ex: "Jours d'ouverture ?" vs "Quels sont les horaires ?").
    """

    def __init__(self, cache_path: str = "data/index/semantic_cache.pkl"):
        self.cache_path = Path(cache_path)
        self.cache_data = [] # Liste de dictionnaires {"query": str, "response": str}
        self.embeddings = None # Matrice np.ndarray des embeddings des requêtes
        self.is_loaded = False
        
        self.cache_path.parent.mkdir(parents=True, exist_ok=True)
        self.load_cache()

    def load_cache(self):
        """Charge le cache depuis le disque."""
        if self.cache_path.exists():
            try:
                with open(self.cache_path, "rb") as f:
                    data = pickle.load(f)
                    self.cache_data = data.get("cache_data", [])
                    self.embeddings = data.get("embeddings", None)
                self.is_loaded = True
                logger.info(f"Cache Sémantique chargé : {len(self.cache_data)} entrées.")
            except Exception as e:
                logger.error(f"Erreur lors du chargement du cache sémantique : {e}")
                self.cache_data = []
                self.embeddings = None
        else:
            logger.info("Aucun cache sémantique trouvé. Création d'un nouveau cache vide.")

    def save_cache(self):
        """Sauvegarde le cache sur le disque."""
        try:
            with open(self.cache_path, "wb") as f:
                pickle.dump({"cache_data": self.cache_data, "embeddings": self.embeddings}, f)
            logger.debug(f"Cache sémantique sauvegardé avec {len(self.cache_data)} entrées.")
        except Exception as e:
            logger.error(f"Erreur lors de la sauvegarde du cache sémantique : {e}")

    def check_cache(self, query_emb: np.ndarray, threshold: float = 0.95) -> Optional[str]:
        """
        Vérifie si une requête très similaire existe déjà dans le cache.
        Retourne la réponse stockée si le score cosinus dépasse le threshold.
        """
        if not self.is_loaded or self.embeddings is None or len(self.cache_data) == 0:
            return None

        try:
            # Calcul de similarité cosinus exact (la méthode dot suppose que les vecteurs sont normés L2)
            similarities = np.dot(self.embeddings, query_emb)
            best_match_idx = int(np.argmax(similarities))
            best_score = float(similarities[best_match_idx])

            if best_score >= threshold:
                matched_query = self.cache_data[best_match_idx]["query"]
                logger.info(f"CACHE HIT 🔥 (score: {best_score:.3f}) - Requete correspondante : '{matched_query}'")
                return self.cache_data[best_match_idx]["response"]
            
            logger.debug(f"CACHE MISS ❄️ (Meilleur score: {best_score:.3f})")
            return None
        except Exception as e:
            logger.error(f"Erreur lors de l'évaluation du cache : {e}")
            return None

    def add_to_cache(self, query_emb: np.ndarray, query: str, response: str):
        """
        Ajoute une nouvelle paire (requête, réponse) dans la base de cache
        et met à jour la matrice d'embeddings.
        """
        try:
            self.cache_data.append({"query": query, "response": response})
            
            # Formater l'embedding en ligne bidimensionnelle
            emb_row = query_emb.reshape(1, -1)
            
            if self.embeddings is None:
                self.embeddings = emb_row
            else:
                self.embeddings = np.vstack([self.embeddings, emb_row])
                
            self.is_loaded = True
            self.save_cache()
            logger.info("Nouvelle réponse ajoutée au cache sémantique.")
        except Exception as e:
            logger.error(f"Erreur lors de l'ajout au cache sémantique : {e}")
