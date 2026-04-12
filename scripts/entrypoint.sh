#!/bin/sh
set -e

echo "Waiting for Redis..."

until redis-cli -h redis ping | grep -q "PONG"; do
    echo "Redis is not ready yet"
    sleep 1
done

echo "Redis is up!"

echo "Running db migrations..."
python manage.py migrate --noinput

echo "Ensuring static/media directories exist and are writable..."
mkdir -p /app/staticfiles /app/media

echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "Compiling translation messages..."
python manage.py compilemessages --noinput || true

echo "Starting application with: $@"
exec "$@"