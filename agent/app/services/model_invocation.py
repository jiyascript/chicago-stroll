from time import sleep
from typing import Any
try:
    from google.genai.errors import ClientError, ServerError
except Exception:  # import-safe for tests without SDK details
    ClientError = ServerError = ()

RETRYABLE_STATUS_CODES = {429, 503, 504}

def is_retryable_error(error: Exception) -> bool:
    if ClientError and isinstance(error, (ClientError, ServerError)):
        code = getattr(error, "code", None) or getattr(error, "status_code", None)
        return code in RETRYABLE_STATUS_CODES
    return getattr(error, "status_code", None) in RETRYABLE_STATUS_CODES

def invoke_runnable_with_fallback(primary, fallback, payload: Any, max_retries: int = 2):
    for attempt in range(max_retries + 1):
        try:
            return primary.invoke(payload)
        except Exception as error:
            if not is_retryable_error(error):
                raise
            if attempt < max_retries:
                sleep(1 + attempt)
    return fallback.invoke(payload)
