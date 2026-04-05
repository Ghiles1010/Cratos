import logging
from celery import shared_task
from django.utils import timezone

logger = logging.getLogger(__name__)


@shared_task(bind=True)
def debug_heartbeat(self):
    """
    Debug task that logs a heartbeat message with timestamp.
    This is useful for testing that Celery Beat is working correctly.
    """
    current_time = timezone.now().strftime("%Y-%m-%d %H:%M:%S")
    message = f"🔥 DEBUG HEARTBEAT: Task executed successfully at {current_time} (Task ID: {self.request.id})"
    
    # Log to both the logger and print for visibility
    logger.info(message)
    print(message)
    
    return {
        'status': 'success',
        'timestamp': current_time,
        'task_id': self.request.id,
        'message': 'Debug heartbeat executed successfully'
    }


@shared_task(bind=True)
def debug_counter(self, count: int = 0):
    """
    Debug task that maintains a counter for testing purposes.
    """
    count += 1
    current_time = timezone.now().strftime("%Y-%m-%d %H:%M:%S")
    message = f"🚀 DEBUG COUNTER: Execution #{count} at {current_time} (Task ID: {self.request.id})"
    
    logger.info(message)
    print(message)
    
    return {
        'status': 'success',
        'timestamp': current_time,
        'task_id': self.request.id,
        'count': count,
        'message': f'Debug counter executed successfully - count: {count}'
    }




