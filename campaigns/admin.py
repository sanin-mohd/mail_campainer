from django.contrib import admin
from django.utils.html import format_html
from django.urls import path
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Campaign, Recipient, DeliveryLog
from .forms import CampaignForm, RecipientUploadForm, RecipientForm
from .importer_v2 import RecipientImporterParallel


@admin.register(Campaign)
class CampaignAdmin(admin.ModelAdmin):
    """Admin interface for Campaign management"""
    
    form = CampaignForm
    
    list_display = [
        'name',
        'subject',
        'status_badge',
        'scheduled_time',
        'delivery_stats',
        'created_by',
        'created_on'
    ]
    
    list_filter = [
        'status',
        'created_on',
        'scheduled_time',
        'created_by'
    ]
    
    search_fields = [
        'name',
        'subject',
        'content'
    ]
    
    readonly_fields = [
        'created_by',
        'created_on',
        'delivery_summary'
    ]
    
    fieldsets = (
        ('Campaign Details', {
            'fields': ('name', 'subject', 'content')
        }),
        ('Scheduling & Status', {
            'fields': ('scheduled_time', 'status')
        }),
        ('Metadata', {
            'fields': ('created_by', 'created_on'),
            'classes': ('collapse',)
        }),
        ('Delivery Statistics', {
            'fields': ('delivery_summary',),
            'classes': ('collapse',)
        })
    )
    
    actions = [
        'mark_as_scheduled',
        'mark_as_draft',
        'mark_as_completed'
    ]
    
    def status_badge(self, obj):
        """Display status with color coding"""
        colors = {
            'draft': '#6c757d',
            'scheduled': '#0d6efd',
            'in_progress': '#ffc107',
            'completed': '#28a745'
        }
        color = colors.get(obj.status, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px; font-weight: bold;">{}</span>',
            color,
            obj.get_status_display()
        )
    status_badge.short_description = 'Status'
    
    def delivery_stats(self, obj):
        """Display delivery statistics"""
        total = obj.logs.count()
        sent = obj.logs.filter(status='sent').count()
        failed = obj.logs.filter(status='failed').count()
        
        if total == 0:
            return format_html('<span style="color: #6c757d;">No deliveries yet</span>')
        
        return format_html(
            '<span style="color: #28a745;">✓ {}</span> / '
            '<span style="color: #dc3545;">✗ {}</span> / '
            '<span style="color: #6c757d;">Total: {}</span>',
            sent, failed, total
        )
    delivery_stats.short_description = 'Delivery Stats'
    
    def delivery_summary(self, obj):
        """Detailed delivery summary for readonly field"""
        # Only show for campaigns that have been processed
        if not obj or not obj.pk:
            return format_html(
                '<div style="max-width: 800px; padding: 15px; background: #e7f3ff; border-radius: 5px; border-left: 4px solid #2196F3; margin: 10px 0;">'
                '<p style="margin: 0; color: #0c5460; font-size: 14px;"><em>💡 Campaign not created yet. Save to see delivery statistics.</em></p>'
                '</div>'
            )
        
        total = obj.logs.count()
        sent = obj.logs.filter(status='sent').count()
        failed = obj.logs.filter(status='failed').count()
        
        if total == 0:
            return format_html(
                '<div style="max-width: 800px; padding: 15px; background: #fff3cd; border-radius: 5px; border-left: 4px solid #ffc107; margin: 10px 0;">'
                '<p style="margin: 0; color: #856404; font-weight: 600; font-size: 14px;"><strong>⏳ No emails sent yet</strong></p>'
                '<p style="margin: 8px 0 0 0; font-size: 13px; color: #856404; line-height: 1.5;">'
                'Emails will be sent when the campaign is scheduled and started by Celery.'
                '</p>'
                '</div>'
            )
        
        # Calculate percentages
        sent_percent = (sent / total * 100) if total > 0 else 0
        failed_percent = (failed / total * 100) if total > 0 else 0
        success_rate = sent_percent
        
        # Determine status color based on success rate
        if success_rate >= 95:
            status_color = '#28a745'  # Green - Excellent
            status_text = 'Excellent'
        elif success_rate >= 85:
            status_color = '#17a2b8'  # Blue - Good
            status_text = 'Good'
        elif success_rate >= 70:
            status_color = '#ffc107'  # Yellow - Fair
            status_text = 'Fair'
        else:
            status_color = '#dc3545'  # Red - Poor
            status_text = 'Needs Attention'
        
        return format_html(
            f'<div style="max-width: 800px; padding: 15px; background: #f8f9fa; border-radius: 5px; border-left: 4px solid {status_color}; margin: 10px 0;">'
            f'<h4 style="margin: 0 0 15px 0; color: #417690; font-size: 14px; font-weight: 600;">📊 Delivery Report</h4>'
            f'<table style="width: 100%; border-collapse: collapse; background: white; border-radius: 3px; overflow: hidden;">'
            f'<tr style="border-bottom: 1px solid #e1e4e8; background: #fafbfc;">'
            f'<td style="padding: 10px 15px; font-weight: 600; color: #24292e;">Total Emails:</td>'
            f'<td style="padding: 10px 15px; text-align: right; font-weight: 600; color: #24292e;">{total}</td>'
            f'</tr>'
            f'<tr style="border-bottom: 1px solid #e1e4e8;">'
            f'<td style="padding: 10px 15px;"><span style="color: #28a745; font-weight: 600;">✓ Successful:</span></td>'
            f'<td style="padding: 10px 15px; text-align: right;"><span style="color: #28a745; font-weight: 700; font-size: 15px;">{sent} ({sent_percent:.1f}%)</span></td>'
            f'</tr>'
            f'<tr style="border-bottom: 1px solid #e1e4e8;">'
            f'<td style="padding: 10px 15px;"><span style="color: #dc3545; font-weight: 600;">✗ Failed:</span></td>'
            f'<td style="padding: 10px 15px; text-align: right;"><span style="color: #dc3545; font-weight: 700; font-size: 15px;">{failed} ({failed_percent:.1f}%)</span></td>'
            f'</tr>'
            f'<tr style="background: #fafbfc;">'
            f'<td style="padding: 12px 15px; font-weight: 600; color: #24292e;">Delivery Rate:</td>'
            f'<td style="padding: 12px 15px; text-align: right;">'
            f'<span style="color: {status_color}; font-weight: 700; font-size: 18px; padding: 5px 12px; background: white; border-radius: 4px; border: 2px solid {status_color}; display: inline-block;">'
            f'{success_rate:.1f}% - {status_text}'
            f'</span>'
            f'</td>'
            f'</tr>'
            f'</table>'
            f'</div>'
        )
    delivery_summary.short_description = 'Delivery Summary'
    
    def save_model(self, request, obj, form, change):
        """Set created_by to current user on creation"""
        if not change:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)
    
    def has_change_permission(self, request, obj=None):
        """Prevent editing campaigns that are in progress or completed"""
        if obj and obj.status in [Campaign.IN_PROGRESS, Campaign.COMPLETED]:
            return False
        return super().has_change_permission(request, obj)
    
    def has_delete_permission(self, request, obj=None):
        """Prevent deletion of campaigns that are in progress or completed"""
        if obj and obj.status in [Campaign.IN_PROGRESS, Campaign.COMPLETED]:
            return False
        return super().has_delete_permission(request, obj)
    
    def get_readonly_fields(self, request, obj=None):
        """Make all fields readonly for in-progress or completed campaigns"""
        # Start with the base readonly fields (created_by, created_on, delivery_summary)
        readonly = list(super().get_readonly_fields(request, obj))
        
        if obj and obj.status in [Campaign.IN_PROGRESS, Campaign.COMPLETED]:
            # Make all fields readonly for running or completed campaigns
            readonly.extend(['name', 'subject', 'content', 'scheduled_time', 'status'])
        
        return readonly
    
    def changeform_view(self, request, object_id=None, form_url='', extra_context=None):
        """Add warning message for in-progress or completed campaigns"""
        extra_context = extra_context or {}
        
        if object_id:
            obj = self.get_object(request, object_id)
            if obj and obj.status in [Campaign.IN_PROGRESS, Campaign.COMPLETED]:
                extra_context['show_save'] = False
                extra_context['show_save_and_continue'] = False
                extra_context['show_save_and_add_another'] = False
                messages.warning(
                    request,
                    f'This campaign is {obj.get_status_display()} and cannot be edited or deleted to protect data integrity. '
                    f'You can only view the details.'
                )
        
        return super().changeform_view(request, object_id, form_url, extra_context)
    
    # Admin Actions
    @admin.action(description='Mark selected campaigns as Scheduled')
    def mark_as_scheduled(self, request, queryset):
        # Only allow changing status for draft campaigns
        editable_campaigns = queryset.exclude(status__in=[Campaign.IN_PROGRESS, Campaign.COMPLETED])
        locked_count = queryset.filter(status__in=[Campaign.IN_PROGRESS, Campaign.COMPLETED]).count()
        
        updated = editable_campaigns.update(status='scheduled')
        
        if updated > 0:
            self.message_user(request, f'{updated} campaign(s) marked as scheduled.')
        if locked_count > 0:
            messages.warning(
                request,
                f'{locked_count} campaign(s) were not updated because they are in progress or completed.'
            )
    
    @admin.action(description='Mark selected campaigns as Draft')
    def mark_as_draft(self, request, queryset):
        # Only allow changing status for scheduled campaigns (not in-progress or completed)
        editable_campaigns = queryset.exclude(status__in=[Campaign.IN_PROGRESS, Campaign.COMPLETED])
        locked_count = queryset.filter(status__in=[Campaign.IN_PROGRESS, Campaign.COMPLETED]).count()
        
        updated = editable_campaigns.update(status='draft')
        
        if updated > 0:
            self.message_user(request, f'{updated} campaign(s) marked as draft.')
        if locked_count > 0:
            messages.warning(
                request,
                f'{locked_count} campaign(s) were not updated because they are in progress or completed.'
            )


