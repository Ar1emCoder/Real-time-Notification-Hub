from datetime import datetime, timezone
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Notification, User
from app.services.quiet_hours import is_quiet, next_allowed_time


async def send_pending_notifications(bot, session: AsyncSession, now: datetime):
    """Отправляет все pending уведомления, время которых наступило.
    Принимает сессию как аргумент для возможности подмены в тестах."""

    stmt = select(Notification).where(
        Notification.status == "pending",
        Notification.send_at <= now
    )
    result = await session.execute(stmt)
    notifications = result.scalars().all()

    print(f"Найдено {len(notifications)} уведомлений для отправки")

    for notif in notifications:
        user_result = await session.execute(
            select(User).where(User.id == notif.user_id)
        )
        user = user_result.scalar_one()

        if is_quiet(now, user.timezone, user.quiet_start, user.quiet_end):
            notif.send_at = next_allowed_time(now, user.timezone, user.quiet_start, user.quiet_end)
            print(f"Уведомление {notif.id} отложено до {notif.send_at}")
        else:
            try:
                await bot.send_message(
                    chat_id=user.telegram_chat_id,
                    text=notif.text
                )
                notif.status = "sent"
                print(f"Уведомление {notif.id} отправлено")
            except Exception as e:
                notif.status = "failed"
                print(f"Ошибка отправки уведомления {notif.id}: {e}")


    await session.commit()