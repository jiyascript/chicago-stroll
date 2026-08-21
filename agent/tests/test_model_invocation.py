from unittest.mock import patch

import pytest

from app.services.model_invocation import (
    invoke_runnable_with_fallback,
)


class FakeRunnable:
    def __init__(self, results):
        self.results = list(results)
        self.calls = 0

    def invoke(self, payload):
        self.calls += 1

        result = self.results.pop(0)

        if isinstance(result, Exception):
            raise result

        return result


def test_primary_success_does_not_use_fallback() -> None:
    primary = FakeRunnable(
        ["primary success"]
    )
    fallback = FakeRunnable(
        ["fallback success"]
    )

    result = invoke_runnable_with_fallback(
        primary=primary,
        fallback=fallback,
        payload="test",
    )

    assert result == "primary success"
    assert primary.calls == 1
    assert fallback.calls == 0


def test_non_retryable_error_fails_immediately() -> None:
    primary = FakeRunnable(
        [ValueError("bad request")]
    )
    fallback = FakeRunnable(
        ["fallback success"]
    )

    with pytest.raises(ValueError):
        invoke_runnable_with_fallback(
            primary=primary,
            fallback=fallback,
            payload="test",
        )

    assert primary.calls == 1
    assert fallback.calls == 0


@patch(
    "app.services.model_invocation.sleep",
)
@patch(
    "app.services.model_invocation.is_retryable_error",
    return_value=True,
)
def test_retryable_error_retries_primary_then_succeeds(
    mock_retryable,
    mock_sleep,
) -> None:
    primary = FakeRunnable(
        [
            RuntimeError("temporary"),
            "primary success",
        ]
    )
    fallback = FakeRunnable(
        ["fallback success"]
    )

    result = invoke_runnable_with_fallback(
        primary=primary,
        fallback=fallback,
        payload="test",
        max_retries=2,
    )

    assert result == "primary success"
    assert primary.calls == 2
    assert fallback.calls == 0
    assert mock_sleep.call_count == 1


@patch(
    "app.services.model_invocation.sleep",
)
@patch(
    "app.services.model_invocation.is_retryable_error",
    return_value=True,
)
def test_fallback_used_after_primary_exhausts_retries(
    mock_retryable,
    mock_sleep,
) -> None:
    primary = FakeRunnable(
        [
            RuntimeError("temporary 1"),
            RuntimeError("temporary 2"),
            RuntimeError("temporary 3"),
        ]
    )
    fallback = FakeRunnable(
        ["fallback success"]
    )

    result = invoke_runnable_with_fallback(
        primary=primary,
        fallback=fallback,
        payload="test",
        max_retries=2,
    )

    assert result == "fallback success"
    assert primary.calls == 3
    assert fallback.calls == 1
    assert mock_sleep.call_count == 2