@admin.register(Recipient)
class RecipientAdmin(admin.ModelAdmin):
    """Admin interface for Recipient management"""
    
    form = RecipientForm  # Use custom form with validation
    
    list_display = [
        'email',
        'name',
        'subscription_badge',
        'created_on'
    ]
    
    list_filter = [
        'subscription_status',
        'created_on'
    ]
    
    search_fields = [
        'email',
        'name'
    ]
    
    actions = [
        'mark_as_subscribed',
        'mark_as_unsubscribed',
        'mark_all_as_unsubscribed'
    ]
    
    def subscription_badge(self, obj):
        """Display subscription status with color coding"""
        if obj.subscription_status == 'subscribed':
            return format_html(
                '<span style="background-color: #28a745; color: white; padding: 3px 10px; border-radius: 3px;">Subscribed</span>'
            )
        else:
            return format_html(
                '<span style="background-color: #dc3545; color: white; padding: 3px 10px; border-radius: 3px;">Unsubscribed</span>'
            )
    subscription_badge.short_description = 'Status'
    
    @admin.action(description='Mark as Subscribed')
    def mark_as_subscribed(self, request, queryset):
        updated = queryset.update(subscription_status='subscribed')
        self.message_user(request, f'{updated} recipient(s) marked as subscribed.')
    
    @admin.action(description='Mark as Unsubscribed')
    def mark_as_unsubscribed(self, request, queryset):
        updated = queryset.update(subscription_status='unsubscribed')
        self.message_user(request, f'{updated} recipient(s) marked as unsubscribed.')

    @admin.action(description='Mark all users as Unsubscribed')
    def mark_all_as_unsubscribed(self, request, queryset):
        total = Recipient.objects.update(subscription_status='unsubscribed')
        self.message_user(request, f'All {total} recipients marked as unsubscribed.')
    
    # Custom URLs for bulk upload
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('bulk-upload/', self.admin_site.admin_view(self.bulk_upload_view), name='campaigns_recipient_bulk_upload'),
        ]
        return custom_urls + urls
    
    def bulk_upload_view(self, request):
        """Handle bulk upload of recipients via CSV/Excel"""
        # Check for running campaigns before showing the form
        running_campaigns = Campaign.objects.filter(status=Campaign.IN_PROGRESS)
        
        if request.method == 'POST':
            if running_campaigns.count() == 0:
                form = RecipientUploadForm(request.POST, request.FILES)
                if form.is_valid():
                    uploaded_file = request.FILES['file']
                    
                    try:
                        # Use the parallel importer for fast processing
                        importer = RecipientImporterParallel(uploaded_file)
                        result = importer.run()
                        
                        # Show success message with stats
                        messages.success(
                            request,
                            f'Successfully imported {result["created"]} recipients. '
                            f'{result["duplicates_skipped"]} duplicates were skipped.'
                        )
                        return redirect('..')
                        
                    except Exception as e:
                        messages.error(request, f'Error importing file: {str(e)}')
            else:
                messages.error(
                    request,
                    f'Cannot upload recipients while {running_campaigns.count()} campaign(s) are in progress.'
                )
                return redirect('..')
        else:
            form = RecipientUploadForm()
        
        context = {
            'form': form,
            'title': 'Bulk Upload Recipients',
            'site_title': 'Campaign Admin',
            'site_header': 'Campaign Administration',
            'opts': self.model._meta,
            'has_view_permission': self.has_view_permission(request),
            'running_campaigns': running_campaigns,  # Pass running campaigns to template
            'running_campaigns_count': running_campaigns.count(),
        }
        return render(request, 'admin/campaigns/recipient/bulk_upload.html', context)
    
    def changelist_view(self, request, extra_context=None):
        """Add bulk upload button to the recipient list view"""
        extra_context = extra_context or {}
        extra_context['show_bulk_upload'] = True
        return super().changelist_view(request, extra_context=extra_context)


