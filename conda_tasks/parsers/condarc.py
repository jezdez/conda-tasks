"""Parser for .condarc task definitions.

Reads task definitions from the ``plugins.conda_tasks.tasks`` section
of ``.condarc`` using conda's configuration loading API. This means tasks
defined in any condarc source (user, system, environment) are automatically
discovered.

Writing (add/remove) still uses direct YAML manipulation since the config
API is read-only.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import yaml

from ..exceptions import TaskNotFoundError, TaskParseError
from .base import TaskFileParser
from .normalize import normalize_tasks

if TYPE_CHECKING:
    from pathlib import Path
    from typing import Any, ClassVar

    from ..models import Task

_CONDARC_KEY = "conda_tasks"


def _raw_tasks_from_condarc() -> dict[str, Any]:
    """Extract raw task definitions from all condarc sources via conda's config API.

    Returns a merged dict of ``{task_name: definition}`` from every condarc
    source that defines ``plugins.conda_tasks.tasks``.
    """
    from conda.base.context import context

    merged: dict[str, Any] = {}
    for _source, data in context.plugins.raw_data.items():
        raw_param = data.get(_CONDARC_KEY)
        if raw_param is None:
            continue
        try:
            raw_value = raw_param._raw_value
        except AttributeError:
            continue
        if not isinstance(raw_value, dict):
            continue
        tasks = raw_value.get("tasks")
        if isinstance(tasks, dict):
            merged.update(tasks)
    return merged


class CondaRCParser(TaskFileParser):
    """Reads task definitions from ``.condarc`` via conda's config API."""

    extensions: ClassVar[tuple[str, ...]] = ()
    filenames: ClassVar[tuple[str, ...]] = (".condarc",)

    def can_handle(self, path: Path) -> bool:
        """Return True if *path* is a ``.condarc`` with task definitions."""
        if path.name not in self.filenames:
            return False
        try:
            data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        except yaml.YAMLError:
            return False
        plugins = data.get("plugins", {})
        if not isinstance(plugins, dict):
            return False
        section = plugins.get("conda_tasks") or plugins.get("conda-tasks")
        return bool(isinstance(section, dict) and section.get("tasks"))

    def parse(self, path: Path) -> dict[str, Task]:
        """Parse tasks from condarc via the config API, falling back to direct YAML."""
        raw_tasks = _raw_tasks_from_condarc()
        if not raw_tasks:
            try:
                data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
            except yaml.YAMLError as exc:
                raise TaskParseError(str(path), str(exc)) from exc
            plugins = data.get("plugins", {})
            section = plugins.get("conda_tasks") or plugins.get("conda-tasks") or {}
            raw_tasks = section.get("tasks", {})
        if not isinstance(raw_tasks, dict):
            raise TaskParseError(
                str(path), "plugins.conda_tasks.tasks must be a mapping"
            )
        return normalize_tasks(raw_tasks)

    def add_task(self, path: Path, name: str, task: Task) -> None:
        """Add or update a task under ``plugins.conda_tasks.tasks`` in ``.condarc``."""
        if path.exists():
            data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        else:
            data = {}

        section = (
            data.setdefault("plugins", {})
            .setdefault("conda_tasks", {})
            .setdefault("tasks", {})
        )
        defn: dict[str, object] = {}
        if task.cmd is not None:
            defn["cmd"] = task.cmd
        if task.depends_on:
            defn["depends-on"] = [d.task for d in task.depends_on]
        if task.description:
            defn["description"] = task.description
        section[name] = defn if defn else task.cmd
        path.write_text(
            yaml.dump(data, default_flow_style=False, sort_keys=False), encoding="utf-8"
        )

    def remove_task(self, path: Path, name: str) -> None:
        """Remove a task from the ``.condarc`` file by name."""
        data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        plugins = data.get("plugins", {})
        section = plugins.get("conda_tasks", plugins.get("conda-tasks", {})).get(
            "tasks", {}
        )
        if name not in section:
            raise TaskNotFoundError(name, list(section.keys()))
        del section[name]
        path.write_text(
            yaml.dump(data, default_flow_style=False, sort_keys=False), encoding="utf-8"
        )
