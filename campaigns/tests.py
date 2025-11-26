"""
Unit Tests for Campaign Email System
Tests the 4 most critical functionalities:
1. Scheduled campaigns are detected and started
2. Emails are sent to recipients in batches
3. Campaigns are finalized when all emails are sent
4. CSV reports are generated and sent to admin
"""

from datetime import timedelta
from unittest.mock import patch

from django.test import TestCase
from django.utils import timezone
from django.core import mail
from django.conf import settings

from .models import Campaign, Recipient, DeliveryLog
from .tasks import (
    check_scheduled_campaigns,
    send_batch,
    finalize_campaign,
    send_campaign_report
)


class Test1_ScheduledCampaignDetection(TestCase):
    """
    CRITICAL TEST #1: Verify scheduled campaigns are detected and started
    This ensures campaigns run at the correct time
    
    NOTE: Celery beat runs check_scheduled_campaigns every 1 minute,
    so we use 2+ minute delays in tests to ensure campaigns are detected.
    """
    
    def setUp(self):
        # Create a campaign scheduled in the past (should start)
        # Use 2 minutes to account for 1-minute beat schedule
        self.past_campaign = Campaign.objects.create(
            name="Past Campaign",
            subject="Test",
            content="welcome_email.html",
            status=Campaign.SCHEDULED,
            scheduled_time=timezone.now() - timedelta(minutes=2)
        )
        
        # Create a campaign scheduled in the future (should not start)
        self.future_campaign = Campaign.objects.create(
            name="Future Campaign",
            subject="Test",
            content="welcome_email.html",
            status=Campaign.SCHEDULED,
            scheduled_time=timezone.now() + timedelta(minutes=2)
        )
    
    @patch('campaigns.tasks.start_campaign_send.delay')
    def test_scheduled_campaign_is_started(self, mock_start):
        """
        Test that past scheduled campaigns are detected and started.
        Campaign is scheduled 2 minutes in the past to account for
        the 1-minute Celery beat interval.
        """
        # Run the scheduler task
        check_scheduled_campaigns()
        
        # Verify past campaign status changed to IN_PROGRESS
        self.past_campaign.refresh_from_db()
        self.assertEqual(self.past_campaign.status, Campaign.IN_PROGRESS)
        
        # Verify start_campaign_send was called
        mock_start.assert_called_once_with(self.past_campaign.pk)
    
    @patch('campaigns.tasks.start_campaign_send.delay')
    def test_future_campaign_not_started(self, mock_start):
        """Test that future campaigns are not started"""
        check_scheduled_campaigns()
        
        # Verify future campaign remains SCHEDULED
        self.future_campaign.refresh_from_db()
        self.assertEqual(self.future_campaign.status, Campaign.SCHEDULED)
    
    @patch('campaigns.tasks.start_campaign_send.delay')
    def test_idempotency_prevents_double_start(self, mock_start):
        """Test that campaign cannot be started twice (idempotency)"""
        # Run scheduler twice
        check_scheduled_campaigns()
        check_scheduled_campaigns()
        
        # Verify start_campaign_send called only once
        self.assertEqual(mock_start.call_count, 1)


class Test2_EmailBatchSending(TestCase):
    """
    CRITICAL TEST #2: Verify emails are sent to recipients and logged
    This is the core functionality of the entire system
    """
    
    def setUp(self):
        self.campaign = Campaign.objects.create(
            name="Test Campaign",
            subject="Test Subject",
            content="<h1>Welcome</h1><p>Hello {{name}}!</p>",
            status=Campaign.IN_PROGRESS
        )
        
        # Create test recipients
        self.recipients = []
        for i in range(3):
            recipient = Recipient.objects.create(
                email=f"user{i}@example.com",
                name=f"User Test {i}",
                subscription_status="subscribed"
            )
            self.recipients.append(recipient)
    
    @patch('campaigns.tasks.send_email_to_recipient')
    def test_emails_sent_to_all_recipients(self, mock_send_email):
        """Test that all recipients in batch receive emails"""
        recipient_ids = [r.pk for r in self.recipients]
        
        # Send batch
        send_batch(self.campaign.pk, recipient_ids)
        
        # Verify send_email_to_recipient called for each recipient
        self.assertEqual(mock_send_email.call_count, 3)
    
    @patch('campaigns.tasks.send_email_to_recipient')
    def test_delivery_logs_created(self, mock_send_email):
        """Test that delivery logs are created for tracking"""
        recipient_ids = [r.pk for r in self.recipients]
        
        # Send batch
        send_batch(self.campaign.pk, recipient_ids)
        
        # Verify delivery logs created
        logs = DeliveryLog.objects.filter(campaign=self.campaign)
        self.assertEqual(logs.count(), 3)
        
        # Verify all logs marked as sent
        sent_logs = logs.filter(status="sent")
        self.assertEqual(sent_logs.count(), 3)
    
    @patch('campaigns.tasks.send_email_to_recipient')
    def test_failed_sends_are_logged(self, mock_send_email):
        """Test that failed email sends are properly logged"""
        # Simulate first email failing
        mock_send_email.side_effect = [
            Exception("SMTP Connection Error"),
            None, None, None, None
        ]
        
        recipient_ids = [r.pk for r in self.recipients]
        send_batch(self.campaign.pk, recipient_ids)
        
        # Verify failure logged
        failed_logs = DeliveryLog.objects.filter(
            campaign=self.campaign,
            status="failed"
        )
        self.assertEqual(failed_logs.count(), 1)
        self.assertIn("SMTP Connection Error", failed_logs.first().failure_reason)
        
        # Verify others succeeded
        sent_logs = DeliveryLog.objects.filter(
            campaign=self.campaign,
            status="sent"
        )
        self.assertEqual(sent_logs.count(), 2)


