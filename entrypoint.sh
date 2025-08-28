#!/bin/sh
set -e

echo "[entrypoint] Starting Django container"

if [ -n "$DB_HOST" ]; then
	echo "[entrypoint] Waiting for database $DB_HOST:$DB_PORT ..."
	# basic wait loop
	for i in $(seq 1 30); do
		nc -z "$DB_HOST" "${DB_PORT:-3306}" && echo "[entrypoint] Database reachable" && break
		echo "[entrypoint] DB not up yet ($i)"; sleep 2;
	done || true
fi

python manage.py migrate --noinput

if [ "${DJANGO_DEBUG}" = "False" ] || [ "${DJANGO_DEBUG}" = "0" ]; then
	echo "[entrypoint] Collecting static files"
	python manage.py collectstatic --noinput
else
	echo "[entrypoint] Skipping collectstatic in DEBUG mode"
fi

exec "$@"
