"""Task file parser registry and auto-detection."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import TYPE_CHECKING

from ..exceptions import NoTaskFileError, TaskParseError
from .base import TaskFileParser
from .condarc import CondaRCParser
from .pixi_toml import PixiTomlParser
from .pyproject_toml import PyprojectTomlParser
from .toml import CondaTasksTomlParser
from .yaml import CondaTasksYAMLParser

if TYPE_CHECKING:
    from ..models import Task

__all__ = ["TaskFileParser", "detect_and_parse", "detect_task_file", "get_parser"]

_SEARCH_ORDER: tuple[str, ...] = (
    "conda-tasks.yml",
    "conda-tasks.toml",
    "pixi.toml",
    "pyproject.toml",
    ".condarc",
)


def _parser_registry() -> list[TaskFileParser]:
    """Return all registered parser instances in detection priority order."""
    return [
        CondaTasksYAMLParser(),
        CondaTasksTomlParser(),
        PixiTomlParser(),
        PyprojectTomlParser(),
        CondaRCParser(),
    ]


def get_parser(path: Path) -> TaskFileParser | None:
    """Return the first parser that can handle *path*, or ``None``."""
    for parser in _parser_registry():
        if parser.can_handle(path):
            return parser
    return None


def detect_task_file(start_dir: Path | None = None) -> Path | None:
    """Walk up from *start_dir* looking for a known task file.

    Returns the first match according to ``_SEARCH_ORDER``, or ``None``.
    """
    if start_dir is None:
        start_dir = Path.cwd()
    start_dir = start_dir.resolve()

    current = start_dir
    while True:
        for name in _SEARCH_ORDER:
            candidate = current / name
            if candidate.is_file():
                parser = get_parser(candidate)
                if parser is not None:
                    return candidate
        parent = current.parent
        if parent == current:
            break
        current = parent
    return None


@lru_cache(maxsize=4)
def _cached_parse(path: str) -> dict[str, Task]:
    """Parse a task file (cached by path string for memoisation)."""
    p = Path(path)
    parser = get_parser(p)
    if parser is None:
        raise TaskParseError(str(p), "no parser found for this file format")
    return parser.parse(p)


def detect_and_parse(
    file_path: Path | None = None,
    start_dir: Path | None = None,
) -> tuple[Path, dict[str, Task]]:
    """Detect (or use *file_path*) a task file and parse it.

    Returns ``(resolved_path, {task_name: Task})``.
    Raises ``NoTaskFileError`` when no file is found.
    """
    if file_path is not None:
        path = file_path.resolve()
    else:
        path = detect_task_file(start_dir)
        if path is None:
            raise NoTaskFileError(str(start_dir or Path.cwd()))
    tasks = _cached_parse(str(path))
    return path, tasks
