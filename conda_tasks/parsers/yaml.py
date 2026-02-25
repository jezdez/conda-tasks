"""Parser for the canonical conda-tasks.yml format."""

from __future__ import annotations

from typing import TYPE_CHECKING

import yaml

from ..exceptions import TaskNotFoundError, TaskParseError
from .base import TaskFileParser
from .normalize import normalize_tasks

if TYPE_CHECKING:
    from pathlib import Path
    from typing import ClassVar

    from ..models import Task


def task_to_yaml_dict(task: Task) -> dict[str, object] | str:
    """Convert a Task to its YAML-serializable representation.

    Returns a plain string when the task is a simple command with no
    extra fields, or a dict otherwise.
    """
    defn: dict[str, object] = {}
    if task.cmd is not None:
        defn["cmd"] = task.cmd
    if task.depends_on:
        defn["depends-on"] = [d.task for d in task.depends_on]
    if task.description:
        defn["description"] = task.description
    if task.env:
        defn["env"] = dict(task.env)
    if task.cwd:
        defn["cwd"] = task.cwd
    if task.clean_env:
        defn["clean-env"] = True
    if task.args:
        defn["args"] = [
            {"arg": a.name, "default": a.default} if a.default else {"arg": a.name}
            for a in task.args
        ]
    if task.inputs:
        defn["inputs"] = list(task.inputs)
    if task.outputs:
        defn["outputs"] = list(task.outputs)
    if task.platforms:
        target: dict[str, dict[str, object]] = {}
        for platform, override in task.platforms.items():
            ov: dict[str, object] = {}
            if override.cmd is not None:
                ov["cmd"] = override.cmd
            if override.env is not None:
                ov["env"] = dict(override.env)
            if override.cwd is not None:
                ov["cwd"] = override.cwd
            if override.clean_env is not None:
                ov["clean-env"] = override.clean_env
            if override.inputs is not None:
                ov["inputs"] = list(override.inputs)
            if override.outputs is not None:
                ov["outputs"] = list(override.outputs)
            target[platform] = ov
        defn["target"] = target

    if len(defn) == 1 and "cmd" in defn:
        return defn["cmd"]  # type: ignore[return-value]
    return defn


def tasks_to_yaml(tasks: dict[str, Task]) -> str:
    """Serialize a full task dict to a ``conda-tasks.yml`` YAML string."""
    data: dict[str, object] = {
        "tasks": {name: task_to_yaml_dict(task) for name, task in tasks.items()}
    }
    return yaml.dump(data, default_flow_style=False, sort_keys=False)


class CondaTasksYAMLParser(TaskFileParser):
    """Reads ``conda-tasks.yml`` files (top-level ``tasks:`` key, YAML)."""

    extensions: ClassVar[tuple[str, ...]] = (".yml", ".yaml")
    filenames: ClassVar[tuple[str, ...]] = ("conda-tasks.yml", "conda-tasks.yaml")

    def can_handle(self, path: Path) -> bool:
        """Return True if *path* is a recognized ``conda-tasks.yml`` filename."""
        return path.name in self.filenames

    def parse(self, path: Path) -> dict[str, Task]:
        """Parse a ``conda-tasks.yml`` file and return its task definitions."""
        try:
            data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        except yaml.YAMLError as exc:
            raise TaskParseError(str(path), str(exc)) from exc

        raw_tasks = data.get("tasks", {})
        if not isinstance(raw_tasks, dict):
            raise TaskParseError(str(path), "'tasks' must be a mapping")
        return normalize_tasks(raw_tasks)

    def add_task(self, path: Path, name: str, task: Task) -> None:
        """Add or update a task in the YAML file, creating it if needed."""
        if path.exists():
            data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        else:
            data = {}

        tasks_section = data.setdefault("tasks", {})
        tasks_section[name] = task_to_yaml_dict(task)
        path.write_text(
            yaml.dump(data, default_flow_style=False, sort_keys=False), encoding="utf-8"
        )

    def remove_task(self, path: Path, name: str) -> None:
        """Remove a task from the YAML file by name."""
        data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        tasks_section = data.get("tasks", {})
        if name not in tasks_section:
            raise TaskNotFoundError(name, list(tasks_section.keys()))
        del tasks_section[name]
        path.write_text(
            yaml.dump(data, default_flow_style=False, sort_keys=False), encoding="utf-8"
        )
