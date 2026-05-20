from django.db import models
from django.urls import reverse


class Company(models.Model):
    name = models.CharField(max_length=150, unique=True)
    website = models.URLField(blank=True)
    description = models.TextField(blank=True)
    location = models.CharField(max_length=150, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']
        verbose_name_plural = 'companies'

    def __str__(self):
        return self.name


class Job(models.Model):
    class JobType(models.TextChoices):
        FULL_TIME = 'full_time', 'Full-time'
        PART_TIME = 'part_time', 'Part-time'
        CONTRACT = 'contract', 'Contract'
        INTERNSHIP = 'internship', 'Internship'
        TEMPORARY = 'temporary', 'Temporary'

    class WorkMode(models.TextChoices):
        REMOTE = 'remote', 'Remote'
        HYBRID = 'hybrid', 'Hybrid'
        ON_SITE = 'on_site', 'On-site'

    title = models.CharField(max_length=200)
    company = models.ForeignKey(Company, on_delete=models.PROTECT, related_name='jobs')
    description = models.TextField()
    location = models.CharField(max_length=100)
    job_type = models.CharField(
        max_length=20,
        choices=JobType.choices,
        default=JobType.FULL_TIME,
        help_text='Employment type for this job.',
    )
    work_mode = models.CharField(
        max_length=20,
        choices=WorkMode.choices,
        default=WorkMode.ON_SITE,
        help_text='Whether this job is remote, hybrid, or on-site.',
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at', 'title']

    def __str__(self):
        return f"{self.title} at {self.company.name}"

    def get_absolute_url(self):
        return reverse('job_detail', kwargs={'pk': self.pk})


class Application(models.Model):
    class Status(models.TextChoices):
        NEW = 'new', 'New'
        REVIEWED = 'reviewed', 'Reviewed'
        INTERVIEW = 'interview', 'Interview'
        REJECTED = 'rejected', 'Rejected'
        HIRED = 'hired', 'Hired'

    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='applications')
    applicant_name = models.CharField(max_length=100)
    email = models.EmailField()
    resume = models.FileField(upload_to='resumes/')
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.NEW,
        help_text='Internal hiring status for this application.',
    )
    applied_on = models.DateTimeField(auto_now_add=True)
    status_updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-applied_on']

    def __str__(self):
        return f"{self.applicant_name} - {self.job.title} ({self.get_status_display()})"
