from django.core.management.base import BaseCommand
from django_celery_beat.models import IntervalSchedule, PeriodicTask
from django.utils import timezone
import json


class Command(BaseCommand):
    help = "Ensure the dispatcher periodic task exists (DB-backed via django-celery-beat)"

    def add_arguments(self, parser):
        parser.add_argument('--every', type=int, default=10, help='Interval value')
        parser.add_argument('--period', type=str, default='seconds', choices=['seconds', 'minutes', 'hours', 'days'], help='Interval period')
        parser.add_argument('--batch-size', type=int, default=100, help='Dispatcher batch size')
        parser.add_argument('--lookback-seconds', type=int, default=60, help='Dispatcher lookback window in seconds')
        parser.add_argument('--name', type=str, default='dispatch-due-tasks', help='PeriodicTask name')
        parser.add_argument('--enabled', action='store_true', default=True, help='Enable the periodic task')

    def handle(self, *args, **options):
        period_map = {
            'seconds': IntervalSchedule.SECONDS,
            'minutes': IntervalSchedule.MINUTES,
            'hours': IntervalSchedule.HOURS,
            'days': IntervalSchedule.DAYS,
        }
        schedule, _ = IntervalSchedule.objects.get_or_create(
            every=options['every'],
            period=period_map[options['period']]
        )

        kwargs = {
            'batch_size': options['batch_size'],
            'lookback_seconds': options['lookback_seconds']
        }

        task, created = PeriodicTask.objects.update_or_create(
            name=options['name'],
            defaults={
                'task': 'scheduler.tasks.dispatcher.dispatch_due_tasks',
                'interval': schedule,
                'kwargs': json.dumps(kwargs),
                'enabled': options['enabled'],
                'start_time': timezone.now(),
            },
        )

        action = 'Created' if created else 'Updated'
        self.stdout.write(self.style.SUCCESS(f"{action} PeriodicTask '{task.name}' (every {options['every']} {options['period']})"))




