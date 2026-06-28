"""``tokenhelm-prompt`` CLI — manage the local prompt registry (FR-013).

Commands: ``init``, ``list``, ``versions``, ``export``, ``diff``. All operate on
a local registry and work offline (Constitution IX). No command ever prints
rendered prompt text, variable values, or secrets (Constitution VII).

Note: ``export`` exports the registry *inventory* (prompts + versions); live
per-call analytics are exported from the Python API (``analytics.export``),
because attributed events are process-local and not persisted by this version.
"""

from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

import click

from tokenhelm_prompt.registry import PromptNotFoundError, YamlRegistry
from tokenhelm_prompt.registry.resolver import resolve_version

_DEFAULT_REGISTRY = "prompts.yaml"


def _registry(path: str) -> YamlRegistry:
    return YamlRegistry(path)


@click.group()
@click.option(
    "--registry",
    "-r",
    default=_DEFAULT_REGISTRY,
    show_default=True,
    help="Path to the local prompt registry file.",
)
@click.pass_context
def cli(ctx: click.Context, registry: str) -> None:
    """TokenHelm Prompt Intelligence registry CLI."""
    ctx.ensure_object(dict)
    ctx.obj["registry_path"] = registry


@cli.command()
@click.pass_context
def init(ctx: click.Context) -> None:
    """Initialize a new local prompt registry."""
    path = Path(ctx.obj["registry_path"])
    if path.exists():
        click.echo(f"error: registry already exists at {path}", err=True)
        raise SystemExit(1)
    reg = _registry(str(path))
    reg._save()  # create the empty store file
    click.echo(f"Initialized prompt registry at {path}")


@cli.command(name="list")
@click.pass_context
def list_prompts(ctx: click.Context) -> None:
    """List registered prompts with their current versions."""
    reg = _registry(ctx.obj["registry_path"])
    prompts = reg.list()
    if not prompts:
        click.echo("(no prompts registered)")
        return
    for p in sorted(prompts, key=lambda x: x.name):
        click.echo(f"{p.name}\t{p.version}\t{p.owner}\t{p.application}\t{p.environment}")


@cli.command()
@click.argument("name")
@click.pass_context
def versions(ctx: click.Context, name: str) -> None:
    """List all immutable versions of a prompt."""
    reg = _registry(ctx.obj["registry_path"])
    try:
        history = reg.versions(name)
    except PromptNotFoundError as exc:
        click.echo(f"error: {exc}", err=True)
        raise SystemExit(1)
    for v in history:
        click.echo(
            f"{v.version}\t{v.status.value}\t{v.created_by}\t{v.created_at.isoformat()}\t{v.hash[:12]}"
        )


@cli.command()
@click.option(
    "--format", "fmt", type=click.Choice(["csv", "json"]), default="csv", show_default=True
)
@click.option("--output", "-o", default=None, help="Output file (defaults to stdout).")
@click.pass_context
def export(ctx: click.Context, fmt: str, output: str | None) -> None:
    """Export the registry inventory (prompts + versions) as CSV or JSON."""
    reg = _registry(ctx.obj["registry_path"])
    rows = []
    for p in reg.list():
        for v in reg.versions(p.name):
            rows.append(
                {
                    "name": p.name,
                    "owner": p.owner,
                    "application": p.application,
                    "environment": p.environment,
                    "version": v.version,
                    "status": v.status.value,
                    "hash": v.hash,
                    "created_at": v.created_at.isoformat(),
                }
            )
    if fmt == "json":
        text = json.dumps(rows, indent=2)
        _emit(text, output)
    else:
        import io

        buf = io.StringIO()
        fields = [
            "name",
            "owner",
            "application",
            "environment",
            "version",
            "status",
            "hash",
            "created_at",
        ]
        writer = csv.DictWriter(buf, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
        _emit(buf.getvalue().rstrip("\n"), output)


@cli.command()
@click.argument("name")
@click.argument("version_a")
@click.argument("version_b")
@click.pass_context
def diff(ctx: click.Context, name: str, version_a: str, version_b: str) -> None:
    """Compare two versions of a prompt by hash (never reveals prompt text)."""
    reg = _registry(ctx.obj["registry_path"])
    try:
        history = reg.versions(name)
        va = resolve_version(history, version_a)
        vb = resolve_version(history, version_b)
    except (PromptNotFoundError, LookupError) as exc:
        click.echo(f"error: {exc}", err=True)
        raise SystemExit(1)
    if va.hash == vb.hash:
        click.echo(f"{name}: {version_a} and {version_b} are identical (template_hash matches)")
    else:
        click.echo(f"{name}: {version_a} and {version_b} differ")
        click.echo(f"  {version_a}: {va.hash[:16]}")
        click.echo(f"  {version_b}: {vb.hash[:16]}")


def _emit(text: str, output: str | None) -> None:
    if output:
        Path(output).write_text(text + "\n", encoding="utf-8")
        click.echo(f"wrote {output}")
    else:
        click.echo(text)


def main(argv: list[str] | None = None) -> int:
    """Console-script entry point."""
    try:
        cli.main(args=argv if argv is not None else sys.argv[1:], standalone_mode=False)
        return 0
    except SystemExit as exc:  # propagate explicit exit codes
        return int(exc.code or 0)
    except click.ClickException as exc:
        exc.show()
        return exc.exit_code


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
