import os
import httpx
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from app.database import get_session
from app.models.player import Player
from app.schemas import (
    player_registration_schema,
    player_login_schema,
    player_public_schema,
    steam_link_schema
)
from app.api.routes.authenticator import hash_player_password, verify_player_password

router = APIRouter()


# --- REGISTRIERUNG ---
@router.post("/", response_model=player_public_schema)
async def register_player(
        registration_data: player_registration_schema,
        database_session: Session = Depends(get_session)
):
    statement = select(Player).where(
        (Player.username == registration_data.username) |
        (Player.email == registration_data.email)
    )
    existing_player = database_session.exec(statement).first()

    if existing_player:
        raise HTTPException(status_code=400, detail="Nutzername oder E-Mail existiert bereits.")

    secure_hash = hash_player_password(registration_data.password)
    new_player = Player(
        username=registration_data.username,
        email=registration_data.email,
        password_hash=secure_hash
    )

    database_session.add(new_player)
    database_session.commit()
    database_session.refresh(new_player)
    return new_player


# --- LOGIN ---
@router.post("/login")
async def login_player(
        login_data: player_login_schema,
        database_session: Session = Depends(get_session)
):
    statement = select(Player).where(Player.username == login_data.username)
    player = database_session.exec(statement).first()

    if not player or not verify_player_password(login_data.password, player.password_hash):
        raise HTTPException(status_code=400, detail="Ungültige Anmeldedaten.")

    return {
        "status": "success",
        "message": f"Willkommen zurück, {player.username}!",
        "player_id": player.id
    }


# --- STEAM VERKNÜPFEN ---
@router.post("/link-steam")
async def link_steam_account(
        link_data: steam_link_schema,
        player_id: str,
        database_session: Session = Depends(get_session)
):
    player = database_session.get(Player, player_id)
    if not player:
        raise HTTPException(status_code=404, detail="Spieler nicht gefunden.")

    player.steam_id = link_data.steam_id
    database_session.add(player)
    database_session.commit()
    return {"status": "success", "message": "Steam verknüpft."}


# --- DER FEHLENDE TEIL: DIE PLAYER-CARD ---
@router.get("/{player_id}/card")
async def get_player_card(
        player_id: str,
        database_session: Session = Depends(get_session)
):
    """Holt Daten von der Steam API für das Frontend."""
    player = database_session.get(Player, player_id)
    if not player or not player.steam_id:
        # Fallback, falls noch kein Steam verknüpft ist
        return {"steam": {"personaname": player.username if player else "Gast"}, "games": []}

    api_key = os.getenv("STEAM_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="Steam API Key fehlt in den Render-Einstellungen.")

    # 1. Profil-Infos (Name, Avatar)
    user_url = f"http://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/?key={api_key}&steamids={player.steam_id}"
    # 2. Spiele-Infos
    games_url = f"http://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/?key={api_key}&steamid={player.steam_id}&format=json&include_appinfo=true"

    async with httpx.AsyncClient() as client:
        try:
            user_resp = await client.get(user_url)
            games_resp = await client.get(games_url)

            user_data = user_resp.json()["response"]["players"][0]
            games_data = games_resp.json().get("response", {}).get("games", [])

            return {
                "steam": user_data,
                "games": games_list_sorted(games_data)  # Hilfsfunktion optional
            }
        except Exception as e:
            raise HTTPException(status_code=502, detail=f"Steam API Fehler: {str(e)}")


def games_list_sorted(games):
    """Sortiert Spiele nach Spielzeit (dein Style: snake_case)."""
    return sorted(games, key=lambda x: x.get("playtime_forever", 0), reverse=True)