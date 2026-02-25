"""Tests for ``conda task remove``."""

from __future__ import annotations

import argparse

import pytest

from conda_tasks.cli.remove import execute_remove
from conda_tasks.exceptions import TaskNotFoundError
from conda_tasks.parsers.yaml import CondaTasksYAMLParser


def test_remove_task(sample_yaml):
    args = argparse.Namespace(
        file=sample_yaml,
        task_name="lint",
        dry_run=False,
        quiet=False,
        verbose=0,
        json=False,
    )
    result = execute_remove(args)
    assert result == 0

    tasks = CondaTasksYAMLParser().parse(sample_yaml)
    assert "lint" not in tasks


def test_remove_nonexistent(sample_yaml):
    args = argparse.Namespace(
        file=sample_yaml,
        task_name="nonexistent",
        dry_run=False,
        quiet=False,
        verbose=0,
        json=False,
    )
    with pytest.raises(TaskNotFoundError):
        execute_remove(args)


def test_remove_dry_run(sample_yaml, capsys):
    args = argparse.Namespace(
        file=sample_yaml,
        task_name="lint",
        dry_run=True,
        quiet=False,
        verbose=0,
        json=False,
    )
    result = execute_remove(args)
    assert result == 0
    assert "[dry-run]" in capsys.readouterr().out

    tasks = CondaTasksYAMLParser().parse(sample_yaml)
    assert "lint" in tasks
