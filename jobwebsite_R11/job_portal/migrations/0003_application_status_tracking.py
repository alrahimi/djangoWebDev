import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('job_portal', '0002_model_options'),
    ]

    operations = [
        migrations.AddField(
            model_name='application',
            name='status',
            field=models.CharField(
                choices=[
                    ('new', 'New'),
                    ('reviewed', 'Reviewed'),
                    ('interview', 'Interview'),
                    ('rejected', 'Rejected'),
                    ('hired', 'Hired'),
                ],
                default='new',
                help_text='Internal hiring status for this application.',
                max_length=20,
            ),
        ),
        migrations.AddField(
            model_name='application',
            name='status_updated_at',
            field=models.DateTimeField(default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='application',
            name='status_updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
    ]
