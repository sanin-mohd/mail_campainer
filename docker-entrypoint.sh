#!/bin/bash

# Exit on error
set -e

# Detect if this is Flower based on the command
if [[ "$*" == *"flower"* ]]; then
    echo "🌸 Starting Flower Monitoring..."
    
    # Wait for Redis to be ready
    echo "⏳ Waiting for Redis..."
    while ! nc -z ${REDIS_HOST:-redis} 6379; do
      sleep 0.1
    done
    echo "✅ Redis is ready!"
    
    echo "✅ Setup complete!"
    echo "🎉 Starting Flower..."
    
    # Execute the main command
    exec "$@"
fi

# For web/celery services
echo "🚀 Starting Campaign Mailer Application..."

# Wait for PostgreSQL to be ready
echo "⏳ Waiting for PostgreSQL..."
while ! nc -z ${DB_HOST:-db} ${DB_PORT:-5432}; do
  sleep 0.1
done
echo "✅ PostgreSQL is ready!"

# Wait for Redis to be ready
echo "⏳ Waiting for Redis..."
while ! nc -z ${REDIS_HOST:-redis} 6379; do
  sleep 0.1
done
echo "✅ Redis is ready!"

# Only run migrations for web service (not for celery workers)
if [[ "$*" == *"runserver"* ]] || [[ "$*" == *"gunicorn"* ]]; then
    # Create database if it doesn't exist
    echo "🗄️  Checking database..."
    PGPASSWORD=${DB_PASSWORD} psql -h ${DB_HOST:-db} -U ${DB_USER:-postgres} -d postgres -tc "SELECT 1 FROM pg_database WHERE datname = '${DB_NAME:-campaign_db}'" | grep -q 1 || {
        echo "📦 Database '${DB_NAME:-campaign_db}' does not exist. Creating..."
        PGPASSWORD=${DB_PASSWORD} psql -h ${DB_HOST:-db} -U ${DB_USER:-postgres} -d postgres -c "CREATE DATABASE ${DB_NAME:-campaign_db};"
        echo "✅ Database created successfully!"
    }
    echo "✅ Database exists!"

    # Run database migrations
    echo "📦 Running database migrations..."
    python manage.py migrate --noinput

    # Create superuser if it doesn't exist
    echo "👤 Creating superuser (if not exists)..."
    python manage.py shell << END
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@gmail.com', 'admin')
    print('✅ Superuser created: username=admin, password=admin')
else:
    print('ℹ️  Superuser already exists')
END

    # Collect static files
    echo "📁 Collecting static files..."
    python manage.py collectstatic --noinput || true
fi

echo "✅ Setup complete!"
echo "🎉 Starting application..."

# Execute the main command
exec "$@"
