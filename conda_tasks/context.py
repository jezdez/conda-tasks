"""Template context variables for Jinja2 rendering.

Provides ``conda.*`` (and ``pixi.*`` alias) template variables that
mirror pixi's built-in template variables.
"""

from __future__ import annotations

import os
from pathlib import Path


class CondaContext:
    """Lazy-evaluated namespace exposed as ``conda.*`` in templates.

    Attribute access is deferred so we only import conda internals when
    a template actually references a variable.
    """

    def __init__(self, manifest_path: Path | None = None):
        self._manifest_path = manifest_path

    @property
    def platform(self) -> str:
        """The conda platform/subdir string, e.g. ``linux-64`` or ``osx-arm64``."""
        from conda.base.context import context

        return context.subdir

    @property
    def environment_name(self) -> str:
        """Name of the currently active conda environment, or ``"base"``."""
        from conda.base.context import context

        if context.active_prefix:
            return Path(context.active_prefix).name
        return "base"

    @property
    def environment(self) -> _EnvironmentProxy:
        """Allows ``{{ conda.environment.name }}`` in templates."""
        return _EnvironmentProxy(self.environment_name)

    @property
    def prefix(self) -> str:
        """Absolute path to the target conda environment prefix."""
        from conda.base.context import context

        return str(context.target_prefix)

    @property
    def version(self) -> str:
        """The installed conda version string."""
        from conda import __version__

        return __version__

    @property
    def manifest_path(self) -> str:
        """Path to the task definition file, or empty string if unknown."""
        return str(self._manifest_path) if self._manifest_path else ""

    @property
    def init_cwd(self) -> str:
        """The working directory at the time of context creation."""
        return os.getcwd()

    @property
    def is_win(self) -> bool:
        """True when running on Windows."""
        from conda.base.constants import on_win

        return on_win

    @property
    def is_unix(self) -> bool:
        """True when running on a Unix-like system (Linux or macOS)."""
        from conda.base.constants import on_win

        return not on_win

    @property
    def is_linux(self) -> bool:
        """True when the host platform is Linux."""
        from conda.base.context import context

        return context.platform == "linux"

    @property
    def is_osx(self) -> bool:
        """True when the host platform is macOS."""
        from conda.base.context import context

        return context.platform == "osx"


class _EnvironmentProxy:
    """Allows ``{{ conda.environment.name }}`` in templates."""

    def __init__(self, name: str):
        self.name = name


def build_template_context(
    manifest_path: Path | None = None,
    task_args: dict[str, str] | None = None,
) -> dict[str, object]:
    """Build the full Jinja2 template context dict.

    The returned dict contains:
    - ``conda``: a CondaContext instance
    - ``pixi``: alias to the same CondaContext (for pixi.toml compat)
    - Any user-supplied task argument values
    """
    ctx = CondaContext(manifest_path=manifest_path)
    result: dict[str, object] = {"conda": ctx, "pixi": ctx}
    if task_args:
        result.update(task_args)
    return result
