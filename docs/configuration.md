# Configuration reference

## Task fields

| Field | Type | Description |
|---|---|---|
| `cmd` | `string` or `list[string]` | Command to execute. `None` for aliases. |
| `args` | `list` | Named arguments with optional defaults. |
| `depends-on` | `list` | Tasks to run before this one. |
| `cwd` | `string` | Working directory for the task. |
| `env` | `dict` | Environment variables to set. |
| `description` | `string` | Human-readable description. |
| `inputs` | `list[string]` | Glob patterns for cache inputs. |
| `outputs` | `list[string]` | Glob patterns for cache outputs. |
| `clean-env` | `bool` | Run with minimal environment variables. |
| `default-environment` | `string` | Conda environment to activate by default. |
| `target` | `dict` | Per-platform overrides (keys are platform strings). |

## File formats

conda-tasks reads from four file formats, checked in this order.

::::{tab-set}

:::{tab-item} pixi.toml

Reads the `[tasks]` and `[target.*.tasks]` tables from an existing pixi manifest.

```toml
[tasks]
build = "python -m build"
test = { cmd = "pytest", depends-on = ["build"] }

[target.win-64.tasks]
build = "python -m build --wheel"
```

:::

:::{tab-item} conda.toml

The canonical conda-native TOML format. Same table structure as `pixi.toml`.

```toml
[tasks]
build = "python -m build"
test = { cmd = "pytest", depends-on = ["build"] }

[tasks.deploy]
cmd = "python -m build --wheel"
description = "Build and deploy"
inputs = ["src/**/*.py"]
outputs = ["dist/"]
env = { PYTHONPATH = "src" }

[target.win-64.tasks]
build = "python -m build --wheel"
```

:::

:::{tab-item} pyproject.toml

Reads from `[tool.conda.tasks]` (preferred), falling back to
`[tool.conda-tasks.tasks]` (legacy) or `[tool.pixi.tasks]`.

```toml
[tool.conda.tasks]
build = "python -m build"

[tool.conda.tasks.test]
cmd = "pytest"
depends-on = ["build"]

[tool.conda.target.win-64.tasks]
build = "python -m build --wheel"
```

:::

:::{tab-item} .condarc

Task definitions loaded through conda's plugin settings API. Available
globally across all projects. Settings from all condarc sources (user,
system, environment) are merged automatically.

```yaml
plugins:
  conda_tasks:
    tasks:
      build:
        cmd: "python -m build"
```

The setting is registered as `conda_tasks` (with `conda-tasks` accepted as an alias).

:::

::::

## Argument definitions

```toml
[tasks.test]
cmd = "pytest {{ path }} {{ flags }}"
args = [
  { arg = "path", default = "tests/" },
  { arg = "flags", default = "-v" },
]
```

## Dependency definitions

Simple list:

```toml
[tasks.check]
depends-on = ["compile", "lint"]
```

With arguments:

```toml
[tasks.check]
depends-on = [
  { task = "test", args = ["tests/unit/"] },
]
```

With environment:

```toml
[tasks.check]
depends-on = [
  { task = "test", environment = "py311" },
]
```
