import os
from sqlmodel import create_engine, SQLModel, Session
from dotenv import load_dotenv

# Lade die Variablen aus der .env Datei (nur für lokales Testen wichtig)
load_dotenv()

# Hol dir die URL aus der Umgebung (Umgebungsvariable)
database_url = os.getenv("DATABASE_URL")

# Falls die URL mit postgres:// anfängt (Neon Standard),
# korrigiere sie für SQLAlchemy zu postgresql://
if database_url and database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://", "postgresql://", 1)

if not database_url:
    raise ValueError("DATABASE_URL wurde nicht gefunden! Prüfe deine .env Datei.")

engine = create_engine(database_url)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session