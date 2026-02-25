"""Parser for the conda-tasks.toml canonical TOML format.

Uses the same structure as pixi.toml tasks:

.. code-block:: toml

    [tasks]
    build = "make build"
    test = { cmd = "pytest", depends-on = ["build"] }

    [target.win-64.tasks]
    build = "nmake build"
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import tomlkit

from ..exceptions import TaskNotFoundError, TaskParseError
from .base import TaskFileParser
from .normalize import normalize_override, normalize_task

if TYPE_CHECKING:
    from pathlib import Path
    from typing import ClassVar

    from tomlkit.items import InlineTable

    from ..models import Task


def _task_to_toml_inline(task: Task) -> str | InlineTable:
    """Convert a Task to a TOML-serializable value (string or inline table).

    Platform overrides are NOT included here -- they go into separate
    ``[target.<platform>.tasks]`` tables.
    """
    defn = tomlkit.inline_table()
    if task.cmd is not None:
        defn.append("cmd", task.cmd)
    if task.depends_on:
        defn.append("depends-on", [d.task for d in task.depends_on])
    if task.description:
        defn.append("description", task.description)
    if task.env:
        defn.append("env", dict(task.env))
    if task.cwd:
        defn.append("cwd", task.cwd)
    if task.clean_env:
        defn.append("clean-env", True)
    if task.args:
        defn.append(
            "args",
            [
                {"arg": a.name, "default": a.default} if a.default else {"arg": a.name}
                for a in task.args
            ],
        )
    if task.inputs:
        defn.append("inputs", list(task.inputs))
    if task.outputs:
        defn.append("outputs", list(task.outputs))

    if len(defn) == 1 and "cmd" in defn:
        return str(defn["cmd"])
    return defn


def tasks_to_toml(tasks: dict[str, Task]) -> str:
    """Serialize a full task dict to ``conda-tasks.toml`` TOML string."""
    doc = tomlkit.document()

    task_table = tomlkit.table()
    for name, task in tasks.items():
        task_table.add(name, _task_to_toml_inline(task))
    doc.add("tasks", task_table)

    targets: dict[str, dict[str, str | InlineTable]] = {}
    for name, task in tasks.items():
        if not task.platforms:
            continue
        for platform, override in task.platforms.items():
            ov = tomlkit.inline_table()
            if override.cmd is not None:
                ov.append("cmd", override.cmd)
            if override.env is not None:
                ov.append("env", dict(override.env))
            if override.cwd is not None:
                ov.append("cwd", override.cwd)
            if override.clean_env is not None:
                ov.append("clean-env", override.clean_env)
            if override.inputs is not None:
                ov.append("inputs", list(override.inputs))
            if override.outputs is not None:
                ov.append("outputs", list(override.outputs))
            targets.setdefault(platform, {})[name] = (
                str(ov["cmd"]) if len(ov) == 1 and "cmd" in ov else ov
            )

    for platform, platform_tasks in targets.items():
        target_tbl = tomlkit.table(is_super_table=True)
        tasks_tbl = tomlkit.table()
        for tname, tval in platform_tasks.items():
            tasks_tbl.add(tname, tval)
        target_tbl.add("tasks", tasks_tbl)
        doc.setdefault("target", tomlkit.table(is_super_table=True)).add(
            platform, target_tbl
        )

    return tomlkit.dumps(doc)


class CondaTasksTomlParser(TaskFileParser):
    """Reads and writes ``conda-tasks.toml`` files.

    Structure is identical to pixi.toml task tables:
    ``[tasks]`` for definitions, ``[target.<platform>.tasks]`` for overrides.
    """

    extensions: ClassVar[tuple[str, ...]] = (".toml",)
    filenames: ClassVar[tuple[str, ...]] = ("conda-tasks.toml",)

    def can_handle(self, path: Path) -> bool:
        """Return True if *path* is a recognized ``conda-tasks.toml`` filename."""
        return path.name in self.filenames

    def parse(self, path: Path) -> dict[str, Task]:
        """Parse a ``conda-tasks.toml`` file including platform overrides."""
        try:
            data = tomlkit.loads(path.read_text(encoding="utf-8")).unwrap()
        except Exception as exc:
            raise TaskParseError(str(path), str(exc)) from exc

        raw_tasks = data.get("tasks", {})
        if not isinstance(raw_tasks, dict):
            raise TaskParseError(str(path), "'tasks' must be a table")

        tasks: dict[str, Task] = {}
        for name, defn in raw_tasks.items():
            tasks[name] = normalize_task(name, defn)

        target = data.get("target", {})
        if isinstance(target, dict):
            for platform, platform_data in target.items():
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
        """Add or update a task in the TOML file, creating it if needed."""
        if path.exists():
            doc = tomlkit.loads(path.read_text(encoding="utf-8"))
        else:
            doc = tomlkit.document()

        tasks_section = doc.setdefault("tasks", tomlkit.table())
        tasks_section[name] = _task_to_toml_inline(task)
        path.write_text(tomlkit.dumps(doc), encoding="utf-8")

    def remove_task(self, path: Path, name: str) -> None:
        """Remove a task from the TOML file by name."""
        doc = tomlkit.loads(path.read_text(encoding="utf-8"))
        tasks_section = doc.get("tasks", {})
        if name not in tasks_section:
            raise TaskNotFoundError(name, list(tasks_section.keys()))
        del tasks_section[name]
        path.write_text(tomlkit.dumps(doc), encoding="utf-8")
