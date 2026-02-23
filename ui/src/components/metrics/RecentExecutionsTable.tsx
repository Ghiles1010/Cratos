import { Activity } from 'lucide-react';
import { cn, relativeTime } from '@/lib/utils';
import type { RecentExecution } from '@/hooks/useMetrics';

interface RecentExecutionsTableProps {
  executions: RecentExecution[];
  generatedAt?: string;
}

export function RecentExecutionsTable({
  executions,
  generatedAt,
}: RecentExecutionsTableProps) {
  return (
    <div className="rounded-lg border border-border bg-bg-card">
      <div className="flex items-center justify-between border-b border-border px-4 py-3">
        <div className="flex items-center gap-2">
          <Activity className="h-4 w-4 text-accent" />
          <h2 className="text-sm font-semibold text-text-primary">
            Recent executions
          </h2>
        </div>
        {generatedAt && (
          <p className="text-[11px] text-text-muted">
            Updated {relativeTime(generatedAt)}
          </p>
        )}
      </div>
      <div className="max-h-[280px] overflow-y-auto">
        {executions.length === 0 ? (
          <div className="flex items-center justify-center py-10 text-sm text-text-muted">
            No executions yet.
          </div>
        ) : (
          <table className="w-full text-xs">
            <thead>
              <tr className="border-b border-border bg-bg-secondary">
                {['Task', 'Status', 'Started', 'Duration (s)', 'Retries'].map(
                  (h) => (
                    <th
                      key={h}
                      className="px-4 py-2 text-left text-[10px] font-semibold uppercase tracking-wide text-text-muted"
                    >
                      {h}
                    </th>
                  ),
                )}
              </tr>
            </thead>
            <tbody>
              {executions.map((e, idx) => (
                <tr
                  key={`${e.task_id}-${e.started_at}-${idx}`}
                  className="border-b border-border last:border-0"
                >
                  <td className="px-4 py-2">
                    <p className="text-[11px] font-medium text-text-primary">
                      {e.task_name}
                    </p>
                    <p className="font-mono text-[10px] text-text-muted">
                      {e.task_id.slice(0, 8)}…
                    </p>
                  </td>
                  <td className="px-4 py-2">
                    <span
                      className={cn(
                        'inline-flex rounded-full px-2 py-0.5 text-[10px] font-medium',
                        e.status === 'success'
                          ? 'bg-emerald-500/10 text-emerald-400'
                          : e.status === 'failed'
                            ? 'bg-red-500/10 text-red-400'
                            : 'bg-zinc-700/40 text-zinc-200',
                      )}
                    >
                      {e.status}
                      {e.is_retry && ' · retry'}
                    </span>
                  </td>
                  <td className="px-4 py-2 text-[11px] text-text-muted">
                    {relativeTime(e.started_at)}
                  </td>
                  <td className="px-4 py-2 text-[11px] text-text-muted tabular-nums">
                    {e.duration_seconds != null
                      ? e.duration_seconds.toFixed(3)
                      : '—'}
                  </td>
                  <td className="px-4 py-2 text-[11px] text-text-muted tabular-nums">
                    {e.retry_count}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}

