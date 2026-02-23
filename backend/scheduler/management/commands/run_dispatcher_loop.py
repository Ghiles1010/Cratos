"""
Management command to run the dispatcher in a loop as a fallback.

This can be used if Celery Beat is unreliable. Run this in a separate container
or as a backup process.
"""

import time
import logging
from django.core.management.base import BaseCommand
from django.utils import timezone
from scheduler.tasks.dispatcher import dispatch_due_tasks

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Run dispatcher in a loop (fallback if Celery Beat is unreliable)"

    def add_arguments(self, parser):
        parser.add_argument(
            '--interval',
            type=int,
            default=10,
            help='Interval between dispatcher runs in seconds (default: 10)',
        )
        parser.add_argument(
            '--batch-size',
            type=int,
            default=100,
            help='Batch size for dispatcher (default: 100)',
        )

    def handle(self, *args, **options):
        interval = options['interval']
        batch_size = options['batch_size']

        self.stdout.write(
            self.style.SUCCESS(
                f'Starting dispatcher loop (interval={interval}s, batch_size={batch_size})'
            )
        )

        try:
            while True:
                try:
                    dispatch_due_tasks(batch_size=batch_size)
                except Exception as e:
                    logger.exception(f'Dispatcher error: {e}')
                    self.stdout.write(
                        self.style.ERROR(f'Dispatcher error: {e}')
                    )

                time.sleep(interval)

        except KeyboardInterrupt:
            self.stdout.write(self.style.SUCCESS('\nStopping dispatcher loop...'))



