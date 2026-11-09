from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class EventCreate(BaseModel):
    telegram_chat_id: str
    send_at: datetime | None = None
    text: str = Field(min_length=1, max_length=500)
    channel: Literal["telegram", "websocket"]


class EventResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    status: str
    created_at: datetime
