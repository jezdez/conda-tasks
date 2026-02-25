"""Fixtures for parser tests."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from pathlib import Path


@pytest.fixture
def sample_pixi_toml(tmp_project: Path) -> Path:
    """Create a sample pixi.toml for testing."""
    content = """\
[tasks]
build = "make build"
test = { cmd = "pytest", depends-on = ["build"] }
lint = { cmd = "ruff check .", description = "Lint the code" }

[target.win-64.tasks]
build = "nmake build"
"""
    path = tmp_project / "pixi.toml"
    path.write_text(content)
    return path


@pytest.fixture
def sample_pyproject(tmp_project: Path) -> Path:
    """Create a sample pyproject.toml with conda-tasks section."""
    content = """\
[project]
name = "example"

[tool.conda-tasks.tasks]
build = "make build"

[tool.conda-tasks.tasks.test]
cmd = "pytest"
depends-on = ["build"]

[tool.conda-tasks.target.win-64.tasks]
build = "nmake build"
"""
    path = tmp_project / "pyproject.toml"
    path.write_text(content)
    return path


@pytest.fixture
def sample_conda_tasks_toml(tmp_project: Path) -> Path:
    """Create a sample conda-tasks.toml for testing."""
    content = """\
[tasks]
build = { cmd = "make build", depends-on = ["configure"] }
configure = "cmake ."
test = { cmd = "pytest", depends-on = ["build"] }

[target.win-64.tasks]
build = "nmake build"
"""
    path = tmp_project / "conda-tasks.toml"
    path.write_text(content)
    return path


@pytest.fixture
def sample_condarc(tmp_project: Path) -> Path:
    """Create a sample .condarc with tasks."""
    content = """\
plugins:
  conda_tasks:
    tasks:
      greet:
        cmd: "echo hello"
        description: "Say hello"
      farewell:
        cmd: "echo goodbye"
        depends-on: [greet]
"""
    path = tmp_project / ".condarc"
    path.write_text(content)
    return path
