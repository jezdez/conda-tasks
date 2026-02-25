"""Tests for ``conda task list``."""

from __future__ import annotations

import argparse

from conda_tasks.cli.list import execute_list


def test_list_tasks(sample_yaml, capsys):
    args = argparse.Namespace(
        file=sample_yaml,
        json=False,
        quiet=False,
        verbose=0,
        dry_run=False,
    )
    result = execute_list(args)
    assert result == 0
    output = capsys.readouterr().out
    assert "build" in output
    assert "configure" in output
    assert "test" in output
    assert "_setup" not in output


def test_list_no_tasks(tmp_path, capsys):
    path = tmp_path / "conda-tasks.yml"
    path.write_text("tasks: {}")

    args = argparse.Namespace(
        file=path,
        json=False,
        quiet=False,
        verbose=0,
        dry_run=False,
    )
    result = execute_list(args)
    assert result == 0
    assert "No tasks" in capsys.readouterr().out


def test_list_json(sample_yaml, monkeypatch):
    """JSON output includes task metadata."""
    captured = {}

    def fake_stdout_json(data):
        captured.update(data)

    import conda.common.io

    monkeypatch.setattr(conda.common.io, "stdout_json", fake_stdout_json, raising=False)

    args = argparse.Namespace(
        file=sample_yaml,
        json=True,
        quiet=False,
        verbose=0,
        dry_run=False,
    )
    result = execute_list(args)
    assert result == 0
    assert "tasks" in captured
    assert "build" in captured["tasks"]
    assert "file" in captured
    # Hidden tasks should be excluded
    assert "_setup" not in captured["tasks"]


def test_list_shows_dependencies(sample_yaml, capsys):
    args = argparse.Namespace(
        file=sample_yaml,
        json=False,
        quiet=False,
        verbose=0,
        dry_run=False,
    )
    execute_list(args)
    output = capsys.readouterr().out
    assert "[depends:" in output


def test_list_cmd_as_list(tmp_path, capsys):
    """List-form commands are joined in the listing."""
    path = tmp_path / "conda-tasks.yml"
    path.write_text(
        "tasks:\n  build:\n    cmd:\n      - cmake\n      - --build\n      - .\n"
    )

    args = argparse.Namespace(
        file=path, json=False, quiet=False, verbose=0, dry_run=False
    )
    execute_list(args)
    output = capsys.readouterr().out
    assert "cmake --build ." in output


def test_list_json_alias(tmp_path, monkeypatch):
    """JSON output marks alias tasks."""
    path = tmp_path / "conda-tasks.yml"
    path.write_text(
        "tasks:\n"
        "  lint:\n    cmd: 'ruff check .'\n"
        "  test:\n    cmd: 'pytest'\n"
        "  check:\n    depends-on: [lint, test]\n"
        "    description: 'Run all'\n"
    )
    captured = {}

    def fake_stdout_json(data):
        captured.update(data)

    import conda.common.io

    monkeypatch.setattr(conda.common.io, "stdout_json", fake_stdout_json, raising=False)

    args = argparse.Namespace(
        file=path, json=True, quiet=False, verbose=0, dry_run=False
    )
    execute_list(args)

    assert captured["tasks"]["check"].get("alias") is True
    assert "depends_on" in captured["tasks"]["check"]
