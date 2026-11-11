import asyncio
from datetime import UTC, datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.celery_app import celery_app
from app.database import async_session_maker
from app.models.notification import Notification
from app.services.notification_sender import send_pending_notifications
from app.services.quiet_hours import is_quiet, next_allowed_time


@celery_app.task(name="tasks.ping")
def ping_task():
    return "pong"


@celery_app.task(name="tasks.process_pending")
def process_pending():
    asyncio.run(_process_pending_async())


async def _process_pending_async():
    import os

    POSTGRES_USER = os.getenv("POSTGRES_USER", "notification_user")
    POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "change_me_in_production")
    POSTGRES_DB = os.getenv("POSTGRES_DB", "notification_hub")
    POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
    POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")

    DATABASE_URL = f"postgresql+asyncpg://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"

    engine = create_async_engine(DATABASE_URL, echo=False)
    session_maker = async_sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )

    try:
        async with session_maker() as session:
            now = datetime.now(UTC)
            stmt = (
                select(Notification)
                .where(Notification.status == "pending", Notification.send_at <= now)
                .limit(50)
            )
            result = await session.execute(stmt)
            events = result.scalars().all()
            print(f"Найдено {len(events)} pending событий")

            for event in events:
                try:
                    if is_quiet(
                        now_utc=now,
                        tz=event.user.timezone,
                        start=event.user.quiet_start,
                        end=event.user.quiet_end,
                    ):
                        new_send_at = next_allowed_time(
                            now_utc=now,
                            tz=event.user.timezone,
                            start=event.user.quiet_start,
                            end=event.user.quiet_end,
                        )

                        # Защита от зацикливания: новое время должно быть в будущем
                        if new_send_at > now:
                            event.send_at = new_send_at
                            await session.commit()
                            print(f"Событие {event.id} перенесено на {new_send_at}")
                            continue  # Пропускаем отправку

                    await send_pending_notifications(event)

                    event.status = "sent"
                    await session.commit()
                    print(f"Событие {event.id} помечено как sent")

                except Exception as e:
                    event.status = "failed"
                    await session.commit()
                    print(f"Ошибка обработки события {event.id}: {e}")
    finally:
        await engine.dispose()
