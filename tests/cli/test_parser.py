"""Tests for CLI parser configuration."""

from __future__ import annotations

import argparse
from pathlib import Path

import pytest

from conda_tasks.cli import execute, generate_parser


def test_returns_parser():
    assert isinstance(generate_parser(), argparse.ArgumentParser)


@pytest.mark.parametrize(
    ("argv", "expected_subcmd"),
    [
        (["list"], "list"),
        (["run", "build"], "run"),
        (["add", "mytask", "echo hello"], "add"),
        (["remove", "mytask"], "remove"),
        (["export"], "export"),
    ],
)
def test_subcommand_routing(argv, expected_subcmd):
    args = generate_parser().parse_args(argv)
    assert args.subcmd == expected_subcmd


@pytest.mark.parametrize(
    ("argv", "attr", "expected"),
    [
        (["run", "build"], "task_name", "build"),
        (["run", "test", "src/tests/"], "task_args", ["src/tests/"]),
        (["run", "build", "--skip-deps"], "skip_deps", True),
        (["run", "build", "--clean-env"], "clean_env", True),
        (
            ["add", "mytask", "echo hello", "--depends-on", "build"],
            "depends_on",
            ["build"],
        ),
        (["remove", "mytask"], "task_name", "mytask"),
        (["--file", "custom.yml", "list"], "file", Path("custom.yml")),
        (["export", "-o", "out.yml"], "output", Path("out.yml")),
    ],
)
def test_parser_args(argv, attr, expected):
    args = generate_parser().parse_args(argv)
    assert getattr(args, attr) == expected


def test_execute_no_subcmd_prints_help(capsys):
    """When subcmd is None and no task_name, print help and return 0."""
    args = argparse.Namespace(subcmd=None)
    result = execute(args)
    assert result == 0
    output = capsys.readouterr().out
    assert "conda task" in output or "usage" in output.lower()


def test_execute_unknown_subcmd_prints_help(capsys):
    """When subcmd is unknown, print help and return 0."""
    args = argparse.Namespace(subcmd="unknown", file=None)
    result = execute(args)
    assert result == 0
    output = capsys.readouterr().out
    assert "conda task" in output or "usage" in output.lower()


def test_execute_dispatches_list(sample_yaml, capsys):
    """execute() with subcmd=list dispatches to execute_list."""
    args = argparse.Namespace(
        subcmd="list",
        file=sample_yaml,
        json=False,
        quiet=False,
        verbose=0,
        dry_run=False,
    )
    result = execute(args)
    assert result == 0
    output = capsys.readouterr().out
    assert "build" in output
    assert "configure" in output


def test_execute_dispatches_export(sample_yaml, capsys):
    """execute() with subcmd=export dispatches to execute_export."""
    args = argparse.Namespace(
        subcmd="export",
        file=sample_yaml,
        output=None,
        export_format="yaml",
        quiet=False,
        verbose=0,
        json=False,
        dry_run=False,
    )
    result = execute(args)
    assert result == 0
    output = capsys.readouterr().out
    assert "tasks:" in output


def test_execute_dispatches_add(tmp_path, capsys):
    """execute() with subcmd=add dispatches to execute_add."""
    path = tmp_path / "conda-tasks.yml"
    path.write_text("tasks: {}")
    args = argparse.Namespace(
        subcmd="add",
        file=path,
        task_name="newtask",
        cmd="echo hello",
        depends_on=[],
        description=None,
        dry_run=False,
        quiet=False,
        verbose=0,
        json=False,
    )
    result = execute(args)
    assert result == 0
    output = capsys.readouterr().out
    assert "newtask" in output


def test_execute_dispatches_remove(sample_yaml, capsys):
    """execute() with subcmd=remove dispatches to execute_remove."""
    args = argparse.Namespace(
        subcmd="remove",
        file=sample_yaml,
        task_name="lint",
        dry_run=False,
        quiet=False,
        verbose=0,
        json=False,
    )
    result = execute(args)
    assert result == 0
    output = capsys.readouterr().out
    assert "lint" in output


def test_execute_run_implicit_subcmd(tmp_path, capsys):
    """When subcmd=None but task_name is present, infer 'run'."""
    path = tmp_path / "conda-tasks.yml"
    path.write_text("tasks:\n  greet:\n    cmd: 'echo hello'\n")
    args = argparse.Namespace(
        subcmd=None,
        file=path,
        task_name="greet",
        task_args=[],
        skip_deps=False,
        dry_run=True,
        quiet=False,
        verbose=0,
        clean_env=False,
        cwd=None,
        prefix=None,
        name=None,
        json=False,
    )
    result = execute(args)
    assert result == 0
    output = capsys.readouterr().out
    assert "[dry-run]" in output
