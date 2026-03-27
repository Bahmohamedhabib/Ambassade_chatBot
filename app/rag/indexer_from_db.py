import os
import shutil
from pathlib import Path
from app.db.database import SessionLocal
from app.db.models import DocumentRecord
from app.extraction.pipeline import ExtractionPipeline
from app.rag.chunker import DocumentChunker
from app.rag.vector_store import VectorStore
from app.utils.logger import setup_logger

logger = setup_logger(__name__)

def reindex_all_documents():
    """
    Réindexe totalement la base de données vectorielle (FAISS)
    à partir des BLOBs stockés dans la base de données SQL.
    """
    logger.info("Début de la réindexation complète FAISS depuis la DB.")
    db = SessionLocal()
    
    # 1. Créer un dossier temporaire pour extraire les fichiers
    PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
    tmp_dir = PROJECT_ROOT / "data" / "raw" / "tmp_db_extract"
    tmp_dir.mkdir(parents=True, exist_ok=True)
    
    try:
        docs = db.query(DocumentRecord).all()
        
        if not docs:
            logger.warning("Aucun document dans la DB. L'index FAISS sera vidé.")
            index_file = PROJECT_ROOT / "data" / "index" / "faiss_index.pkl"
            if index_file.exists():
                index_file.unlink()
            store = VectorStore()
            return
            
        # On supprime physiquement l'ancien index pour forcer une recréation propre
        index_file = PROJECT_ROOT / "data" / "index" / "faiss_index.pkl"
        if index_file.exists():
            index_file.unlink()
            
        pipeline = ExtractionPipeline()
        chunker = DocumentChunker()
        store = VectorStore() # Crée un index vierge automatiquement
        
        total_chunks = 0
        
        for doc in docs:
            file_path = tmp_dir / doc.filename
            # Écrire le BLOB sur le disque temporairement
            with open(file_path, "wb") as f:
                f.write(doc.file_data)
                
            logger.info(f"Traitement du document DB: {doc.filename}")
            
            # 2. Extraire le texte
            extracted_docs = pipeline.process_document(file_path)
            
            # 3. Ajouter la catégorie aux métadonnées
            for ext_doc in extracted_docs:
                ext_doc["metadata"]["category"] = doc.category
                
            # 4. Chunking
            chunks = chunker.chunk_documents(extracted_docs)
            total_chunks += len(chunks)
            
            # 5. Indexation locale
            store.add_documents(chunks)
            
        logger.info(f"Réindexation terminée. {total_chunks} chunks indexés dans FAISS.")
        
    except Exception as e:
        logger.error(f"Erreur lors de la réindexation FAISS : {e}")
    finally:
        # Nettoyage
        if tmp_dir.exists():
            shutil.rmtree(tmp_dir)
        db.close()
