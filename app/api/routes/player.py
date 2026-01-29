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


@router.post("/", response_model=player_public_schema)
async def register_player(
        registration_data: player_registration_schema,
        database_session: Session = Depends(get_session)
):
    """Erstellt einen neuen Spieler-Account in der Neon Datenbank."""
    # Prüfen, ob Username oder Email bereits existieren
    statement = select(Player).where(
        (Player.username == registration_data.username) |
        (Player.email == registration_data.email)
    )
    existing_player = database_session.exec(statement).first()

    if existing_player:
        raise HTTPException(
            status_code=400,
            detail="Nutzername oder E-Mail-Adresse wird bereits verwendet."
        )

    # Passwort sicher hashen
    secure_password_hash = hash_player_password(registration_data.password)

    # Neues Player-Objekt erstellen
    new_player = Player(
        username=registration_data.username,
        email=registration_data.email,
        password_hash=secure_password_hash
    )

    database_session.add(new_player)
    database_session.commit()
    database_session.refresh(new_player)

    return new_player


@router.post("/login")
async def login_player(
        login_data: player_login_schema,
        database_session: Session = Depends(get_session)
):
    """Prüft die Anmeldedaten und gibt die Player-ID zurück."""
    statement = select(Player).where(Player.username == login_data.username)
    player = database_session.exec(statement).first()

    if not player:
        raise HTTPException(status_code=400, detail="Ungültige Anmeldedaten.")

    # Passwort-Vergleich via Authenticator
    password_is_correct = verify_player_password(login_data.password, player.password_hash)

    if not password_is_correct:
        raise HTTPException(status_code=400, detail="Ungültige Anmeldedaten.")

    return {
        "status": "success",
        "message": f"Willkommen zurück, {player.username}!",
        "player_id": player.id
    }


@router.post("/link-steam")
async def link_steam_account(
        link_data: steam_link_schema,
        player_id: str,  # Wir nehmen die ID hier als Query oder Header, je nach Wunsch
        database_session: Session = Depends(get_session)
):
    """Verknüpft eine SteamID64 mit einem bestehenden Account."""
    statement = select(Player).where(Player.id == player_id)
    player = database_session.exec(statement).first()

    if not player:
        raise HTTPException(status_code=404, detail="Spieler nicht gefunden.")

    player.steam_id = link_data.steam_id

    database_session.add(player)
    database_session.commit()
    database_session.refresh(player)

    return {"status": "success", "message": "Steam-Account erfolgreich verknüpft."}