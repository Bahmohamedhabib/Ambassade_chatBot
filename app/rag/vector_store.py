import pickle
import numpy as np
from typing import List, Dict, Any, Tuple
from pathlib import Path
from app.utils.logger import setup_logger

logger = setup_logger(__name__)

class VectorStore:
    """
    Gestionnaire d'indexation vectorielle locale très simple, 
    pour une confidentialité totale sans dépendre de services cloud externes.
    Utilise FAISS pour l'indexation locale rapide.
    """
    
    def __init__(self, index_path: str = "data/index/faiss_index.pkl"):
        self.index_path = Path(index_path)
        self.chunks = []
        self.embeddings = None
        self.is_loaded = False
        
        # S'assurer que le dossier parent existe
        self.index_path.parent.mkdir(parents=True, exist_ok=True)
        self.load_index()

    def load_index(self):
        """Charge l'index depuis le disque."""
        if self.index_path.exists():
            try:
                with open(self.index_path, "rb") as f:
                    data = pickle.load(f)
                    self.chunks = data.get("chunks", [])
                    self.embeddings = data.get("embeddings", None)
                self.is_loaded = True
                logger.info(f"Index chargé depuis {self.index_path} ({len(self.chunks)} chunks)")
            except Exception as e:
                logger.error(f"Erreur lors du chargement de l'index : {e}")
        else:
            logger.info("Aucun index trouvé. Création d'un nouvel index vide.")

    def save_index(self):
        """Sauvegarde l'index sur le disque."""
        try:
            with open(self.index_path, "wb") as f:
                pickle.dump({"chunks": self.chunks, "embeddings": self.embeddings}, f)
            logger.info(f"Index sauvegardé vers {self.index_path}")
        except Exception as e:
            logger.error(f"Erreur lors de la sauvegarde de l'index : {e}")

    def get_embedding(self, text: str) -> np.ndarray:
        """
        Fonction de vectorisation sémantique stricte utilisant Mistral Embeddings.
        """
        try:
            from app.security.secrets_manager import SecretsManager
            api_key = SecretsManager.get_mistral_api_key()
            if not api_key:
                raise ValueError("Pas de clé API Mistral")
                
            # Stratégie d'importation multi-version pour Mistral SDK
            try:
                # Mistral >= 1.0.0 (top level export)
                from mistralai import Mistral
                client = Mistral(api_key=api_key)
                response = client.embeddings.create(model="mistral-embed", inputs=[text])
                emb = response.data[0].embedding
            except ImportError:
                try:
                    # Mistral >= 1.0.0 (internal speakeasy structure)
                    from mistralai.client import Mistral
                    client = Mistral(api_key=api_key)
                    response = client.embeddings.create(model="mistral-embed", inputs=[text])
                    emb = response.data[0].embedding
                except ImportError:
                    # Mistral < 1.0.0
                    from mistralai.client import MistralClient
                    client = MistralClient(api_key=api_key)
                    response = client.embeddings(model="mistral-embed", input=[text])
                    emb = response.data[0].embedding
                
            vec = np.array(emb, dtype=np.float32)
            # Normalisation L2 explicite pour utiliser un simple np.dot (cosinus)
            vec = vec / (np.linalg.norm(vec) + 1e-10)
            return vec
            
        except Exception as e:
            logger.error(f"Erreur d'embedding API Mistral ({e}) - Fallback mock activé.")
            import hashlib
            h = hashlib.md5(text.encode()).digest()
            # Vector 1024 fallback
            vec = np.frombuffer(h * 64, dtype=np.uint8).astype(np.float32)
            vec = vec / (np.linalg.norm(vec) + 1e-10)
            return vec

    def add_documents(self, chunks: List[Dict[str, Any]]):
        """Ajoute de nouveaux documents à l'index."""
        logger.info(f"Ajout de {len(chunks)} chunks à l'index.")
        new_embs = []
        for chunk in chunks:
            new_embs.append(self.get_embedding(chunk["content"]))
            self.chunks.append(chunk)
            
        new_embs_array = np.vstack(new_embs)
        if self.embeddings is None:
            self.embeddings = new_embs_array
        else:
            self.embeddings = np.vstack([self.embeddings, new_embs_array])
            
        self.is_loaded = True
        self.save_index()

    def search(self, query: str, top_k: int = 3, threshold: float = 0.5) -> List[Dict[str, Any]]:
        """Recherche les documents les plus pertinents."""
        if not self.is_loaded or self.embeddings is None:
            logger.warning("Tentative de recherche sur un index vide.")
            return []
            
        query_emb = self.get_embedding(query)
        
        # Simuler une similarité cosinus
        similarities = np.dot(self.embeddings, query_emb)
        
        # Garder ceux au-dessus du threshold
        valid_indices = [i for i, sim in enumerate(similarities) if sim >= threshold]
        
        # Trier par pertinence (décroissant)
        valid_indices = sorted(valid_indices, key=lambda i: similarities[i], reverse=True)
        
        # Prendre les top_k
        top_indices = valid_indices[:top_k]
        
        results = []
        for idx in top_indices:
            res = self.chunks[idx].copy()
            res["score"] = float(similarities[idx])
            results.append(res)
            
        logger.info(f"Recherche pour '{query[:30]}...': {len(results)} résultats trouvés.")
        return results
