"""Post-install release smoke test.

Run against a FRESHLY INSTALLED `tokenhelm-prompt` (from TestPyPI or PyPI) in an
isolated virtual environment. It verifies that the published artifact imports and
works end-to-end, and that the core TokenHelm dependency it builds on is present.

Exits 0 on success, non-zero on the first failure. No network/provider calls.
"""

from __future__ import annotations

import sys
from datetime import datetime, timezone
from decimal import Decimal

failures: list[str] = []


def check(label: str, cond: bool) -> None:
    status = "PASS" if cond else "FAIL"
    print(f"{status}  {label}")
    if not cond:
        failures.append(label)


def main() -> int:
    # --- Released package: tokenhelm-prompt ---------------------------------
    import tokenhelm_prompt

    check("tokenhelm_prompt importable", bool(tokenhelm_prompt))
    check("tokenhelm_prompt.__version__ present", bool(tokenhelm_prompt.__version__))
    print("  tokenhelm-prompt version:", tokenhelm_prompt.__version__)

    from tokenhelm_prompt import YamlRegistry, analytics, make_dispatcher, tracker

    # Registry round-trip (offline).
    import tempfile
    import os

    tmp = tempfile.mkdtemp()
    reg = YamlRegistry(os.path.join(tmp, "smoke.yaml"))
    reg.register(
        "smoke",
        owner="rel",
        application="ci",
        environment="test",
        template="Hello {name}",
    )
    check("registry: register + resolve", reg.get("smoke").version == "v1")

    # Attribution end-to-end through the dispatcher seam.
    import tokenhelm as th

    tracker.use_registry(reg)
    disp = make_dispatcher()
    event = th.LLMEvent(
        provider=th.LLMProvider.OPENAI,
        model="gpt-4",
        input_tokens=1,
        output_tokens=1,
        total_tokens=2,
        latency=0.01,
        cost=Decimal("0.001"),
        timestamp=datetime.now(timezone.utc),
    )
    with tracker.prompt("smoke"):
        disp.dispatch(event)
    by_prompt = {a.prompt_name: a for a in analytics.by_prompt()}
    check("attribution + analytics: event attributed to prompt", by_prompt.get("smoke") is not None)
    by_version = {a.prompt_version: a for a in analytics.by_version()}
    check("attribution: carries version", by_version.get("v1") is not None)

    # --- Core dependency: tokenhelm -----------------------------------------
    check("tokenhelm (core) importable", bool(th))
    check("tokenhelm.__version__ present", bool(getattr(th, "__version__", None)))
    print("  tokenhelm core version:", getattr(th, "__version__", "?"))
    check("core: TokenHelm() constructs", th.TokenHelm() is not None)
    check("core: ConsoleLogger() constructs", th.ConsoleLogger() is not None)
    th.TokenHelm().configure()
    check("core: configure() callable", callable(th.TokenHelm.configure))
    check("core: track() exists", callable(th.TokenHelm.track))
    check("core: track_stream() exists", callable(th.TokenHelm.track_stream))

    print()
    if failures:
        print(f"SMOKE TEST FAILED: {len(failures)} check(s) failed -> {failures}")
        return 1
    print("SMOKE TEST PASSED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
