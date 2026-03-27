import bcrypt
from app.db.database import SessionLocal
from app.db.models import AdminUser

class AuthManager:
    """Gestion de l'authentification administrateur avec bcrypt."""

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Vérifie si le mot de passe correspond au hash."""
        return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

    @staticmethod
    def authenticate_admin(username: str, password: str) -> bool:
        """
        Vérifie les credentials dans la DB.
        Retourne True si valide, False sinon.
        """
        db = SessionLocal()
        try:
            admin = db.query(AdminUser).filter(AdminUser.username == username).first()
            if not admin:
                return False
            
            return AuthManager.verify_password(password, admin.password_hash)
        finally:
            db.close()
