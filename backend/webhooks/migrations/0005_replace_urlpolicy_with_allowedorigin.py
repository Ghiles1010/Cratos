"""
Replace the URLPolicy singleton with an AllowedOrigin allowlist table.
"""
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('webhooks', '0004_urlpolicy_singleton'),
    ]

    operations = [
        migrations.DeleteModel('URLPolicy'),
        migrations.CreateModel(
            name='AllowedOrigin',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('scheme', models.CharField(
                    choices=[('http', 'http'), ('https', 'https')],
                    max_length=5,
                )),
                ('host', models.CharField(max_length=255)),
                ('port', models.PositiveIntegerField()),
            ],
            options={
                'verbose_name': 'Allowed Origin',
                'verbose_name_plural': 'Allowed Origins',
                'unique_together': {('scheme', 'host', 'port')},
            },
        ),
    ]
