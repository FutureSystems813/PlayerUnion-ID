from sqlmodel import SQLModel, Field
from uuid import UUID, uuid4
from datetime import datetime
from typing import Optional

class Player(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    username: str = Field(index=True)
    email: Optional[str] = None
    steam_id: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
