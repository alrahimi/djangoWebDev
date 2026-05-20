from django.db import migrations, models
import django.db.models.deletion


JOB_TYPE_DEFAULTS = {
    'Junior Python Developer': 'full_time',
    'Data Entry Specialist': 'part_time',
    'Web Content Assistant': 'contract',
}

WORK_MODE_DEFAULTS = {
    'Junior Python Developer': 'remote',
    'Data Entry Specialist': 'on_site',
    'Web Content Assistant': 'hybrid',
}


def create_companies_and_link_jobs(apps, schema_editor):
    Company = apps.get_model('job_portal', 'Company')
    Job = apps.get_model('job_portal', 'Job')

    for job in Job.objects.all():
        company_name = (getattr(job, 'company_name', '') or 'Unknown Company').strip() or 'Unknown Company'
        company, _created = Company.objects.get_or_create(
            name=company_name,
            defaults={
                'location': job.location,
                'description': f'Employer for {company_name} job postings.',
            },
        )
        job.company = company
        job.job_type = JOB_TYPE_DEFAULTS.get(job.title, 'full_time')
        job.work_mode = WORK_MODE_DEFAULTS.get(job.title, 'on_site')
        job.save(update_fields=['company', 'job_type', 'work_mode'])


def unlink_jobs_from_companies(apps, schema_editor):
    Job = apps.get_model('job_portal', 'Job')
    for job in Job.objects.select_related('company'):
        job.company_name = job.company.name if job.company_id else 'Unknown Company'
        job.save(update_fields=['company_name'])


class Migration(migrations.Migration):

    dependencies = [
        ('job_portal', '0003_application_status_tracking'),
    ]

    operations = [
        migrations.CreateModel(
            name='Company',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=150, unique=True)),
                ('website', models.URLField(blank=True)),
                ('description', models.TextField(blank=True)),
                ('location', models.CharField(blank=True, max_length=150)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name_plural': 'companies',
                'ordering': ['name'],
            },
        ),
        migrations.RenameField(
            model_name='job',
            old_name='company',
            new_name='company_name',
        ),
        migrations.AddField(
            model_name='job',
            name='job_type',
            field=models.CharField(
                choices=[
                    ('full_time', 'Full-time'),
                    ('part_time', 'Part-time'),
                    ('contract', 'Contract'),
                    ('internship', 'Internship'),
                    ('temporary', 'Temporary'),
                ],
                default='full_time',
                help_text='Employment type for this job.',
                max_length=20,
            ),
        ),
        migrations.AddField(
            model_name='job',
            name='work_mode',
            field=models.CharField(
                choices=[
                    ('remote', 'Remote'),
                    ('hybrid', 'Hybrid'),
                    ('on_site', 'On-site'),
                ],
                default='on_site',
                help_text='Whether this job is remote, hybrid, or on-site.',
                max_length=20,
            ),
        ),
        migrations.AddField(
            model_name='job',
            name='company',
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name='jobs',
                to='job_portal.company',
            ),
        ),
        migrations.RunPython(create_companies_and_link_jobs, unlink_jobs_from_companies),
        migrations.AlterField(
            model_name='job',
            name='company',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name='jobs',
                to='job_portal.company',
            ),
        ),
        migrations.RemoveField(
            model_name='job',
            name='company_name',
        ),
    ]
