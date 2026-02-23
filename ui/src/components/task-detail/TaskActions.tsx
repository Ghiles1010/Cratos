import { XCircle, Pause, Play, RotateCcw, Trash2 } from 'lucide-react';
import { Button } from '@/components/ui/Button';
import type { Task } from '@/lib/api';
import {
  useCancelTask,
  usePauseTask,
  useResumeTask,
  useRetryTask,
  useDeleteTask,
} from '@/hooks/useTaskActions';

interface TaskActionsProps {
  task: Task;
  onDelete: () => void;
  confirmDelete: boolean;
  onConfirmDelete: (confirm: boolean) => void;
}

export function TaskActions({
  task,
  onDelete,
  confirmDelete,
  onConfirmDelete,
}: TaskActionsProps) {
  const cancel = useCancelTask();
  const pause = usePauseTask();
  const resume = useResumeTask();
  const retry = useRetryTask();
  const del = useDeleteTask();

  const handleDelete = () => {
    if (!confirmDelete) {
      onConfirmDelete(true);
      return;
    }
    del.mutate(task.task_id, { onSuccess: onDelete });
    onConfirmDelete(false);
  };

  return (
    <div className="flex flex-wrap gap-2">
      {task.status === 'scheduled' && !task.is_paused && (
        <Button
          variant="danger"
          size="sm"
          onClick={() => cancel.mutate(task.task_id)}
          disabled={cancel.isPending}
        >
          <XCircle className="h-3.5 w-3.5" /> Cancel
        </Button>
      )}
      {task.is_recurring && !task.is_paused && task.status === 'scheduled' && (
        <Button
          variant="warning"
          size="sm"
          onClick={() => pause.mutate(task.task_id)}
          disabled={pause.isPending}
        >
          <Pause className="h-3.5 w-3.5" /> Pause
        </Button>
      )}
      {task.is_paused && (
        <Button
          variant="success"
          size="sm"
          onClick={() => resume.mutate(task.task_id)}
          disabled={resume.isPending}
        >
          <Play className="h-3.5 w-3.5" /> Resume
        </Button>
      )}
      {task.status === 'failed' && (
        <Button
          variant="success"
          size="sm"
          onClick={() => retry.mutate(task.task_id)}
          disabled={retry.isPending}
        >
          <RotateCcw className="h-3.5 w-3.5" /> Retry
        </Button>
      )}
      <Button
        variant={confirmDelete ? 'danger' : 'secondary'}
        size="sm"
        onClick={handleDelete}
        disabled={del.isPending}
      >
        <Trash2 className="h-3.5 w-3.5" />
        {confirmDelete ? 'Confirm delete?' : 'Delete'}
      </Button>
    </div>
  );
}

