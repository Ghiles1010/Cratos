from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('scheduler', '0008_alter_taskschedule_callback_url'),
    ]

    operations = [
        migrations.AddField(
            model_name='taskschedule',
            name='webhook_secret',
            field=models.CharField(
                blank=True,
                default='',
                help_text='Optional secret for HMAC-SHA256 webhook signature (X-Cratos-Signature header)',
                max_length=255,
            ),
        ),
    ]
