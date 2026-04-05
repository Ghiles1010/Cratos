"""
Move WebhookSigningKey from apiauth → webhooks.

Database: renames apiauth_webhooksigningkey → webhooks_webhooksigningkey (data preserved).
State: registers the model under the webhooks app.
"""
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('webhooks', '0001_initial'),
        ('apiauth', '0002_webhooksigningkey'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            # Rename the existing table — data is preserved.
            database_operations=[
                migrations.RunSQL(
                    sql='ALTER TABLE apiauth_webhooksigningkey RENAME TO webhooks_webhooksigningkey;',
                    reverse_sql='ALTER TABLE webhooks_webhooksigningkey RENAME TO apiauth_webhooksigningkey;',
                ),
            ],
            # Register the model in the webhooks app state.
            state_operations=[
                migrations.CreateModel(
                    name='WebhookSigningKey',
                    fields=[
                        ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                        ('secret', models.CharField(max_length=64, unique=True)),
                        ('created_at', models.DateTimeField(auto_now_add=True)),
                        ('last_rotated_at', models.DateTimeField(auto_now_add=True)),
                        ('user', models.OneToOneField(
                            on_delete=django.db.models.deletion.CASCADE,
                            related_name='webhook_signing_key',
                            to=settings.AUTH_USER_MODEL,
                        )),
                    ],
                    options={
                        'verbose_name': 'Webhook Signing Key',
                        'verbose_name_plural': 'Webhook Signing Keys',
                    },
                ),
            ],
        ),
    ]
