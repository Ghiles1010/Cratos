"""
Add the singleton enforcement column to URLPolicy.

The unique BooleanField replaces the save()-override pk=1 pattern.
The existing row (pk=1) gets singleton=True via the default.
"""
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('webhooks', '0003_alter_urlpolicy'),
    ]

    operations = [
        migrations.AddField(
            model_name='urlpolicy',
            name='singleton',
            field=models.BooleanField(default=True, editable=False, unique=True),
        ),
    ]
