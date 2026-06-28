"""One-way hashing helpers for privacy-safe prompt capture (Constitution VII).

``template_hash`` hashes the template *string*; ``variable_hash`` hashes the
sorted set of variable *names* only — never their values. Neither input is
persisted; only the resulting digests are.
"""

from __future__ import annotations

import hashlib
import re
from collections.abc import Iterable

# Matches ``{name}`` / ``{{name}}`` style placeholders; captures the identifier.
_PLACEHOLDER = re.compile(r"\{\{?\s*([A-Za-z_][A-Za-z0-9_]*)\s*\}?\}")


def template_hash(template: str) -> str:
    """Return the SHA-256 hex digest of the template string."""
    return hashlib.sha256(template.encode("utf-8")).hexdigest()


def variable_names(template: str) -> list[str]:
    """Extract distinct placeholder variable names from a template, sorted."""
    return sorted({m.group(1) for m in _PLACEHOLDER.finditer(template)})


def variable_hash(names: Iterable[str]) -> str:
    """Return the SHA-256 hex digest over the sorted, de-duplicated names."""
    joined = "\n".join(sorted(set(names)))
    return hashlib.sha256(joined.encode("utf-8")).hexdigest()


def variable_hash_from_template(template: str) -> str:
    """Convenience: hash the variable names discovered in ``template``."""
    return variable_hash(variable_names(template))
