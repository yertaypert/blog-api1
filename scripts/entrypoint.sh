#!/bin/sh
set -e

echo "Waiting for Redis..."

while ! redis-cli -h redis ping | grep -q "PONG"; do
    echo "Redis is not ready yet"
    sleep 1
done

echo "Redis is up!"

echo "Running db migrations..."
python manage.py migrate

echo "Collecting static files..."
python manage.py collectstatic

echo "Compiling translation messages..."
python manage.py compilemessages

echo "Starting application with: $@"
exec "$@"