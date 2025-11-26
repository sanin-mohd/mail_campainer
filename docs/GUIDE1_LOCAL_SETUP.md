# Quick Setup Guide for Bulk Upload Feature

## Prerequisites Installation

Run the following command to install required packages:

```bash
pip install -r requirements.txt
```

## Configuration Steps

### 1. Environment Variables
Create a `.env` file in your project root and get secrets for `.env.example`

### 2. Database Setup

Make sure PostgreSQL is running, then:

```bash
# Create the database
createdb campaign_db

# Or using psql
psql -U postgres -c "CREATE DATABASE campaign_db;"
```

### 3. Run Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### 4. Create Superuser

```bash
python manage.py createsuperuser
```

### 5. Start the Server

```bash
python manage.py runserver
```

### 6. Access Admin

Go to: http://localhost:8000/admin

## Testing the Bulk Upload

1. Login to Django Admin
2. Go to **Campaigns → Recipients**
3. Click **"Bulk Upload Recipients"** button
4. Upload the provided `sample_recipients.csv` file
5. See the import statistics

## Verification

After setup, verify everything is working:

```bash
# Test database connection
python manage.py dbshell
\dt  # List tables
\q   # Quit

# Check for any migrations
python manage.py showmigrations
```

## Troubleshooting

### Issue: "Redis connection error"
Make sure Redis is running:
```bash
redis-cli ping
# Should return: PONG
```

### Issue: Database connection error
Check PostgreSQL is running:
```bash
psql -U postgres -l
```

## Next Steps

1. ✅ Install dependencies
2. ✅ Configure environment variables
3. ✅ Create database
4. ✅ Run migrations
5. ✅ Create superuser
6. ✅ Test bulk upload with sample file
7. ✅ Create your own CSV/Excel file
8. ✅ Start importing recipients!

Enjoy your high-performance bulk recipient import system! 🚀
