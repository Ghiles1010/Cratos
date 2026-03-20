from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('scheduler', '0011_remove_taskschedule_webhook_secret'),
    ]

    operations = [
        # Rename tables
        migrations.AlterModelTable(
            name='TaskSchedule',
            table='cratos_task_schedule',
        ),
        migrations.AlterModelTable(
            name='TaskExecution',
            table='cratos_task_execution',
        ),

        # Rename TaskSchedule indexes
        migrations.RenameIndex(
            model_name='taskschedule',
            old_name='orkera_task_user_id_b85c8c_idx',
            new_name='cratos_task_schedule_user_status_idx',
        ),
        migrations.RenameIndex(
            model_name='taskschedule',
            old_name='orkera_task_next_ru_c69d6e_idx',
            new_name='cratos_task_schedule_next_run_idx',
        ),

        # Rename TaskExecution indexes
        migrations.RenameIndex(
            model_name='taskexecution',
            old_name='orkera_task_task_id_c4a065_idx',
            new_name='cratos_task_execution_task_started_idx',
        ),
        migrations.RenameIndex(
            model_name='taskexecution',
            old_name='orkera_task_status_899550_idx',
            new_name='cratos_task_execution_status_idx',
        ),
        migrations.RenameIndex(
            model_name='taskexecution',
            old_name='orkera_task_started_d5b2f8_idx',
            new_name='cratos_task_execution_started_idx',
        ),
    ]
