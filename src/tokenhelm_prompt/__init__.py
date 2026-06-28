"""TokenHelm Prompt Intelligence — additive prompt attribution for TokenHelm.

Public surface (no framework/provider SDKs imported here — Constitution III)::

    from tokenhelm_prompt import (
        tracker, prompt, analytics, make_dispatcher,
        YamlRegistry, SqliteRegistry,
    )

Optional framework integrations live under ``tokenhelm_prompt.integrations`` and
are imported lazily only when you reference them.
"""

from __future__ import annotations

from tokenhelm_prompt.analytics import (
    Aggregate,
    Analytics,
    PromptEventStore,
    analytics,
    default_store,
)
from tokenhelm_prompt.models import (
    EventStatus,
    Prompt,
    PromptEvent,
    PromptMetadata,
    Version,
    VersionStatus,
)
from tokenhelm_prompt.registry import (
    PromptConflictError,
    PromptNotFoundError,
    PromptRegistry,
    PromptValidationError,
    RegistryError,
    SqliteRegistry,
    YamlRegistry,
)
from tokenhelm_prompt.tracking import (
    PromptEnrichingDispatcher,
    PromptTracker,
    make_dispatcher,
    prompt,
    tracker,
)

__version__ = "0.1.0"

__all__ = [
    "__version__",
    # tracking
    "tracker",
    "prompt",
    "PromptTracker",
    "PromptEnrichingDispatcher",
    "make_dispatcher",
    # analytics
    "analytics",
    "Analytics",
    "Aggregate",
    "PromptEventStore",
    "default_store",
    # registry
    "PromptRegistry",
    "YamlRegistry",
    "SqliteRegistry",
    "RegistryError",
    "PromptNotFoundError",
    "PromptConflictError",
    "PromptValidationError",
    # models
    "Prompt",
    "Version",
    "VersionStatus",
    "PromptEvent",
    "EventStatus",
    "PromptMetadata",
]
