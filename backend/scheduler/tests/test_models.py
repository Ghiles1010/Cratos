from django.contrib.auth.models import User
from django.test import TestCase

from scheduler.models import ScheduleType, TaskSchedule


class TaskScheduleTest(TestCase):
    def test_cron_task_is_recurring(self):
        user = User.objects.create_user("bob", password="pass")
        task = TaskSchedule.objects.create(
            task_name="my_task",
            user=user,
            schedule_type=ScheduleType.CRON,
            cron_expression="* * * * *",
        )
        self.assertTrue(task.is_recurring)
