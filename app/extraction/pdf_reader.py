import fitz  # PyMuPDF
from pathlib import Path
from typing import List, Dict, Any
from app.utils.logger import setup_logger

logger = setup_logger(__name__)

class PDFReader:
    """Classe pour lire et extraire le texte brut des PDF avec PyMuPDF."""
    
    @staticmethod
    def extract_text(file_path: str) -> List[Dict[str, Any]]:
        """
        Extrait le texte page par page d'un fichier PDF.
        Retourne une liste de dictionnaires avec numéro de page et contenu.
        """
        path = Path(file_path)
        if not path.exists():
            logger.error(f"Fichier inexistant : {file_path}")
            raise FileNotFoundError(f"Le fichier {file_path} est introuvable.")
            
        pages_content = []
        try:
            doc = fitz.open(str(path))
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                # Extraire le texte de manière structurée pour un meilleur rendu
                text = page.get_text("text") 
                
                # Check simple si la page semble scannée (très peu de texte)
                # Si très peu de caractères, on pourra déléguer à l'OCR
                if len(text.strip()) < 50:
                    logger.info(f"Page {page_num + 1} de {path.name} potentiellement scannée (peu de texte).")
                
                pages_content.append({
                    "content": text.strip(),
                    "metadata": {
                        "source": path.name,
                        "page": page_num + 1,
                        "total_pages": len(doc)
                    }
                })
            doc.close()
            logger.info(f"Extraction réussie pour {path.name} : {len(pages_content)} pages.")
        except Exception as e:
            logger.error(f"Erreur lors de l'extraction de {file_path}: {str(e)}")
            raise
            
        return pages_content

    @staticmethod
    def is_pdf(file_path: str) -> bool:
        return str(file_path).lower().endswith(".pdf")
