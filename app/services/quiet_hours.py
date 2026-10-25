from datetime import datetime, time, timezone, timedelta
from zoneinfo import ZoneInfo

def is_quiet(now_utc, tz, start, end) -> bool:
    # Перевод UTC в локальное время пользователя
    local_tz = ZoneInfo(tz)
    local_now = now_utc.astimezone(local_tz)
    t = local_now.time()

    # Отключение 'тихих часов'
    if start == end:
        return False

    if start < end:
        return start <= t < end
    else:
        return t >= start or t < end  # за пределами - тихие часы


def next_allowed_time(now_utc, tz, start, end):
    if not is_quiet(now_utc, tz, start, end):
        return now_utc
    local_tz = ZoneInfo(tz)
    local_now = now_utc.astimezone(local_tz)
    end_dt_today = datetime.combine(local_now.date(), end, tzinfo=local_tz)

    if end_dt_today <= local_now:
        end_dt_today += timedelta(days=1)

    return end_dt_today.astimezone(timezone.utc)