from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from app.database import create_db_and_tables
from app.api.routes.player import router as player_router
import os

app = FastAPI(title="PlayerUnion ID")

@app.on_event("startup")
def on_startup():
    create_db_and_tables()

app.include_router(player_router, prefix="/players")

base_path = os.path.dirname(os.path.abspath(__file__))
frontend_dir = os.path.join(base_path, "", "frontend")
app.mount("/frontend", StaticFiles(directory=frontend_dir, html=True), name="frontend")
