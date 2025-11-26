import csv
import os
import logging
from io import StringIO

from celery import shared_task, Task
from django.db import transaction
from django.conf import settings
from django.core.mail import EmailMessage

from .models import Campaign, Recipient, DeliveryLog
from .providers import get_rate_limit_for_provider, send_email_to_recipient

logger = logging.getLogger(__name__)

BATCH_SIZE = int(os.getenv("CAMPAIGN_BATCH_SIZE", 200))
LOG_BATCH = 500  # delivery log bulk size

class BaseTaskWithRetry(Task):
    autoretry_for = (Exception,)
    max_retries = 3
    default_retry_delay = 10  # seconds
    retry_backoff = True

@shared_task(name="campaigns.tasks.check_scheduled_campaigns", bind=True)
def check_scheduled_campaigns(self):
    """
    Run every minute (via beat). Find campaigns scheduled to run, and kick off send.
    Marks campaign status -> IN_PROGRESS and calls start_campaign_send.delay(...)
    """
    logger.info("Checking for scheduled campaigns to start...")
    from django.utils import timezone as django_timezone
    now = django_timezone.now()  # Use Django timezone-aware now (respects USE_TZ and TIME_ZONE)
    campaigns = Campaign.objects.filter(status=Campaign.SCHEDULED, scheduled_time__lte=now)
    for c in campaigns:
        # idempotency: mark as IN_PROGRESS inside transaction if still SCHEDULED
        with transaction.atomic():
            refreshed = Campaign.objects.select_for_update().get(pk=c.pk)

            if refreshed.status != Campaign.SCHEDULED:
                # Scenario: Two Celery beat schedulers running simultaneously (avoid double start_campaign_send)
                continue
            refreshed.status = Campaign.IN_PROGRESS
            refreshed.save(update_fields=["status"])
        # spawn starter task
        start_campaign_send.delay(refreshed.pk)
    logger.info(f"Found and started {campaigns.count()} scheduled campaigns.")

@shared_task(name="campaigns.tasks.start_campaign_send")
def start_campaign_send(campaign_id: int):
    """
    Break recipients into batches and enqueue send_batch tasks.
    Uses chunked DB querying to avoid loading all recipients at once.
    """
    logger.info(f"Starting campaign send for Campaign ID: {campaign_id}")
    # frequently-used recipient queryset (attached filtering here)
    recipients_qs = Recipient.objects.filter(subscription_status="subscribed").order_by("id")
    total = recipients_qs.count()
    if total == 0:
        # nothing to do: finalize immediately
        finalize_campaign.delay(campaign_id)
        return

    # chunk by id ranges for memory-efficiency
    # fetch ids in pages to avoid large offsets
    page_size = BATCH_SIZE
    offset = 0
    while offset < total:
        ids = list(recipients_qs.values_list("id", flat=True)[offset:offset+page_size])
        if not ids:
            break
        # enqueue send batch
        send_batch.apply_async(args=[campaign_id, ids], queue="senders")
        offset += page_size
    logger.info(f"Enqueued send batches for {total} recipients in campaign ID: {campaign_id}")
    # Optionally enqueue a finalizer that runs after tasks finish (we schedule with ETA or rely on finalizer to run after some time)
    # Simpler: schedule a finalize attempt after a reasonable TTL (e.g., 5 minutes + estimate)
    finalize_campaign.apply_async(args=[campaign_id], countdown=300)

@shared_task(bind=True, name="campaigns.tasks.send_batch", base=BaseTaskWithRetry, rate_limit=get_rate_limit_for_provider())
def send_batch(self, campaign_id: int, recipient_ids: list):
    """
    Send emails to one batch of recipients.
    - rate_limit decorator helps respect provider constraints (per worker).
    - Uses bulk_create for DeliveryLog for efficiency.
    """
    logger.info(f"Sending batch for Campaign ID: {campaign_id} to {len(recipient_ids)} recipients.")
    campaign = Campaign.objects.get(pk=campaign_id)
    recipients = list(Recipient.objects.filter(id__in=recipient_ids))
    logs = []
    created_logs = 0
    for r in recipients:
        try:
            send_email_to_recipient(campaign, r)
            logs.append(DeliveryLog(campaign=campaign, recipient=r, recipient_email=r.email, status="sent"))
        except Exception as exc:
            logs.append(DeliveryLog(campaign=campaign, recipient=r, recipient_email=r.email, status="failed", failure_reason=str(exc)))
        # flush logs in chunks to keep memory low
        if len(logs) >= LOG_BATCH:
            DeliveryLog.objects.bulk_create(logs, ignore_conflicts=True)
            created_logs += len(logs)
            logs = []
    if logs:
        DeliveryLog.objects.bulk_create(logs, ignore_conflicts=True)
        created_logs += len(logs)
    logger.info(f"Completed sending batch for Campaign ID: {campaign_id} to {len(recipient_ids)} recipients.")
    return {"created_logs": created_logs, "batch_size": len(recipient_ids)}

