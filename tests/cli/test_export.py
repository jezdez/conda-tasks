"""Tests for ``conda task export``."""

from __future__ import annotations

import argparse
import importlib

import pytest

from conda_tasks.cli.export import execute_export
from conda_tasks.parsers.toml import CondaTasksTomlParser
from conda_tasks.parsers.yaml import CondaTasksYAMLParser


@pytest.mark.parametrize(
    ("export_format", "expected_marker"),
    [
        ("yaml", "tasks:"),
        ("toml", "[tasks]"),
    ],
    ids=["yaml-stdout", "toml-stdout"],
)
def test_export_to_stdout(sample_yaml, capsys, export_format, expected_marker):
    args = argparse.Namespace(
        file=sample_yaml,
        output=None,
        export_format=export_format,
        quiet=False,
        verbose=0,
        json=False,
        dry_run=False,
    )
    result = execute_export(args)
    assert result == 0
    output = capsys.readouterr().out
    assert expected_marker in output
    assert "build" in output
    assert "configure" in output


@pytest.mark.parametrize(
    ("export_format", "out_filename", "parser_module", "parser_class"),
    [
        (
            "yaml",
            "exported.yml",
            "conda_tasks.parsers.yaml",
            "CondaTasksYAMLParser",
        ),
        (
            "toml",
            "exported.toml",
            "conda_tasks.parsers.toml",
            "CondaTasksTomlParser",
        ),
    ],
    ids=["yaml-file", "toml-file"],
)
def test_export_to_file(
    sample_yaml, tmp_path, export_format, out_filename, parser_module, parser_class
):
    out_path = tmp_path / out_filename
    args = argparse.Namespace(
        file=sample_yaml,
        output=out_path,
        export_format=export_format,
        quiet=False,
        verbose=0,
        json=False,
        dry_run=False,
    )
    result = execute_export(args)
    assert result == 0
    assert out_path.exists()

    mod = importlib.import_module(parser_module)
    cls = getattr(mod, parser_class)
    tasks = cls().parse(out_path)
    assert "build" in tasks
    assert "test" in tasks
    assert "lint" in tasks


@pytest.mark.parametrize(
    "export_format",
    ["yaml", "toml"],
    ids=["yaml", "toml"],
)
def test_export_from_pixi_toml(tmp_path, export_format):
    """Export from pixi.toml produces valid conda-tasks.{yml,toml}."""
    pixi = tmp_path / "pixi.toml"
    pixi.write_text(
        '[tasks]\nbuild = "make build"\n'
        'test = { cmd = "pytest", depends-on = ["build"] }\n'
        "\n[target.win-64.tasks]\n"
        'build = "nmake build"\n'
    )

    suffix = ".yml" if export_format == "yaml" else ".toml"
    out_path = tmp_path / f"conda-tasks{suffix}"
    args = argparse.Namespace(
        file=pixi,
        output=out_path,
        export_format=export_format,
        quiet=False,
        verbose=0,
        json=False,
        dry_run=False,
    )
    result = execute_export(args)
    assert result == 0

    if export_format == "yaml":
        tasks = CondaTasksYAMLParser().parse(out_path)
    else:
        tasks = CondaTasksTomlParser().parse(out_path)

    assert "build" in tasks
    assert "test" in tasks
    assert tasks["test"].depends_on[0].task == "build"
    assert tasks["build"].platforms is not None
    assert "win-64" in tasks["build"].platforms
