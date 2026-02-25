# Configuration Reference

## Task Fields

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

## File Formats

### conda-tasks.yml (canonical YAML)

```yaml
tasks:
  build:
    cmd: "python -m build"
    depends-on: [compile]
    description: "Build the package"
    inputs: ["src/**/*.py"]
    outputs: ["dist/"]
    env:
      PYTHONPATH: "src"
    target:
      win-64:
        cmd: "python -m build --wheel"
```

### conda-tasks.toml (canonical TOML)

Uses the same table structure as `pixi.toml`:

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

### pixi.toml

```toml
[tasks]
build = "python -m build"
test = { cmd = "pytest", depends-on = ["build"] }

[target.win-64.tasks]
build = "python -m build --wheel"
```

### pyproject.toml

```toml
[tool.conda-tasks.tasks]
build = "python -m build"

[tool.conda-tasks.tasks.test]
cmd = "pytest"
depends-on = ["build"]

[tool.conda-tasks.target.win-64.tasks]
build = "python -m build --wheel"
```

Falls back to `[tool.pixi.tasks]` if `[tool.conda-tasks.tasks]` is absent.

### .condarc

Task definitions in `.condarc` are loaded through conda's plugin settings API.
They are available globally across all projects.

```yaml
plugins:
  conda_tasks:
    tasks:
      build:
        cmd: "python -m build"
```

The setting is registered as `conda_tasks` (with `conda-tasks` accepted as an alias).
Settings from all condarc sources (user, system, environment) are merged automatically.

## Argument Definitions

```yaml
tasks:
  test:
    cmd: "pytest {{ path }} {{ flags }}"
    args:
      - arg: path
        default: "tests/"
      - arg: flags
        default: "-v"
```

## Dependency Definitions

Simple list:

```yaml
depends-on: [compile, lint]
```

With arguments:

```yaml
depends-on:
  - task: test
    args: ["tests/unit/"]
```

With environment:

```yaml
depends-on:
  - task: test
    environment: "py311"
```
