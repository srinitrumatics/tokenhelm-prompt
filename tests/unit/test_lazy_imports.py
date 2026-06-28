"""Constitution III: core imports with no framework SDKs; integrations stay lazy (T044)."""

from __future__ import annotations

import importlib

import pytest

INTEGRATIONS = [
    "tokenhelm_prompt.integrations.langchain",
    "tokenhelm_prompt.integrations.llamaindex",
    "tokenhelm_prompt.integrations.crewai",
    "tokenhelm_prompt.integrations.google_adk",
    "tokenhelm_prompt.integrations.openai_agents",
    "tokenhelm_prompt.integrations.haystack",
]


def test_core_import_pulls_in_no_framework_sdk():
    import tokenhelm_prompt  # noqa: F401
    import sys

    for sdk in ("langchain_core", "llama_index", "crewai", "agents", "haystack"):
        assert sdk not in sys.modules, f"core import unexpectedly loaded {sdk}"


@pytest.mark.parametrize("module", INTEGRATIONS)
def test_integration_module_imports_without_sdk(module):
    # Importing the integration module must succeed even when the SDK is absent;
    # only calling its factory would require the dependency.
    mod = importlib.import_module(module)
    assert mod is not None
