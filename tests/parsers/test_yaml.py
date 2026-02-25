"""Tests for conda_tasks.parsers.yaml."""

from __future__ import annotations

import pytest

from conda_tasks.exceptions import TaskNotFoundError, TaskParseError
from conda_tasks.models import Task, TaskArg, TaskDependency, TaskOverride
from conda_tasks.parsers.yaml import (
    CondaTasksYAMLParser,
    task_to_yaml_dict,
    tasks_to_yaml,
)


def test_can_handle(sample_yaml):
    parser = CondaTasksYAMLParser()
    assert parser.can_handle(sample_yaml)
    assert not parser.can_handle(sample_yaml.parent / "other.yml")


@pytest.mark.parametrize(
    "task_name",
    ["build", "configure", "test", "lint", "check", "_setup", "platform-task"],
)
def test_parse_contains_task(sample_yaml, task_name):
    tasks = CondaTasksYAMLParser().parse(sample_yaml)
    assert task_name in tasks


@pytest.mark.parametrize(
    ("task_name", "attr", "expected"),
    [
        ("lint", "cmd", "ruff check ."),
        ("build", "inputs", ["src/**/*.py"]),
        ("build", "outputs", ["dist/"]),
        ("test", "clean_env", True),
        ("test", "env", {"PYTHONPATH": "src"}),
    ],
)
def test_parse_task_attr(sample_yaml, task_name, attr, expected):
    tasks = CondaTasksYAMLParser().parse(sample_yaml)
    assert getattr(tasks[task_name], attr) == expected


def test_parse_depends_on(sample_yaml):
    tasks = CondaTasksYAMLParser().parse(sample_yaml)
    assert len(tasks["build"].depends_on) == 1
    assert tasks["build"].depends_on[0].task == "configure"


def test_parse_alias(sample_yaml):
    tasks = CondaTasksYAMLParser().parse(sample_yaml)
    assert tasks["check"].is_alias
    assert tasks["check"].cmd is None


def test_parse_args(sample_yaml):
    tasks = CondaTasksYAMLParser().parse(sample_yaml)
    test = tasks["test"]
    assert len(test.args) == 1
    assert test.args[0].name == "test_path"
    assert test.args[0].default == "tests/"


def test_parse_hidden(sample_yaml):
    tasks = CondaTasksYAMLParser().parse(sample_yaml)
    assert tasks["_setup"].is_hidden


def test_parse_platform_override(sample_yaml):
    tasks = CondaTasksYAMLParser().parse(sample_yaml)
    pt = tasks["platform-task"]
    assert pt.platforms is not None
    assert "win-64" in pt.platforms
    assert pt.platforms["win-64"].cmd == "rd /s /q build"


def test_add_task(tmp_project):
    path = tmp_project / "conda-tasks.yml"
    parser = CondaTasksYAMLParser()
    task = Task(name="new", cmd="echo new")
    parser.add_task(path, "new", task)

    tasks = parser.parse(path)
    assert "new" in tasks
    assert tasks["new"].cmd == "echo new"


def test_remove_task(sample_yaml):
    parser = CondaTasksYAMLParser()
    parser.remove_task(sample_yaml, "lint")
    tasks = parser.parse(sample_yaml)
    assert "lint" not in tasks


def test_remove_nonexistent(sample_yaml):
    with pytest.raises(TaskNotFoundError):
        CondaTasksYAMLParser().remove_task(sample_yaml, "nonexistent")


def test_parse_invalid(tmp_project):
    path = tmp_project / "conda-tasks.yml"
    path.write_text(": :\n  - invalid: [yaml")
    with pytest.raises(TaskParseError):
        CondaTasksYAMLParser().parse(path)


def test_to_yaml_dict_simple_cmd():
    task = Task(name="build", cmd="make")
    assert task_to_yaml_dict(task) == "make"


def test_to_yaml_dict_with_fields():
    task = Task(
        name="test",
        cmd="pytest",
        depends_on=[TaskDependency(task="build")],
        description="Run tests",
        env={"PYTHONPATH": "src"},
        clean_env=True,
        inputs=["src/**/*.py"],
        outputs=["results/"],
    )
    result = task_to_yaml_dict(task)
    assert isinstance(result, dict)
    assert result["cmd"] == "pytest"
    assert result["depends-on"] == ["build"]
    assert result["description"] == "Run tests"
    assert result["env"] == {"PYTHONPATH": "src"}
    assert result["clean-env"] is True
    assert result["inputs"] == ["src/**/*.py"]
    assert result["outputs"] == ["results/"]


def test_to_yaml_dict_with_args():
    task = Task(
        name="test",
        cmd="pytest {{ path }}",
        args=[TaskArg(name="path", default="tests/")],
    )
    result = task_to_yaml_dict(task)
    assert isinstance(result, dict)
    assert result["args"] == [{"arg": "path", "default": "tests/"}]


def test_to_yaml_dict_with_platforms():
    task = Task(
        name="clean",
        cmd="rm -rf build/",
        platforms={
            "win-64": TaskOverride(cmd="rd /s /q build"),
            "osx-arm64": TaskOverride(env={"MACOSX_DEPLOYMENT_TARGET": "11.0"}),
        },
    )
    result = task_to_yaml_dict(task)
    assert isinstance(result, dict)
    assert result["target"] == {
        "win-64": {"cmd": "rd /s /q build"},
        "osx-arm64": {"env": {"MACOSX_DEPLOYMENT_TARGET": "11.0"}},
    }


def test_tasks_to_yaml_roundtrip(tmp_path):
    """Serializing then parsing should preserve tasks."""
    tasks = {
        "build": Task(name="build", cmd="make"),
        "test": Task(
            name="test",
            cmd="pytest",
            depends_on=[TaskDependency(task="build")],
        ),
    }
    yaml_text = tasks_to_yaml(tasks)
    out = tmp_path / "conda-tasks.yml"
    out.write_text(yaml_text)
    parsed = CondaTasksYAMLParser().parse(out)
    assert set(parsed.keys()) == {"build", "test"}
    assert parsed["build"].cmd == "make"
    assert parsed["test"].depends_on[0].task == "build"
