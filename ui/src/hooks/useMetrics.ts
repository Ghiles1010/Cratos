import { useQuery } from '@tanstack/react-query';

type TasksByStatus = Record<string, number>;
type ExecutionsByStatus = Record<string, number>;

export interface RecentExecution {
  task_id: string;
  task_name: string;
  status: string;
  started_at: string;
  completed_at: string | null;
  duration_seconds: number | null;
  retry_count: number;
  is_retry: boolean;
  execution_number?: number;
}

export interface MetricsResponse {
  generated_at: string;
  tasks_by_status: TasksByStatus;
  executions_by_status: ExecutionsByStatus;
  overdue_tasks: number;
  avg_execution_duration_seconds: number;
  recent_executions: RecentExecution[];
}

const BASE = import.meta.env.VITE_SCHEDULER_API_URL || 'http://localhost:9101';

export function useMetrics() {
  return useQuery<MetricsResponse>({
    queryKey: ['metrics'],
    queryFn: async () => {
      const res = await fetch(`${BASE}/metrics/json/`, {
        credentials: 'include',
      });
      if (!res.ok) {
        throw new Error(`HTTP ${res.status}`);
      }
      return (await res.json()) as MetricsResponse;
    },
    refetchInterval: 15_000,
  });
}

