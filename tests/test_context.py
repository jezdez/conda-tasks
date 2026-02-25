"""Tests for conda_tasks.context."""

from __future__ import annotations

import os
from pathlib import Path

import pytest
from conda import __version__ as conda_version
from conda.base.context import Context, context

from conda_tasks.context import CondaContext, build_template_context


def test_platform():
    assert CondaContext().platform == context.subdir


@pytest.mark.parametrize(
    ("on_win_val", "expected_win", "expected_unix"),
    [
        (False, False, True),
        (True, True, False),
    ],
)
def test_is_win(monkeypatch, on_win_val, expected_win, expected_unix):
    monkeypatch.setattr("conda.base.constants.on_win", on_win_val)
    ctx = CondaContext()
    assert ctx.is_win is expected_win
    assert ctx.is_unix is expected_unix


@pytest.mark.parametrize(
    ("platform_val", "attr"),
    [
        ("osx", "is_osx"),
        ("linux", "is_linux"),
    ],
)
def test_platform_flag(platform_val, attr):
    ctx = CondaContext()
    assert getattr(ctx, attr) == (context.platform == platform_val)


@pytest.mark.parametrize(
    ("manifest_path", "expected"),
    [
        (Path("/some/project/conda-tasks.yml"), "/some/project/conda-tasks.yml"),
        (None, ""),
    ],
    ids=["with-path", "none"],
)
def test_manifest_path(manifest_path, expected):
    ctx = CondaContext(manifest_path=manifest_path)
    assert ctx.manifest_path == expected


def test_environment_name():
    ctx = CondaContext()
    if context.active_prefix:
        expected = Path(context.active_prefix).name
    else:
        expected = "base"
    assert ctx.environment_name == expected


def test_environment_name_fallback(monkeypatch):
    monkeypatch.setattr(Context, "active_prefix", property(lambda self: ""))
    assert CondaContext().environment_name == "base"


def test_environment_proxy():
    ctx = CondaContext()
    assert ctx.environment.name == ctx.environment_name


def test_prefix():
    assert CondaContext().prefix == context.target_prefix


def test_version():
    assert CondaContext().version == conda_version


def test_init_cwd():
    assert CondaContext().init_cwd == os.getcwd()


def test_build_context_has_conda_and_pixi():
    ctx = build_template_context()
    assert "conda" in ctx
    assert "pixi" in ctx
    assert ctx["conda"] is ctx["pixi"]


def test_build_context_task_args():
    ctx = build_template_context(task_args={"path": "tests/"})
    assert ctx["path"] == "tests/"
