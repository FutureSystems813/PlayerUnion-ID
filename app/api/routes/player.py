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
# WICHTIG: Diese Funktionen nutzen jetzt direkt bcrypt ohne passlib-Ballast
from app.api.routes.authenticator import hash_player_password, verify_player_password

router = APIRouter()

@router.post("/", response_model=player_public_schema)
async def register_player(
    registration_data: player_registration_schema,
    database_session: Session = Depends(get_session)
):
    """Erstellt einen neuen Spieler-Account in der Neon Datenbank."""
    # Check auf Dubletten
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

    # Passwort sicher hashen (direkt via bcrypt)
    secure_hash = hash_player_password(registration_data.password)

    # Neues Player-Objekt erstellen
    new_player = Player(
        username=registration_data.username,
        email=registration_data.email,
        password_hash=secure_hash
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

    # Sicherheits-Tipp: Gleiche Fehlermeldung für "User nicht da" und "Passwort falsch"
    # verhindert Account-Fishing.
    if not player:
        raise HTTPException(status_code=400, detail="Ungültige Anmeldedaten.")

    # Passwort-Vergleich via bcrypt (unser neuer Authenticator)
    if not verify_player_password(login_data.password, player.password_hash):
        raise HTTPException(status_code=400, detail="Ungültige Anmeldedaten.")

    return {
        "status": "success",
        "message": f"Willkommen zurück, {player.username}!",
        "player_id": player.id
    }


@router.post("/link-steam")
async def link_steam_account(
    link_data: steam_link_schema,
    player_id: str,
    database_session: Session = Depends(get_session)
):
    """Verknüpft eine SteamID64 mit einem bestehenden Account."""
    # player_id kommt hier als Query-Parameter, passend zu deinem fetch() im Frontend
    player = database_session.get(Player, player_id)

    if not player:
        raise HTTPException(status_code=404, detail="Spieler nicht gefunden.")

    player.steam_id = link_data.steam_id

    database_session.add(player)
    database_session.commit()
    database_session.refresh(player)

    return {"status": "success", "message": "Steam-Account erfolgreich verknüpft."}