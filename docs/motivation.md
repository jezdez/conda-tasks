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

conda-tasks is deliberately scoped as a task runner only. It does not
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

- Use any conda workflow for environments (manual, `environment.yml`,
  `conda-lock`, constructor)
- Share task definitions across teams without coupling to a specific
  dependency specification
- Run the same tasks against different environments via `-n`
- Adopt conda-tasks incrementally without changing your existing
  environment management

## Comparison to pixi tasks

conda-tasks is designed for feature parity with pixi's task system on
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
| Dependency management | Built-in | Not included (use conda) |
| Environment creation | Built-in | Not included (use conda) |

### Key differences

- Dependency management: pixi creates and manages environments from its
  manifest. conda-tasks does not -- you create environments with conda and
  point tasks at them. See {doc}`tutorials/coming-from-pixi` for a migration
  guide.
- Template engine: conda-tasks uses Jinja2 (Python-native, widely available)
  instead of MiniJinja (Rust). The template syntax is identical.
- Shell: conda-tasks uses the native platform shell via `subprocess` instead
  of `deno_task_shell`. Cross-platform commands are handled via platform-specific
  task overrides or Jinja2 conditionals.
- File formats: conda-tasks reads from `conda-tasks.yml`, `pixi.toml`,
  `pyproject.toml`, and `.condarc`. pixi only reads from `pixi.toml` and
  `pyproject.toml`.
- Conda integration: tasks can target specific conda environments using
  `-n`/`-p` flags, matching conda's standard interface.

## Prior art

The idea of running commands from a project definition is not new in the
conda ecosystem. Several tools have explored this space, each with a
different scope.

### anaconda-project

[anaconda-project](https://github.com/anaconda/anaconda-project)
was one of the first tools to combine conda environments with project
commands. Its `anaconda-project.yml` lets you define named commands,
platform-specific variants (`unix:` / `windows:`), and service
dependencies. Running `anaconda-project run` automatically sets up the
environment before executing. It focuses on reproducible project
launchers rather than build-style task graphs -- there is no way to
express dependencies between commands, no caching, and no templating.

### conda-project

[conda-project](https://github.com/conda-incubator/conda-project) is a
community successor to anaconda-project, maintained under conda-incubator.
It modernizes the workflow with `conda-lock` integration and a
`conda project run` command. Like its predecessor, it centers on
environment management and command execution rather than task
orchestration -- commands cannot depend on each other.

### conda-execute

[conda-execute](https://github.com/pelson/conda-execute) takes a
different approach: embed environment requirements directly in a script's
header comments, then run it in an auto-created temporary environment.
It is aimed at one-off scripts rather than multi-step project workflows.

### conda run

Conda itself ships `conda run -n <env> <command>`, which activates an
environment and runs a single command. It is the low-level primitive that
conda-tasks builds on, but it has no concept of task definitions,
dependencies, or caching.

### General-purpose Python task runners

Tools like [tox](https://tox.wiki), [nox](https://nox.thea.codes),
[invoke](https://www.pyinvoke.org), and
[hatch](https://hatch.pypa.io) each provide ways to define and run
project tasks. tox and nox focus on test-matrix automation with
virtualenvs; invoke is a general-purpose Make replacement; hatch offers
scripts and environment matrices for Python projects. None of them
integrate directly with conda environments or conda's plugin system.

### pixi

[pixi](https://pixi.sh) by [prefix.dev](https://prefix.dev) was the
first tool to ship a full-featured task runner tightly integrated with
conda package management: task dependencies, platform overrides,
input/output caching, template variables, and task arguments. Its task
system is the direct inspiration for conda-tasks. The key difference is
that pixi manages both environments and tasks, while conda-tasks
deliberately handles only the task-running side and leaves environment
management to conda.

## Acknowledgements

conda-tasks would not exist without the work of the
[prefix.dev](https://prefix.dev) team on [pixi](https://github.com/prefix-dev/pixi).
The task system design -- dependency graphs, platform overrides, caching,
template variables, and the overall developer experience -- comes directly
from their implementation. We are grateful for their contribution to the
conda ecosystem and for setting the bar on what a project task runner
should look like.

The [anaconda-project](https://github.com/anaconda/anaconda-project)
and [conda-project](https://github.com/conda-incubator/conda-project)
teams explored running commands from project manifests long before
conda-tasks existed. Their work informed how project-level automation
fits into the conda ecosystem.
