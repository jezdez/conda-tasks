"""Task model dataclasses for conda-tasks."""

from __future__ import annotations

from dataclasses import dataclass, field, fields
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Any


@dataclass
class TaskArg:
    """A named argument that can be passed to a task."""

    name: str
    default: str | None = None


@dataclass
class TaskDependency:
    """A reference to another task that must run first."""

    task: str
    args: list[str | dict[str, str]] = field(default_factory=list)
    environment: str | None = None


@dataclass
class TaskOverride:
    """Per-platform override for any task field.

    Non-None fields replace the base task's values when the override
    is merged into a Task via ``Task.resolve_for_platform``.
    """

    cmd: str | list[str] | None = None
    args: list[TaskArg] | None = None
    depends_on: list[TaskDependency] | None = None
    cwd: str | None = None
    env: dict[str, str] | None = None
    inputs: list[str] | None = None
    outputs: list[str] | None = None
    clean_env: bool | None = None


@dataclass
class Task:
    """A single task definition with all its configuration."""

    name: str
    cmd: str | list[str] | None = None
    args: list[TaskArg] = field(default_factory=list)
    depends_on: list[TaskDependency] = field(default_factory=list)
    cwd: str | None = None
    env: dict[str, str] = field(default_factory=dict)
    description: str | None = None
    inputs: list[str] = field(default_factory=list)
    outputs: list[str] = field(default_factory=list)
    clean_env: bool = False
    default_environment: str | None = None
    platforms: dict[str, TaskOverride] | None = None

    @property
    def is_alias(self) -> bool:
        """True when the task is just a dependency grouping with no command."""
        return self.cmd is None and bool(self.depends_on)

    @property
    def is_hidden(self) -> bool:
        """Hidden tasks (prefixed with ``_``) are omitted from listings."""
        return self.name.startswith("_")

    def resolve_for_platform(self, subdir: str) -> Task:
        """Return a copy of this task with platform overrides merged in.

        *subdir* is a conda platform string such as ``linux-64`` or ``osx-arm64``.
        If there is no matching override the task is returned unchanged.
        """
        if not self.platforms or subdir not in self.platforms:
            return self

        override = self.platforms[subdir]
        kwargs: dict[str, Any] = {}
        for f in fields(self):
            if f.name in ("name", "platforms", "description", "default_environment"):
                kwargs[f.name] = getattr(self, f.name)
                continue
            override_val = (
                getattr(override, f.name, None) if hasattr(override, f.name) else None
            )
            if override_val is not None:
                kwargs[f.name] = override_val
            else:
                kwargs[f.name] = getattr(self, f.name)
        return Task(**kwargs)
