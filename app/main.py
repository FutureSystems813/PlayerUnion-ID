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

# 3. Statische Dateien (Frontend) Pfad-Konfiguration
# Wir ermitteln den Pfad relativ zur main.py, um Fehler auf Render zu vermeiden
current_directory = os.path.dirname(os.path.abspath(__file__)) # Verzeichnis: app/
root_directory = os.path.dirname(current_directory)            # Hauptverzeichnis
frontend_directory = os.path.join(root_directory, "frontend")

# Prüfen, ob der Frontend-Ordner existiert, bevor wir ihn mounten
if os.path.exists(frontend_directory):
    # 'html=True' lässt /frontend/ automatisch die index.html laden
    app.mount("/frontend", StaticFiles(directory=frontend_directory, html=True), name="frontend")
    print(f"INFO: Frontend erfolgreich gemountet unter: {frontend_directory}")
else:
    print(f"WARNUNG: Frontend-Verzeichnis nicht gefunden unter: {frontend_directory}")

# 4. Root-Route für Bequemlichkeit
@app.get("/")
async def root_redirect():
    """Leitet Besucher der Haupt-URL direkt zum Frontend weiter."""
    return RedirectResponse(url="/frontend/")

@app.get("/health")
async def health_check():
    """Einfacher Status-Check für Render."""
    return {"status": "online", "database": "connected"}