@shared_task(name="campaigns.tasks.finalize_campaign", bind=True)
def finalize_campaign(self, campaign_id: int):
    """
    Determine whether all recipients have a DeliveryLog and mark campaign completed.
    Generate a CSV report and email admin.
    This is safe to call multiple times; it checks counts and only mark COMPLETED when appropriate.
    """
    logger.info(f"Finalizing campaign ID: {campaign_id} [Task: {self.request.id}]")
    campaign = Campaign.objects.get(pk=campaign_id)
    # safety: only finalize IN_PROGRESS campaigns
    if campaign.status != Campaign.IN_PROGRESS:
        logger.warning(f"Campaign ID: {campaign_id} is not IN_PROGRESS (status: {campaign.status}). Skipping finalization. [Task: {self.request.id}]")
        return {"status": "skipped", "reason": f"Campaign status is {campaign.status}"}

    # Determine total intended recipients (for this example, all subscribed users)
    recipients_qs = Recipient.objects.filter(subscription_status="subscribed")
    total_expected = recipients_qs.count()

    # count logs for this campaign
    logs_count = DeliveryLog.objects.filter(campaign=campaign).count()

    # If logs_count < total_expected, we assume not all batches have finished yet.
    # You may improve this by tracking enqueued batches. Here we ensure we don't prematurely mark completed.
    if logs_count < total_expected:
        # Re-check later
        logger.info(f"Campaign ID: {campaign_id} not yet complete ({logs_count}/{total_expected} logs). Rechecking later. [Task: {self.request.id}]")
        finalize_campaign.apply_async(args=[campaign_id], countdown=120)  # re-check in 2 minutes
        return {"status": "pending", "logs_count": logs_count, "total_expected": total_expected}

    # All done -> mark completed
    campaign.status = Campaign.COMPLETED
    campaign.save(update_fields=["status"])

    # Generate and send CSV report
    send_campaign_report.delay(campaign_id)
    logger.info(f"Campaign ID: {campaign_id} marked as COMPLETED with {logs_count} logs. [Task: {self.request.id}]")
    return {"status": "completed", "logs_count": logs_count}

@shared_task(name="campaigns.tasks.send_campaign_report")
def send_campaign_report(campaign_id: int):
    logger.info(f"Generating and sending report for Campaign ID: {campaign_id}")
    from django.utils import timezone as django_timezone
    
    campaign = Campaign.objects.get(pk=campaign_id)
    logs_qs = DeliveryLog.objects.filter(campaign=campaign).order_by("recipient_email").values(
        "recipient_email", "status", "failure_reason", "sent_at"
    )
    # stream into CSV
    buffer = StringIO()
    writer = csv.writer(buffer)
    writer.writerow(["recipient_email", "status", "failure_reason", "sent_at"])
    for row in logs_qs.iterator():
        # Convert to Django timezone (Asia/Kolkata) and format as dd/mm/yyyy HH:MM:SS
        if row["sent_at"]:
            local_time = django_timezone.localtime(row["sent_at"])
            formatted_time = local_time.strftime("%d/%m/%Y %H:%M:%S")
        else:
            formatted_time = ""
        writer.writerow([row["recipient_email"], row["status"], row["failure_reason"] or "", formatted_time])

    csv_content = buffer.getvalue().encode("utf-8")
    subject = f"Campaign Report: {campaign.name}"
    body = f"Attached is the delivery report for campaign '{campaign.name}'."

    # Email to admin(s)
    email = EmailMessage(subject=subject, body=body, from_email=settings.DEFAULT_FROM_EMAIL, to=[settings.ADMIN_REPORT_EMAIL])
    email.attach(f"{campaign.name}_report.csv", csv_content, "text/csv")
    email.send(fail_silently=False)
    buffer.close()
    logger.info(f"Report for Campaign ID: {campaign_id} sent to admin.")
    return {"rows": logs_qs.count()}
