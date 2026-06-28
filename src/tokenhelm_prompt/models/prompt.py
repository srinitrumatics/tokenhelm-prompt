"""The :class:`Prompt` entity — a named, owned, versioned prompt identity.

Identity is metadata only; no rendered template text is ever stored here
(Constitution IV and VII).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone

_REQUIRED = ("id", "name", "owner", "application", "environment")


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


@dataclass
class Prompt:
    """Registered prompt metadata.

    ``version`` is the currently-resolved version identifier; the immutable
    revision history lives in the registry as :class:`~tokenhelm_prompt.models.version.Version`
    records.
    """

    id: str
    name: str
    version: str
    owner: str
    application: str
    environment: str
    description: str = ""
    tags: list[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=_utcnow)

    def __post_init__(self) -> None:
        for attr in _REQUIRED:
            value = getattr(self, attr)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"Prompt.{attr} is required and must be non-empty")
