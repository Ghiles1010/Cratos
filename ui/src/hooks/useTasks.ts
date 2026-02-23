import { useQuery } from '@tanstack/react-query';
import { tasks, type TaskListResponse } from '@/lib/api';

interface UseTasksOptions {
  page?: number;
  pageSize?: number;
  autoRefresh?: boolean;
}

/**
 * Fetch paginated tasks with optional auto-refresh.
 */
export function useTasks({
  page = 1,
  pageSize = 20,
  autoRefresh = false,
}: UseTasksOptions = {}) {
  return useQuery<TaskListResponse>({
    queryKey: ['tasks', page, pageSize],
    queryFn: () => tasks.list(page, pageSize),
    refetchInterval: autoRefresh ? 10_000 : false,
    placeholderData: (prev) => prev, // keep previous data while fetching
  });
}

/**
 * Fetch a single task by ID.
 */
export function useTask(taskId: string | null) {
  return useQuery({
    queryKey: ['task', taskId],
    queryFn: () => tasks.get(taskId!),
    enabled: !!taskId,
  });
}



