import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse

# Importe aus deinen Modulen
from app.database import create_db_and_tables
from app.api.routes.player import router as player_router

# Initialisierung der FastAPI App
app = FastAPI(title="PlayerUnion ID")

# 1. Datenbank beim Start vorbereiten
@app.on_event("startup")
def on_startup():
    """Erstellt alle Tabellen in der Neon-Datenbank, falls sie noch nicht existieren."""
    create_db_and_tables()

# 2. API-Routen einbinden
# Alle Spieler-Funktionen (Register, Login, Steam-Link) sind hier gebündelt
app.include_router(player_router, prefix="/players", tags=["Players"])

# Ermittle mögliche Pfade für den frontend-Ordner
current_dir = os.path.dirname(os.path.abspath(__file__)) # /opt/render/project/src/app
root_dir = os.path.dirname(current_dir)                 # /opt/render/project/src

# Wir prüfen zwei Varianten:
# 1. Neben dem app-Ordner (root/frontend)
# 2. Im root-Verzeichnis selbst
frontend_path = os.path.join(root_dir, "frontend")

if not os.path.exists(frontend_path):
    # Fallback: Suche im aktuellen Verzeichnis
    frontend_path = os.path.join(os.getcwd(), "frontend")

if os.path.exists(frontend_path):
    app.mount("/frontend", StaticFiles(directory=frontend_path, html=True), name="frontend")
    print(f"INFO: Frontend aktiv unter {frontend_path}")
else:
    print(f"KRITISCHER FEHLER: Frontend-Ordner existiert nicht! Aktuelles Verzeichnis: {os.getcwd()}")
    print(f"Inhalt von root: {os.listdir(root_dir)}")

# 4. Root-Route für Bequemlichkeit
@app.get("/")
async def root_redirect():
    """Leitet Besucher der Haupt-URL direkt zum Frontend weiter."""
    return RedirectResponse(url="/frontend/")

@app.get("/health")
async def health_check():
    """Einfacher Status-Check für Render."""
    return {"status": "online", "database": "connected"}