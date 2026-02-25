"""Custom exceptions for conda-tasks."""

from __future__ import annotations

from conda.exceptions import CondaError


class CondaTasksError(CondaError):
    """Base exception for all conda-tasks errors."""


class TaskNotFoundError(CondaTasksError):
    """Raised when a referenced task does not exist."""

    def __init__(self, task_name: str, available: list[str] | None = None):
        msg = f"Task '{task_name}' not found."
        if available:
            msg += f" Available tasks: {', '.join(sorted(available))}"
        super().__init__(msg)


class CyclicDependencyError(CondaTasksError):
    """Raised when the task dependency graph contains a cycle."""

    def __init__(self, cycle: list[str]):
        path = " -> ".join(cycle)
        super().__init__(f"Cyclic dependency detected: {path}")


class TaskParseError(CondaTasksError):
    """Raised when a task definition file cannot be parsed."""

    def __init__(self, path: str, reason: str):
        super().__init__(f"Failed to parse '{path}': {reason}")


class TaskExecutionError(CondaTasksError):
    """Raised when a task command exits with a non-zero status."""

    def __init__(self, task_name: str, exit_code: int):
        super().__init__(f"Task '{task_name}' failed with exit code {exit_code}")


class NoTaskFileError(CondaTasksError):
    """Raised when no task definition file is found."""

    def __init__(self, search_dir: str):
        super().__init__(
            f"No task file found in '{search_dir}'. "
            "Create a conda-tasks.yml, pixi.toml, or pyproject.toml "
            "with task definitions."
        )
