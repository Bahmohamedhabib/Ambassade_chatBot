import os
import sys
import bcrypt
from datetime import datetime

# S'assurer que le module app est accessible
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.db.database import engine, Base, SessionLocal
from app.db.models import AdminUser
from app.security.secrets_manager import SecretsManager

def init_db():
    print("Création des tables dans la base de données...")
    Base.metadata.create_all(bind=engine)
    print("Tables créées avec succès.")
    
    db = SessionLocal()
    
    # Vérifier si l'admin existe déjà
    admin_username = SecretsManager.get_admin_username()
    admin_password = SecretsManager.get_admin_password()
    
    admin_exists = db.query(AdminUser).filter(AdminUser.username == admin_username).first()
    
    if not admin_exists:
        print(f"Création de l'utilisateur administrateur '{admin_username}'...")
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(admin_password.encode('utf-8'), salt).decode('utf-8')
        
        new_admin = AdminUser(
            username=admin_username,
            password_hash=hashed,
            role="admin",
            created_at=datetime.utcnow()
        )
        db.add(new_admin)
        db.commit()
        print(f"Administrateur créé. Login: '{admin_username}'.")
    else:
        print(f"L'utilisateur {admin_username} existe déjà.")

    db.close()

if __name__ == "__main__":
    init_db()
