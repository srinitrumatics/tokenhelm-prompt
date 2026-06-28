"""Version resolution: latest ``active`` by default, or an exact pinned version."""

from __future__ import annotations

from tokenhelm_prompt.models import Version, VersionStatus


def resolve_version(versions: list[Version], version: str | None) -> Version:
    """Resolve which :class:`Version` applies.

    - ``version`` given → that exact version (or :class:`KeyError`-style miss).
    - otherwise → the latest ``active`` version; if none are active, the most
      recently created version overall.
    """
    if not versions:
        raise LookupError("prompt has no versions")

    if version is not None:
        for candidate in versions:
            if candidate.version == version:
                return candidate
        raise LookupError(f"version {version!r} not found")

    active = [v for v in versions if v.status is VersionStatus.ACTIVE]
    pool = active or versions
    # Latest by creation time; ties fall back to insertion order (last wins).
    return max(pool, key=lambda v: (v.created_at, versions.index(v)))
