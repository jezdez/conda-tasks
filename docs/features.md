# Features

## Task Commands

A task's `cmd` can be a simple string or a list of strings that are joined with spaces:

```yaml
tasks:
  build:
    cmd: "python -m build"
  build-alt:
    cmd: ["python", "-m", "build", "--wheel"]
```

## Task Aliases

Tasks with no `cmd` that only list dependencies act as aliases:

```yaml
tasks:
  check:
    depends-on: [test, lint, typecheck]
    description: "Run all checks"
```

In TOML formats (`conda-tasks.toml` or `pixi.toml`), this is the shorthand list form:

```toml
[tasks]
check = [{ task = "test" }, { task = "lint" }, { task = "typecheck" }]
```

## Hidden Tasks

Tasks prefixed with `_` are hidden from `conda task list` but can still be
referenced as dependencies or run explicitly:

```yaml
tasks:
  _setup:
    cmd: "mkdir -p build/"
  build:
    cmd: "make"
    depends-on: [_setup]
```

## Task Arguments

Tasks can accept named arguments with optional defaults:

```yaml
tasks:
  test:
    cmd: "pytest {{ test_path }} -v"
    args:
      - arg: test_path
        default: "tests/"
    description: "Run tests on a path"
```

Run with:

```bash
conda task run test src/tests/
```

## Template Variables

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

## Environment Variables

Tasks can set environment variables:

```yaml
tasks:
  test:
    cmd: "pytest"
    env:
      PYTHONPATH: "src"
      DATABASE_URL: "sqlite:///test.db"
```

## Clean Environment

Run a task with only essential environment variables:

```yaml
tasks:
  isolated-test:
    cmd: "pytest"
    clean-env: true
```

Or via CLI: `conda task run test --clean-env`

## Caching

When `inputs` and `outputs` are specified, conda-tasks caches results
and skips re-execution when inputs haven't changed:

```yaml
tasks:
  build:
    cmd: "python -m build"
    inputs: ["src/**/*.py", "pyproject.toml"]
    outputs: ["dist/*.whl"]
```

## Platform-Specific Tasks

Override task fields per platform:

```yaml
tasks:
  clean:
    cmd: "rm -rf build/"
    target:
      win-64:
        cmd: "rd /s /q build"
```

Or use template conditionals:

```yaml
tasks:
  clean:
    cmd: "{% if conda.is_win %}rd /s /q build{% else %}rm -rf build/{% endif %}"
```

## Conda Environments

Tasks run inside conda environments. The environment is resolved in this order:

1. `-n`/`--name` or `-p`/`--prefix` CLI flag
2. `default-environment` field on the task
3. `environment` in dependency entries
4. Currently active environment (`CONDA_PREFIX`)

```yaml
tasks:
  test-legacy:
    cmd: "pytest"
    default-environment: "py38-compat"
```
