# AGENTS.md — conda-tasks coding guidelines

## Project structure

- CLI modules are separated by subcommand, mirroring conda's own CLI
  layout. Each subcommand lives in its own module under `conda_tasks/cli/`
  (e.g., `run.py`, `list.py`, `add.py`, `remove.py`, `export.py`).
  `cli/main.py` contains parser configuration and dispatch; `cli/__init__.py`
  is a thin re-export shim (`configure_parser`, `execute`, `generate_parser`).

- Parser implementations use submodules, not subpackages. The canonical
  format parsers live at `conda_tasks/parsers/toml.py`,
  `conda_tasks/parsers/pixi_toml.py`, `conda_tasks/parsers/pyproject_toml.py`,
  and `conda_tasks/parsers/condarc.py` — plain modules, not directories
  with `__init__.py`. Only create a subpackage when there are multiple
  files to group.

- Tests mirror the source structure. Tests for `conda_tasks/cli/run.py`
  live in `tests/cli/test_run.py`, tests for `conda_tasks/parsers/toml.py`
  live in `tests/parsers/test_toml.py`, etc. Test module names match their
  corresponding source module names.

## Imports

- Use relative imports for all intra-package references
  (`from .models import Task`, `from ..exceptions import TaskParseError`).
  Absolute `conda_tasks.*` imports should only appear in tests and
  entry points.

- Inline (lazy) imports are reserved for performance-critical paths.
  Acceptable cases: `plugin.py` hooks (loaded on every `conda` invocation),
  `cli/main.py` subcommand dispatch (only the chosen handler is loaded),
  `template.py` Jinja2 import (skipped when no template markers are present),
  `runner.py` conda activation imports (only needed when running in a conda
  env), and `context.py` property methods (lazy by design). Everywhere else,
  imports belong at the top of the module.

## Dependencies

- Minimize the dependency graph. Prefer stdlib or already-required packages
  over adding new ones. When a single library covers multiple use cases
  (e.g., `tomlkit` for both reading and writing TOML), use it instead of
  carrying separate read-only and read-write libraries.

- Pin minimum versions in `pyproject.toml` dependencies (e.g.,
  `"tomlkit >=0.13"`), not exact versions.

## Typing and linting

- All code must be typed using modern annotations (`str | None` not
  `Optional[str]`, `list[str]` not `List[str]`). `ClassVar` from `typing`
  is the correct annotation for class-level attributes — it is not
  deprecated.

- Use `ty` for type checking and `ruff` for linting and formatting.
  Both are configured in `pyproject.toml`.

- Use `from __future__ import annotations` in all modules.

## Testing

- Tests are plain `pytest` functions — no `unittest.TestCase` classes.

- Use `pytest` native fixtures (`tmp_path`, `monkeypatch`, `capsys`)
  instead of `unittest.mock`. Prefer `monkeypatch.setattr` with simple
  fakes or recording closures over `MagicMock` / `patch`.

- Use `pytest.mark.parametrize` extensively. When multiple test cases
  exercise the same logic with different inputs, consolidate them into
  a single parameterized test.

- Shared fixtures belong in `conftest.py` at the appropriate level
  (root `tests/conftest.py` for cross-cutting fixtures, subdirectory
  `conftest.py` for module-specific ones).

- Coverage is measured with `pytest-cov`. Thresholds and exclusions are
  configured in `pyproject.toml` under `[tool.coverage.*]`. Run
  `pixi run -e <test-env> test-cov` to generate a coverage report.

## Conda integration

- Follow standard conda CLI patterns: use `-n`/`--name` and
  `-p`/`--prefix` for environment targeting, not custom flags like
  `--environment`.

- Use conda's own APIs where available (e.g., `conda.base.constants.on_win`,
  `conda.base.context.context`, `context.plugins.raw_data` for `.condarc`
  settings) rather than reimplementing platform detection or config parsing.

- The plugin registers via `pluggy` hooks (`conda_subcommands`,
  `conda_settings`) and the `[project.entry-points.conda]` entry point.

## Documentation

- Docs use Sphinx with `conda-sphinx-theme`, `myst-parser`, and
  `sphinx-design`.

- Follow the Diataxis framework: tutorials, how-to guides, reference,
  and explanation sections.

- Key difference from pixi must be documented prominently:
  `conda-tasks` is a task runner only — it does not install dependencies
  or manage environments.

- Avoid excessive bold and italic in prose, list items, and headings.
  Don't bold every list item or key term — let the text speak for
  itself. In docstrings, use `*param*` for parameter names (standard
  Sphinx convention) but avoid bold elsewhere.

- Keep `sphinx-design` tab labels short. Use "TOML" / "pyproject.toml"
  instead of full filenames when the tab content already identifies the
  file. This prevents tab overflow on narrow viewports.

- The API reference is split into focused sub-pages by concern (models,
  parsers, execution, context) rather than a single monolithic page.
  The index uses `sphinx-design` grid cards for navigation.

## Parser search order

- The parser registry searches for task manifests in this order:
  1. `pixi.toml` — pixi-native format (task compatibility)
  2. `conda.toml` — conda-native task manifest
  3. `pyproject.toml` — embedded under `[tool.conda.tasks]`,
     `[tool.conda-tasks.tasks]` (legacy), or `[tool.pixi.tasks]`
  4. `.condarc` — tasks defined via conda settings

- All parsers produce task models via the same base interface.
  Parser-specific logic stays in the parser; downstream code only
  depends on the model.
