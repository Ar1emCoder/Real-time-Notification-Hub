import pytest
from datetime import datetime, time, timezone
from zoneinfo import ZoneInfo

from app.services.quiet_hours import is_quiet, next_allowed_time

@pytest.mark.parametrize("utc_zone, tz, start, end, expected", [
    # Окно через полночь (23:00 - 08:00), пользователь в UTC
    ("2026-10-25 22:59:00", "UTC", time(23, 0), time(8, 0), False),  # До окна — не тихо
    ("2026-10-25 23:00:00", "UTC", time(23, 0), time(8, 0), True),  # Начало окна — тихо
    ("2026-10-25 23:59:00", "UTC", time(23, 0), time(8, 0), True),  # Внутри окна — тихо
    ("2026-10-26 07:59:00", "UTC", time(23, 0), time(8, 0), True),  # Внутри окна — тихо
    ("2026-10-26 08:00:00", "UTC", time(23, 0), time(8, 0), False),  # Конец окна — не тихо

    # Окно внутри суток (13:00 - 15:00)
    ("2026-10-25 12:59:00", "UTC", time(13, 0), time(15, 0), False),
    ("2026-10-25 13:00:00", "UTC", time(13, 0), time(15, 0), True),
    ("2026-10-25 14:59:00", "UTC", time(13, 0), time(15, 0), True),
    ("2026-10-25 15:00:00", "UTC", time(13, 0), time(15, 0), False),

    # Пользователь в другом часовом поясе (Москва = UTC+3)
    # 23:00 UTC = 02:00 MSK (тихо, если окно 01:00-09:00)
    ("2026-10-25 23:00:00", "Europe/Moscow", time(1, 0), time(9, 0), True),

    # start == end — тихие часы отключены
    ("2026-10-25 12:00:00", "UTC", time(12, 0), time(12, 0), False),
])
def test_is_quiet(utc_zone, tz, start, end, expected):
    now_utc = datetime.fromisoformat(utc_zone).replace(tzinfo=timezone.utc)
    assert  is_quiet(now_utc, tz, start, end) == expected


@pytest.mark.parametrize("utc_now, tz, start, end, expected_utc", [
    # Не тихо — возвращаем now_utc
    ("2026-10-25 10:00:00", "UTC", time(23, 0), time(8, 0), "2026-10-25 10:00:00"),

    # Тихо, окно через полночь, сейчас 23:30 → конец окна завтра 08:00
    ("2026-10-25 23:30:00", "UTC", time(23, 0), time(8, 0), "2026-10-26 08:00:00"),

    # Тихо, окно через полночь, сейчас 03:00 → конец окна сегодня 08:00
    ("2026-10-26 03:00:00", "UTC", time(23, 0), time(8, 0), "2026-10-26 08:00:00"),
])
def test_next_allowed_time(utc_now, tz, start, end, expected_utc):
    now_utc = datetime.fromisoformat(utc_now).replace(tzinfo=timezone.utc)
    result = next_allowed_time(now_utc, tz, start, end)
    expected = datetime.fromisoformat(expected_utc).replace(tzinfo=timezone.utc)
    assert result == expected