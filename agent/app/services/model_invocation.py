"""Reliable model invocation with retry and fallback."""
from unittest.mock import patch
import pytest
from time import sleep
from typing import Any
from google.genai.errors import ClientError,ServerError


RETRYABLE_STATUS_CODES = {
    429,
    503,
    504,
}


def is_retryable_error(error: Exception,) -> bool:
    """Return whether a model error is transient."""

    if not isinstance(
        error,
        (ClientError, ServerError),
    ):
        return False

    status_code = getattr(
        error,
        "code",
        None,
    )

    if status_code is None:
        status_code = getattr(
            error,
            "status_code",
            None,
        )

    return (
        status_code
        in RETRYABLE_STATUS_CODES
    )


def invoke_runnable_with_fallback(
    primary,
    fallback,
    payload: Any,
    max_retries: int = 2,
):
    """Retry primary model, then invoke fallback."""

    last_error: Exception | None = None

    for attempt in range(max_retries + 1):
        try:
            return primary.invoke(payload)

        except Exception as error:
            if not is_retryable_error(error):
                raise

            last_error = error

            if attempt < max_retries:
                sleep(1 + attempt)

    try:
        return fallback.invoke(payload)

    except Exception:
        if last_error is not None:
            raise last_error

        raise