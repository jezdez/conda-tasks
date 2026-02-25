"""Shared fixtures for conda-tasks tests."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from conda_tasks.models import Task, TaskDependency, TaskOverride

if TYPE_CHECKING:
    from pathlib import Path

pytest_plugins = (
    "conda.testing",
    "conda.testing.fixtures",
)


@pytest.fixture
def tmp_project(tmp_path: Path) -> Path:
    """A temporary directory acting as a project root."""
    return tmp_path


@pytest.fixture
def sample_yaml(tmp_project: Path) -> Path:
    """Create a sample conda-tasks.yml for testing."""
    content = """\
tasks:
  build:
    cmd: "make build"
    depends-on: [configure]
    description: "Build the project"
    inputs: ["src/**/*.py"]
    outputs: ["dist/"]
  configure:
    cmd: "cmake -G Ninja -S . -B .build"
    description: "Configure build system"
  test:
    cmd: "pytest {{ test_path }}"
    args:
      - arg: test_path
        default: "tests/"
    env:
      PYTHONPATH: "src"
    clean-env: true
  lint:
    cmd: "ruff check ."
  check:
    depends-on: [test, lint]
    description: "Run all checks"
  _setup:
    cmd: "mkdir -p build/"
  platform-task:
    cmd: "rm -rf build/"
    target:
      win-64:
        cmd: "rd /s /q build"
"""
    path = tmp_project / "conda-tasks.yml"
    path.write_text(content)
    return path


@pytest.fixture
def simple_task() -> Task:
    return Task(name="build", cmd="make build", description="Build it")


@pytest.fixture
def task_with_deps() -> dict[str, Task]:
    return {
        "configure": Task(name="configure", cmd="cmake ."),
        "build": Task(
            name="build",
            cmd="make",
            depends_on=[TaskDependency(task="configure")],
        ),
        "test": Task(
            name="test",
            cmd="pytest",
            depends_on=[TaskDependency(task="build")],
        ),
    }


@pytest.fixture
def task_with_overrides() -> Task:
    return Task(
        name="clean",
        cmd="rm -rf build/",
        platforms={
            "win-64": TaskOverride(cmd="rd /s /q build"),
            "osx-arm64": TaskOverride(env={"MACOSX_DEPLOYMENT_TARGET": "11.0"}),
        },
    )


@pytest.fixture
def alias_task() -> Task:
    return Task(
        name="check",
        depends_on=[
            TaskDependency(task="test"),
            TaskDependency(task="lint"),
        ],
    )
