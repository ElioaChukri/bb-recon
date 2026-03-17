set shell := ["bash", "-c"]

# Runs the default task (help) if no task is specified
default: help

# Display this help message
help:
    @just --list

# Sync all dependencies and build the project
build:
    uv sync

# Lint the codebase using ruff
lint:
    uv run ruff check --fix