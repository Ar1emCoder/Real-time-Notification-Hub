from datetime import datetime, timezone
from sqlalchemy import select

from app.database import async_session_maker
from app.models import Notification, User


async def send_pending_notifications(bot):
    """Отправляет все pending уведомления, время которых наступило"""
    async with async_session_maker() as session:
        # 1. Находим все pending уведомления, время которых наступило
        stmt = select(Notification).where(
            Notification.status == "pending",
            Notification.send_at <= datetime.now(timezone.utc)
        )
        result = await session.execute(stmt)
        notifications = result.scalars().all()

        print(f"Найдено {len(notifications)} уведомлений для отправки")

        # 2. Отправляем каждое
        for notif in notifications:
            try:
                # Находим пользователя
                user_result = await session.execute(
                    select(User).where(User.id == notif.user_id)
                )
                user = user_result.scalar_one()

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