# Coming from pixi

If you have been using pixi's task system, conda-tasks will feel familiar.
This tutorial explains the differences and shows how to migrate.

## The big picture

In pixi, a single `pixi.toml` manages both your dependencies and your
tasks. When you run `pixi run test`, pixi:

1. Reads the dependency specification from `pixi.toml`
2. Creates or updates the environment (solving, downloading, installing)
3. Activates the environment
4. Runs the task

conda-tasks only does step 3 and 4. It is a task runner, not a package
manager. Environment creation and dependency management remain the
responsibility of conda itself.

:::{card} Why the separation?
:class-card: sd-border-info

Conda already has mature, well-tested tools for dependency management:
`environment.yml`, `conda create`, `conda lock`, the solver, channels,
and more. Duplicating that in a task runner plugin would create a second
source of truth and re-invent complexity that conda handles well.

By keeping tasks separate from dependencies, you can:

- Use any conda workflow for environments (manual, `environment.yml`,
  `conda-lock`, constructor)
- Share task definitions across teams without coupling to a specific
  environment specification
- Run the same tasks against different environments via `-n`
:::

## What stays the same

Almost everything about the task *definitions* is identical:

| Feature | pixi | conda-tasks |
|---|---|---|
| String commands | `build = "make"` | `build = "make"` (TOML) |
| Dict commands | `{cmd = "pytest", depends-on = [...]}` | Same |
| Dependencies | `depends-on` | Same |
| Task aliases | `[{task = "a"}, {task = "b"}]` | `depends-on: [a, b]` |
| Platform overrides | `[target.win-64.tasks]` | Same |
| Environment variables | `env = {KEY = "val"}` | Same |
| Clean environment | `clean-env = true` | Same |
| Hidden tasks | `_prefixed` | Same |
| Caching | `inputs` / `outputs` | Same |

## What is different

### 1. No automatic dependency installation

This is the key difference. In pixi you might write:

```toml
# pixi.toml
[dependencies]
python = ">=3.12"
pytest = "*"
ruff = "*"

[tasks]
test = "pytest tests/"
```

With conda-tasks, the environment setup happens separately:

```bash
# Step 1: create the environment (conda's job)
conda create -n myproject python pytest ruff -y
conda activate myproject

# Step 2: define tasks (conda-tasks' job)
# conda.toml
```

```toml
[tasks]
test = "pytest tests/"
```

### 2. Template engine: Jinja2 instead of MiniJinja

pixi uses MiniJinja (Rust). conda-tasks uses Jinja2 (Python). The template
syntax is identical for all practical purposes -- `{{ pixi.platform }}`
works in conda-tasks when reading from `pixi.toml`, and `{{ conda.platform }}`
is available everywhere.

The only difference you might notice is that Jinja2 supports a few extra
filters and features not present in MiniJinja. You are unlikely to hit any
incompatibilities going the other direction.

### 3. Shell execution

pixi uses `deno_task_shell`, a cross-platform shell that understands commands
like `rm` on Windows. conda-tasks uses the native platform shell (`sh` on
Unix, `cmd` on Windows).

For cross-platform compatibility, use platform overrides:

```toml
[tasks]
clean = "rm -rf build/"

[target.win-64.tasks]
clean = "rd /s /q build"
```

Or use Jinja2 conditionals:

```toml
[tasks]
clean = "{% if conda.is_win %}rd /s /q build{% else %}rm -rf build/{% endif %}"
```

### 4. Additional file formats

conda-tasks reads from four sources (in detection priority order):

1. `pixi.toml` -- reads your existing pixi tasks directly
2. `conda.toml` -- canonical TOML format (same table structure as pixi.toml)
3. `pyproject.toml` -- reads `[tool.conda.tasks]`, `[tool.conda-tasks.tasks]`, or `[tool.pixi.tasks]`
4. `.condarc` -- global tasks via conda's settings API

pixi only reads from `pixi.toml` and `pyproject.toml`. `conda.toml`
uses an identical layout to pixi's `[tasks]` tables.

### 5. Conda environment targeting

conda-tasks uses conda's standard `-n`/`-p` flags to run tasks in specific
environments:

```bash
conda task run test -n py311-compat
```

This mirrors `conda run -n ...` and works with any existing conda environment.

## Migrating a pixi.toml

If you have an existing `pixi.toml`, you have two options:

### Option A: Use pixi.toml directly (zero migration)

conda-tasks reads `pixi.toml` natively. Just install conda-tasks and run:

```bash
conda task run test
```

It will pick up your existing `[tasks]` and `[target.*.tasks]` tables.
You only need to set up the conda environment separately.

### Option B: Export to conda.toml

If you prefer a dedicated file or want to decouple from pixi, use the
built-in `export` command to convert automatically:

```bash
conda task export --file pixi.toml -o conda.toml
```

This reads your existing `pixi.toml` tasks (including platform overrides)
and writes a fully equivalent `conda.toml`. You can also export to stdout
for inspection:

```bash
conda task export --file pixi.toml
```

::::{tab-set}

:::{tab-item} pixi.toml

```toml
[tasks]
build = "python -m build"
test = { cmd = "pytest", depends-on = ["build"] }
lint = { cmd = "ruff check .", description = "Lint the code" }

[target.win-64.tasks]
build = "python -m build --wheel"
```

:::

:::{tab-item} Exported conda.toml

```toml
[tasks]
build = "python -m build"
test = { cmd = "pytest", depends-on = ["build"] }
lint = { cmd = "ruff check .", description = "Lint the code" }

[target.win-64.tasks]
build = "python -m build --wheel"
```

:::

::::

## Typical migration checklist

- [ ] Identify the dependencies from `pixi.toml` and create a matching
      conda environment (`conda create` or `environment.yml`)
- [ ] Either keep using `pixi.toml` for tasks (option A) or export
      (option B: `conda task export --file pixi.toml -o conda.toml`)
- [ ] Replace any `pixi run <task>` calls with `conda task run <task>`
- [ ] If using CI, add an environment setup step before the task step
      (see {doc}`ci-pipeline`)
- [ ] Test that `conda task list` shows all expected tasks

## Next steps

- {doc}`ci-pipeline` -- setting up conda-tasks in CI
- {doc}`../features` -- full feature reference
