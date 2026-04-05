from django.db import migrations, models

import webhooks.models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name='URLPolicy',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('blocked_networks', models.JSONField(
                    default=list,
                    help_text='CIDR ranges to block. Example: ["10.0.0.0/8", "192.168.0.0/16"]. Both IPv4 and IPv6 CIDRs are supported.',
                )),
                ('allowed_hosts', models.JSONField(
                    default=list,
                    help_text='Hostnames or literal IP addresses that are always allowed, even if they would otherwise match a blocked network or suffix. Example: ["host.docker.internal", "192.168.1.50"]',
                )),
                ('blocked_domain_suffixes', models.JSONField(
                    default=list,
                    help_text='Domain suffixes to block. Example: [".local", ".internal"]. Matched case-insensitively against the full hostname.',
                )),
            ],
            options={
                'verbose_name': 'URL Policy',
                'verbose_name_plural': 'URL Policy',
            },
        ),
    ]
