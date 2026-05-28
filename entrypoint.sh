#!/bin/bash

set -e

echo "Waiting for PostgreSQL..."
while ! pg_isready -h db -p 5432 -U events_user; do
  sleep 1
done

echo "PostgreSQL is ready!"

echo "Running migrations..."
python manage.py makemigrations
python manage.py migrate

echo "Starting application..."
exec "$@"
