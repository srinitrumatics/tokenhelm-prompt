"""The :class:`PromptRegistry` interface plus a reusable in-memory engine.

Backends (YAML, SQLite, or custom) subclass :class:`_RegistryEngine` and override
:meth:`_load` / :meth:`_save`. The engine holds all CRUD + versioning logic so the
behavior is identical across backends (Constitution VIII: append-only versions).
"""

from __future__ import annotations

import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timezone

from tokenhelm_prompt.lib import hashing
from tokenhelm_prompt.models import Prompt, Version, VersionStatus
from tokenhelm_prompt.registry.resolver import resolve_version


class RegistryError(Exception):
    """Base class for registry errors."""


class PromptNotFoundError(RegistryError):
    """Raised when a prompt (or version) is not in the registry."""


class PromptConflictError(RegistryError):
    """Raised when registering a name that already exists."""


class PromptValidationError(RegistryError, ValueError):
    """Raised when prompt metadata is invalid."""


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


@dataclass
class _Record:
    """Internal per-prompt record: metadata + append-only version history."""

    prompt: Prompt
    versions: list[Version] = field(default_factory=list)
    # variable_hash is non-sensitive (hashes of names) kept parallel to versions.
    variable_hashes: dict[str, str] = field(default_factory=dict)


class PromptRegistry(ABC):
    """Public registry contract (see contracts/registry.md)."""

    @abstractmethod
    def register(
        self,
        name: str,
        *,
        owner: str,
        application: str,
        environment: str,
        template: str,
        description: str = "",
        tags: list[str] | None = None,
        created_by: str | None = None,
        version: str | None = None,
    ) -> Prompt: ...

    @abstractmethod
    def get(self, name: str, version: str | None = None) -> Prompt: ...

    @abstractmethod
    def list(self) -> list[Prompt]: ...

    @abstractmethod
    def delete(self, name: str) -> None: ...

    @abstractmethod
    def add_version(
        self,
        name: str,
        *,
        template: str,
        created_by: str | None = None,
        version: str | None = None,
        status: VersionStatus = VersionStatus.ACTIVE,
    ) -> Version: ...

    @abstractmethod
    def versions(self, name: str) -> list[Version]: ...


class _RegistryEngine(PromptRegistry):
    """Concrete CRUD/versioning engine with pluggable persistence hooks."""

    def __init__(self) -> None:
        self._records: dict[str, _Record] = {}
        self._load()

    # ---- persistence hooks (overridden by backends) -------------------------
    def _load(self) -> None:  # pragma: no cover - default no-op
        """Populate ``self._records`` from the backing store."""

    def _save(self) -> None:  # pragma: no cover - default no-op
        """Persist ``self._records`` to the backing store."""

    # ---- helpers ------------------------------------------------------------
    @staticmethod
    def _next_version(existing: list[Version]) -> str:
        return f"v{len(existing) + 1}"

    def _require(self, name: str) -> _Record:
        try:
            return self._records[name]
        except KeyError:
            raise PromptNotFoundError(f"prompt {name!r} not found") from None

    def _resolved_prompt(self, record: _Record, version: str | None) -> Prompt:
        resolved = resolve_version(record.versions, version)
        base = record.prompt
        return Prompt(
            id=base.id,
            name=base.name,
            version=resolved.version,
            owner=base.owner,
            application=base.application,
            environment=base.environment,
            description=base.description,
            tags=list(base.tags),
            created_at=base.created_at,
        )

    # ---- CRUD ---------------------------------------------------------------
    def register(
        self,
        name: str,
        *,
        owner: str,
        application: str,
        environment: str,
        template: str,
        description: str = "",
        tags: list[str] | None = None,
        created_by: str | None = None,
        version: str | None = None,
    ) -> Prompt:
        if name in self._records:
            raise PromptConflictError(f"prompt {name!r} already registered")
        try:
            ver_str = version or "v1"
            initial = Version(
                version=ver_str,
                hash=hashing.template_hash(template),
                created_by=created_by or owner,
                created_at=_utcnow(),
                status=VersionStatus.ACTIVE,
            )
            prompt = Prompt(
                id=uuid.uuid4().hex,
                name=name,
                version=ver_str,
                owner=owner,
                application=application,
                environment=environment,
                description=description,
                tags=list(tags or []),
            )
        except ValueError as exc:
            raise PromptValidationError(str(exc)) from exc
        record = _Record(prompt=prompt, versions=[initial])
        record.variable_hashes[ver_str] = hashing.variable_hash_from_template(template)
        self._records[name] = record
        self._save()
        return self._resolved_prompt(record, None)

    def get(self, name: str, version: str | None = None) -> Prompt:
        return self._resolved_prompt(self._require(name), version)

    def list(self) -> list[Prompt]:
        return [self._resolved_prompt(r, None) for r in self._records.values()]

    def delete(self, name: str) -> None:
        self._require(name)
        del self._records[name]
        self._save()

    def add_version(
        self,
        name: str,
        *,
        template: str,
        created_by: str | None = None,
        version: str | None = None,
        status: VersionStatus = VersionStatus.ACTIVE,
    ) -> Version:
        record = self._require(name)
        ver_str = version or self._next_version(record.versions)
        if any(v.version == ver_str for v in record.versions):
            raise PromptConflictError(f"version {ver_str!r} already exists for {name!r}")
        new_version = Version(
            version=ver_str,
            hash=hashing.template_hash(template),
            created_by=created_by or record.prompt.owner,
            created_at=_utcnow(),
            status=status,
        )
        if status is VersionStatus.ACTIVE:
            # Only one active version at a time; demote prior actives.
            record.versions = [
                v
                if v.status is not VersionStatus.ACTIVE
                else Version(
                    v.version, v.hash, v.created_by, v.created_at, VersionStatus.DEPRECATED
                )
                for v in record.versions
            ]
        record.versions.append(new_version)
        record.variable_hashes[ver_str] = hashing.variable_hash_from_template(template)
        record.prompt.version = resolve_version(record.versions, None).version
        self._save()
        return new_version

    def versions(self, name: str) -> list[Version]:
        return list(self._require(name).versions)

    # ---- attribution support -----------------------------------------------
    def metadata_for(self, name: str, version: str | None = None):
        """Return attribution fields for ``name`` (used by the tracker)."""
        record = self._require(name)
        resolved = resolve_version(record.versions, version)
        return {
            "prompt_id": record.prompt.id,
            "prompt_version": resolved.version,
            "owner": record.prompt.owner,
            "application": record.prompt.application,
            "environment": record.prompt.environment,
            "template_hash": resolved.hash,
            "variable_hash": record.variable_hashes.get(resolved.version),
        }
