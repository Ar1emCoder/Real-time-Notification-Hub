from dataclasses import dataclass
from typing import Optional


@dataclass
class RetryDecision:
    should_retry: bool
    delay: float | None = None


def classify_error(exc) -> RetryDecision:
    if isinstance(exc, NetworkError):
        return RetryDecision(should_retry=True, delay=None)

    if isinstance(exc, TelegramRetryAfterError):
        return RetryDecision(should_retry=True, delay=exc.retry_after)

    if isinstance(exc, (BotBlockedError, InvalidTokenError)):
        return RetryDecision(should_retry=False, delay=None)

    if isinstance(exc, (BotBlockedError, InvalidTokenError, ChatNotFoundError)):
        return RetryDecision(should_retry=False, delay=None)

    return RetryDecision(should_retry=True, delay=None)


class NetworkError(Exception):
    pass


class TelegramRetryAfterError(Exception):
    def __init__(self, retry_after: float):
        self.retry_after = retry_after


class BotBlockedError(Exception):
    pass


class InvalidTokenError(Exception):
    pass


class ServerError(Exception):
    pass


class ChatNotFoundError(Exception):
    pass
