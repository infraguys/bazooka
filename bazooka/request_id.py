import contextvars
from typing import Optional

REQUEST_ID_HEADER = "X-Request-ID"

_request_id_ctx: contextvars.ContextVar[Optional[str]] = contextvars.ContextVar(
    "bazooka_request_id",
    default=None,
)


def get_request_id() -> Optional[str]:
    return _request_id_ctx.get()


def set_request_id(request_id: Optional[str]) -> contextvars.Token:
    return _request_id_ctx.set(request_id)


def reset_request_id(token: contextvars.Token) -> None:
    _request_id_ctx.reset(token)
