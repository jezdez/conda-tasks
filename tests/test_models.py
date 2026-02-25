"""Tests for conda_tasks.models."""

from __future__ import annotations

import pytest

from conda_tasks.exceptions import TaskNotFoundError
from conda_tasks.models import Task, TaskArg, TaskDependency, TaskOverride


@pytest.mark.parametrize(
    ("default", "expected"),
    [
        (None, None),
        ("tests/", "tests/"),
    ],
    ids=["required", "optional"],
)
def test_task_arg(default, expected):
    arg = TaskArg(name="path", default=default) if default else TaskArg(name="path")
    assert arg.name == "path"
    assert arg.default == expected


def test_task_dependency_simple():
    dep = TaskDependency(task="build")
    assert dep.task == "build"
    assert dep.args == []
    assert dep.environment is None


def test_task_dependency_with_args_and_env():
    dep = TaskDependency(task="test", args=["src/"], environment="py311")
    assert dep.args == ["src/"]
    assert dep.environment == "py311"


@pytest.mark.parametrize(
    ("name", "expected_hidden"),
    [
        ("build", False),
        ("_internal", True),
        ("__double", True),
        ("visible", False),
    ],
)
def test_task_is_hidden(name, expected_hidden):
    task = Task(name=name, cmd="echo x")
    assert task.is_hidden is expected_hidden


def test_task_simple_command():
    task = Task(name="build", cmd="make")
    assert task.cmd == "make"
    assert not task.is_alias


def test_task_alias(alias_task):
    assert alias_task.is_alias
    assert alias_task.cmd is None


def test_task_list_command():
    task = Task(name="build", cmd=["python", "-m", "build"])
    assert task.cmd == ["python", "-m", "build"]


def test_task_env_vars():
    task = Task(name="test", cmd="pytest", env={"PYTHONPATH": "src"})
    assert task.env == {"PYTHONPATH": "src"}


@pytest.mark.parametrize(
    ("kwargs", "attr", "expected"),
    [
        ({"cmd": "nmake"}, "cmd", "nmake"),
        ({"env": {"CC": "gcc"}}, "env", {"CC": "gcc"}),
        ({"cwd": "/tmp"}, "cwd", "/tmp"),
        ({"clean_env": True}, "clean_env", True),
    ],
)
def test_task_override(kwargs, attr, expected):
    ov = TaskOverride(**kwargs)
    assert getattr(ov, attr) == expected


@pytest.mark.parametrize(
    "platform",
    ["linux-64", "linux-aarch64"],
    ids=["no-platforms", "no-match"],
)
def test_resolve_returns_self_when_no_override(platform, simple_task):
    resolved = simple_task.resolve_for_platform(platform)
    assert resolved is simple_task


@pytest.mark.parametrize(
    ("platform", "expected_cmd", "expected_env"),
    [
        ("win-64", "rd /s /q build", {}),
        ("osx-arm64", "rm -rf build/", {"MACOSX_DEPLOYMENT_TARGET": "11.0"}),
    ],
)
def test_resolve_platform_override(
    task_with_overrides, platform, expected_cmd, expected_env
):
    resolved = task_with_overrides.resolve_for_platform(platform)
    assert resolved is not task_with_overrides
    assert resolved.name == "clean"
    assert resolved.cmd == expected_cmd
    assert resolved.env == expected_env


@pytest.mark.parametrize(
    ("available", "expected_in", "expected_not_in"),
    [
        (["a", "b", "c"], "a, b, c", None),
        (None, None, "Available"),
    ],
    ids=["with-available", "no-available"],
)
def test_task_not_found_error(available, expected_in, expected_not_in):
    if available:
        err = TaskNotFoundError("missing", available)
    else:
        err = TaskNotFoundError("missing")
    assert "missing" in str(err)
    if expected_in:
        assert expected_in in str(err)
    if expected_not_in:
        assert expected_not_in not in str(err)
