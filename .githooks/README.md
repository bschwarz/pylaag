# Git Hooks

This directory contains git hooks for the pylaag project.

## Pre-commit Hook

The pre-commit hook runs the following checks before each commit:

1. **Ruff Check** (`uv run ruff check --fix`) - Lints the code and auto-fixes issues
2. **Ruff Format** (`uv run ruff format`) - Formats the code
3. **Pytest** (`uv run pytest`) - Runs all tests

If any of these checks fail, the commit will be aborted.

## Installation

### Option 1: Copy the hook (recommended for individual setup)

```bash
cp .githooks/pre-commit .git/hooks/pre-commit
chmod +x .git/hooks/pre-commit
```

### Option 2: Configure git to use this hooks directory (recommended for team)

```bash
git config core.hooksPath .githooks
```

This will make git use all hooks in the `.githooks` directory automatically.

## Bypassing the Hook

If you need to bypass the pre-commit hook (not recommended), you can use:

```bash
git commit --no-verify
```

## Customization

To modify the pre-commit checks, edit `.githooks/pre-commit` and reinstall the hook.
