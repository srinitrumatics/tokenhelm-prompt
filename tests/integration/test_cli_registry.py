"""US1: CLI init/list/versions/diff/export (T013)."""

from __future__ import annotations

from click.testing import CliRunner

from tokenhelm_prompt.cli.main import cli
from tokenhelm_prompt.registry import YamlRegistry


def _seed(path):
    reg = YamlRegistry(path)
    reg.register(
        "invoice",
        owner="ana",
        application="billing",
        environment="prod",
        template="Summarize {invoice}",
    )
    reg.add_version("invoice", template="Summarize {invoice} now", created_by="ana")
    return reg


def test_init_creates_registry(tmp_path):
    path = tmp_path / "p.yaml"
    runner = CliRunner()
    result = runner.invoke(cli, ["-r", str(path), "init"])
    assert result.exit_code == 0
    assert path.exists()


def test_init_refuses_overwrite(tmp_path):
    path = tmp_path / "p.yaml"
    runner = CliRunner()
    runner.invoke(cli, ["-r", str(path), "init"])
    result = runner.invoke(cli, ["-r", str(path), "init"])
    assert result.exit_code == 1
    assert "already exists" in result.output


def test_list_and_versions(tmp_path):
    path = tmp_path / "p.yaml"
    _seed(path)
    runner = CliRunner()
    listing = runner.invoke(cli, ["-r", str(path), "list"])
    assert "invoice" in listing.output and "v2" in listing.output

    versions = runner.invoke(cli, ["-r", str(path), "versions", "invoice"])
    assert "v1" in versions.output and "v2" in versions.output
    assert "deprecated" in versions.output and "active" in versions.output


def test_versions_unknown_prompt_errors(tmp_path):
    path = tmp_path / "p.yaml"
    _seed(path)
    runner = CliRunner()
    result = runner.invoke(cli, ["-r", str(path), "versions", "nope"])
    assert result.exit_code == 1


def test_diff_reports_difference_without_text(tmp_path):
    path = tmp_path / "p.yaml"
    _seed(path)
    runner = CliRunner()
    result = runner.invoke(cli, ["-r", str(path), "diff", "invoice", "v1", "v2"])
    assert result.exit_code == 0
    assert "differ" in result.output
    # never leaks template text
    assert "Summarize" not in result.output


def test_export_json_inventory(tmp_path):
    path = tmp_path / "p.yaml"
    _seed(path)
    out = tmp_path / "inv.json"
    runner = CliRunner()
    result = runner.invoke(cli, ["-r", str(path), "export", "--format", "json", "-o", str(out)])
    assert result.exit_code == 0
    assert out.exists()
    assert "invoice" in out.read_text()
