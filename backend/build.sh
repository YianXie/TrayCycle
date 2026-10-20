#!/usr/bin/env bash

# exit on error
set -o errexit

# install uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# sync dependencies
uv sync

# run migrations and collect static files
uv run python manage.py collectstatic --no-input
uv run python manage.py migrate