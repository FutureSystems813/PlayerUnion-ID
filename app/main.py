import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from app.database import create_db_and_tables, get_session
from app.api.routes.player import router as player_router

app = FastAPI(title="PlayerUnion ID")

@app.on_event("startup")
def on_startup():
    # Erstellt die Tabellen in Neon beim Start
    create_db_and_tables()

# Füge den Router hinzu
app.include_router(player_router, prefix="/players")

# Statische Dateien (Frontend)
# Wir nutzen os.path.join für die Sicherheit
base_path = os.path.dirname(os.path.abspath(__file__))
frontend_directory = os.path.join(base_path, "frontend")

if os.path.exists(frontend_directory):
    app.mount("/frontend", StaticFiles(directory=frontend_directory, html=True), name="frontend")
else:
    print(f"Warnung: Der Ordner {frontend_directory} wurde nicht gefunden!")

@app.get("/")
async def redirect_to_frontend():
    return {"message": "System läuft. Gehe zu /frontend/"}