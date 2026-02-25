# Motivation

## Why conda-tasks?

Conda is a powerful package and environment manager, but it has lacked a
built-in task runner. Projects often rely on `Makefile`, `tox`, `nox`,
`invoke`, or ad-hoc shell scripts for common workflows like building,
testing, and linting.

[pixi](https://pixi.sh) introduced an excellent task system that integrates
tightly with project configuration. conda-tasks brings that same capability
to conda as a plugin, so existing conda users can define and run tasks without
switching tools.

## Tasks, not dependencies

conda-tasks is deliberately scoped as a **task runner only**. It does not
create environments, install packages, or manage dependencies. That is
conda's job.

In pixi, a single `pixi.toml` manages both dependencies and tasks. Running
`pixi run test` implicitly solves, installs, and activates an environment
before executing the task. conda-tasks separates these concerns:

| Responsibility | In pixi | In conda + conda-tasks |
|---|---|---|
| Define dependencies | `pixi.toml` `[dependencies]` | `environment.yml`, `conda create`, etc. |
| Solve and install | `pixi run` (implicit) | `conda install`, `conda env create` |
| Define tasks | `pixi.toml` `[tasks]` | `conda-tasks.yml` (or `pixi.toml`, `pyproject.toml`, `.condarc`) |
| Run tasks | `pixi run <task>` | `conda task run <task>` |

This separation is intentional. Conda already has mature, well-tested tools
for dependency management -- the solver, `environment.yml`, `conda lock`,
channels, and more. Duplicating that machinery in a task runner would create a
second source of truth and added complexity that conda handles well on its own.

With the split approach you can:

- Use **any** conda workflow for environments (manual, `environment.yml`,
  `conda-lock`, constructor)
- Share task definitions across teams without coupling to a specific
  dependency specification
- Run the same tasks against **different environments** via `-n`
- Adopt conda-tasks incrementally without changing your existing
  environment management

## Comparison to pixi tasks

conda-tasks is designed for **feature parity** with pixi's task system on
the task-running side:

| Feature | pixi | conda-tasks |
|---|---|---|
| String commands | Yes | Yes |
| Task dependencies | Yes | Yes |
| Task aliases | Yes | Yes |
| Task arguments | Yes | Yes |
| Jinja2 templates | MiniJinja | Jinja2 |
| Context variables | `pixi.*` | `conda.*` (+ `pixi.*` alias) |
| Caching (inputs/outputs) | Yes | Yes |
| Platform overrides | `[target.<platform>.tasks]` | Same + `target:` in YAML |
| Environment variables | Yes | Yes |
| Clean environment | Yes | Yes |
| Hidden tasks (`_` prefix) | Yes | Yes |
| **Dependency management** | **Built-in** | **Not included** (use conda) |
| **Environment creation** | **Built-in** | **Not included** (use conda) |

### Key differences

- **Dependency management**: pixi creates and manages environments from its
  manifest. conda-tasks does not -- you create environments with conda and
  point tasks at them. See {doc}`tutorials/coming-from-pixi` for a migration
  guide.
- **Template engine**: conda-tasks uses Jinja2 (Python-native, widely available)
  instead of MiniJinja (Rust). The template syntax is identical.
- **Shell**: conda-tasks uses the native platform shell via `subprocess` instead
  of `deno_task_shell`. Cross-platform commands are handled via platform-specific
  task overrides or Jinja2 conditionals.
- **File formats**: conda-tasks reads from `conda-tasks.yml`, `pixi.toml`,
  `pyproject.toml`, and `.condarc`. pixi only reads from `pixi.toml` and
  `pyproject.toml`.
- **Conda integration**: Tasks can target specific conda environments using
  `-n`/`-p` flags, matching conda's standard interface.
