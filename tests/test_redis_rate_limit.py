import time

import pytest
import redis

from rate_limiter.redis_rate_limit import allow


@pytest.fixture(scope="function")
def redis_client():
    client = redis.Redis(host="localhost", port=6379, db=15)
    client.flushdb()
    yield client
    client.flushdb()
    client.close()


def test_first_request_allowed(redis_client):
    result = allow(redis_client, "user:1", limit=3, window=60)
    assert result is True


def test_over_limit_blocked(redis_client):
    for _ in range(3):
        assert allow(redis_client, "user:1", limit=3, window=60) is True
    assert allow(redis_client, "user:1", 3, window=60) is False


def test_window_expires_and_resets(redis_client):
    for _ in range(2):
        assert allow(redis_client, "user:1", limit=2, window=1) is True
    assert allow(redis_client, "user:1", limit=2, window=1) is False

    # обновление счетчика limit
    time.sleep(1.1)
    assert allow(redis_client, "user:1", limit=1, window=1) is True


def test_users_are_independent(redis_client):
    for _ in range(2):
        assert allow(redis_client, "user:1", limit=2, window=1) is True
    assert allow(redis_client, "user:1", limit=2, window=1) is False

    assert allow(redis_client, "user:2", limit=2, window=1) is True
