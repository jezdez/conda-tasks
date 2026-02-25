"""Parser for pyproject.toml task definitions.

Reads from:
- ``[tool.conda-tasks.tasks]`` (preferred)
- ``[tool.pixi.tasks]`` (fallback for pixi compatibility)

Platform overrides:
- ``[tool.conda-tasks.target.<platform>.tasks]``
- ``[tool.pixi.target.<platform>.tasks]``
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import tomlkit

from ..exceptions import TaskParseError
from .base import TaskFileParser
from .normalize import normalize_override, normalize_task

if TYPE_CHECKING:
    from pathlib import Path
    from typing import ClassVar

    from ..models import Task


class PyprojectTomlParser(TaskFileParser):
    """Reads task definitions from ``pyproject.toml``."""

    extensions: ClassVar[tuple[str, ...]] = (".toml",)
    filenames: ClassVar[tuple[str, ...]] = ("pyproject.toml",)

    def can_handle(self, path: Path) -> bool:
        """Return True if *path* is a ``pyproject.toml`` with task definitions."""
        if path.name not in self.filenames:
            return False
        try:
            data = tomlkit.loads(path.read_text(encoding="utf-8")).unwrap()
        except Exception:
            return False
        tool = data.get("tool", {})
        return bool(
            tool.get("conda-tasks", {}).get("tasks")
            or tool.get("pixi", {}).get("tasks")
        )

    def parse(self, path: Path) -> dict[str, Task]:
        """Parse task definitions from ``[tool.conda-tasks]`` or ``[tool.pixi]``."""
        try:
            data = tomlkit.loads(path.read_text(encoding="utf-8")).unwrap()
        except Exception as exc:
            raise TaskParseError(str(path), str(exc)) from exc

        tool = data.get("tool", {})
        conda_tasks_section = tool.get("conda-tasks", {})
        pixi_section = tool.get("pixi", {})

        raw_tasks = conda_tasks_section.get("tasks") or pixi_section.get("tasks") or {}
        target_section = (
            conda_tasks_section.get("target") or pixi_section.get("target") or {}
        )

        if not isinstance(raw_tasks, dict):
            raise TaskParseError(str(path), "tasks must be a table")

        tasks: dict[str, Task] = {}
        for name, defn in raw_tasks.items():
            tasks[name] = normalize_task(name, defn)

        if isinstance(target_section, dict):
            for platform, platform_data in target_section.items():
                if not isinstance(platform_data, dict):
                    continue
                platform_tasks = platform_data.get("tasks", {})
                for name, defn in platform_tasks.items():
                    override = normalize_override(
                        defn if isinstance(defn, dict) else {"cmd": defn}
                    )
                    if name in tasks:
                        existing = tasks[name]
                        if existing.platforms is None:
                            existing.platforms = {}
                        existing.platforms[platform] = override
                    else:
                        task = normalize_task(name, defn)
                        task.platforms = {platform: override}
                        tasks[name] = task

        return tasks

    def add_task(self, path: Path, name: str, task: Task) -> None:
        """Not supported — ``pyproject.toml`` is read-only."""
        raise NotImplementedError(
            "Writing to pyproject.toml is not supported. Use conda-tasks.yml instead."
        )

    def remove_task(self, path: Path, name: str) -> None:
        """Not supported — ``pyproject.toml`` is read-only."""
        raise NotImplementedError(
            "Writing to pyproject.toml is not supported. Use conda-tasks.yml instead."
        )