class Test3_CampaignFinalization(TestCase):
    """
    CRITICAL TEST #3: Verify campaigns are finalized when all emails sent
    This ensures campaigns don't get stuck in IN_PROGRESS state
    
    NOTE: finalize_campaign uses polling with countdown delays:
    - Initial call: countdown=300s (5 minutes) from start_campaign_send
    - Retry calls: countdown=120s (2 minutes) if not all logs ready
    """
    
    def setUp(self):
        self.campaign = Campaign.objects.create(
            name="Test Campaign",
            subject="Test Subject",
            content="<h1>Test Email</h1>",
            status=Campaign.IN_PROGRESS
        )
        
        # Create 4 recipients
        self.recipients = []
        for i in range(4):
            recipient = Recipient.objects.create(
                email=f"user{i}@example.com",
                name=f"User{i}",
                subscription_status="subscribed"
            )
            self.recipients.append(recipient)
    
    @patch('campaigns.tasks.send_campaign_report.delay')
    def test_campaign_finalized_when_complete(self, mock_report):
        """Test campaign marked as COMPLETED when all logs exist"""
        # Create delivery logs for all recipients
        for recipient in self.recipients:
            DeliveryLog.objects.create(
                campaign=self.campaign,
                recipient=recipient,
                recipient_email=recipient.email,
                status="sent"
            )
        
        # Call finalize_campaign directly (task runs synchronously in tests)
        result = finalize_campaign(self.campaign.pk)
        
        # Verify campaign marked as COMPLETED
        self.campaign.refresh_from_db()
        self.assertEqual(self.campaign.status, Campaign.COMPLETED)
        
        # Verify report task called
        mock_report.assert_called_once_with(self.campaign.pk)
        
        # Verify return value indicates success
        self.assertEqual(result['status'], 'completed')
        self.assertEqual(result['logs_count'], 4)
    
    @patch('campaigns.tasks.finalize_campaign.apply_async')
    def test_campaign_reschedules_if_incomplete(self, mock_reschedule):
        """
        Test campaign reschedules if not all emails sent yet.
        Task will reschedule with countdown=120s (2 minutes) to check again.
        """
        # Create logs for only 2 out of 4 recipients
        for recipient in self.recipients[:2]:
            DeliveryLog.objects.create(
                campaign=self.campaign,
                recipient=recipient,
                recipient_email=recipient.email,
                status="sent"
            )
        
        # Call finalize_campaign directly
        result = finalize_campaign(self.campaign.pk)
        
        # Verify campaign still IN_PROGRESS
        self.campaign.refresh_from_db()
        self.assertEqual(self.campaign.status, Campaign.IN_PROGRESS)
        
        # Verify task rescheduled with countdown=120
        mock_reschedule.assert_called_once()
        call_kwargs = mock_reschedule.call_args[1]
        self.assertEqual(call_kwargs['countdown'], 120, 
            "Task should reschedule with 120 second countdown")
        
        # Verify return value shows pending
        self.assertEqual(result['status'], 'pending')
        self.assertEqual(result['logs_count'], 2)
        self.assertEqual(result['total_expected'], 4)
    
    def test_skips_already_completed_campaigns(self):
        """Test finalization skips campaigns that are already completed"""
        # Mark campaign as completed
        self.campaign.status = Campaign.COMPLETED
        self.campaign.save()
        
        # Call finalize_campaign directly
        result = finalize_campaign(self.campaign.pk)
        
        # Verify skipped
        self.assertEqual(result['status'], 'skipped')


