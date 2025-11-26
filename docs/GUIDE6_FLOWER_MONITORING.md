# Flower Monitoring Guide

Complete guide to monitoring your email campaign system using Flower (Celery monitoring tool).

## Table of Contents
- [Quick Start](#quick-start)
- [Accessing Flower](#accessing-flower)
- [Dashboard Overview](#dashboard-overview)
- [Monitoring Tasks](#monitoring-tasks)

---

## Quick Start

### 1. Start Flower with Docker

**Development:**
```bash
docker-compose up -d flower
```

**Production:**
```bash
docker-compose -f docker-compose.prod.yml up -d flower
```

### 2. Access Flower UI

**Local Development:**
```
http://localhost:5555
```

**With Nginx (Production):**
```
https://yourdomain.com/flower
```

**Default Credentials:**
- Username: `admin` (or from FLOWER_USER env var)
- Password: `admin` (or from FLOWER_PASSWORD env var)

⚠️ **Security Warning:** Change default credentials in production!

---

## Accessing Flower

### Authentication Setup

1. **Set credentials in .env:**
```bash
FLOWER_USER=your_username
FLOWER_PASSWORD=your_secure_password
```

2. **Restart Flower service:**
```bash
docker-compose restart flower
```


## Dashboard Overview

### Main Dashboard Sections

#### 1. **Workers Overview** (Top Section)
```
┌────────────────────────────────────────┐
│  Workers: 2 active                     │
│  Tasks: 1,234 completed, 5 active      │
│  Queues: default, email_senders        │
└────────────────────────────────────────┘
```

**What to Monitor:**
- ✅ Active workers count (should match replicas)
- ✅ Task completion rate
- ✅ Queue backlogs

#### 2. **Task Types** (Middle Section)
Shows all registered tasks:
- `campaigns.tasks.check_scheduled_campaigns`
- `campaigns.tasks.send_batch`
- `campaigns.tasks.finalize_campaign`

**Key Metrics:**
- **Success rate:** Should be > 95%
- **Average runtime:** `send_batch` should be < 10s
- **Failure count:** Investigate if > 1%

#### 3. **Recent Tasks** (Bottom Section)
Real-time task execution stream

**Columns:**
- **Name:** Task function name
- **UUID:** Unique task identifier
- **State:** SUCCESS, FAILURE, PENDING, STARTED, RETRY
- **Received:** Timestamp when queued
- **Started:** Timestamp when execution began
- **Runtime:** Execution duration
- **Args:** Task arguments (batch details)

---
