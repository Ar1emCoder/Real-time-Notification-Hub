from itertools import chain

import pytest
from unittest.mock import AsyncMock
from datetime import datetime, time, timezone
from sqlalchemy import select

from app.models import User, Notification
from app.services.notification_sender import send_pending_notifications

@pytest.mark.asyncio
@pytest.mark.parametrize(
    "test_name, tz, q_start, q_end, now, notif_time, expected_status, expected_send_at, should_send",
    [
        # Случай 1: Отложение отправки
        (
            "night_postponed",
            "UTC", time(23, 0), time(8, 0),
            datetime(2026, 10, 31, 23, 30, tzinfo=timezone.utc),
            datetime(2026, 10, 31, 23, 30, tzinfo=timezone.utc),
            "pending",
            datetime(2026, 11, 1, 8, 0, tzinfo=timezone.utc),
            False
        ),
        # Случай 2: Вывоз отправки уведомления - 1 раз
        (
            "day_sent",
            "UTC", time(23,0), time(8, 0),
            datetime(2026, 10, 31, 12, 0, tzinfo=timezone.utc),
            datetime(2026, 10, 31, 12, 0, tzinfo=timezone.utc),
            "sent",
            datetime(2026, 10, 31, 12, 0, tzinfo=timezone.utc),
            True
        ),
        # Случай 3: Тихие часы отключены - start = end
        (
            "quiet_hours_disabled",
            "UTC", time(12, 0), time(12, 0),
            datetime(2026, 10, 31, 12, 0, tzinfo=timezone.utc),
            datetime(2026, 10, 31, 12, 0, tzinfo=timezone.utc),
            "sent",
            datetime(2026, 10 ,31, 12, 0, tzinfo=timezone.utc),
            True
        ),
        # Случай 4: Другой часовой пояс (Москва = UTC + 3)
        (
            "different_timezone",
            "Europe/Moscow", time(1, 0), time(9, 0),
            datetime(2026, 10 ,31, 23, 0, tzinfo=timezone.utc),
            datetime(2026, 10 ,31, 23, 0, tzinfo=timezone.utc),
            "pending",
            datetime(2026, 11, 1, 6, 0, tzinfo=timezone.utc),
            False
        ),
    ],
)
async def test_send_pending_with_quiet_hours(
        async_session,
        test_name, tz, q_start, q_end, now, notif_time, expected_status, expected_send_at, should_send
):
    user = User(
        telegram_chat_id=f"test_user_{test_name}",
        timezone=tz,
        quiet_start=q_start,
        quiet_end=q_end
    )
    async_session.add(user)
    await async_session.commit()

    notif=Notification(
        user_id=user.id,
        text=f"Тестовое сообщение {test_name}",
        channel="telegram",
        send_at=notif_time,
        status="pending"
    )
    async_session.add(notif)
    await async_session.commit()

    mock_bot = AsyncMock()
    await send_pending_notifications(mock_bot, async_session, now)
    if should_send:
        mock_bot.send_message.assert_awaited_once()
    else:
        mock_bot.send_message.assert_not_called()

    # Проверяем состояние в БД
    result = await async_session.execute(
        select(Notification).where(Notification.id == notif.id)
    )
    updated_notif = result.scalar_one()

    assert updated_notif.status == expected_status, f"Статус не совпадает в тесте {test_name}"
    assert updated_notif.send_at == expected_send_at, f"Время send_at не совпадает в тесте {test_name}"