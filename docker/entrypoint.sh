#!/bin/sh
set -e

DB_PATH="${DJANGO_DB_PATH:-/app/db.sqlite3}"
mkdir -p "$(dirname "$DB_PATH")"

python manage.py migrate --noinput
python manage.py collectstatic --noinput

exec "$@"
