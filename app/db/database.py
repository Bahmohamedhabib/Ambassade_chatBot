import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from pathlib import Path
import dotenv

dotenv.load_dotenv()

# Par défaut, base SQLite locale dans le dossier data/raw/private
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
DB_DIR = PROJECT_ROOT / "data" / "raw" / "private"
DB_DIR.mkdir(parents=True, exist_ok=True)

# URL de connexion : on peut utiliser DATABASE_URL du .env pour switcher vers Postgres (ex: postgresql://user:pass@host/db)
DATABASE_URL = os.environ.get("DATABASE_URL", f"sqlite:///{DB_DIR / 'chatbot.db'}")

# Création de l'engin SQLAlchemy
# Paramètre connect_args spécial pour SQLite pour éviter les erreurs de mode thread avec Streamlit
connect_args = {"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
engine = create_engine(DATABASE_URL, connect_args=connect_args)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