@admin.register(DeliveryLog)
class DeliveryLogAdmin(admin.ModelAdmin):
    """Admin interface for Delivery Log management"""
    
    list_display = [
        'campaign',
        'recipient_email',
        'status_badge',
        'sent_at',
        'failure_reason_short'
    ]
    
    list_filter = [
        'status',
        'sent_at',
        'campaign'
    ]
    
    search_fields = [
        'recipient_email',
        'campaign__name',
        'failure_reason'
    ]
    
    readonly_fields = [
        'campaign',
        'recipient',
        'recipient_email',
        'status',
        'sent_at',
        'failure_reason'
    ]
    
    def status_badge(self, obj):
        """Display status with color coding"""
        if obj.status == 'sent':
            return format_html(
                '<span style="background-color: #28a745; color: white; padding: 3px 10px; border-radius: 3px;">Sent</span>'
            )
        else:
            return format_html(
                '<span style="background-color: #dc3545; color: white; padding: 3px 10px; border-radius: 3px;">Failed</span>'
            )
    status_badge.short_description = 'Status'
    
    def failure_reason_short(self, obj):
        """Display shortened failure reason"""
        if obj.failure_reason:
            return obj.failure_reason[:50] + '...' if len(obj.failure_reason) > 50 else obj.failure_reason
        return '-'
    failure_reason_short.short_description = 'Failure Reason'
    
    def has_add_permission(self, request):
        """Disable manual creation of delivery logs"""
        return False
