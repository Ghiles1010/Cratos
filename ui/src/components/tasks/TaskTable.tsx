import { RefreshCw, AlertCircle } from 'lucide-react';
import { Badge, statusVariant } from '@/components/ui';
import { relativeTime, scheduleLabel } from '@/lib/utils';
import type { Task } from '@/lib/api';

interface TaskTableProps {
  tasks: Task[];
  isLoading: boolean;
  onSelect: (id: string) => void;
}

export function TaskTable({ tasks, isLoading, onSelect }: TaskTableProps) {
  if (isLoading) {
    return (
      <div className="flex items-center justify-center rounded-lg border border-border bg-bg-card py-16">
        <RefreshCw className="h-5 w-5 animate-spin text-text-muted" />
      </div>
    );
  }

  if (tasks.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center rounded-lg border border-border bg-bg-card py-16 gap-3">
        <AlertCircle className="h-8 w-8 text-text-muted" />
        <p className="text-sm text-text-muted">
          No tasks found. Create one to get started.
        </p>
      </div>
    );
  }

  return (
    <div className="overflow-hidden rounded-lg border border-border bg-bg-card">
      <table className="w-full text-sm">
        <thead>
          <tr className="border-b border-border bg-bg-secondary">
            {['Task', 'Schedule', 'Status', 'Next Run', 'Runs', 'Retries'].map(
              (h) => (
                <th
                  key={h}
                  className="px-4 py-2.5 text-left text-[11px] font-semibold uppercase tracking-wider text-text-muted"
                >
                  {h}
                </th>
              ),
            )}
          </tr>
        </thead>
        <tbody>
          {tasks.map((t) => (
            <tr
              key={t.task_id}
              onClick={() => onSelect(t.task_id)}
              className="border-b border-border last:border-0 cursor-pointer transition-colors hover:bg-bg-card-hover"
            >
              <td className="px-4 py-3">
                <p className="font-medium text-text-primary">{t.task_name}</p>
                <p className="mt-0.5 font-mono text-[11px] text-text-muted">
                  {t.task_id.slice(0, 8)}…
                </p>
              </td>
              <td className="px-4 py-3">
                <Badge
                  variant={t.schedule_type === 'one_off' ? 'gray' : 'purple'}
                >
                  {scheduleLabel(
                    t.schedule_type,
                    t.cron_expression,
                    t.interval_seconds,
                  )}
                </Badge>
                {t.task_timezone !== 'UTC' && (
                  <p className="mt-1 text-[11px] text-text-muted">
                    {t.task_timezone}
                  </p>
                )}
              </td>
              <td className="px-4 py-3">
                <div className="flex items-center gap-1.5">
                  {t.is_overdue && (
                    <span
                      className="h-2 w-2 rounded-full bg-red-400 animate-pulse-dot"
                      title="Overdue: Task should have run but hasn't yet. It will execute when the dispatcher runs."
                    />
                  )}
                  <Badge variant={statusVariant(t.status)}>{t.status}</Badge>
                  {t.is_paused && <Badge variant="orange">paused</Badge>}
                </div>
              </td>
              <td className="px-4 py-3 text-xs text-text-muted" title={t.next_run_at ?? ''}>
                {relativeTime(t.next_run_at)}
              </td>
              <td className="px-4 py-3 text-xs text-text-muted tabular-nums">
                {t.run_count}
              </td>
              <td className="px-4 py-3 text-xs text-text-muted tabular-nums">
                {t.retry_policy !== 'none'
                  ? `${t.retry_count}/${t.max_retries}`
                  : '—'}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

