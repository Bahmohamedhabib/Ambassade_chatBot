import os
import sys
import bcrypt
from datetime import datetime

# S'assurer que le module app est accessible
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.db.database import engine, Base, SessionLocal
from app.db.models import AdminUser

def init_db():
    print("Création des tables dans la base de données...")
    Base.metadata.create_all(bind=engine)
    print("Tables créées avec succès.")
    
    db = SessionLocal()
    
    # Vérifier si l'admin existe déjà
    admin_exists = db.query(AdminUser).filter(AdminUser.username == "admin").first()
    
    if not admin_exists:
        print("Création de l'utilisateur administrateur par défaut...")
        # Mot de passe par défaut : admin123 (à changer en production)
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(b"admin123", salt).decode('utf-8')
        
        new_admin = AdminUser(
            username="admin",
            password_hash=hashed,
            role="admin",
            created_at=datetime.utcnow()
        )
        db.add(new_admin)
        db.commit()
        print("Administrateur créé. Login: 'admin', Password: 'admin123'. Pensez à le changer !")
    else:
        print("L'utilisateur admin existe déjà.")

    db.close()

if __name__ == "__main__":
    init_db()
