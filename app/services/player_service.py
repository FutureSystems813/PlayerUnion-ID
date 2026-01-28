from sqlmodel import Session
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
