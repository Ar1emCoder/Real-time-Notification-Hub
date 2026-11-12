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


# функция отметки события
async def _process_pending_async():
    # импортируем библиотеку для использования os.getenv()
    import os

    # получаем значения с БД для работы с Postgres
    postgres_user = os.getenv("POSTGRES_USER", "notification_user")
    postgres_password = os.getenv("POSTGRES_PASSWORD", "change_me_in_production")
    postgres_db = os.getenv("POSTGRES_DB", "notification_hub")
    postgres_host = os.getenv("POSTGRES_HOST", "localhost")
    postgres_port = os.getenv("POSTGRES_PORT", "5432")

    database_url = f"postgresql+asyncpg://{postgres_user}:{postgres_password}@{postgres_host}:{postgres_port}/{postgres_db}"

    # создаем движок для бд
    engine = create_async_engine(database_url, echo=False)
    # создаем асинхронную сессию
    session_maker = async_sessionmaker(
        # указываем синхронный или асинхронный и коммит что ли
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    # начало обработки исключения
    try:
        # как я понимаю, если находим сессию - подключаемся и работаем с ней
        async with session_maker() as session:
            # задаем конкретное - настоящее - время по utc - часовому поясу
            now = datetime.now(UTC)
            # делаем запрос к бд тк, он сложный - используем select с условием, что статус - в ожидании и отправление ранее или сейчас c .limit(50) ограничивает выборку 50 записями за один раз, чтобы не перегружать память и БД.)
            stmt = (
                select(Notification)
                .where(Notification.status == "pending", Notification.send_at <= now)
                .limit(50)
            )
            # создаем задачу асинхронную (await - которая может переключиться пока выполняется) - работаем с тем же stmt
            result = await session.execute(stmt)
            # извлекаем одно число
            events = result.scalars().all()
            # выводим кол-во событий в ожидании находящихся
            print(f"Найдено {len(events)} pending событий")

            # перебираем все события
            for event in events:
                # обработка исключения
                try:
                    # проверяем работу тихих часов если True - выполняется
                    if is_quiet(
                        # получаем данное время
                        now_utc=now,
                        # как я понимаю, текущий часовой пояс
                        tz=event.user.timezone,
                        # начало тихих часов события
                        start=event.user.quiet_start,
                        # конец тихих часов события
                        end=event.user.quiet_end,
                    ):
                        # новая отправка (время) - скорее всего переназначение по времени либо часовому поясу и тп
                        new_send_at = next_allowed_time(
                            now_utc=now,
                            tz=event.user.timezone,
                            start=event.user.quiet_start,
                            end=event.user.quiet_end,
                        )

                        # Защита от зацикливания: новое время должно быть в будущем
                        if new_send_at > now:
                            # переназначаем отправку уведомления
                            event.send_at = new_send_at
                            # используем асинхронную конструкцию сессии и коммитим
                            await session.commit()
                            # выводим какое события и насколько оно перенесено
                            print(f"Событие {event.id} перенесено на {new_send_at}")
                            continue  # Пропускаем отправку

                    # отравляем сообщение по событию конкретному
                    await send_pending_notifications(event)

                    # меняем статус на отправлено
                    event.status = "sent"
                    # запоминаем - коммитим
                    await session.commit()
                    # выводим что событие помечено как sent - выполненное
                    print(f"Событие {event.id} помечено как sent")

                # обработка исключения (2 блок) - вывод ошибки
                except Exception as e:
                    # меняем статус на failed
                    event.status = "failed"
                    # коммитим
                    await session.commit()
                    # выводим ошибку
                    print(f"Ошибка обработки события {event.id}: {e}")
    # завершаем ошибку после корректного выполнения - после выполнения события
    finally:
        # ГАРАНТИРОВАННО закрываем пул соединений с БД при завершении задачи
        await engine.dispose()
