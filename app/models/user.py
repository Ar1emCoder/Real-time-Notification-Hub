from datetime import datetime, time
from sqlalchemy import Column, String, Time, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    telegram_chat_id: Mapped[str] = mapped_column(String, unique=True, index=True)
    quiet_start: Mapped[time | None] = mapped_column(Time, nullable=True, default=time(23, 0))
    quiet_end: Mapped[time | None] = mapped_column(Time, nullable=True, default=time(8, 0))
    timezone: Mapped[str] = mapped_column(String, default="UTC")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

    notifications: Mapped[list["Notification"]] = relationship("Notification", back_populates="user", cascade="all, delete-orphan")