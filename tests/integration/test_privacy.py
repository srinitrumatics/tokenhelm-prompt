"""US4: stored records contain only metadata + hashes (T031, SC-006)."""

from __future__ import annotations

import dataclasses

from tokenhelm_prompt import make_dispatcher, tracker
from tokenhelm_prompt.analytics.store import default_store

SECRET = "sk-live-DEADBEEF-super-secret"
TEMPLATE = "Translate {document} using key " + SECRET + " for {customer}"


def test_no_rendered_text_or_secret_in_stored_event(registry, make_event):
    registry.register(
        "translate", owner="o", application="a", environment="prod", template=TEMPLATE
    )
    tracker.use_registry(registry)
    disp = make_dispatcher()

    with tracker.prompt("translate"):
        disp.dispatch(make_event())

    event = default_store.all()[0]
    blob = repr(dataclasses.asdict(event))
    assert SECRET not in blob
    assert "Translate" not in blob
    assert "{document}" not in blob


def test_registry_file_never_contains_template_text(registry):
    registry.register(
        "translate", owner="o", application="a", environment="prod", template=TEMPLATE
    )
    on_disk = registry.path.read_text(encoding="utf-8")
    assert SECRET not in on_disk
    assert "Translate" not in on_disk
    # but the template hash is present
    assert registry.versions("translate")[0].hash in on_disk


def test_metadata_carries_hashes(registry):
    registry.register(
        "translate", owner="o", application="a", environment="prod", template=TEMPLATE
    )
    tracker.use_registry(registry)
    with tracker.prompt("translate"):
        meta = tracker.current_prompt()
    assert meta.template_hash and len(meta.template_hash) == 64
    assert meta.variable_hash and len(meta.variable_hash) == 64
