import pytest

from rate_limiter.rate_limiter import RateLimiter


class TestRateLimiter:
    def test_allows_under_limit(self):
        limiter = RateLimiter(limit=3, window_seconds=60)

        assert limiter.allow("user1", now=1.0) is True
        assert limiter.allow("user2", now=2.0) is True
        assert limiter.allow("user1", now=3.0) is True

    def test_blocks_when_limit_reached(self):
        limiter = RateLimiter(limit=2, window_seconds=60)

        assert limiter.allow("user1", now=1.0) is True
        assert limiter.allow("user1", now=2.0) is True
        assert limiter.allow("user1", now=3.0) is False  # лимит достигнут

    def test_different_keys_are_independent(self):
        limiter = RateLimiter(limit=1, window_seconds=60)

        assert limiter.allow("user1", now=1.0) is True
        assert limiter.allow("user2", now=1.0) is True  # другой ключ
        assert limiter.allow("user1", now=2.0) is False

    def test_sliding_window_main_case(self):
        limiter = RateLimiter(limit=5, window_seconds=300)

        for _ in range(5):
            assert (
                limiter.allow("user1", now=299.0) is True
            )  # не достигают лимита - проходят

        for _ in range(5):
            assert (
                limiter.allow("user1", now=301.0) is False
            )  # больше чем положено - не проходят
