class RateLimiter:
    def __init__(self, limit: int, window_seconds: int):
        self.limit = limit
        self.window_seconds = window_seconds
        self.requests: dict[str, list[float]] = {}

    def allow(self, key: str, now: float) -> bool:
        if key not in self.requests:
            self.requests[key] = []

        self.requests[key] = [
            timestamp
            for timestamp in self.requests[key]
            if timestamp > now - self.window_seconds
        ]

        if len(self.requests[key]) < self.limit:
            self.requests[key].append(now)
            return True
        else:
            return False
