from django.contrib import admin
from django.utils import timezone
from django.utils.html import format_html

from .models import Application, Company, Job


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ('name', 'location', 'website_link', 'job_count', 'created_at', 'updated_at')
    search_fields = ('name', 'location', 'website', 'description')
    list_filter = ('location', 'created_at', 'updated_at')
    readonly_fields = ('created_at', 'updated_at')
    date_hierarchy = 'created_at'

    fieldsets = (
        ('Company', {
            'fields': ('name', 'website', 'location', 'description'),
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
        }),
    )

    @admin.display(description='Website')
    def website_link(self, obj):
        if not obj.website:
            return '-'
        return format_html('<a href="{}" target="_blank" rel="noopener">Website</a>', obj.website)

    @admin.display(description='Jobs')
    def job_count(self, obj):
        return obj.jobs.count()


@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'company',
        'location',
        'job_type',
        'work_mode',
        'created_at',
        'application_count',
    )
    search_fields = ('title', 'company__name', 'company__description', 'description', 'location')
    list_filter = ('company', 'job_type', 'work_mode', 'location', 'created_at')
    autocomplete_fields = ('company',)
    date_hierarchy = 'created_at'

    @admin.display(description='Applications')
    def application_count(self, obj):
        return obj.applications.count()


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = (
        'applicant_name',
        'email',
        'job',
        'company_name',
        'status',
        'applied_on',
        'status_updated_at',
        'resume_link',
    )
    list_editable = ('status',)
    search_fields = ('applicant_name', 'email', 'job__title', 'job__company__name')
    list_filter = ('status', 'job__company', 'job', 'applied_on', 'status_updated_at')
    date_hierarchy = 'applied_on'
    readonly_fields = ('applied_on', 'status_updated_at', 'resume_link')
    actions = (
        'mark_as_new',
        'mark_as_reviewed',
        'mark_as_interview',
        'mark_as_rejected',
        'mark_as_hired',
    )

    fieldsets = (
        ('Applicant', {
            'fields': ('applicant_name', 'email', 'resume_link', 'resume'),
        }),
        ('Job and Status', {
            'fields': ('job', 'status'),
        }),
        ('Timestamps', {
            'fields': ('applied_on', 'status_updated_at'),
        }),
    )

    @admin.display(description='Company', ordering='job__company__name')
    def company_name(self, obj):
        return obj.job.company.name

    @admin.display(description='Resume')
    def resume_link(self, obj):
        if not obj.resume:
            return '-'
        return format_html('<a href="{}" target="_blank" rel="noopener">Open resume</a>', obj.resume.url)

    def _mark_status(self, request, queryset, status):
        status_value = status.value if hasattr(status, 'value') else status
        status_label = status.label if hasattr(status, 'label') else Application.Status(status_value).label
        updated_count = queryset.update(status=status_value, status_updated_at=timezone.now())
        self.message_user(request, f'{updated_count} application(s) marked as {status_label}.')

    @admin.action(description='Mark selected applications as New')
    def mark_as_new(self, request, queryset):
        self._mark_status(request, queryset, Application.Status.NEW)

    @admin.action(description='Mark selected applications as Reviewed')
    def mark_as_reviewed(self, request, queryset):
        self._mark_status(request, queryset, Application.Status.REVIEWED)

    @admin.action(description='Mark selected applications as Interview')
    def mark_as_interview(self, request, queryset):
        self._mark_status(request, queryset, Application.Status.INTERVIEW)

    @admin.action(description='Mark selected applications as Rejected')
    def mark_as_rejected(self, request, queryset):
        self._mark_status(request, queryset, Application.Status.REJECTED)

    @admin.action(description='Mark selected applications as Hired')
    def mark_as_hired(self, request, queryset):
        self._mark_status(request, queryset, Application.Status.HIRED)
