import { useQuery } from '@tanstack/react-query';
import { tasks, type TaskListResponse } from '@/lib/api';

interface UseTasksOptions {
  page?: number;
  pageSize?: number;
  autoRefresh?: boolean;
  search?: string;
}

/**
 * Fetch paginated tasks with optional auto-refresh and server-side search.
 */
export function useTasks({
  page = 1,
  pageSize = 20,
  autoRefresh = false,
  search = '',
}: UseTasksOptions = {}) {
  return useQuery<TaskListResponse>({
    queryKey: ['tasks', page, pageSize, search],
    queryFn: () => tasks.list(page, pageSize, search),
    refetchInterval: autoRefresh ? 10_000 : false,
    placeholderData: (prev) => prev,
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



