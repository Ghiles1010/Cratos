import { Badge } from '@/components/ui/Badge';
import { relativeTime } from '@/lib/utils';

interface Execution {
  execution_number: number;
  status: string;
  started_at: string | null;
  completed_at: string | null;
  duration_seconds: number | null;
  http_status_code: number | null;
  error_type: string | null;
  error_message: string | null;
  retry_count: number;
  is_retry: boolean;
}

interface ExecutionHistoryListProps {
  executions: Execution[];
}

export function ExecutionHistoryList({
  executions,
}: ExecutionHistoryListProps) {
  return (
    <div className="space-y-2 max-h-64 overflow-y-auto">
      {executions.map((exec) => (
        <div
          key={exec.execution_number}
          className="rounded border border-border bg-bg-primary p-2 text-xs"
        >
          <div className="flex items-center justify-between mb-1">
            <div className="flex items-center gap-2">
              <Badge
                variant={
                  exec.status === 'success'
                    ? 'green'
                    : exec.status === 'failed'
                      ? 'red'
                      : exec.status === 'running'
                        ? 'yellow'
                        : 'gray'
                }
              >
                #{exec.execution_number} {exec.status}
              </Badge>
              {exec.is_retry && <Badge variant="orange">retry</Badge>}
            </div>
            {exec.duration_seconds !== null && (
              <span className="text-text-muted">
                {exec.duration_seconds.toFixed(2)}s
              </span>
            )}
          </div>
          <div className="text-text-muted space-y-0.5">
            {exec.started_at && (
              <div>Started: {relativeTime(exec.started_at)}</div>
            )}
            {exec.http_status_code && (
              <div>HTTP: {exec.http_status_code}</div>
            )}
            {exec.error_type && (
              <div className="text-red-400">
                {exec.error_type}: {exec.error_message?.slice(0, 100)}
                {exec.error_message && exec.error_message.length > 100 && '…'}
              </div>
            )}
          </div>
        </div>
      ))}
    </div>
  );
}

