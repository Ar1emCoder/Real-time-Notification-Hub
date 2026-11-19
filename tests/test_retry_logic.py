from datetime import UTC, datetime, timedelta
from types import SimpleNamespace

import pytest

from retry_logic import next_retry_delay, register_failure


@pytest.mark.parametrize(
    "initial_attempts, expected_status, expected_attempts, expected_delay_minutes",
    [
        (0, "pending", 1, 1),  # Первая попытка -> ждём 1 минуту
        (1, "pending", 2, 5),  # Вторая попытка -> ждём 5 минут
        (2, "pending", 3, 30),  # Третья попытка -> ждём 30 минут
        (3, "failed", 4, None),  # Лимит исчерпан -> failed
    ],
)
def test_register_failure_logic(
    initial_attempts, expected_status, expected_attempts, expected_delay_minutes
):
    """Тест проверяет, что register_failure корректно обновляет поля события."""

    # Создаём заглушку события
    event = SimpleNamespace(
        attempts=initial_attempts,
        status="pending",
        last_error="",
        send_at=datetime(2026, 11, 19, 20, 0, 0, tzinfo=UTC),
    )

    # Фиксированное время "сейчас"
    now = datetime(2026, 11, 19, 20, 0, 0, tzinfo=UTC)

    # Фиктивная ошибка
    error = Exception("Telegram API Timeout")

    # Вызываем функцию, которую мы напишем
    register_failure(event, error, now)

    # Проверяем результат
    assert event.attempts == expected_attempts
    assert event.status == expected_status
    assert event.last_error == "Telegram API Timeout"

    if expected_delay_minutes is not None:
        expected_send_at = now + timedelta(minutes=expected_delay_minutes)
        assert event.send_at == expected_send_at
    else:
        # Если failed, send_at не должен измениться
        assert event.send_at == datetime(2026, 11, 19, 20, 0, 0, tzinfo=UTC)


def test_register_failure_truncates_long_error():
    """Тест проверяет, что длинные ошибки обрезаются до 500 символов."""
    event = SimpleNamespace(
        attempts=0,
        status="pending",
        last_error="",
        send_at=datetime(2026, 11, 19, 20, 0, 0, tzinfo=UTC),
    )

    now = datetime(2026, 11, 19, 20, 0, 0, tzinfo=UTC)
    long_error = Exception("x" * 1000)  # Ошибка длиной 1000 символов

    register_failure(event, long_error, now)

    assert len(event.last_error) == 500
