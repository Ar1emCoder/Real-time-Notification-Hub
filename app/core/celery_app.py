import logging
import os

from celery import Celery
from celery.schedules import crontab

logger = logging.getLogger(__name__)

# Получаем URL Redis из окружения
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

# Создаём приложение.
# include=["app.tasks"] — это ключевой момент! Он говорит Celery
# лениво загрузить задачи, избегая циклических импортов на старте.
celery_app = Celery(
    "notification_worker",
    broker=REDIS_URL,
    backend=REDIS_URL,
    include=["app.tasks"],
)

# Настройки сериализации и часового пояса
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
)

# Расписание для Celery Beat
celery_app.conf.beat_schedule = {
    "process-pending-every-minute": {
        "task": "tasks.process_pending",
        "schedule": crontab(minute="*/1"),
    },
}
