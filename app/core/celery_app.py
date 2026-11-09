import logging
import os

from celery import Celery

logger = logging.getLogger(__name__)

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

celery_app = Celery("notification_worker", broker=REDIS_URL, backend=REDIS_URL)

celery_app.conf.update(
    task_serializer="json",
    assert_content=["json"],
    result_serialize="json",
    timezone="UTC",
    enable_utc=True,
)


@celery_app.task(name="task.ping")
def ping_task() -> str:
    logger.info("Celery worker is alive and processing tasks!")
    return "pong"
