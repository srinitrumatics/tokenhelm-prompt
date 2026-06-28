"""Additional CLI paths: empty list, stdout export, diff edge cases, main()."""

from __future__ import annotations

from click.testing import CliRunner

from tokenhelm_prompt.cli.main import cli, main
from tokenhelm_prompt.registry import YamlRegistry


def test_list_empty_registry(tmp_path):
    path = tmp_path / "p.yaml"
    YamlRegistry(path)._save()
    result = CliRunner().invoke(cli, ["-r", str(path), "list"])
    assert "no prompts" in result.output


def test_export_csv_to_stdout(tmp_path):
    path = tmp_path / "p.yaml"
    reg = YamlRegistry(path)
    reg.register("p", owner="o", application="a", environment="prod", template="t {x}")
    result = CliRunner().invoke(cli, ["-r", str(path), "export"])
    assert result.exit_code == 0
    assert "name,owner" in result.output  # csv header to stdout


def test_diff_identical_versions(tmp_path):
    path = tmp_path / "p.yaml"
    reg = YamlRegistry(path)
    reg.register("p", owner="o", application="a", environment="prod", template="same")
    reg.add_version("p", template="same", created_by="o")  # identical hash
    result = CliRunner().invoke(cli, ["-r", str(path), "diff", "p", "v1", "v2"])
    assert "identical" in result.output


def test_diff_unknown_version_errors(tmp_path):
    path = tmp_path / "p.yaml"
    reg = YamlRegistry(path)
    reg.register("p", owner="o", application="a", environment="prod", template="t")
    result = CliRunner().invoke(cli, ["-r", str(path), "diff", "p", "v1", "v9"])
    assert result.exit_code == 1


def test_main_entrypoint_returns_zero(tmp_path):
    path = tmp_path / "p.yaml"
    assert main(["-r", str(path), "init"]) == 0


def test_main_entrypoint_usage_error_nonzero():
    # Missing required argument → click UsageError → non-zero exit code.
    assert main(["versions"]) != 0
