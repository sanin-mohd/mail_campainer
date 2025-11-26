from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model

class Recipient(models.Model):
    SUBSCRIBED = "subscribed"
    UNSUBSCRIBED = "unsubscribed"
    STATUS_CHOICES = [(SUBSCRIBED, "Subscribed"), (UNSUBSCRIBED, "Unsubscribed")]

    name = models.CharField(max_length=255, blank=True)
    email = models.EmailField(unique=True, db_index=True)
    subscription_status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=SUBSCRIBED)
    created_on = models.DateTimeField(auto_now_add=True)

    class Meta:
            ordering = ["email"]
    
    def __str__(self): return self.email

class Campaign(models.Model):
    DRAFT = "draft"
    SCHEDULED = "scheduled"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    STATUS_CHOICES = [
        (DRAFT, "Draft"), (SCHEDULED, "Scheduled"), (IN_PROGRESS, "In Progress"), (COMPLETED, "Completed")
    ]

    name = models.CharField(max_length=255)
    subject = models.CharField(max_length=255)
    content = models.TextField()  # allow HTML
    scheduled_time = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=DRAFT)
    created_by = models.ForeignKey(get_user_model(), null=True, on_delete=models.SET_NULL)
    created_on = models.DateTimeField(auto_now_add=True)

    def __str__(self): return self.name

class DeliveryLog(models.Model):
    campaign = models.ForeignKey(Campaign, related_name="logs", on_delete=models.CASCADE)
    recipient = models.ForeignKey(Recipient, null=True, on_delete=models.SET_NULL)
    recipient_email = models.EmailField(db_index=True)
    status = models.CharField(max_length=10, choices=[("sent","Sent"),("failed","Failed")])
    failure_reason = models.TextField(blank=True, null=True)
    sent_at = models.DateTimeField(default=timezone.now)

    def __str__(self): return f"{self.campaign.name} to {self.recipient_email} - {self.status}"