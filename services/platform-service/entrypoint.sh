#!/bin/bash

# Wait for database to be ready (optional but good practice)
# For now, we rely on depends_on in docker-compose

echo "Applying database migrations..."
python manage.py makemigrations
python manage.py migrate

echo "Starting server..."
exec "$@"
