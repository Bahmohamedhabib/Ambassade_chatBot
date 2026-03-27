import os
import sys
from pathlib import Path

# S'assurer que le dossier racine est dans le sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.extraction.pipeline import ExtractionPipeline
from app.rag.chunker import DocumentChunker
from app.rag.vector_store import VectorStore
from app.utils.logger import setup_logger

logger = setup_logger("index_documents")

def main():
    logger.info("Démarrage du script d'indexation.")
    
    # 1. Initialiser les composants
    pipeline = ExtractionPipeline()
    chunker = DocumentChunker(chunk_size=800, chunk_overlap=150)
    store = VectorStore()
    
    # 2. Trouver les documents dans data/raw
    raw_dir = Path("data/raw")
    if not raw_dir.exists():
        logger.error("Le dossier data/raw n'existe pas.")
        return
        
    documents = []
    # Pour ce test, on cherche les txt et pdf
    for ext in ['*.txt', '*.pdf']:
        documents.extend(list(raw_dir.glob(ext)))
        
    if not documents:
        logger.warning("Aucun document trouvé dans data/raw.")
        return
        
    for doc_path in documents:
        logger.info(f"Traitement du fichier : {doc_path.name}")
        try:
            # Extraction
            pages = pipeline.process_document(str(doc_path))
            # Chunking
            chunks = chunker.chunk_documents(pages)
            # Ajout à l'index
            store.add_documents(chunks)
            logger.info(f"-> {len(chunks)} chunks indexés pour {doc_path.name}.")
        except Exception as e:
            logger.error(f"Erreur lors du traitement de {doc_path.name} : {e}")
            
    logger.info("Indexation terminée avec succès.")
    
if __name__ == "__main__":
    main()
