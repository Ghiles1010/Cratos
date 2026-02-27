"""
Refactor URLPolicy:
  - Add allow_local BooleanField (default False)
  - Remove blocked_domain_suffixes JSONField
  - blocked_networks is retained (extra CIDRs on top of built-in rules)
"""
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('webhooks', '0002_webhooksigningkey'),
    ]

    operations = [
        migrations.AddField(
            model_name='urlpolicy',
            name='allow_local',
            field=models.BooleanField(
                default=False,
                help_text='Allow private / loopback / link-local IPs after resolution.',
            ),
        ),
        migrations.RemoveField(
            model_name='urlpolicy',
            name='blocked_domain_suffixes',
        ),
        migrations.AlterField(
            model_name='urlpolicy',
            name='blocked_networks',
            field=models.JSONField(
                default=list,
                help_text='Additional CIDRs to block explicitly (on top of built-in rules). Example: ["169.254.169.254/32"]',
            ),
        ),
        migrations.AlterField(
            model_name='urlpolicy',
            name='allowed_hosts',
            field=models.JSONField(
                default=list,
                help_text='Hostnames or literal IPs always allowed, even if local. Example: ["host.docker.internal", "192.168.1.50"]',
            ),
        ),
    ]
