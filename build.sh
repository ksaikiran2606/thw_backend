#!/usr/bin/env bash
# Exit on error
set -o errexit

# Install dependencies using Poetry
poetry install --no-dev

# Collect static files
python manage.py collectstatic --no-input

# Apply database migrations
python manage.py migrate