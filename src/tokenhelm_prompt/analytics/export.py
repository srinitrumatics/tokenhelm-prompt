"""Export analytics aggregates to CSV (tabular) and JSON (structured)."""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Sequence

_FIELDS = ["key", "prompt_name", "prompt_version", "calls", "latency", "tokens", "cost", "failures"]


def export_aggregates(aggregates: Sequence, fmt: str, path: str) -> None:
    """Write ``aggregates`` to ``path`` as ``csv`` (FR-011) or ``json`` (FR-012)."""
    rows = [a.as_dict() for a in aggregates]
    fmt = fmt.lower()
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)

    if fmt == "csv":
        with target.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=_FIELDS)
            writer.writeheader()
            writer.writerows(rows)
    elif fmt == "json":
        target.write_text(json.dumps(rows, indent=2, default=str), encoding="utf-8")
    else:
        raise ValueError(f"unsupported export format: {fmt!r} (use 'csv' or 'json')")
