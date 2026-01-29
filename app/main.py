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

app.include_router(player_router, prefix="/players", tags=["Players"])

# --- PFAD-LOGIK FÜR app/frontend ---
# Da die main.py im Ordner 'app' liegt, ist der frontend-Ordner ein Nachbar
current_file_dir = os.path.dirname(os.path.abspath(__file__)) # Dies ist der 'app' Ordner
frontend_path = os.path.join(current_file_dir, "frontend")

print(f"DEBUG: Suche Frontend in: {frontend_path}")

if os.path.exists(frontend_path):
    # WICHTIG: StaticFiles braucht den korrekten absoluten Pfad
    app.mount("/frontend", StaticFiles(directory=frontend_path, html=True), name="frontend")
    print("✅ Frontend erfolgreich in app/frontend gefunden!")
else:
    print(f"❌ FEHLER: Ordner nicht gefunden unter {frontend_path}")
    # Sicherheits-Check: Was sieht Python im app-Ordner?
    print(f"DEBUG: Inhalt von {current_file_dir}: {os.listdir(current_file_dir)}")

@app.get("/")
async def root():
    return RedirectResponse(url="/frontend/")