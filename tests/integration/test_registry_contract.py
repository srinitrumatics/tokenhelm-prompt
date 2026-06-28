"""US1: registry CRUD + version resolution contract (T011).

Runs the same contract against both bundled backends (Constitution IX).
"""

from __future__ import annotations

import pytest

from tokenhelm_prompt.registry import (
    PromptConflictError,
    PromptNotFoundError,
    SqliteRegistry,
    YamlRegistry,
)


@pytest.fixture(params=["yaml", "sqlite"])
def backend(request, tmp_path):
    if request.param == "yaml":
        return YamlRegistry(tmp_path / "prompts.yaml")
    return SqliteRegistry(tmp_path / "prompts.db")


def test_register_get_list_delete(backend):
    backend.register(
        "greet", owner="o", application="app", environment="prod", template="Hi {name}"
    )
    assert backend.get("greet").name == "greet"
    assert [p.name for p in backend.list()] == ["greet"]

    backend.delete("greet")
    assert backend.list() == []
    with pytest.raises(PromptNotFoundError):
        backend.get("greet")


def test_duplicate_registration_conflicts(backend):
    backend.register("greet", owner="o", application="app", environment="prod", template="Hi")
    with pytest.raises(PromptConflictError):
        backend.register("greet", owner="o", application="app", environment="prod", template="Hi")


def test_missing_metadata_is_rejected(backend):
    from tokenhelm_prompt.registry import PromptValidationError

    with pytest.raises(PromptValidationError):
        backend.register("", owner="o", application="app", environment="prod", template="Hi")


def test_persistence_round_trip(backend):
    backend.register("greet", owner="o", application="app", environment="prod", template="Hi {x}")
    backend.add_version("greet", template="Hi there {x}", created_by="o")

    # Re-open the same store from disk → state is reloaded.
    reopened = type(backend)(backend.path)
    assert [v.version for v in reopened.versions("greet")] == ["v1", "v2"]
    assert reopened.get("greet").version == "v2"
