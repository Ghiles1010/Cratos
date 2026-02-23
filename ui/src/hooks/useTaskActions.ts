import { useMutation, useQueryClient } from '@tanstack/react-query';
import { tasks, type CreateTaskPayload } from '@/lib/api';
import { toast } from 'sonner';

/** Invalidate all task-related queries. */
function useInvalidateTasks() {
  const qc = useQueryClient();
  return () => qc.invalidateQueries({ queryKey: ['tasks'] });
}

export function useCreateTask() {
  const invalidate = useInvalidateTasks();
  return useMutation({
    mutationFn: (payload: CreateTaskPayload) => tasks.create(payload),
    onSuccess: (data) => {
      toast.success(`Task "${data.task_name}" created`);
      invalidate();
    },
    onError: (err: Error) => toast.error(`Create failed: ${err.message}`),
  });
}

export function useCancelTask() {
  const invalidate = useInvalidateTasks();
  return useMutation({
    mutationFn: (id: string) => tasks.cancel(id),
    onSuccess: () => { toast.success('Task cancelled'); invalidate(); },
    onError: (err: Error) => toast.error(err.message),
  });
}

export function usePauseTask() {
  const invalidate = useInvalidateTasks();
  return useMutation({
    mutationFn: (id: string) => tasks.pause(id),
    onSuccess: () => { toast.success('Task paused'); invalidate(); },
    onError: (err: Error) => toast.error(err.message),
  });
}

export function useResumeTask() {
  const invalidate = useInvalidateTasks();
  return useMutation({
    mutationFn: (id: string) => tasks.resume(id),
    onSuccess: () => { toast.success('Task resumed'); invalidate(); },
    onError: (err: Error) => toast.error(err.message),
  });
}

export function useRetryTask() {
  const invalidate = useInvalidateTasks();
  return useMutation({
    mutationFn: (id: string) => tasks.retry(id),
    onSuccess: () => { toast.success('Task queued for retry'); invalidate(); },
    onError: (err: Error) => toast.error(err.message),
  });
}

export function useDeleteTask() {
  const invalidate = useInvalidateTasks();
  return useMutation({
    mutationFn: (id: string) => tasks.delete(id),
    onSuccess: () => { toast.success('Task deleted'); invalidate(); },
    onError: (err: Error) => toast.error(err.message),
  });
}



