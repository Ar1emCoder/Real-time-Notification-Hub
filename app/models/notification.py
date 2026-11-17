from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.user import User


class Notification(Base):
    __tablename__ = "notifications"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    text: Mapped[str] = mapped_column(String)
    channel: Mapped[str] = mapped_column(String)  # "telegram" или "websocket"
    status: Mapped[str] = mapped_column(
        String, default="pending"
    )  # pending, sent, failed
    send_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow
    )

    # server_default - нужен чтоб Alembic смог добавить колонку в таблицу, где уже есть строки
    attempts: Mapped[int] = mapped_column(Integer, server_default="0", nullable=False)
    last_error: Mapped[str | None] = mapped_column(
        String(500), nullable=True
    )  # String(500) - ограничили ошибку 500 знаками

    user: Mapped["User"] = relationship("User", back_populates="notifications")
