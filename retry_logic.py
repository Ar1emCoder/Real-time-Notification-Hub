from datetime import datetime, timedelta


def next_retry_delay(attempts: int) -> timedelta | None:
    list_pause = [timedelta(minutes=1), timedelta(minutes=5), timedelta(minutes=30)]
    if (attempts > len(list_pause)) or attempts < 1:
        return None
    return list_pause[attempts - 1]


def register_failure(event, error: Exception, now: datetime) -> None:
    event.attempts += 1
    event.last_error = str(error)[:500]
    delay = next_retry_delay(event.attempts)
    if delay is None:
        event.status = "failed"
    else:
        event.send_at = now + delay
        event.status = "pending"
