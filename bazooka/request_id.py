from __future__ import annotations

import contextvars
from typing import Optional
import uuid

REQUEST_ID_HEADER = "X-Request-ID"

_request_id_ctx: contextvars.ContextVar[Optional[str]] = contextvars.ContextVar(
    "bazooka_request_id",
    default=None,
)


def get_request_id() -> Optional[str]:
    return _request_id_ctx.get()


def generate_request_id() -> str:
    return str(uuid.uuid4())


def resolve_request_id(request_id: Optional[str] = None) -> str:
    return request_id or generate_request_id()


def set_request_id(
    request_id: Optional[str] = None,
) -> contextvars.Token[Optional[str]]:
    return _request_id_ctx.set(resolve_request_id(request_id))


def reset_request_id(token: contextvars.Token[Optional[str]]) -> None:
    _request_id_ctx.reset(token)
