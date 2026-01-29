from sqlmodel import SQLModel, Field
from typing import Optional
from uuid import UUID, uuid4

class Player(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    username: str = Field(unique=True, index=True)
    email: str = Field(unique=True, index=True)
    password_hash: str
    steam_id: Optional[str] = Field(default=None)