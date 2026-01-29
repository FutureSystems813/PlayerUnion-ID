from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field
import uuid


class Player(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    username: str = Field(index=True, unique=True)
    email: str = Field(unique=True)
    password_hash: str
    steam_id: Optional[str] = Field(default=None)

    # Hier ist der Fix: default_factory sorgt für den aktuellen Zeitstempel
    created_at: datetime = Field(default_factory=datetime.now)