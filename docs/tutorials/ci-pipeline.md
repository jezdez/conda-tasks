# Using conda-tasks in CI

This tutorial shows how to set up conda-tasks in a CI pipeline.
Because conda-tasks separates task running from dependency management,
your CI configuration will have two distinct phases: **environment setup**
and **task execution**.

## The two-phase pattern

Every CI job follows the same structure:

1. **Set up the conda environment** with the tools your tasks need
2. **Run tasks** using `conda task`

This is different from pixi-based CI, where `pixi run` handles both
phases in a single command.

## GitHub Actions

```yaml
name: CI
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    defaults:
      run:
        shell: bash -el {0}
    steps:
      # Phase 1: environment setup
      - uses: actions/checkout@v4
      - uses: conda-incubator/setup-miniconda@v3
        with:
          activate-environment: ci
          environment-file: environment.yml

      # Phase 2: task execution
      - run: conda task run check
```

With an `environment.yml` like:

```yaml
name: ci
channels:
  - conda-forge
dependencies:
  - python=3.12
  - conda-tasks
  - pytest
  - ruff
```

:::{tip}
By putting `conda-tasks` in `environment.yml`, it is available as soon
as the environment is activated. No separate install step needed.
:::

## GitLab CI

```yaml
test:
  image: condaforge/miniforge3:latest
  script:
    # Phase 1
    - conda env create -f environment.yml
    - conda activate ci
    # Phase 2
    - conda task run check
```

## Without environment.yml

If you prefer explicit installs:

```yaml
steps:
  - uses: actions/checkout@v4
  - uses: conda-incubator/setup-miniconda@v3
    with:
      activate-environment: ci

  - name: Install dependencies
    run: conda install -n ci python pytest ruff conda-tasks -y

  - name: Run checks
    run: conda task run check
```

## Multi-environment testing

A common pattern is testing across multiple Python versions. Because
conda-tasks lets you target any environment with `-n`, you can:

```yaml
jobs:
  test:
    strategy:
      matrix:
        python: ["3.10", "3.11", "3.12", "3.13"]
    runs-on: ubuntu-latest
    defaults:
      run:
        shell: bash -el {0}
    steps:
      - uses: actions/checkout@v4
      - uses: conda-incubator/setup-miniconda@v3
        with:
          activate-environment: test
      - run: |
          conda install -n test python=${{ matrix.python }} pytest conda-tasks -y
      - run: conda task run test
```

## Caching in CI

If your tasks use `inputs`/`outputs` caching, the cache directory
(`~/.cache/conda-tasks` on Linux, `~/Library/Caches/conda-tasks` on macOS)
can be preserved between runs:

```yaml
- uses: actions/cache@v4
  with:
    path: ~/.cache/conda-tasks
    key: conda-tasks-${{ hashFiles('src/**/*.py') }}
```

## Key takeaway

The separation between environment setup and task execution is explicit
in CI. This gives you full control over your environment -- you can use
`environment.yml`, `conda lock`, or manual `conda install` -- while
keeping your task definitions clean and reusable.

## Next steps

- {doc}`../configuration` -- all supported file formats
- {doc}`../features` -- full feature reference
