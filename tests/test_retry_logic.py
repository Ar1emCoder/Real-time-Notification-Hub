from datetime import timedelta

import pytest

from retry_logic import next_retry_delay


@pytest.mark.parametrize(
    "attempts, expected_delay",
    [
        (1, timedelta(minutes=1)),
        (2, timedelta(minutes=5)),
        (3, timedelta(minutes=30)),
        (4, None),
        (10, None),
    ],
)
def test_next_retry_delay(attempts, expected_delay):
    result = next_retry_delay(attempts)

    assert result == expected_delay
