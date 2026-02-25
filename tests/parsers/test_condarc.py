"""Tests for conda_tasks.parsers.condarc."""

from __future__ import annotations

import pytest
import yaml

import conda_tasks.parsers.condarc as condarc_mod
from conda_tasks.exceptions import TaskNotFoundError, TaskParseError
from conda_tasks.models import Task, TaskDependency
from conda_tasks.parsers.condarc import CondaRCParser


def test_can_handle(sample_condarc):
    assert CondaRCParser().can_handle(sample_condarc)


@pytest.mark.parametrize(
    ("content", "expected"),
    [
        ("channels:\n  - conda-forge\n", False),
        (": :\n  - invalid [yaml", False),
        ("plugins: not-a-dict\n", False),
        (
            "plugins:\n  conda-tasks:\n    tasks:\n      hi:\n        cmd: echo hi\n",
            True,
        ),
    ],
    ids=["no-tasks", "invalid-yaml", "non-dict-plugins", "dash-alias"],
)
def test_can_handle_variants(tmp_project, content, expected):
    path = tmp_project / ".condarc"
    path.write_text(content)
    assert CondaRCParser().can_handle(path) is expected


@pytest.mark.parametrize("task_name", ["greet", "farewell"])
def test_parse_contains_task(sample_condarc, task_name):
    tasks = CondaRCParser().parse(sample_condarc)
    assert task_name in tasks


@pytest.mark.parametrize(
    ("task_name", "attr", "expected"),
    [
        ("greet", "cmd", "echo hello"),
    ],
)
def test_parse_task_attr(sample_condarc, task_name, attr, expected):
    tasks = CondaRCParser().parse(sample_condarc)
    assert getattr(tasks[task_name], attr) == expected


def test_parse_depends(sample_condarc):
    tasks = CondaRCParser().parse(sample_condarc)
    assert tasks["farewell"].depends_on[0].task == "greet"


def test_add_and_remove(tmp_project):
    path = tmp_project / ".condarc"
    parser = CondaRCParser()

    task = Task(name="hello", cmd="echo hi")
    parser.add_task(path, "hello", task)

    tasks = parser.parse(path)
    assert "hello" in tasks

    parser.remove_task(path, "hello")
    assert not parser.can_handle(path)


def test_add_task_with_depends_and_description(tmp_project):
    path = tmp_project / ".condarc"
    content = (
        "plugins:\n  conda_tasks:\n    tasks:\n      existing:\n        cmd: echo hi\n"
    )
    path.write_text(content)

    task = Task(
        name="newtask",
        cmd="echo new",
        depends_on=[TaskDependency(task="existing")],
        description="A new task",
    )
    parser = CondaRCParser()
    parser.add_task(path, "newtask", task)

    data = yaml.safe_load(path.read_text())
    section = data["plugins"]["conda_tasks"]["tasks"]
    assert "newtask" in section
    assert section["newtask"]["depends-on"] == ["existing"]
    assert section["newtask"]["description"] == "A new task"


def test_add_task_creates_file(tmp_project):
    path = tmp_project / ".condarc"
    # File doesn't exist yet
    parser = CondaRCParser()
    parser.add_task(path, "hello", Task(name="hello", cmd="echo hello"))
    assert path.exists()
    data = yaml.safe_load(path.read_text())
    assert data["plugins"]["conda_tasks"]["tasks"]["hello"]["cmd"] == "echo hello"


def test_remove_task_from_condarc(tmp_project):
    content = (
        "plugins:\n  conda_tasks:\n    tasks:\n      greet:\n        cmd: echo hi\n"
        "      farewell:\n        cmd: echo bye\n"
    )
    path = tmp_project / ".condarc"
    path.write_text(content)

    parser = CondaRCParser()
    parser.remove_task(path, "greet")

    data = yaml.safe_load(path.read_text())
    assert "greet" not in data["plugins"]["conda_tasks"]["tasks"]
    assert "farewell" in data["plugins"]["conda_tasks"]["tasks"]


def test_remove_nonexistent_from_condarc(tmp_project):
    content = (
        "plugins:\n  conda_tasks:\n    tasks:\n      greet:\n        cmd: echo hi\n"
    )
    path = tmp_project / ".condarc"
    path.write_text(content)

    with pytest.raises(TaskNotFoundError):
        CondaRCParser().remove_task(path, "nonexistent")


@pytest.mark.parametrize(
    "key",
    ["conda_tasks", "conda-tasks"],
    ids=["underscore", "dash"],
)
def test_parse_falls_back_to_file(tmp_project, monkeypatch, key):
    """When _raw_tasks_from_condarc returns empty, parse reads the file directly."""
    content = f"plugins:\n  {key}:\n    tasks:\n      hello:\n        cmd: echo hi\n"
    path = tmp_project / ".condarc"
    path.write_text(content)

    monkeypatch.setattr(condarc_mod, "_raw_tasks_from_condarc", lambda: {})
    tasks = CondaRCParser().parse(path)

    assert "hello" in tasks
    assert tasks["hello"].cmd == "echo hi"


@pytest.mark.parametrize(
    ("content", "match"),
    [
        (": :\n  - broken [yaml", "condarc"),
        ("plugins:\n  conda_tasks:\n    tasks: not-a-mapping\n", "must be a mapping"),
    ],
    ids=["invalid-yaml", "non-dict-tasks"],
)
def test_parse_error(tmp_project, monkeypatch, content, match):
    """Malformed condarc content raises TaskParseError."""
    path = tmp_project / ".condarc"
    path.write_text(content)

    monkeypatch.setattr(condarc_mod, "_raw_tasks_from_condarc", lambda: {})
    with pytest.raises(TaskParseError, match=match):
        CondaRCParser().parse(path)


def test_add_task_simple_cmd_only(tmp_project):
    """add_task with cmd only (no depends/description) stores correctly."""
    path = tmp_project / ".condarc"
    task = Task(name="simple", cmd="echo hi")
    parser = CondaRCParser()
    parser.add_task(path, "simple", task)

    data = yaml.safe_load(path.read_text())
    section = data["plugins"]["conda_tasks"]["tasks"]
    assert section["simple"]["cmd"] == "echo hi"
