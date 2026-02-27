# conda-tasks

The missing task runner for conda, inspired by [pixi](https://pixi.sh).

```bash
conda task run test     # builds first, then tests
conda task list         # shows all available tasks
```

```toml
# conda.toml
[tasks]
build = "python -m build"
test = { cmd = "pytest tests/ -v", depends-on = ["build"] }
lint = "ruff check ."

[tasks.check]
depends-on = ["test", "lint"]
```

---

::::{grid} 2
:gutter: 3

:::{grid-item-card} {octicon}`rocket` Getting started
:link: quickstart
:link-type: doc

Install conda-tasks and define your first task in under a minute.
:::

:::{grid-item-card} {octicon}`mortar-board` Tutorials
:link: tutorials/index
:link-type: doc

Step-by-step guides: your first project, migrating from pixi, CI setup.
:::

:::{grid-item-card} {octicon}`list-unordered` Features
:link: features
:link-type: doc

Dependencies, templates, caching, arguments, platform overrides,
environment targeting, and more.
:::

:::{grid-item-card} {octicon}`gear` Configuration
:link: configuration
:link-type: doc

All task fields, file formats (`conda.toml`,
`pixi.toml`, `pyproject.toml`, `.condarc`), and examples.
:::

:::{grid-item-card} {octicon}`terminal` CLI reference
:link: reference/cli
:link-type: doc

Complete `conda task` command-line documentation.
:::

:::{grid-item-card} {octicon}`code` API reference
:link: reference/api
:link-type: doc

Python API for models, parsers, graph resolution, caching, and
template rendering.
:::

::::

```{toctree}
:hidden:

quickstart
tutorials/index
features
configuration
reference/cli
reference/api
motivation
changelog
```
