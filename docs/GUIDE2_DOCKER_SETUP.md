# 🚀 Quick Start Guide

Get your email campaign system up and running in minutes.

---

## Prerequisites

- Docker 20.10+
- Docker Compose 2.0+
- Git

---

## 1. Clone Repository

```bash
git clone <repository-url>
cd campaign
```

---

## 2. Configure Environment

```bash
# Copy environment template
cp .env.example .env.docker

# Edit configuration (get all secrets)
nano .env.docker
```

### Required Settings

```bash
# SendGrid API Key (Get from https://sendgrid.com)
SENDGRID_API_KEY=your-sendgrid-api-key
SENDGRID_FROM_EMAIL=noreply@yourdomain.com

# Database
DB_NAME=campaign_db_docker
DB_USER=postgres
DB_PASSWORD=your-secure-password

# Flower Monitoring
FLOWER_USER=admin
FLOWER_PASSWORD=your-secure-password
```

---

## 3. Start Services

### Understanding Docker Commands

| Scenario | Command | What It Does |
|----------|---------|--------------|
| **First time setup** | `docker-compose up -d --build` | Builds images from Dockerfile, then starts containers |
| **After code changes** | `docker-compose up -d --build` | Rebuilds images with latest code, restarts containers |
| **Regular start** | `docker-compose up -d` | Starts containers (uses existing images) |
| **Force rebuild** | `docker-compose build --no-cache && docker-compose up -d` | Clears cache, rebuilds from scratch |

### Quick Start Command

```bash
# Recommended: Build and start (works for first time and updates)
docker-compose up -d --build

# Check service status
docker-compose ps

# View logs
docker-compose logs -f
```

**💡 Tip:** The `--build` flag ensures Docker builds/rebuilds images before starting. This works even if images don't exist yet (first time users) or need updating (after code changes).

### Expected Output

```
NAME                               STATUS
campaign_db                        Up (healthy)
campaign_redis                     Up (healthy)
campaign_web                       Up
campaign_celery_worker_scheduler   Up
campaign_celery_worker_sender_1    Up
campaign_celery_worker_sender_2    Up
campaign_celery_worker_sender_3    Up
campaign_celery_worker_sender_4    Up
campaign_celery_beat               Up
campaign_flower                    Up
```

---

## 4. Access Application

### Django Admin
- **URL**: http://localhost:8000/admin
- **Username**: `admin`
- **Password**: `admin`

### Flower Monitoring
- **URL**: http://localhost:5555/flower/
- **Username**: `admin` (from .env.docker)
- **Password**: `admin` (from .env.docker)

---

## 5. Create Your First Campaign

### Step 1: Log in to Django Admin
Navigate to http://localhost:8000/admin and log in.

### Step 2: Create Campaign
1. Click **Campaigns** → **Add Campaign**
2. Fill in the form:
   - **Name**: "Welcome Email"
   - **Subject**: "Welcome to Our Platform!"
   - **Content**: Use HTML email template (see [Campaign Examples Guide](CAMPAIGN_EXAMPLES_GUIDE.md))
   - **Scheduled At**: Select future date/time

3. Click **Save**

### Step 3: Upload Recipients
1. Click **Import Recipients** button
2. Upload CSV file with columns: `email,first_name,last_name`
3. Click **Import**

Example CSV:
```csv
email,first_name,last_name
john@example.com,John,Doe
jane@example.com,Jane,Smith
```

### Step 4: Monitor Execution
1. Campaign will execute automatically at scheduled time
2. Monitor in **Flower**: http://localhost:5555/flower/
3. View delivery status in **Django Admin** → **Delivery Logs**

---

## 6. Verify Setup

### Check Workers in Flower
1. Go to http://localhost:5555/flower/
2. Click **Workers** tab
3. Verify 5 workers are active:
   - 1 scheduler worker
   - 4 sender workers

### Check Campaign Status
1. Go to Django Admin → **Campaigns**
2. Check delivery summary (color-coded):
   - 🟢 Green: > 95% delivered
   - 🟡 Yellow: 80-95% delivered
   - 🔴 Red: < 80% delivered

---


## Useful Commands

### First Time Setup or After Code Changes
```bash
# Build images and start services
docker-compose up -d --build

# Or build separately then start
docker-compose build
docker-compose up -d
```

### Regular Operations
```bash
# Start services (images already built)
docker-compose up -d

# Start with logs visible
docker-compose up

# Stop all services
docker-compose down

# Restart services
docker-compose restart
```

### Debugging & Logs
```bash
# View all logs
docker-compose logs -f

# View specific service logs
docker-compose logs -f web

# Check service status
docker-compose ps

# Check all containers (including stopped)
docker-compose ps -a
```

### Clean Up & Fresh Start
```bash
# Stop and remove containers (keeps volumes/data)
docker-compose down

# Stop and remove volumes (fresh database)
docker-compose down -v

# Remove old images and rebuild everything
docker-compose down --rmi local
docker-compose build --no-cache
docker-compose up -d
```

### Scaling & Performance
```bash
# Scale sender workers (more email throughput)
docker-compose up -d --scale celery_worker_sender_1=2

# Wait for services to initialize
sleep 10 && docker-compose ps
```

### Database Operations
```bash
# Execute Django commands
docker-compose exec web python manage.py shell
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py createsuperuser

# Database backup
docker-compose exec db pg_dump -U postgres campaign_db_docker > backup.sql

# Database restore
docker-compose exec -T db psql -U postgres campaign_db_docker < backup.sql
```

---

