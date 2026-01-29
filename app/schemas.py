from pydantic import BaseModel, EmailStr
from typing import Optional
from uuid import UUID


# Das Schema für die Registrierung
class player_registration_schema(BaseModel):
    username: str
    email: EmailStr
    password: str


# Das Schema für den Login
class player_login_schema(BaseModel):
    username: str
    password: str


# Das Schema für die Steam-Verknüpfung
class steam_link_schema(BaseModel):
    steam_id: str


# Das Schema für die öffentliche Antwort (Response)
class player_public_schema(BaseModel):
    id: UUID
    username: str
    email: Optional[EmailStr] = None
    steam_id: Optional[str] = None

    class Config:
        # Erlaubt Pydantic, Daten direkt aus SQLAlchemy-Modellen zu lesen
        from_attributes = True