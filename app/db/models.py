from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, LargeBinary
from datetime import datetime
from app.db.database import Base

class AdminUser(Base):
    __tablename__ = "admin_users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(20), default="admin")
    created_at = Column(DateTime, default=datetime.utcnow)

class DocumentRecord(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(255), unique=True, index=True, nullable=False)
    category = Column(String(100), nullable=True)  # ex: passeport, visa, etat_civil
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    # Le contenu du document PDF stocké directement en BLOB
    file_data = Column(LargeBinary, nullable=False)

class InteractionLog(Base):
    """Pour les statistiques et le suivi des performances"""
    __tablename__ = "interactions"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    query = Column(Text, nullable=False)
    response_text = Column(Text, nullable=True)  # Ajout de la réponse complète
    response_status = Column(String(50)) # SUCCESS, NO_SOURCES, ERROR, BLOCKED
    is_malicious = Column(Boolean, default=False)
    token_used = Column(Integer, default=0) # Estimation ou vrai coût API
    response_length = Column(Integer, default=0)
