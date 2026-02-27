# Features

## Task commands

A task's `cmd` can be a simple string or a list of strings that are joined with spaces:

```toml
[tasks]
build = "python -m build"
build-alt = { cmd = ["python", "-m", "build", "--wheel"] }
```

## Task aliases

Tasks with no `cmd` that only list dependencies act as aliases:

```toml
[tasks.check]
depends-on = ["test", "lint", "typecheck"]
description = "Run all checks"
```

## Hidden tasks

Tasks prefixed with `_` are hidden from `conda task list` but can still be
referenced as dependencies or run explicitly:

```toml
[tasks]
_setup = "mkdir -p build/"

[tasks.build]
cmd = "make"
depends-on = ["_setup"]
```

## Task arguments

Tasks can accept named arguments with optional defaults:

```toml
[tasks.test]
cmd = "pytest {{ test_path }} -v"
args = [
  { arg = "test_path", default = "tests/" },
]
description = "Run tests on a path"
```

Run with:

```bash
conda task run test src/tests/
```

## Template variables

Commands support Jinja2 templates with `conda.*` context variables:

| Variable | Description |
|---|---|
| `{{ conda.platform }}` | Current platform (e.g., `osx-arm64`) |
| `{{ conda.environment.name }}` | Active environment name |
| `{{ conda.prefix }}` | `CONDA_PREFIX` path |
| `{{ conda.version }}` | conda version |
| `{{ conda.manifest_path }}` | Path to the task file |
| `{{ conda.init_cwd }}` | CWD when `conda task` was invoked |
| `{{ conda.is_win }}` | `True` on Windows |
| `{{ conda.is_unix }}` | `True` on non-Windows |
| `{{ conda.is_linux }}` | `True` on Linux |
| `{{ conda.is_osx }}` | `True` on macOS |

When reading from `pixi.toml`, `{{ pixi.platform }}` etc. also work as aliases.

## Environment variables

```toml
[tasks.test]
cmd = "pytest"
env = { PYTHONPATH = "src", DATABASE_URL = "sqlite:///test.db" }
```

## Clean environment

Run a task with only essential environment variables:

```toml
[tasks]
isolated-test = { cmd = "pytest", clean-env = true }
```

Or via CLI: `conda task run test --clean-env`

## Caching

When `inputs` and `outputs` are specified, conda-tasks caches results
and skips re-execution when inputs haven't changed:

```toml
[tasks.build]
cmd = "python -m build"
inputs = ["src/**/*.py", "pyproject.toml"]
outputs = ["dist/*.whl"]
```

:::{tip}
The cache uses a fast `(mtime, size)` pre-check before falling back to SHA-256
hashing, so the overhead on cache hits is minimal.
:::

## Platform-specific tasks

Override task fields per platform using the `target` key:

::::{tab-set}

:::{tab-item} TOML

```toml
[tasks]
clean = "rm -rf build/"

[target.win-64.tasks]
clean = "rd /s /q build"
```

:::

:::{tab-item} Jinja2 conditional

```toml
[tasks]
clean = "{% if conda.is_win %}rd /s /q build{% else %}rm -rf build/{% endif %}"
```

:::

::::

## Conda environments

Tasks run inside conda environments. The environment is resolved in this order:

1. `-n`/`--name` or `-p`/`--prefix` CLI flag
2. `default-environment` field on the task
3. `environment` in dependency entries
4. Currently active environment (`CONDA_PREFIX`)

```toml
[tasks.test-legacy]
cmd = "pytest"
default-environment = "py38-compat"
```

```bash
conda task run test -n py311-compat
```
