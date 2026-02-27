# Your first project with conda-tasks

This tutorial walks you through setting up a Python project with conda-tasks
from scratch. By the end you will have a working build-test-lint workflow
driven entirely by `conda task`.

## Prerequisites

- conda (24.7 or later) installed
- conda-tasks installed (`conda install conda-tasks`)

## 1. Create the project

Start with a small Python package:

```bash
mkdir myproject && cd myproject
mkdir -p src/myproject tests
```

Create `src/myproject/__init__.py`:

```python
def greet(name: str) -> str:
    return f"Hello, {name}!"
```

Create `tests/test_greet.py`:

```python
from myproject import greet

def test_greet():
    assert greet("world") == "Hello, world!"
```

And a minimal `pyproject.toml`:

```toml
[project]
name = "myproject"
version = "0.1.0"
requires-python = ">=3.10"
```

## 2. Set up your conda environment

conda-tasks is a task runner, not a package manager. It does not create
environments or install dependencies for you -- that is conda's job. This
separation is intentional: your environment definition lives in one place
(`environment.yml`, `conda create`, etc.) and your task definitions live in
another (`conda.toml`).

Create the environment with the tools your tasks will need:

```bash
conda create -n myproject python pytest ruff -y
conda activate myproject
```

:::{tip}
If you are used to pixi, where `pixi.toml` manages both dependencies *and*
tasks, the key difference here is that conda-tasks focuses only on the task
side. Dependency management stays with conda's existing tools, giving you
the full power of `environment.yml`, `conda lock`, and conda's solver
without duplicating any of that machinery.
:::

## 3. Define your tasks

Create a `conda.toml` in the project root:

```toml
[tasks]
test = { cmd = "pytest tests/ -v", description = "Run the test suite" }
lint = { cmd = "ruff check src/", description = "Lint the source code" }
format = { cmd = "ruff format src/ tests/", description = "Auto-format all Python files" }

[tasks.check]
depends-on = ["lint", "test"]
description = "Run all checks"
```

## 4. Run tasks

List available tasks:

```bash
conda task list
```

```text
Tasks from /path/to/myproject/conda.toml:

  check   Run all checks  [depends: lint, test]
  format  Auto-format all Python files
  lint    Lint the source code
  test    Run the test suite
```

Run a single task:

```bash
conda task run test
```

Run the full check suite (lint + test, in dependency order):

```bash
conda task run check
```

## 5. Add caching

Avoid re-running expensive tasks when nothing has changed by declaring
inputs and outputs:

```toml
[tasks.test]
cmd = "pytest tests/ -v"
description = "Run the test suite"
inputs = ["src/**/*.py", "tests/**/*.py"]
outputs = []
```

On the second run with unchanged files you will see:

```text
  [cached] test
```

## 6. Add platform-specific tasks

If your project needs platform-specific commands, use the `target` key:

```toml
[tasks]
clean = { cmd = "rm -rf build/ dist/", description = "Clean build artifacts" }

[target.win-64.tasks]
clean = "rd /s /q build dist"
```

## 7. Run in a different environment

You can run tasks against any conda environment, not just the active one:

```bash
conda task run test -n some-other-env
```

This activates `some-other-env` for the duration of the task, just like
`conda run -n some-other-env`.

## What you have learned

- conda-tasks is a task runner -- environments and dependencies are managed
  separately by conda
- Tasks are defined in `conda.toml` (or other supported formats)
- Tasks can depend on each other, forming an execution graph
- Caching and platform overrides help keep workflows fast and portable
- The `-n` flag lets you target any conda environment

## Next steps

- {doc}`coming-from-pixi` -- if you are migrating from pixi
- {doc}`../features` -- full reference of all task features
- {doc}`../configuration` -- all supported file formats and fields
