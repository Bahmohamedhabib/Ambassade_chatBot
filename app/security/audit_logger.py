from typing import Optional
from app.db.database import SessionLocal
from app.db.models import InteractionLog
from datetime import datetime
from app.utils.logger import setup_logger
import json
from pathlib import Path

logger = setup_logger(__name__)

class AuditLogger:
    """Système de journalisation d'audit."""
    
    # Garder la logique de fichier texte en backup local pour la console
    LOG_DIR = Path("data/raw/private/logs")
    
    @staticmethod
    def _ensure_dir():
        AuditLogger.LOG_DIR.mkdir(parents=True, exist_ok=True)
            
    @staticmethod
    def log_interaction(
        query: str, 
        sources_found: bool,
        response_length: int,
        blocked: bool,
        flag: str,
        token_used: int = 0,
        response_text: str = ""
    ):
        """Log l'interaction dans la DB et dans un fichier JSONL."""
        AuditLogger._ensure_dir()
        
        is_malicious = (flag == "PROMPT_INJECTION") or (flag == "JAILBREAK")
        
        # 1. Logging en Base de Données (Priorité pour UI Admin)
        db = SessionLocal()
        try:
            interaction = InteractionLog(
                query=query,
                response_text=response_text,
                response_status=flag,
                is_malicious=is_malicious,
                token_used=token_used,
                response_length=response_length,
                timestamp=datetime.utcnow()
            )
            db.add(interaction)
            db.commit()
        except Exception as e:
            logger.error(f"Erreur d'écriture dans l'InteractionLog DB : {e}")
        finally:
            db.close()

        # 2. Logging Fichier (Backup technique de sécurité)
        log_file = AuditLogger.LOG_DIR / "security_audit.jsonl"
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "query_length": len(query),
            "blocked": blocked,
            "sources_found": sources_found,
            "response_length": response_length,
            "flag": flag
        }
        
        try:
            with open(log_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(log_entry) + "\n")
        except Exception as e:
            logger.error(f"Erreur d'écriture dans l'audit file: {e}")
            
        # Logging technique standard     
        logger.info(f"Action: INTERACTION | Query_Length: {len(query)} | Blocked: {blocked} | Sources_Found: {sources_found} | Response_Length: {response_length} | Flag: {flag}")

    @staticmethod
    def log_security_event(event_type: str, details: str, severity: str = "INFO"):
        logger.log(
            level=30 if severity == "WARNING" else (40 if severity == "ERROR" else 20),
            msg=f"SECURITY_EVENT | Type: {event_type} | Details: {details}"
        )
