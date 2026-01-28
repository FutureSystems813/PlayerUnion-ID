from fastapi import APIRouter, HTTPException, Depends
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
