# Quick Start

## Installation

```bash
conda install conda-tasks
```

## Your First Task File

Create a `conda-tasks.yml` in your project root:

```yaml
tasks:
  hello:
    cmd: "echo Hello from conda-tasks!"
    description: "A simple hello world task"
```

Run it:

```bash
conda task run hello
```

## Task Dependencies

Tasks can depend on other tasks:

```yaml
tasks:
  compile:
    cmd: "gcc -o main main.c"
    description: "Compile the program"
  test:
    cmd: "./main --test"
    depends-on: [compile]
    description: "Run tests"
```

Running `conda task run test` will first run `compile`, then `test`.

## Listing Tasks

```bash
conda task list
```

## Supported File Formats

conda-tasks automatically detects task definitions from these files (in order):

1. **`conda-tasks.yml`** -- canonical YAML format
2. **`conda-tasks.toml`** -- canonical TOML format (same structure as pixi.toml)
3. **`pixi.toml`** -- reads the `[tasks]` table directly
4. **`pyproject.toml`** -- reads `[tool.conda-tasks.tasks]` or `[tool.pixi.tasks]`
5. **`.condarc`** -- reads `plugins.conda_tasks.tasks` (via conda's settings API)

## Running in a Specific Environment

```bash
conda task run test -n myenv
```

This activates `myenv` before running the task, just like `conda run -n myenv`.
