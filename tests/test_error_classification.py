import pytest

from rate_limiter.error_classification import (
    BotBlockedError,
    ChatNotFoundError,
    InvalidTokenError,
    NetworkError,
    RetryDecision,
    ServerError,
    TelegramRetryAfterError,
    classify_error,
)


@pytest.mark.parametrize(
    "exc, expected",
    [
        # добавление случаев
        (
            NetworkError(),
            RetryDecision(should_retry=True, delay=None),
        ),  # Сетевая ошибка - таймаут
        (
            TelegramRetryAfterError(retry_after=30),
            RetryDecision(should_retry=True, delay=30),
        ),  # 429
        (
            BotBlockedError(),
            RetryDecision(should_retry=False, delay=None),
        ),  # Бот заблокирован
        (
            InvalidTokenError(),
            RetryDecision(should_retry=False, delay=None),
        ),  # Неверный токен - 401
        (
            ServerError(),
            RetryDecision(should_retry=True, delay=None),
        ),  # Ошибка сервера - таймаут
        (
            ChatNotFoundError(),
            RetryDecision(should_retry=False, delay=None),
        ),  # Не найден чат - отклонить запрос
    ],
)
def test_classify_error(exc, expected):
    result = classify_error(exc)
    assert result.should_retry == expected.should_retry
    assert result.delay == expected.delay
