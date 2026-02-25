# conda-tasks

[![Tests](https://github.com/jezdez/conda-tasks/actions/workflows/test.yml/badge.svg)](https://github.com/jezdez/conda-tasks/actions/workflows/test.yml)
[![Docs](https://github.com/jezdez/conda-tasks/actions/workflows/docs.yml/badge.svg)](https://jezdez.github.io/conda-tasks/)
[![License](https://img.shields.io/github/license/jezdez/conda-tasks)](https://github.com/jezdez/conda-tasks/blob/main/LICENSE)
[![Python](https://img.shields.io/badge/python-3.10%E2%80%933.14-blue)](https://github.com/jezdez/conda-tasks)

The missing task runner for conda, inspired by [pixi](https://pixi.sh).

Define tasks in your project, wire up dependencies between them, and run
everything through `conda task`. Works with your existing conda environments
-- no new package manager required.

## Quick start

Create a `conda-tasks.yml` in your project root:

```yaml
tasks:
  build:
    cmd: "python -m build"
  test:
    cmd: "pytest tests/ -v"
    depends-on: [build]
  lint:
    cmd: "ruff check ."
  check:
    depends-on: [test, lint]
```

```
$ conda task run check
  ▶ build
  ▶ lint
  ▶ test
```

## Why?

Conda handles environments and packages. But there's no built-in way to
define project tasks -- the kind of thing you'd otherwise put in a `Makefile`,
`tox.ini`, or a pile of shell scripts. pixi solved this well, but it's a
separate tool with its own environment management.

conda-tasks brings the task runner part to conda as a plugin. You keep using
conda for environments, and get a proper task system on top.

## What it does

- Task dependencies with topological ordering (`depends-on`)
- Jinja2 templates in commands (`{{ conda.platform }}`, conditionals)
- Task arguments with defaults
- Input/output caching -- skip tasks when nothing changed
- Per-platform overrides for cross-platform projects
- Run tasks in any conda environment (`-n myenv`)
- Reads from `conda-tasks.yml`, `conda-tasks.toml`, `pixi.toml`,
  `pyproject.toml`, or `.condarc`

## Installation

```bash
conda install -c conda-forge conda-tasks
```

## What it doesn't do

conda-tasks is a task runner, not a package manager. It does not create
environments or install dependencies -- that's conda's job. If you're
coming from pixi where `pixi run` handles both, see the
[migration guide](https://jezdez.github.io/conda-tasks/tutorials/coming-from-pixi/).

## Documentation

https://jezdez.github.io/conda-tasks/

## Acknowledgements

The task system in conda-tasks is directly inspired by the work of the
[prefix.dev](https://prefix.dev) team on [pixi](https://github.com/prefix-dev/pixi).
Their design of task definitions, dependency graphs, platform overrides,
and caching provided the blueprint for this plugin. conda-tasks exists
because pixi demonstrated that a good task runner belongs in every
project workflow.

## License

BSD 3-Clause. See [LICENSE](LICENSE).
