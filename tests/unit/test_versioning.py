"""US1: version immutability and resolution (T012)."""

from __future__ import annotations

import pytest

from tokenhelm_prompt.models import Version, VersionStatus
from tokenhelm_prompt.registry.resolver import resolve_version


def test_register_creates_initial_active_version(registry):
    registry.register("p", owner="o", application="a", environment="prod", template="hi {x}")
    versions = registry.versions("p")
    assert len(versions) == 1
    assert versions[0].status is VersionStatus.ACTIVE
    assert registry.get("p").version == "v1"


def test_change_creates_new_immutable_version_old_retained(registry):
    registry.register("p", owner="o", application="a", environment="prod", template="v1 {x}")
    first_hash = registry.versions("p")[0].hash
    registry.add_version("p", template="v2 body {x}", created_by="o")

    versions = registry.versions("p")
    assert [v.version for v in versions] == ["v1", "v2"]
    # Old version is unchanged (immutable) and still retrievable.
    assert registry.versions("p")[0].hash == first_hash
    assert registry.get("p", version="v1").version == "v1"
    # Newest active resolves as current.
    assert registry.get("p").version == "v2"
    assert registry.versions("p")[0].status is VersionStatus.DEPRECATED


def test_resolver_pins_exact_version():
    now = __import__("datetime").datetime.now(__import__("datetime").timezone.utc)
    vs = [
        Version("v1", "h1", "o", now, VersionStatus.DEPRECATED),
        Version("v2", "h2", "o", now, VersionStatus.ACTIVE),
    ]
    assert resolve_version(vs, "v1").version == "v1"
    assert resolve_version(vs, None).version == "v2"


def test_resolver_missing_version_raises():
    now = __import__("datetime").datetime.now(__import__("datetime").timezone.utc)
    vs = [Version("v1", "h1", "o", now, VersionStatus.ACTIVE)]
    with pytest.raises(LookupError):
        resolve_version(vs, "v9")


def test_version_dataclass_is_frozen():
    now = __import__("datetime").datetime.now(__import__("datetime").timezone.utc)
    v = Version("v1", "h", "o", now)
    with pytest.raises(Exception):
        v.hash = "tampered"  # type: ignore[misc]
