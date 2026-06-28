"""Post-install release smoke test for ``tokenhelm-prompt``.

Run against a FRESHLY INSTALLED ``tokenhelm-prompt`` (from TestPyPI or PyPI) in an
isolated virtual environment. It proves the published artifact imports, resolves
its ``tokenhelm`` core dependency, and works end-to-end. Exits non-zero on the
first failure. No network/provider calls.

Note on API shape: ``PromptRegistry`` is an abstract base class, so this test
uses the concrete ``YamlRegistry`` backend, and ``register()`` is called with the
metadata it requires (owner/application/environment/template). ``PromptTracker``
takes a *registry*. This matches the shipped public API.
"""

from __future__ import annotations

import os
import sys
import tempfile

# Imports the release must satisfy (core dependency + this package).
from tokenhelm import ConsoleLogger, TokenHelm
from tokenhelm_prompt import PromptRegistry, PromptTracker, YamlRegistry

failures: list[str] = []


def check(label: str, cond: bool) -> None:
    print(f"{'PASS' if cond else 'FAIL'}  {label}")
    if not cond:
        failures.append(label)


def main() -> int:
    import tokenhelm
    import tokenhelm_prompt

    # --- import + dependency resolution + versions --------------------------
    print("tokenhelm core version:", tokenhelm.__version__)
    print("tokenhelm-prompt version:", tokenhelm_prompt.__version__)
    check("import: tokenhelm (core dependency resolved)", bool(tokenhelm.__version__))
    check("import: tokenhelm_prompt", bool(tokenhelm_prompt.__version__))

    # --- core API present ---------------------------------------------------
    client = TokenHelm()
    check("core: TokenHelm() constructs", client is not None)
    check("core: ConsoleLogger() constructs", ConsoleLogger() is not None)

    # --- PromptRegistry works (via concrete backend) ------------------------
    registry = YamlRegistry(os.path.join(tempfile.mkdtemp(), "smoke.yaml"))
    check("registry: is a PromptRegistry", isinstance(registry, PromptRegistry))
    prompt = registry.register(
        name="invoice_summary",
        owner="release",
        application="ci",
        environment="test",
        template="Summarize invoice {invoice_id}",
        version="v1",
    )
    check("registry: register returns prompt at v1", prompt.version == "v1")
    check("registry: get resolves v1", registry.get("invoice_summary").version == "v1")

    # --- PromptTracker + context manager work -------------------------------
    tracker = PromptTracker(registry)
    with tracker.prompt("invoice_summary", version="v1"):
        active = tracker.current_prompt()
        check("tracker: context manager attributes prompt", active.prompt_name == "invoice_summary")
        check("tracker: resolves registered version", active.prompt_version == "v1")
    check("tracker: context manager restores on exit", tracker.current_prompt() is None)

    # --- explicit asserts from the release spec -----------------------------
    assert client is not None
    assert registry is not None

    print()
    if failures:
        print(f"SMOKE TEST FAILED: {len(failures)} check(s) failed -> {failures}")
        return 1
    print("SMOKE TEST PASSED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
