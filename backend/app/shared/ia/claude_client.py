from functools import lru_cache

from anthropic import AsyncAnthropic

# Si el modelo principal rechaza la solicitud, la API reintenta con un modelo de respaldo.
FALLBACK = {"betas": ["server-side-fallback-2026-07-01"], "fallbacks": "default"}


@lru_cache
def get_claude() -> AsyncAnthropic:
    return AsyncAnthropic(timeout=30.0, max_retries=2)
