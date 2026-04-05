import { useQuery } from '@tanstack/react-query';
import { tasks, type Task } from '@/lib/api';

/**
 * Fetch a single task by ID, auto-refetching every 10 seconds.
 */
export function useTaskDetail(taskId: string) {
  return useQuery<Task>({
    queryKey: ['task', taskId],
    queryFn: () => tasks.get(taskId),
    enabled: !!taskId,
    refetchInterval: 10_000,
  });
}
