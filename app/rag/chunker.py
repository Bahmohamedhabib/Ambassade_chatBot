from typing import List, Dict, Any
from langchain_text_splitters import RecursiveCharacterTextSplitter
from app.utils.logger import setup_logger

logger = setup_logger(__name__)

class DocumentChunker:
    """Classe pour diviser le texte extrait en segments pertinents (chunks)."""
    
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        # On utilise RecursiveCharacterTextSplitter de Langchain pour de bons résultats
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            separators=["\n\n", "\n", ".", " ", ""],
            length_function=len
        )

    def chunk_documents(self, extracted_pages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Prend la sortie de l'ExtractionPipeline et retourne une liste de chunks.
        """
        logger.info(f"Début du découpage en chunks (taille: {self.chunk_size}, chevauchement: {self.chunk_overlap})")
        
        all_chunks = []
        for page in extracted_pages:
            content = page.get("content", "")
            metadata = page.get("metadata", {})
            
            if not content.strip():
                continue
                
            texts = self.splitter.split_text(content)
            
            for i, text in enumerate(texts):
                chunk_metadata = metadata.copy()
                chunk_metadata["chunk_index"] = i
                all_chunks.append({
                    "content": text,
                    "metadata": chunk_metadata
                })
                
        logger.info(f"Découpage terminé. {len(all_chunks)} chunks générés.")
        return all_chunks
