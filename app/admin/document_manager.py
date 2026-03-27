from typing import List, Dict, Any
from app.db.database import SessionLocal
from app.db.models import DocumentRecord
from datetime import datetime

class DocumentManager:
    """Gestion des documents PDF en base de données."""

    @staticmethod
    def upload_document(filename: str, file_bytes: bytes, category: str = "general") -> DocumentRecord:
        """Sauvegarde un document PDF en BLOB dans la DB."""
        db = SessionLocal()
        try:
            # Vérifier s'il existe déjà
            existing_doc = db.query(DocumentRecord).filter(DocumentRecord.filename == filename).first()
            if existing_doc:
                # Update
                existing_doc.file_data = file_bytes
                existing_doc.category = category
                existing_doc.uploaded_at = datetime.utcnow()
                doc = existing_doc
            else:
                doc = DocumentRecord(
                    filename=filename,
                    file_data=file_bytes,
                    category=category
                )
                db.add(doc)
            db.commit()
            db.refresh(doc)
            return doc
        finally:
            db.close()

    @staticmethod
    def get_all_documents() -> List[Dict[str, Any]]:
        """Récupère la liste des documents (sans le BLOB pour la légèreté)."""
        db = SessionLocal()
        try:
            docs = db.query(DocumentRecord.id, DocumentRecord.filename, DocumentRecord.category, DocumentRecord.uploaded_at).all()
            return [{"id": d.id, "filename": d.filename, "category": d.category, "uploaded_at": d.uploaded_at} for d in docs]
        finally:
            db.close()

    @staticmethod
    def delete_document(doc_id: int) -> bool:
        """Supprime un document de la DB."""
        db = SessionLocal()
        try:
            doc = db.query(DocumentRecord).filter(DocumentRecord.id == doc_id).first()
            if doc:
                db.delete(doc)
                db.commit()
                return True
            return False
        finally:
            db.close()

    @staticmethod
    def get_document_content(doc_id: int) -> bytes:
        """Récupère le BLOB d'un document."""
        db = SessionLocal()
        try:
            doc = db.query(DocumentRecord).filter(DocumentRecord.id == doc_id).first()
            if doc:
                return doc.file_data
            return b""
        finally:
            db.close()
