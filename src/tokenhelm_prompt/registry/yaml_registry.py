"""Offline, human-editable YAML registry backend (the default).

Works with no network access (Constitution IX). Persists metadata + version
history (hashes only — never template text).
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

import yaml

from tokenhelm_prompt.models import Prompt, Version, VersionStatus
from tokenhelm_prompt.registry.base import _Record, _RegistryEngine


class YamlRegistry(_RegistryEngine):
    """A registry stored as a single YAML document."""

    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)
        super().__init__()

    def _load(self) -> None:
        if not self.path.exists():
            return
        raw = yaml.safe_load(self.path.read_text(encoding="utf-8")) or {}
        for name, entry in raw.get("prompts", {}).items():
            meta = entry["metadata"]
            prompt = Prompt(
                id=meta["id"],
                name=name,
                version=meta["version"],
                owner=meta["owner"],
                application=meta["application"],
                environment=meta["environment"],
                description=meta.get("description", ""),
                tags=list(meta.get("tags", [])),
                created_at=datetime.fromisoformat(meta["created_at"]),
            )
            versions = [
                Version(
                    version=v["version"],
                    hash=v["hash"],
                    created_by=v["created_by"],
                    created_at=datetime.fromisoformat(v["created_at"]),
                    status=VersionStatus(v["status"]),
                )
                for v in entry.get("versions", [])
            ]
            record = _Record(prompt=prompt, versions=versions)
            record.variable_hashes = dict(entry.get("variable_hashes", {}))
            self._records[name] = record

    def _save(self) -> None:
        doc: dict = {"prompts": {}}
        for name, record in self._records.items():
            p = record.prompt
            doc["prompts"][name] = {
                "metadata": {
                    "id": p.id,
                    "version": p.version,
                    "owner": p.owner,
                    "application": p.application,
                    "environment": p.environment,
                    "description": p.description,
                    "tags": list(p.tags),
                    "created_at": p.created_at.isoformat(),
                },
                "versions": [
                    {
                        "version": v.version,
                        "hash": v.hash,
                        "created_by": v.created_by,
                        "created_at": v.created_at.isoformat(),
                        "status": v.status.value,
                    }
                    for v in record.versions
                ],
                "variable_hashes": dict(record.variable_hashes),
            }
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(yaml.safe_dump(doc, sort_keys=True), encoding="utf-8")
