import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse

from app.database import create_db_and_tables
from app.api.routes.player import router as player_router

app = FastAPI(title="PlayerUnion ID")

@app.on_event("startup")
def on_startup():
    create_db_and_tables()

# API Routen (Login, Register, etc.)
app.include_router(player_router, prefix="/players", tags=["Players"])

# --- PFAD-LOGIK FIX ---
# Wir nutzen den absoluten Pfad des Projekts
base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
frontend_path = os.path.join(base_path, "frontend")

# Debug-Ausgabe für die Render-Logs
print(f"DEBUG: Suche Frontend in: {frontend_path}")

if os.path.exists(frontend_path):
    app.mount("/frontend", StaticFiles(directory=frontend_path, html=True), name="frontend")
    print("✅ Frontend erfolgreich gemountet!")
else:
    # Falls Render den Ordner woanders abgelegt hat
    fallback_path = os.path.join(os.getcwd(), "frontend")
    if os.path.exists(fallback_path):
        app.mount("/frontend", StaticFiles(directory=fallback_path, html=True), name="frontend")
        print(f"✅ Frontend im Fallback gefunden: {fallback_path}")
    else:
        print(f"❌ FEHLER: Ordner 'frontend' nicht gefunden. Inhalt Root: {os.listdir(base_path)}")

@app.get("/")
async def root():
    return RedirectResponse(url="/frontend/")