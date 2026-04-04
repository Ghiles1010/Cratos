import { RefreshCw } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { Badge, statusVariant } from '@/components/ui';
import { relativeTime, scheduleLabel } from '@/lib/utils';
import type { Task } from '@/lib/api';

interface TaskTableProps {
  tasks: Task[];
  isLoading: boolean;
}

export function TaskTable({ tasks, isLoading }: TaskTableProps) {
  const navigate = useNavigate();

  if (isLoading) {
    return (
      <div className="flex items-center justify-center border border-border py-16">
        <RefreshCw className="h-4 w-4 animate-spin text-text-muted" />
      </div>
    );
  }

  if (tasks.length === 0) {
    return (
      <div className="flex items-center justify-center border border-border py-16">
        <p className="text-sm text-text-muted">No tasks. Create one to get started.</p>
      </div>
    );
  }

  return (
    <div className="border border-border overflow-hidden">
      <table className="w-full text-sm">
        <thead>
          <tr className="border-b border-border bg-bg-secondary">
            {['Task', 'Schedule', 'Status', 'Next Run', 'Runs', 'Retries'].map((h) => (
              <th
                key={h}
                className="px-4 py-2 text-left text-[11px] font-medium text-text-muted"
              >
                {h}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {tasks.map((t) => (
            <tr
              key={t.task_id}
              onClick={() => navigate(`/tasks/${t.task_id}`)}
              className="border-b border-border last:border-0 cursor-pointer transition-colors hover:bg-bg-card group"
            >
              <td className="px-4 py-3">
                <div className="flex items-center gap-2">
                  <div className="w-0.5 h-8 rounded-full bg-transparent group-hover:bg-accent transition-colors shrink-0" />
                  <div>
                    <p className="font-medium text-text-primary">{t.task_name}</p>
                    <p className="font-mono text-[11px] text-text-muted">
                      {t.task_id.slice(0, 8)}
                    </p>
                  </div>
                </div>
              </td>
              <td className="px-4 py-3">
                <Badge variant={t.schedule_type === 'one_off' ? 'gray' : 'purple'}>
                  {scheduleLabel(t.schedule_type, t.cron_expression, t.interval_seconds)}
                </Badge>
                {t.task_timezone !== 'UTC' && (
                  <p className="mt-1 font-mono text-[11px] text-text-muted">{t.task_timezone}</p>
                )}
              </td>
              <td className="px-4 py-3">
                <div className="flex items-center gap-1.5">
                  {t.is_overdue && (
                    <span
                      className="h-1.5 w-1.5 rounded-full bg-red-400 animate-pulse-dot shrink-0"
                      title="Overdue"
                    />
                  )}
                  <Badge variant={statusVariant(t.status)}>{t.status}</Badge>
                  {t.is_paused && <Badge variant="orange">paused</Badge>}
                </div>
              </td>
              <td className="px-4 py-3 font-mono text-[12px] text-text-muted" title={t.next_run_at ?? ''}>
                {relativeTime(t.next_run_at)}
              </td>
              <td className="px-4 py-3 font-mono text-[12px] text-text-muted tabular-nums">
                {t.run_count}
              </td>
              <td className="px-4 py-3 font-mono text-[12px] text-text-muted tabular-nums">
                {t.retry_policy !== 'none' ? `${t.retry_count}/${t.max_retries}` : '—'}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
