#!/bin/sh
set -e

echo "Running database migrations..."
/app/.venv/bin/alembic upgrade head

echo "Seeding dev admin account..."
/app/.venv/bin/python scripts/seed_admin.py

echo "Starting server..."
exec "$@"
