from typing import List, Dict, Any
from pathlib import Path
from app.utils.logger import setup_logger
from app.extraction.pdf_reader import PDFReader
from app.extraction.docling_parser import DoclingParser
from app.extraction.mistral_ocr import MistralOCR

logger = setup_logger(__name__)

class ExtractionPipeline:
    """Orchestrateur hybride pour l'extraction de contenu."""
    
    def __init__(self):
        self.pdf_reader = PDFReader()
        self.docling = DoclingParser()
        self.ocr = MistralOCR()

    def process_document(self, file_path: str) -> List[Dict[str, Any]]:
        """
        Détermine la meilleure stratégie pour extraire le texte d'un document.
        """
        path = Path(file_path)
        logger.info(f"Démarrage du pipeline d'extraction pour {path.name}")
        
        if not path.exists():
            raise FileNotFoundError(f"Le fichier n'existe pas : {file_path}")
            
        extension = path.suffix.lower()
        extracted_content = []
        
        if extension == '.pdf':
            # 1. Essayer PyMuPDF d'abord pour voir la quantité de texte
            pages = self.pdf_reader.extract_text(file_path)
            
            # 2. Analyser la qualité (stratégie hybride)
            total_text_length = sum(len(p['content']) for p in pages)
            
            # Simple heuristique: si moins de 100 caractères par page en moyenne, c'est probablement un scan
            if total_text_length / max(1, len(pages)) < 100:
                logger.warning("Document PDF détecté comme scanné. Basculement vers Mistral OCR.")
                # Idéalement, on découperait le PDF en images pour l'OCR de chaque page
                extracted_content = self.ocr.extract_from_image(file_path)
            else:
                logger.info("Document PDF natif riche en texte. Utilisation directe.")
                # On pourrait utiliser Docling ici pour structurer les tableaux etc.
                extracted_content = pages
                
        elif extension in ['.png', '.jpg', '.jpeg']:
            logger.info("Image détectée. Utilisation de Mistral OCR.")
            extracted_content = self.ocr.extract_from_image(file_path)
        elif extension == '.txt':
            logger.info("Fichier texte détecté. Lecture directe pour les tests.")
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                extracted_content = [{
                    "content": content,
                    "metadata": {"source": path.name, "page": 1, "total_pages": 1}
                }]
            except Exception as e:
                logger.error(f"Erreur de lecture du fichier texte: {e}")
                raise
        else:
            logger.error(f"Format non supporté: {extension}")
            raise ValueError(f"Format non supporté: {extension}. Utilisez PDF, TXT ou Image (PNG/JPG).")
            
        logger.info(f"Pipeline d'extraction terminé pour {path.name}")
        return extracted_content
