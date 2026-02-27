"""
Remove WebhookSigningKey state from apiauth (table already renamed by webhooks migration).
"""
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('apiauth', '0002_webhooksigningkey'),
        # Must run after the webhooks migration that renames the table.
        ('webhooks', '0002_webhooksigningkey'),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            # Table was already renamed by webhooks/0002 — nothing to do in DB.
            database_operations=[],
            state_operations=[
                migrations.DeleteModel('WebhookSigningKey'),
            ],
        ),
    ]
