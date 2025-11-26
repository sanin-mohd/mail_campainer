# 📧 High-Performance Email Campaign Management System

A production-ready, scalable email campaign management system built with Django, Celery, and Redis. Designed to handle bulk email campaigns with support for 200,000+ recipients per campaign.

![Django](https://img.shields.io/badge/Django-5.2.8-green.svg)
![Celery](https://img.shields.io/badge/Celery-5.5.3-blue.svg)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-blue.svg)
![Redis](https://img.shields.io/badge/Redis-7-red.svg)
![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)

---

## 📋 Table of Contents

- [Features](#-features)
- [Architecture](#-architecture)
- [Technology Stack](#-technology-stack)
- [System Architecture Diagram](#-system-architecture-diagram)
- [Scalability & Performance](#-scalability--performance)
- [Quick Start](#-quick-start)
- [Environment Setup](#-environment-setup)
- [Docker Deployment](#-docker-deployment)
- [Project Structure](#-project-structure)
- [API Endpoints](#-api-endpoints)
- [Monitoring](#-monitoring)
- [Configuration](#-configuration)
- [Production Deployment](#-production-deployment)
- [Troubleshooting](#-troubleshooting)

---

## ✨ Features

### Core Functionality
- 📨 **Bulk Email Campaigns**: Send emails to 200,000+ recipients
- 👥 **Recipient Management**: Import recipients via CSV/Excel with validation
- 📊 **Campaign Scheduling**: Schedule campaigns with timezone support (Asia/Kolkata)
- 📈 **Delivery Tracking**: Real-time delivery status monitoring
- 🎨 **HTML Email Templates**: Rich HTML email support with inline CSS
- 🔄 **Campaign Status Management**: Draft, Scheduled, In Progress, Completed, Failed states

### Email Provider Integration
- ✅ **SendGrid** (Primary) - 600 emails/second on Pro plan
- ✅ **Gmail SMTP** (Fallback) - For testing (500 emails/day limit)
- 🔄 **Automatic Retry**: Failed email retry with exponential backoff
- ⚡ **Rate Limiting**: Configurable rate limits per provider

### Performance & Scalability
- 🚀 **Batch Processing**: 200 emails per batch (configurable)
- ⚙️ **Parallel Workers**: 4 sender workers + 1 scheduler worker
- 🔄 **Celery Task Queue**: Distributed task processing
- 📊 **Concurrency Control**: 10 concurrent email sending tasks
- 💾 **Redis Caching**: Session and result caching
- 🔒 **Idempotency**: Prevents duplicate campaign execution

### Monitoring & Observability
- 🌸 **Flower Dashboard**: Real-time Celery task monitoring
- 📊 **Admin Dashboard**: Campaign statistics and delivery summary
- 📝 **Comprehensive Logging**: Django, Celery, and Nginx logs
- 🎯 **Health Checks**: Container health monitoring


---

## 🏗️ Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         Client Layer                             │
│                   (Web Browser / API Client)                     │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ↓
┌─────────────────────────────────────────────────────────────────┐
│                    Nginx Reverse Proxy                           │
│  • Static File Serving    • Gzip Compression                    │
│  • Rate Limiting          • Security Headers                    │
│  • SSL Termination        • Load Balancing                      │
└──────────┬──────────────────────────────────┬───────────────────┘
           │                                  │
           ↓                                  ↓
┌──────────────────────┐         ┌──────────────────────┐
│   Django Web App     │         │  Flower Monitoring   │
│   (Gunicorn WSGI)    │         │   (Port 5555)        │
│   • Admin Interface  │         │   • Worker Status    │
│   • Campaign CRUD    │         │   • Task Monitoring  │
│   • Recipient Import │         │   • Real-time Metrics│
└──────────┬───────────┘         └──────────────────────┘
           │
           ↓
┌─────────────────────────────────────────────────────────────────┐
│                      PostgreSQL Database                         │
│  • Campaign Data      • Delivery Logs                           │
│  • Recipients         • User Management                          │
└─────────────────────────────────────────────────────────────────┘
           │
           ↓
┌─────────────────────────────────────────────────────────────────┐
│                      Redis Cache & Broker                        │
│  • Celery Message Broker    • Session Cache                     │
│  • Result Backend           • Rate Limit Counter                │
└──────────┬──────────────────────────────────────────────────────┘
           │
           ↓
┌─────────────────────────────────────────────────────────────────┐
│                      Celery Workers                              │
│                                                                  │
│  ┌─────────────────────┐     ┌──────────────────────────────┐  │
│  │  Scheduler Worker   │     │    Sender Workers (×4)       │  │
│  │  • Concurrency: 2   │     │    • Concurrency: 2 each     │  │
│  │  • Queue: scheduler │     │    • Queue: senders          │  │
│  │  • Task: Check      │     │    • Task: Send Batches      │  │
│  │    Scheduled        │     │    • Task: Finalize          │  │
│  │    Campaigns        │     │      Campaigns               │  │
│  └─────────────────────┘     └──────────────────────────────┘  │
│                                                                  │
│  ┌─────────────────────┐                                        │
│  │   Celery Beat       │                                        │
│  │  • Periodic Tasks   │                                        │
│  │  • Runs every 1 min │                                        │
│  └─────────────────────┘                                        │
└──────────┬───────────────────────────────────────────────────────┘
           │
           ↓
┌─────────────────────────────────────────────────────────────────┐
│                    Email Service Providers                       │
│  • SendGrid API (Primary)    • Gmail SMTP (Fallback)           │
│  • 600 emails/sec capacity    • 500 emails/day (testing)       │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🛠️ Technology Stack

### Backend
- **Django 5.2.8** - Web framework
- **Django Admin** - Campaign management interface
- **Django ORM** - Database abstraction
- **Python 3.11** - Programming language

### Task Queue & Processing
- **Celery 5.5.3** - Distributed task queue
- **Redis 7** - Message broker & result backend
- **Celery Beat** - Periodic task scheduler
- **Flower 2.0.1** - Celery monitoring tool

### Database & Cache
- **PostgreSQL 15** - Primary database
- **Redis** - Session cache & Celery broker
- **django-redis 6.0.0** - Django Redis integration

### Email Delivery
- **SendGrid** - Primary email service (600/sec)
- **Gmail SMTP** - Fallback service (testing)
- **python-http-client 3.3.7** - SendGrid client

### Data Processing
- **pandas 2.3.3** - CSV/Excel processing
- **openpyxl 3.1.5** - Excel file handling
- **numpy 2.3.5** - Numerical operations

### Production Server
- **Gunicorn 23.0.0** - WSGI HTTP server
- **Nginx** - Reverse proxy & static file server
- **Docker & Docker Compose** - Containerization

---

## 📊 System Architecture Diagram

### Campaign Processing Flow

```
┌────────────────────────────────────────────────────────────────┐
│                     Campaign Creation Flow                      │
└────────────────────────────────────────────────────────────────┘

1. Admin Creates Campaign
   ↓
2. Upload Recipients (CSV/Excel)
   ↓
3. Validation & Import
   │
   ├─ Duplicate Check
   ├─ Email Format Validation
   └─ Batch Insert (PostgreSQL COPY ~2M rows/sec)
   ↓
4. Schedule Campaign
   ↓
5. Campaign Status: SCHEDULED

┌────────────────────────────────────────────────────────────────┐
│                    Campaign Execution Flow                      │
└────────────────────────────────────────────────────────────────┘

1. Celery Beat (Every 1 minute)
   ↓
2. check_scheduled_campaigns()
   │
   ├─ Query scheduled campaigns (scheduled_at <= now)
   ├─ Idempotency check (prevent duplicate execution)
   └─ Change status: SCHEDULED → IN_PROGRESS
   ↓
3. start_campaign_send()
   │
   ├─ Calculate total batches (recipients / batch_size)
   ├─ Create DeliveryLog entries
   └─ Queue send_batch tasks → Senders Queue
   ↓
4. send_batch() × 4 Workers (Parallel)
   │
   ├─ Fetch batch recipients (200 per batch)
   ├─ Send via SendGrid API
   │   │
   │   ├─ Success → Update DeliveryLog (status: sent)
   │   └─ Failure → Retry (max 3 attempts)
   │
   └─ On last batch → Queue finalize_campaign()
   ↓
5. finalize_campaign()
   │
   ├─ Aggregate delivery stats
   ├─ Calculate success rate
   ├─ Change status: IN_PROGRESS → COMPLETED
   └─ Send completion report (optional)

┌────────────────────────────────────────────────────────────────┐
│                      Monitoring Flow                            │
└────────────────────────────────────────────────────────────────┘

Flower Dashboard
├─ View Workers (5 total: 1 scheduler + 4 senders)
├─ Monitor Tasks (SUCCESS, FAILURE, RETRY states)
├─ Track Performance (throughput, success rate)
└─ Real-time Metrics (queue length, active tasks)

Django Admin
├─ Campaign Statistics
├─ Delivery Summary (color-coded)
│   ├─ Green: > 95% delivered
│   ├─ Yellow: 80-95% delivered
│   └─ Red: < 80% delivered
└─ DeliveryLog Details
```

---

## 🚀 Scalability & Performance

### Current Capacity

| Metric | Value | Configuration |
|--------|-------|---------------|
| **Concurrent Email Sending** | 8 tasks | 4 workers × 2 concurrency |
| **Scheduler Tasks** | 2 tasks | 1 worker × 2 concurrency |
| **Total Concurrency** | 10 tasks | 5 workers, 10 total slots |
| **Batch Size** | 200 emails | Configurable via `CAMPAIGN_BATCH_SIZE` |
| **SendGrid Rate** | 600/sec | Pro plan limit |
| **Effective Rate** | 400/sec | 2 workers × 200 emails/batch |
| **200k Campaign Duration** | ~8-10 hours | With 2 sender workers |

### Performance Benchmarks

#### Email Sending Throughput

#### Scaled Flow (4 Workers, concurrency 2):
```
Campaign (200k emails)
    ↓
start_campaign_send() → Creates 1000 tasks
    ↓
4 Workers process tasks in parallel
    ↓
Rate: 2 × 4 × 200 = 1600 emails/second (but limited by SendGrid's 600/s)
Time: 200,000 ÷ 1600 = ~125 seconds = ~2 minutes ⚡
```

```

#### Recipient Import Performance
```
Method: PostgreSQL COPY with multiprocessing
File Size        | Recipients    | Import Time
-----------------|---------------|-------------
5 MB CSV         | ~100,000        | 2-3 seconds
3 MB xlsx        | ~100,000       | 3-5 seconds
```

### Scaling Strategies

#### 1. **Horizontal Scaling** (Recommended)

**Add More Sender Workers:**
```bash
# Development
docker-compose up -d --scale celery_worker_sender=8

# Production (edit docker-compose.prod.yml)
# Add more sender worker services (sender_5, sender_6, etc.)
```

**Result:**
- 8 workers × 2 concurrency = 16 concurrent tasks
- 200k emails in ~4-5 hours (2x faster)

#### 2. **Vertical Scaling**

**Increase Worker Concurrency:**
```yaml
# docker-compose.yml
celery_worker_sender_1:
  command: celery -A mailer_project worker -Q senders -l info -c 4  # Changed from 2
```

**Result:**
- 4 workers × 4 concurrency = 16 concurrent tasks
- Requires more CPU/RAM per container

#### 3. **Batch Size Optimization**

**Increase Batch Size:**
```bash
# .env.docker
CAMPAIGN_BATCH_SIZE=500  # Changed from 200
```

**Trade-offs:**
- ✅ Fewer database queries
- ✅ Better throughput
- ⚠️ Higher memory usage per task
- ⚠️ Longer task duration

#### 4. **SendGrid Upgrade**

| Plan | Rate Limit | Monthly Emails | Cost |
|------|------------|----------------|------|
| **Essentials** | 200/sec | 100k | $19.95/mo |
| **Pro** | 600/sec | Unlimited | $89.95/mo |
| **Premier** | 1000/sec | Unlimited | Custom |

Upgrade to Premier → 1000/sec → 200k emails in ~3-4 hours

### Load Balancing

**Multi-Instance Django:**
```yaml
# docker-compose.prod.yml
services:
  web_1:
    # Django instance 1
  web_2:
    # Django instance 2
  
  nginx:
    # Load balance between web_1 and web_2
```

**Nginx Configuration:**
```nginx
upstream django {
    server web_1:8000;
    server web_2:8000;
}
```

### Database Optimization

**Connection Pooling:**
```python
# settings.py
DATABASES = {
    'default': {
        'CONN_MAX_AGE': 600,  # 10 minutes
        'OPTIONS': {
            'connect_timeout': 10,
        }
    }
}
```

**Indexing:**
- Campaign: `status`, `scheduled_at`
- Recipient: `campaign_id`, `email`
- DeliveryLog: `campaign_id`, `status`

### Monitoring & Auto-Scaling

**Resource Monitoring:**
```bash
# Check container resources
docker stats

# Check worker utilization
curl -u admin:admin http://localhost:5555/api/workers
```

**Auto-scaling triggers:**
- CPU usage > 70%
- Queue length > 1000 tasks
- Average task duration > 30 seconds

---

## 🚀 Quick Start

### Prerequisites

- Docker 20.10+
- Docker Compose 2.0+
- Git

### 1. Clone Repository

```bash
git clone <repository-url>
cd campaign
```

### 2. Configure Environment

```bash
# Copy environment template
cp .env.example .env.docker

# Edit configuration
nano .env.docker
```

**Required Settings:**
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

### 3. Start Services

```bash
# Build and start all services
docker-compose up -d

# Check service status
docker-compose ps

# View logs
docker-compose logs -f
```

### 4. Access Application

- **Django Admin**: http://localhost:8000/admin
  - Username: `admin`
  - Password: `admin`

- **Flower Monitoring**: http://localhost:5555/flower/
  - Username: `admin` (from .env.docker)
  - Password: `admin` (from .env.docker)

### 5. Create Your First Campaign

1. Log in to Django Admin
2. Navigate to **Campaigns**
3. Click **Add Campaign**
4. Fill in:
   - Name: "Welcome Email"
   - Subject: "Welcome to Our Platform!"
   - Content: (HTML email template)
   - Scheduled At: (future datetime)
5. Click **Save**
6. Upload recipients via **Import Recipients**
7. Campaign will execute automatically at scheduled time

---

## 🌍 Environment Setup

### Development Setup (Local)

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
nano .env  # Update with your settings

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Start Redis (required)
redis-server

# Start Celery worker
celery -A mailer_project worker -l info

# Start Celery beat
celery -A mailer_project beat -l info

# Run development server
python manage.py runserver
```

### Docker Setup (Recommended)

See [Quick Start](#-quick-start) above.

---

## 🐳 Docker Deployment

### Service Architecture

```yaml
Services:
├── db (PostgreSQL 15)
├── redis (Redis 7)
├── web (Django + Gunicorn)
├── celery_worker_scheduler (1 worker, concurrency 2)
├── celery_worker_sender_1 (concurrency 2)
├── celery_worker_sender_2 (concurrency 2)
├── celery_worker_sender_3 (concurrency 2)
├── celery_worker_sender_4 (concurrency 2)
├── celery_beat (Periodic scheduler)
└── flower (Monitoring dashboard)
```

### Docker Commands

```bash
# Build images
docker-compose build

# Start services
docker-compose up -d

# Stop services
docker-compose down

# View logs
docker-compose logs -f [service_name]

# Restart specific service
docker-compose restart web

# Scale workers
docker-compose up -d --scale celery_worker_sender_1=2

# Execute commands in container
docker-compose exec web python manage.py shell

# Database backup
docker-compose exec db pg_dump -U postgres campaign_db_docker > backup.sql
```

### Production Deployment

```bash
# Use production configuration
docker-compose -f docker-compose.prod.yml up -d

# View production logs
docker-compose -f docker-compose.prod.yml logs -f

# Scale production workers
docker-compose -f docker-compose.prod.yml up -d --scale celery_worker_sender_1=4
```

---

## 📁 Project Structure

## File Structure

```
campaign/
├── campaigns/
│   ├── migrations/
│   │   └── __init__.py
│   ├── templates/
│   │   └── admin/
│   │       └── campaigns/
│   │           └── recipient/
│   │               ├── bulk_upload.html
│   │               └── change_list.html
│   ├── __pycache__/
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── forms.py
│   ├── importer_v1.py
│   ├── importer_v2.py
│   ├── models.py
│   ├── providers.py
│   ├── tasks.py
│   ├── tests.py (14 unit tests)
│   ├── test_runner.py (celebration on success)
│   ├── utils.py
│   └── views.py
├── mailer_project/
│   ├── __pycache__/
│   ├── __init__.py
│   ├── asgi.py
│   ├── celery.py
│   ├── settings.py (logging + TEST_RUNNER config)
│   ├── urls.py
│   └── wsgi.py
├── email_templates/
│   ├── welcome_email.html
│   ├── newsletter.html
│   ├── promotional.html
│   ├── event_invitation.html
│   └── product_update.html
├── logs/
│   ├── django.log
│   ├── celery.log
│   ├── email.log
│   └── error.log
├── docs/
│   ├── GUIDE1_LOCAL_SETUP.md
│   ├── GUIDE2_DOCKER_SETUP.md
│   ├── GUIDE3_BULK_UPLOAD.md
│   ├── GUIDE4_EMAIL_TEST_SCRIPTS.md
│   ├── GUIDE5_CAMPAIGN_EXAMPLES.md
│   ├── GUIDE6_FLOWER_MONITORING.md
│   
├── staticfiles/
├── venv/
├── .dockerignore
├── .env
├── .env.docker
├── .env.example
├── .env.production
├── .gitignore
├── celerybeat-schedule
├── celerybeat-schedule.db
├── docker-compose.yml
├── docker-compose.prod.yml
├── docker-entrypoint.sh
├── Dockerfile
├── manage.py
├── nginx.conf
├── README.md
├── requirements.txt
├── sample_recipients.csv
├── sample_recipients_100k.csv
├── sample_recipients_100k.xlsx
├── test_gmail.py
└── test_sendgrid.py
```


---

## 🔌 API Endpoints

### Django Admin (Web UI)

```
/admin/                             # Admin dashboard
/admin/campaigns/campaign/          # Campaign management
/admin/campaigns/recipient/         # Recipient management
/admin/campaigns/deliverylog/       # Delivery logs
/admin/import-recipients/           # CSV/Excel import
```

### Flower Monitoring

```
/flower/                            # Flower dashboard
/flower/workers                     # Worker status
/flower/tasks                       # Task monitoring
/flower/api/workers                 # Workers API
/flower/api/tasks                   # Tasks API
```

---

## 📊 Monitoring

### Flower Dashboard

Access at `http://localhost:5555/flower/`

**Key Metrics:**
- **Workers**: View all 5 workers (1 scheduler + 4 senders)
- **Tasks**: Real-time task execution status
- **Success Rate**: Percentage of successful email deliveries
- **Throughput**: Tasks completed per minute
- **Queue Length**: Pending tasks in Redis

### Django Admin

**Campaign Statistics:**
- Total recipients
- Emails sent
- Success rate
- Failed deliveries
- Campaign duration

**Delivery Summary** (Color-coded):
- 🟢 Green: > 95% delivered
- 🟡 Yellow: 80-95% delivered
- 🔴 Red: < 80% delivered

### Logs

```bash
# Django logs
docker-compose logs web

# Celery worker logs
docker-compose logs celery_worker_sender_1

# Celery beat logs
docker-compose logs celery_beat

# Flower logs
docker-compose logs flower

# All logs
docker-compose logs -f
```

---

## ⚙️ Configuration

### Key Settings

#### Email Provider

```bash
# .env.docker

# SendGrid (Primary)
SENDGRID_API_KEY=SG.xxx
SENDGRID_FROM_EMAIL=noreply@yourdomain.com
SENDGRID_RATE_LIMIT_PER_SEC=100

# Gmail (Fallback - Testing Only)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
```

#### Celery Configuration

```bash
CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/1
CELERY_WORKER_PREFETCH_MULTIPLIER=1
CAMPAIGN_BATCH_SIZE=200
```

#### Database

```bash
DB_NAME=campaign_db_docker
DB_USER=postgres
DB_PASSWORD=your-password
DB_HOST=db
DB_PORT=5432
```

### Rate Limiting

**SendGrid:**
```python
# campaigns/tasks.py
@shared_task(rate_limit="1/s")  # 200 emails per second per worker
def send_batch(campaign_id, batch_number, total_batches):
    # ...
```

**Nginx:**
```nginx
# nginx.conf
limit_req_zone $binary_remote_addr zone=api:10m rate=100r/s;
limit_req_zone $binary_remote_addr zone=admin:10m rate=10r/s;
```

---

## 🌐 Production Deployment

### 1. Update Configuration

```bash
# .env (production)
DEBUG=False
SECRET_KEY=<generate-strong-secret-key>
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com

DB_PASSWORD=<strong-password>
REDIS_PASSWORD=<strong-password>
FLOWER_PASSWORD=<strong-password>

SENDGRID_API_KEY=<production-api-key>
```

### 2. Update Nginx

```nginx
# nginx.conf
server_name yourdomain.com www.yourdomain.com;

# Add SSL
listen 443 ssl http2;
ssl_certificate /etc/nginx/ssl/cert.pem;
ssl_certificate_key /etc/nginx/ssl/key.pem;
```

### 3. Deploy

```bash
# Build production images
docker-compose -f docker-compose.prod.yml build

# Start production services
docker-compose -f docker-compose.prod.yml up -d

# Collect static files
docker-compose -f docker-compose.prod.yml exec web python manage.py collectstatic --noinput

# Run migrations
docker-compose -f docker-compose.prod.yml exec web python manage.py migrate

# Create superuser
docker-compose -f docker-compose.prod.yml exec web python manage.py createsuperuser
```

---


### Health Checks

```bash
# Check all services
docker-compose ps

# Check worker status
curl -u admin:admin http://localhost:5555/api/workers

# Check database connection
docker-compose exec web python manage.py dbshell

# Check Redis connection
docker-compose exec redis redis-cli ping
```

# HOW TO RUN TESTS
```bash


# Run all tests:
   docker-compose exec web python manage.py test campaigns
#
# Run with verbose output:
   docker-compose exec web python manage.py test campaigns --verbosity=2
#
# Run specific test class:
   docker-compose exec web python manage.py test campaigns.tests.Test1_ScheduledCampaignDetection
#
# Run specific test method:
   docker-compose exec web python manage.py test campaigns.tests.Test1_ScheduledCampaignDetection.test_scheduled_campaign_is_started
#
``````

---

## 📚 Additional Documentation - visit docs/**

---

## 🤝 Contributing

Contributions are welcome! Please follow these guidelines:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---


**Built with ❤️ using Django, Celery, and Docker**
