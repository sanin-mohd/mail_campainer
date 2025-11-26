from django import forms
from django.contrib.admin import widgets as admin_widgets
from django.core.exceptions import ValidationError
from .models import Campaign, Recipient


def check_campaigns_in_progress():
    """
    Check if any campaigns are currently in progress.
    Raises ValidationError if any campaign is running.
    """
    running_campaigns = Campaign.objects.filter(status=Campaign.IN_PROGRESS)
    if running_campaigns.exists():
        campaign_names = ', '.join([f'"{c.name}"' for c in running_campaigns[:3]])
        count = running_campaigns.count()
        raise ValidationError(
            f'Cannot add recipients while {count} campaign(s) are in progress: {campaign_names}. '
            f'Please wait until the campaign(s) complete before adding recipients.'
        )


class RecipientUploadForm(forms.Form):
    file = forms.FileField(
        help_text="Upload CSV or Excel file containing recipients."
    )
    
    def clean_file(self):
        """Validate that no campaigns are running before allowing bulk upload"""
        check_campaigns_in_progress()
        return self.cleaned_data['file']


class RecipientForm(forms.ModelForm):
    """Form for adding/editing individual recipients"""
    
    class Meta:
        model = Recipient
        fields = ['name', 'email', 'subscription_status']
    
    def clean(self):
        """Validate that no campaigns are running before allowing recipient addition"""
        cleaned_data = super().clean()
        
        # Only check for new recipients (not when editing existing ones)
        if not self.instance.pk:
            check_campaigns_in_progress()
        
        return cleaned_data

class CampaignForm(forms.ModelForm):
    """Form for creating and editing campaigns"""
    
    class Meta:
        model = Campaign
        fields = ['name', 'subject', 'content', 'scheduled_time', 'status']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'vTextField',
                'placeholder': 'Enter campaign name'
            }),
            'subject': forms.TextInput(attrs={
                'class': 'vTextField',
                'placeholder': 'Enter email subject line'
            }),
            'content': forms.Textarea(attrs={
                'class': 'vLargeTextField',
                'rows': 10,
                'placeholder': 'Enter email content (HTML or plain text)'
            }),
            'scheduled_time': admin_widgets.AdminSplitDateTime(),
            'status': forms.Select(attrs={
                'class': 'vTextField'
            })
        }
        help_texts = {
            'content': 'You can use HTML tags for formatting.',
            'scheduled_time': 'Leave blank to save as draft. Set a future time (more than 1 hour from now) to schedule.',
        }
    
    def clean(self):
        """Validate that campaigns in progress or completed cannot be edited"""
        cleaned_data = super().clean()
        
        # Check if editing an existing campaign (not creating a new one)
        if self.instance and self.instance.pk:
            # Prevent editing campaigns that are in progress or completed
            if self.instance.status in [Campaign.IN_PROGRESS, Campaign.COMPLETED]:
                raise ValidationError(
                    f'Cannot edit campaign "{self.instance.name}" because it is {self.instance.get_status_display()}. '
                    f'Only campaigns with status "Draft" or "Scheduled" can be edited to protect data integrity.'
                )
        
        return cleaned_data
    
    def clean_scheduled_time(self):
        """Validate scheduled time is at least one hour from now and has 1hr gap from other campaigns"""
        from django.utils import timezone
        from datetime import timedelta
        
        scheduled_time = self.cleaned_data.get('scheduled_time')
        
        if scheduled_time:
            now = timezone.now()
            minimum_time = now + timedelta(hours=1)
            
            # Check if scheduled time is in the future
            # if scheduled_time < now:
            #     raise forms.ValidationError('Scheduled time must be in the future.')
            # elif scheduled_time < minimum_time:
            #     raise forms.ValidationError('Scheduled time must be at least 1 hour from now.')
            
            # Check for conflicts with other scheduled campaigns
            time_buffer = timedelta(hours=1)
            start_range = scheduled_time - time_buffer
            end_range = scheduled_time + time_buffer
            
            # Query for campaigns within the time range
            conflicting_campaigns = Campaign.objects.filter(
                scheduled_time__range=(start_range, end_range),
                status__in=['scheduled', 'draft']  # Only check scheduled and draft campaigns
            )
            
            # Exclude the current campaign if editing (not creating)
            if self.instance and self.instance.pk:
                conflicting_campaigns = conflicting_campaigns.exclude(pk=self.instance.pk)
            
            if conflicting_campaigns.exists():
                conflicting_campaign = conflicting_campaigns.first()
                conflict_time = conflicting_campaign.scheduled_time.strftime('%Y-%m-%d %H:%M')
                raise forms.ValidationError(
                    f'Another campaign "{conflicting_campaign.name}" is scheduled at {conflict_time}. '
                    f'Please ensure at least 1 hour gap between campaigns.'
                )
        
        return scheduled_time
