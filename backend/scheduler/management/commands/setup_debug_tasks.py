from django.core.management.base import BaseCommand
from django_celery_beat.models import IntervalSchedule, PeriodicTask
from django.utils import timezone
import json


class Command(BaseCommand):
    help = "Set up debug periodic tasks for testing Celery Beat functionality"

    def add_arguments(self, parser):
        parser.add_argument(
            '--heartbeat-interval', 
            type=int, 
            default=1, 
            help='Heartbeat task interval in seconds (default: 1)'
        )
        parser.add_argument(
            '--counter-interval', 
            type=int, 
            default=5, 
            help='Counter task interval in seconds (default: 5)'
        )
        parser.add_argument(
            '--enable-heartbeat', 
            action='store_true', 
            default=True,
            help='Enable the heartbeat debug task'
        )
        parser.add_argument(
            '--enable-counter', 
            action='store_true', 
            default=True,
            help='Enable the counter debug task'
        )
        parser.add_argument(
            '--disable-all', 
            action='store_true', 
            help='Disable all debug tasks'
        )

    def handle(self, *args, **options):
        if options['disable_all']:
            # Disable all debug tasks
            disabled_count = PeriodicTask.objects.filter(
                name__in=['debug-heartbeat', 'debug-counter']
            ).update(enabled=False)
            self.stdout.write(
                self.style.SUCCESS(f"Disabled {disabled_count} debug periodic tasks")
            )
            return

        # Create schedules
        heartbeat_schedule, _ = IntervalSchedule.objects.get_or_create(
            every=options['heartbeat_interval'],
            period=IntervalSchedule.SECONDS
        )

        counter_schedule, _ = IntervalSchedule.objects.get_or_create(
            every=options['counter_interval'],
            period=IntervalSchedule.SECONDS
        )

        # Set up heartbeat task
        if options['enable_heartbeat']:
            heartbeat_task, created = PeriodicTask.objects.update_or_create(
                name='debug-heartbeat',
                defaults={
                    'task': 'scheduler.tasks.debug.debug_heartbeat',
                    'interval': heartbeat_schedule,
                    'enabled': True,
                    'start_time': timezone.now(),
                },
            )
            action = 'Created' if created else 'Updated'
            self.stdout.write(
                self.style.SUCCESS(
                    f"{action} debug heartbeat task (every {options['heartbeat_interval']} seconds)"
                )
            )

        # Set up counter task
        if options['enable_counter']:
            counter_kwargs = {'count': 0}
            counter_task, created = PeriodicTask.objects.update_or_create(
                name='debug-counter',
                defaults={
                    'task': 'scheduler.tasks.debug.debug_counter',
                    'interval': counter_schedule,
                    'kwargs': json.dumps(counter_kwargs),
                    'enabled': True,
                    'start_time': timezone.now(),
                },
            )
            action = 'Created' if created else 'Updated'
            self.stdout.write(
                self.style.SUCCESS(
                    f"{action} debug counter task (every {options['counter_interval']} seconds)"
                )
            )

        self.stdout.write(
            self.style.SUCCESS(
                "✅ Debug tasks set up successfully! "
                "Monitor the logs to see the periodic task execution."
            )
        )




