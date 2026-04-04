import { RefreshCw } from 'lucide-react';
import { cn, relativeTime } from '@/lib/utils';
import { useMetrics } from '@/hooks/useMetrics';

export default function Metrics() {
  const { data, isLoading, isFetching, refetch } = useMetrics();

  const totalExecutions = data
    ? Object.values(data.executions_by_status).reduce((sum, c) => sum + c, 0)
    : 0;
  const failedExecutions = data?.executions_by_status['failed'] ?? 0;
  const failRate = totalExecutions > 0
    ? ((failedExecutions / totalExecutions) * 100).toFixed(1)
    : '0.0';

  const stats = [
    {
      label: 'overdue',
      value: data?.overdue_tasks ?? 0,
      alert: (data?.overdue_tasks ?? 0) > 0,
    },
    {
      label: 'fail rate',
      value: `${failRate}%`,
      alert: parseFloat(failRate) > 10,
    },
    {
      label: 'avg duration',
      value: data ? `${data.avg_execution_duration_seconds.toFixed(3)}s` : '—',
      alert: false,
    },
  ];

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="font-mono text-lg font-bold text-text-primary tracking-tight">metrics</h1>
        <button
          type="button"
          onClick={() => void refetch()}
          disabled={isFetching}
          className={cn(
            'inline-flex items-center gap-1.5 border border-border bg-bg-card px-3 py-1.5 text-xs font-mono text-text-muted transition-colors hover:text-text-primary',
            isFetching && 'opacity-50',
          )}
        >
          <RefreshCw className={cn('h-3 w-3', isFetching && 'animate-spin')} />
          Refresh
        </button>
      </div>

      {/* Key numbers */}
      <div className="flex border border-border divide-x divide-border">
        {stats.map(({ label, value, alert }) => (
          <div key={label} className="flex-1 px-5 py-4 bg-bg-card">
            <p className={cn('font-mono text-2xl font-bold tabular-nums', alert ? 'text-red-400' : 'text-text-primary')}>
              {isLoading ? '—' : value}
            </p>
            <p className="mt-0.5 font-mono text-[11px] text-text-muted uppercase tracking-wider">{label}</p>
          </div>
        ))}
      </div>

      {/* Recent executions */}
      <div className="border border-border bg-bg-card">
        <div className="flex items-center justify-between border-b border-border px-4 py-3">
          <h2 className="font-mono text-xs font-semibold text-text-primary uppercase tracking-wider">Recent executions</h2>
          {data?.generated_at && (
            <span className="font-mono text-[11px] text-text-muted">
              {relativeTime(data.generated_at)}
            </span>
          )}
        </div>

        {isLoading ? (
          <div className="flex items-center justify-center py-12">
            <RefreshCw className="h-4 w-4 animate-spin text-text-muted" />
          </div>
        ) : !data?.recent_executions.length ? (
          <div className="flex items-center justify-center py-12">
            <p className="font-mono text-sm text-text-muted">No executions yet.</p>
          </div>
        ) : (
          <table className="w-full text-xs">
            <thead>
              <tr className="border-b border-border bg-bg-secondary">
                {['Task', 'Status', 'Started', 'Duration', 'Retries'].map((h) => (
                  <th key={h} className="px-4 py-2 text-left font-mono text-[10px] text-text-muted">
                    {h}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {data.recent_executions.map((e, idx) => (
                <tr key={`${e.task_id}-${idx}`} className="border-b border-border last:border-0 hover:bg-bg-card-hover">
                  <td className="px-4 py-2.5">
                    <p className="font-medium text-text-primary">{e.task_name}</p>
                    <p className="font-mono text-[10px] text-text-muted">{e.task_id.slice(0, 8)}</p>
                  </td>
                  <td className="px-4 py-2.5">
                    <span className={cn(
                      'font-mono text-[10px] font-semibold uppercase tracking-wider',
                      e.status === 'success' ? 'text-emerald-400' :
                      e.status === 'failed' ? 'text-red-400' : 'text-text-muted',
                    )}>
                      {e.status}{e.is_retry ? ' ·retry' : ''}
                    </span>
                  </td>
                  <td className="px-4 py-2.5 font-mono text-[11px] text-text-muted">
                    {relativeTime(e.started_at)}
                  </td>
                  <td className="px-4 py-2.5 font-mono text-[11px] text-text-muted tabular-nums">
                    {e.duration_seconds != null ? `${e.duration_seconds.toFixed(3)}s` : '—'}
                  </td>
                  <td className="px-4 py-2.5 font-mono text-[11px] text-text-muted tabular-nums">
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
