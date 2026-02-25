# conda-tasks

**Pixi-style task runner plugin for conda.**

conda-tasks adds a `conda task` subcommand that brings [pixi's powerful task
runner system](https://pixi.sh/latest/features/tasks/) to conda. Define tasks
in your project, then run them with `conda task run <name>`.

## Installation

```bash
conda install conda-tasks
```

## Quick Example

Create a `conda-tasks.yml` in your project root:

```yaml
tasks:
  build:
    cmd: "python -m build"
    description: "Build the package"
  test:
    cmd: "pytest tests/ -v"
    depends-on: [build]
    description: "Run the test suite"
  lint:
    cmd: "ruff check ."
    description: "Lint the codebase"
  check:
    depends-on: [test, lint]
    description: "Run all checks"
```

Then run:

```bash
conda task run test     # builds first, then tests
conda task list         # shows all available tasks
```

## Features

- **Multiple file formats** -- `conda-tasks.yml`, `pixi.toml`, `pyproject.toml`, `.condarc`
- **Dependency graphs** -- tasks depend on other tasks with automatic ordering
- **Jinja2 templates** -- use `{{ conda.platform }}` and other variables in commands
- **Task arguments** -- pass arguments with defaults
- **Caching** -- skip re-execution when inputs haven't changed
- **Cross-platform** -- per-platform task overrides for OS-specific commands
- **Conda environments** -- run tasks in specific environments with `-n`/`-p`

```{toctree}
:maxdepth: 2
:caption: Getting Started

quickstart
tutorials/index
```

```{toctree}
:maxdepth: 2
:caption: User Guide

features
configuration
```

```{toctree}
:maxdepth: 2
:caption: Reference

reference/cli
reference/api
```

```{toctree}
:maxdepth: 2
:caption: About

motivation
changelog
```
