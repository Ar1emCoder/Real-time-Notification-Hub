from datetime import timedelta


def next_retry_delay(attempts: int) -> timedelta | None:
    list_pause = [timedelta(minutes=1), timedelta(minutes=5), timedelta(minutes=30)]
    if (attempts > len(list_pause)) or attempts < 1:
        return None
    return list_pause[attempts - 1]
