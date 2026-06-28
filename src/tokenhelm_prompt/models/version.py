"""The :class:`Version` entity — an immutable revision of a prompt.

Versions are append-only: a template change creates a new version, never a
mutation of an existing one (Constitution VIII).
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class VersionStatus(str, Enum):
    ACTIVE = "active"
    DEPRECATED = "deprecated"
    ARCHIVED = "archived"


@dataclass(frozen=True)
class Version:
    """An immutable prompt revision.

    ``hash`` is the one-way ``template_hash`` (SHA-256 of the template string);
    the template text itself is never persisted.
    """

    version: str
    hash: str
    created_by: str
    created_at: datetime
    status: VersionStatus = VersionStatus.ACTIVE
