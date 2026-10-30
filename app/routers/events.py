from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas import EventCreate, EventResponse
from app.models import User, Notification
from app.database import get_db
from datetime import datetime

from sqlalchemy import select

router = APIRouter(prefix="/events", tags=["events"])

@router.post("/", response_model=EventResponse, status_code=status.HTTP_201_CREATED)
async def create_event(event: EventCreate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.telegram_chat_id == event.telegram_chat_id))
    person = result.scalar_one_or_none()
    if not person:
        raise HTTPException(status_code=404, detail="User not found")

    notification = Notification(
        user_id=person.id,
        text=event.text,
        channel=event.channel,
        send_at=event.send_at or datetime.utcnow(),
        status="pending"
    )
    db.add(notification)
    await db.commit()
    await db.refresh(notification) # чтоб получить id и created_at

    return notification