class Test4_ReportGeneration(TestCase):
    """
    CRITICAL TEST #4: Verify CSV reports are generated and sent to admin
    This ensures admins get delivery reports for tracking
    """
    
    def setUp(self):
        self.campaign = Campaign.objects.create(
            name="Test Campaign",
            subject="Test Subject",
            content="<h1>Test Email</h1>",
            status=Campaign.COMPLETED
        )
        
        # Create recipients and delivery logs
        for i in range(3):
            recipient = Recipient.objects.create(
                email=f"user{i}@example.com",
                name=f"User Test{i}",
                subscription_status="subscribed"
            )
            
            # First 2 succeed, last one fails
            DeliveryLog.objects.create(
                campaign=self.campaign,
                recipient=recipient,
                recipient_email=recipient.email,
                status="sent" if i < 2 else "failed",
                failure_reason="SMTP Timeout" if i == 2 else None
            )
    
    def test_report_email_sent_to_admin(self):
        """Test that report email is sent to admin"""
        send_campaign_report(self.campaign.pk)
        
        # Verify email sent
        self.assertEqual(len(mail.outbox), 1)
        
        # Verify email details
        email = mail.outbox[0]
        self.assertIn(self.campaign.name, email.subject)
        self.assertEqual(email.to, [settings.ADMIN_REPORT_EMAIL])
    
    def test_csv_attachment_included(self):
        """Test that CSV file is attached to report email"""
        send_campaign_report(self.campaign.pk)
        
        email = mail.outbox[0]
        
        # Verify attachment exists
        self.assertEqual(len(email.attachments), 1)
        
        # Verify attachment is CSV
        filename, content, mimetype = email.attachments[0]
        self.assertTrue(filename.endswith('.csv'))
        self.assertEqual(mimetype, 'text/csv')
    
    def test_csv_contains_all_delivery_logs(self):
        """Test that CSV contains all delivery log records"""
        send_campaign_report(self.campaign.pk)
        
        email = mail.outbox[0]
        filename, content, mimetype = email.attachments[0]
        
        # Content is already a string (or decode if bytes)
        csv_content = content if isinstance(content, str) else content.decode('utf-8')
        
        # Verify headers
        self.assertIn('recipient_email', csv_content)
        self.assertIn('status', csv_content)
        self.assertIn('failure_reason', csv_content)
        self.assertIn('sent_at', csv_content)
        
        # Verify all 3 recipients in CSV (3 data rows + 1 header)
        lines = csv_content.strip().split('\n')
        self.assertEqual(len(lines), 4)
        
        # Verify email addresses present
        self.assertIn('user0@example.com', csv_content)
        self.assertIn('user1@example.com', csv_content)
        self.assertIn('user2@example.com', csv_content)
    
    def test_csv_date_format_correct(self):
        """Test that dates are formatted as dd/mm/yyyy HH:MM:SS"""
        send_campaign_report(self.campaign.pk)
        
        email = mail.outbox[0]
        filename, content, mimetype = email.attachments[0]
        
        # Content is already a string (or decode if bytes)
        csv_content = content if isinstance(content, str) else content.decode('utf-8')
        
        # Verify date format using regex
        import re
        date_pattern = r'\d{2}/\d{2}/\d{4} \d{2}:\d{2}:\d{2}'
        matches = re.findall(date_pattern, csv_content)
        
        # Should have 3 dates (one per recipient)
        self.assertGreaterEqual(len(matches), 3, 
            "CSV should contain dates in dd/mm/yyyy HH:MM:SS format")
    
    def test_task_returns_row_count(self):
        """Test that task returns count of rows processed"""
        result = send_campaign_report(self.campaign.pk)
        
        self.assertIn('rows', result)
        self.assertEqual(result['rows'], 3)


# ============================================================================
# HOW TO RUN TESTS
# ============================================================================
#
# Run all tests:
#   docker-compose exec web python manage.py test campaigns
#
# Run with verbose output:
#   docker-compose exec web python manage.py test campaigns --verbosity=2
#
# Run specific test class:
#   docker-compose exec web python manage.py test campaigns.tests.Test1_ScheduledCampaignDetection
#
# Run specific test method:
#   docker-compose exec web python manage.py test campaigns.tests.Test1_ScheduledCampaignDetection.test_scheduled_campaign_is_started
#
# ============================================================================

