#!/bin/sh
set -e

python - <<'PY'
import os
import time

use_sqlite = os.getenv("DJANGO_USE_SQLITE", "").strip().lower() in {"1", "true", "yes", "on"}

if use_sqlite:
    raise SystemExit(0)

import psycopg

config = {
    "dbname": os.getenv("POSTGRES_DB", "user_management"),
    "user": os.getenv("POSTGRES_USER", "user_management"),
    "password": os.getenv("POSTGRES_PASSWORD", "user_management_password"),
    "host": os.getenv("POSTGRES_HOST", "db"),
    "port": os.getenv("POSTGRES_PORT", "5432"),
}

for attempt in range(1, 31):
    try:
        with psycopg.connect(**config):
            print("Database connection established.")
            break
    except psycopg.OperationalError:
        print(f"Waiting for PostgreSQL... ({attempt}/30)")
        time.sleep(2)
else:
    raise SystemExit("PostgreSQL did not become available in time.")
PY

python manage.py migrate --noinput
python manage.py collectstatic --noinput

exec "$@"

