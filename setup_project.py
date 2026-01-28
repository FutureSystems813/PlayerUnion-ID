import os

# Definition der Ordnerstruktur
folders = [
    "app",
    "app/api",
    "app/api/routes",
    "app/models",
    "app/services",
    "app/frontend"
]

# Definition der Dateien und Inhalte
files = {
    "app/models/player.py": """from sqlmodel import SQLModel, Field
from uuid import UUID, uuid4
from datetime import datetime
from typing import Optional

class Player(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    username: str = Field(index=True)
    email: Optional[str] = None
    steam_id: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
""",

    "app/database.py": """from sqlmodel import create_engine, SQLModel, Session
import os

sqlite_url = "sqlite:///./playerunion.db"
engine = create_engine(sqlite_url, connect_args={"check_same_thread": False})

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session
""",

    "app/services/player_service.py": """from sqlmodel import Session
from app.models.player import Player
from uuid import UUID

def create_player(session: Session, username: str, email: str = None):
    db_player = Player(username=username, email=email)
    session.add(db_player)
    session.commit()
    session.refresh(db_player)
    return db_player

def get_player(session: Session, player_id: str):
    try:
        return session.get(Player, UUID(player_id))
    except:
        return None

def link_steam(session: Session, player_id: str, steam_id: str):
    player = get_player(session, player_id)
    if player:
        player.steam_id = steam_id
        session.add(player)
        session.commit()
        session.refresh(player)
    return player
""",

    "app/services/steam_service.py": """import httpx

STEAM_API_KEY = "7EE60BB0BB2E91DD391DC6B11356EBBC"

async def get_owned_games(steam_id: str):
    url = "https://api.steampowered.com/IPlayerService/GetOwnedGames/v1/"
    params = {"key": STEAM_API_KEY, "steamid": steam_id, "include_appinfo": 1}
    async with httpx.AsyncClient() as client:
        res = await client.get(url, params=params)
        return res.json().get("response", {}).get("games", [])

async def get_player_summary(steam_id: str):
    url = "https://api.steampowered.com/ISteamUser/GetPlayerSummaries/v2/"
    params = {"key": STEAM_API_KEY, "steamids": steam_id}
    async with httpx.AsyncClient() as client:
        res = await client.get(url, params=params)
        players = res.json().get("response", {}).get("players", [])
        return players[0] if players else None
""",

    "app/api/routes/player.py": """from fastapi import APIRouter, HTTPException, Depends
from sqlmodel import Session
from app.database import get_session
from app.services import player_service, steam_service
from pydantic import BaseModel

router = APIRouter()

class PlayerCreate(BaseModel):
    username: str
    email: str | None = None

class SteamLink(BaseModel):
    steam_id: str

@router.post("/")
async def register(data: PlayerCreate, session: Session = Depends(get_session)):
    return player_service.create_player(session, data.username, data.email)

@router.post("/{player_id}/link")
async def link(player_id: str, data: SteamLink, session: Session = Depends(get_session)):
    player = player_service.link_steam(session, player_id, data.steam_id)
    if not player: raise HTTPException(404, "ID nicht gefunden")
    return player

@router.get("/{player_id}/card")
async def get_card(player_id: str, session: Session = Depends(get_session)):
    player = player_service.get_player(session, player_id)
    if not player or not player.steam_id:
        raise HTTPException(400, "Kein Steam verknüpft")
    profile = await steam_service.get_player_summary(player.steam_id)
    games = await steam_service.get_owned_games(player.steam_id)
    return {"player": player, "steam": profile, "games": games}
""",

    "main.py": """from fastapi import FastAPI
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
frontend_dir = os.path.join(base_path, "app", "frontend")
app.mount("/frontend", StaticFiles(directory=frontend_dir, html=True), name="frontend")
""",

    "app/frontend/index.html": """<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <title>PlayerUnion ID | Dashboard</title>
    <style>
        body { font-family: sans-serif; background: #0f172a; color: white; padding: 40px; text-align: center; }
        .card { background: #1e293b; padding: 20px; border-radius: 10px; margin: 10px auto; max-width: 500px; border: 1px solid #334155; }
        input { width: 80%; padding: 10px; margin: 10px 0; border-radius: 5px; border: none; }
        button { padding: 10px 20px; background: #7000ff; color: white; border: none; border-radius: 5px; cursor: pointer; }
        #union-card { display: none; border-left: 5px solid #00f2ff; text-align: left; }
    </style>
</head>
<body>
    <h1>PLAYERUNION ID</h1>
    <div class="card">
        <h3>1. Registrieren</h3>
        <input type="text" id="uname" placeholder="Username">
        <button onclick="reg()">Erstellen</button>
    </div>
    <div class="card">
        <h3>2. Steam Link</h3>
        <input type="text" id="pid" placeholder="Pulse-ID">
        <input type="text" id="sid" placeholder="SteamID64">
        <button onclick="link()">Verknüpfen</button>
    </div>
    <div id="union-card" class="card">
        <h2 id="name"></h2>
        <p id="status"></p>
        <div id="games"></div>
    </div>
    <script>
        async function reg() {
            const r = await fetch('/players/', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({username:document.getElementById('uname').value})});
            const d = await r.json(); document.getElementById('pid').value = d.id;
        }
        async function link() {
            const pid = document.getElementById('pid').value;
            await fetch(`/players/${pid}/link`, {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({steam_id:document.getElementById('sid').value})});
            load(pid);
        }
        async function load(pid) {
            const r = await fetch(`/players/${pid}/card`);
            const d = await r.json();
            document.getElementById('union-card').style.display = 'block';
            document.getElementById('name').innerText = d.steam.personaname;
            document.getElementById('status').innerText = "Spiele gefunden: " + d.games.length;
        }
    </script>
</body>
</html>
"""
}

# Erstellung
print("Erstelle PlayerUnion ID Projektstruktur...")
for folder in folders:
    os.makedirs(folder, exist_ok=True)

for path, content in files.items():
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)

print("Fertig! Starte den Server mit: uvicorn main:app --reload")