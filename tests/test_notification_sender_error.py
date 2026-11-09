from datetime import UTC, datetime
from unittest.mock import AsyncMock

import pytest
from sqlalchemy import select

from app.models import Notification, User
from app.services.notification_sender import send_pending_notifications


@pytest.mark.asyncio
async def test_send_success(async_session):
    user = User(
        telegram_chat_id="test_success_123",
        timezone="UTC",
        quiet_start=None,
        quiet_end=None,
    )
    async_session.add(user)
    await async_session.commit()

    now = datetime(2026, 11, 4, 12, 0, tzinfo=UTC)
    notif = Notification(
        user_id=user.id,
        text="Test message",
        channel="telegram",
        send_at=now,
        status="pending",
    )
    async_session.add(notif)
    await async_session.commit()

    mock_bot = AsyncMock()
    await send_pending_notifications(mock_bot, async_session, now)
    result = await async_session.execute(
        select(Notification).where(Notification.id == notif.id)
    )
    updated_notif = result.scalar_one()

    assert updated_notif.status == "sent"
    mock_bot.send_message.assert_awaited_once()


@pytest.mark.asyncio
async def test_send_failure(async_session):
    user = User(
        telegram_chat_id="test_error_123",
        timezone="UTC",
        quiet_start=None,
        quiet_end=None,
    )
    async_session.add(user)
    await async_session.commit()

    now = datetime(2026, 11, 4, 12, 0, tzinfo=UTC)
    notif = Notification(
        user_id=user.id,
        text="Test message",
        channel="telegram",
        send_at=now,
        status="pending",
    )
    async_session.add(notif)
    await async_session.commit()

    mock_bot = AsyncMock()
    mock_bot.send_message.side_effect = Exception("Telegram API error")

    await send_pending_notifications(mock_bot, async_session, now)
    result = await async_session.execute(
        select(Notification).where(Notification.id == notif.id)
    )
    updated_notif = result.scalar_one()

    assert updated_notif.status == "failed"
    assert updated_notif.send_at == now
