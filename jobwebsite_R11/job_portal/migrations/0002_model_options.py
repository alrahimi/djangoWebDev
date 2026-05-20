from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('job_portal', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='application',
            options={'ordering': ['-applied_on']},
        ),
        migrations.AlterModelOptions(
            name='job',
            options={'ordering': ['-created_at', 'title']},
        ),
    ]
