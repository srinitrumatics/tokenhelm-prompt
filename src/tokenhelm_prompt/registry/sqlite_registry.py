"""Local SQLite registry backend for indexed / larger registries.

Offline by default (Constitution IX). Stores metadata + version hashes only.
"""

from __future__ import annotations

import sqlite3
from datetime import datetime
from pathlib import Path

from tokenhelm_prompt.models import Prompt, Version, VersionStatus
from tokenhelm_prompt.registry.base import _Record, _RegistryEngine

_SCHEMA = """
CREATE TABLE IF NOT EXISTS prompts (
    name TEXT PRIMARY KEY,
    id TEXT NOT NULL,
    current_version TEXT NOT NULL,
    owner TEXT NOT NULL,
    application TEXT NOT NULL,
    environment TEXT NOT NULL,
    description TEXT NOT NULL DEFAULT '',
    tags TEXT NOT NULL DEFAULT '',
    created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS versions (
    name TEXT NOT NULL,
    version TEXT NOT NULL,
    hash TEXT NOT NULL,
    variable_hash TEXT,
    created_by TEXT NOT NULL,
    created_at TEXT NOT NULL,
    status TEXT NOT NULL,
    ord INTEGER NOT NULL,
    PRIMARY KEY (name, version)
);
"""


class SqliteRegistry(_RegistryEngine):
    """A registry persisted to a SQLite database file."""

    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)
        super().__init__()

    def _connect(self) -> sqlite3.Connection:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(self.path)
        conn.executescript(_SCHEMA)
        return conn

    def _load(self) -> None:
        if not self.path.exists():
            # Touch schema so the file exists for subsequent saves.
            self._connect().close()
            return
        conn = self._connect()
        try:
            for row in conn.execute("SELECT * FROM prompts"):
                cols = row
                name = cols[0]
                prompt = Prompt(
                    id=cols[1],
                    name=name,
                    version=cols[2],
                    owner=cols[3],
                    application=cols[4],
                    environment=cols[5],
                    description=cols[6],
                    tags=[t for t in cols[7].split("\n") if t],
                    created_at=datetime.fromisoformat(cols[8]),
                )
                versions: list[Version] = []
                var_hashes: dict[str, str] = {}
                for v in conn.execute(
                    "SELECT version, hash, variable_hash, created_by, created_at, status "
                    "FROM versions WHERE name=? ORDER BY ord",
                    (name,),
                ):
                    versions.append(
                        Version(
                            version=v[0],
                            hash=v[1],
                            created_by=v[3],
                            created_at=datetime.fromisoformat(v[4]),
                            status=VersionStatus(v[5]),
                        )
                    )
                    if v[2] is not None:
                        var_hashes[v[0]] = v[2]
                record = _Record(prompt=prompt, versions=versions)
                record.variable_hashes = var_hashes
                self._records[name] = record
        finally:
            conn.close()

    def _save(self) -> None:
        conn = self._connect()
        try:
            conn.execute("DELETE FROM prompts")
            conn.execute("DELETE FROM versions")
            for name, record in self._records.items():
                p = record.prompt
                conn.execute(
                    "INSERT INTO prompts VALUES (?,?,?,?,?,?,?,?,?)",
                    (
                        name,
                        p.id,
                        p.version,
                        p.owner,
                        p.application,
                        p.environment,
                        p.description,
                        "\n".join(p.tags),
                        p.created_at.isoformat(),
                    ),
                )
                for ordinal, v in enumerate(record.versions):
                    conn.execute(
                        "INSERT INTO versions VALUES (?,?,?,?,?,?,?,?)",
                        (
                            name,
                            v.version,
                            v.hash,
                            record.variable_hashes.get(v.version),
                            v.created_by,
                            v.created_at.isoformat(),
                            v.status.value,
                            ordinal,
                        ),
                    )
            conn.commit()
        finally:
            conn.close()
