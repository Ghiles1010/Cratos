from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('scheduler', '0010_remove_taskschedule_orkera_task_status_32466f_idx_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='taskschedule',
            name='webhook_secret',
        ),
    ]
