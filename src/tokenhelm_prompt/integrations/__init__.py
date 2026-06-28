"""Optional framework integrations (Constitution III).

Importing this subpackage — or any module in it — must never import a framework
SDK. Each module exposes a factory that imports its SDK lazily, so the core stays
installable and importable without any optional dependency.

Available modules: ``langchain``, ``llamaindex``, ``crewai``, ``google_adk``,
``openai_agents``, ``haystack``.
"""

from __future__ import annotations
