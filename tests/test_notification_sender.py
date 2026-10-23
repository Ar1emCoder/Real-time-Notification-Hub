import pytest
from unittest.mock import AsyncMock
from sqlalchemy import select
from datetime import datetime, timezone

from app.models import User, Notification
from app.services.notification_sender import send_pending_notifications


@pytest.mark.asyncio
async def test_send_pending_notifications_success(async_session):
    user = User(telegram_chat_id="test_123", timezone="UTC")
    async_session.add(user)
    await async_session.commit()

    notif = Notification(
        user_id=user.id,
        text="Текстовое сообщение",
        channel="telegram",
        send_at=datetime.now(timezone.utc),
        status="pending"
    )
    async_session.add(notif)
    await async_session.commit()


    mock_bot = AsyncMock()
    await send_pending_notifications(mock_bot, async_session)

    assert mock_bot.send_message.called
    assert mock_bot.send_message.call_args.kwargs["chat_id"] == "test_123"

    result = await async_session.execute(select(Notification).where(Notification.id == notif.id))
    updated_notif = result.scalar_one()
    assert updated_notif.status == "sent"