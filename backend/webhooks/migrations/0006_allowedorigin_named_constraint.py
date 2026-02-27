"""
Replace the unique_together constraint on AllowedOrigin with a named
UniqueConstraint (easier to reference in future alterations).
"""
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('webhooks', '0005_replace_urlpolicy_with_allowedorigin'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='allowedorigin',
            unique_together=set(),
        ),
        migrations.AddConstraint(
            model_name='allowedorigin',
            constraint=models.UniqueConstraint(
                fields=['scheme', 'host', 'port'],
                name='uniq_allowed_origin',
            ),
        ),
    ]
