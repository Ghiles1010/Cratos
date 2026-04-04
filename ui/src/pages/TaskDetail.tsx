import { useState, useMemo } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  ArrowLeft,
  Copy,
  ExternalLink,
  Loader2,
  ChevronLeft,
  ChevronRight,
  ChevronDown,
} from 'lucide-react';
import { toast } from 'sonner';
import {
  BarChart,
  Bar,
  Cell,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
} from 'recharts';
import { useTaskDetail } from '@/hooks/useTaskDetail';
import type { TaskExecution } from '@/lib/api';
import { Badge, statusVariant } from '@/components/ui/Badge';
import { Section, Row, JsonBlock, TaskActions } from '@/components/task-detail';
import { fmtDate, relativeTime, scheduleLabel } from '@/lib/utils';

const PAGE_SIZE = 10;

export default function TaskDetail() {
  const { taskId } = useParams<{ taskId: string }>();
  const navigate = useNavigate();
  const { data: task, isLoading } = useTaskDetail(taskId ?? '');

  const [confirmDelete, setConfirmDelete] = useState(false);
  const [historyPage, setHistoryPage] = useState(1);
  const [expandedExec, setExpandedExec] = useState<number | null>(null);

  const handleCopyId = () => {
    if (task) {
      void navigator.clipboard.writeText(task.task_id);
      toast.success('Task ID copied');
    }
  };

  // Pagination for execution history
  const executions = task?.execution_history ?? [];
  const totalExecPages = Math.max(1, Math.ceil(executions.length / PAGE_SIZE));
  const pagedExecutions = useMemo(() => {
    const start = (historyPage - 1) * PAGE_SIZE;
    return executions.slice(start, start + PAGE_SIZE);
  }, [executions, historyPage]);

  // Execution stats computed from history
  const execStats = useMemo(() => {
    if (!executions.length) return null;
    const successCount = executions.filter((e: TaskExecution) => e.status === 'success').length;
    const durations = executions
      .map((e: TaskExecution) => e.duration_seconds)
      .filter((d: number | null): d is number => d !== null);
    const avgDuration =
      durations.length > 0
        ? durations.reduce((a: number, b: number) => a + b, 0) / durations.length
        : null;
    const lastFailed = [...executions]
      .reverse()
      .find((e: TaskExecution) => e.status === 'failed');
    return {
      successRate: Math.round((successCount / executions.length) * 100),
      total: executions.length,
      avgDuration,
      lastError: lastFailed?.error_type ?? null,
    };
  }, [executions]);

  // Chart data: execution status breakdown
  const chartData = useMemo(() => {
    const counts: Record<string, number> = {};
    executions.forEach((e: TaskExecution) => {
      counts[e.status] = (counts[e.status] ?? 0) + 1;
    });
    return Object.entries(counts).map(([status, count]) => ({ status, count }));
  }, [executions]);

  const statusBarColor = (status: string) => {
    if (status === 'success') return '#34d399';
    if (status === 'failed') return '#f87171';
    if (status === 'running') return '#fbbf24';
    return '#71717a';
  };

  if (isLoading || !task) {
    return (
      <div className="flex items-center justify-center py-40">
        <Loader2 className="h-6 w-6 animate-spin text-text-muted" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Back */}
      <button
        type="button"
        onClick={() => navigate('/')}
        className="inline-flex items-center gap-1.5 text-sm text-text-muted hover:text-text-primary transition-colors"
      >
        <ArrowLeft className="h-4 w-4" />
        Tasks
      </button>

      {/* Page header */}
      <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
        <div>
          <h1 className="text-2xl font-bold text-text-primary">{task.task_name}</h1>
          <div className="mt-1 flex items-center gap-2">
            <code className="text-[12px] text-text-muted font-mono">{task.task_id}</code>
            <button onClick={handleCopyId} title="Copy ID">
              <Copy className="h-3.5 w-3.5 text-text-muted hover:text-text-primary transition-colors" />
            </button>
          </div>
        </div>
        <div className="flex flex-col items-end gap-2">
          <TaskActions
            task={task}
            onDelete={() => navigate('/')}
            confirmDelete={confirmDelete}
            onConfirmDelete={setConfirmDelete}
          />
          <span className="text-xs text-text-muted">
            Updated {relativeTime(task.updated_at)}
          </span>
        </div>
      </div>

      {/* Two-column layout */}
      <div className="grid grid-cols-1 gap-4 lg:grid-cols-5">
        {/* ── LEFT (60%) ─────────────────────────────────── */}
        <div className="space-y-4 lg:col-span-3">
          {/* Schedule & Config */}
          <Section title="Schedule & Config">
            <Row
              label="Type"
              value={scheduleLabel(
                task.schedule_type,
                task.cron_expression,
                task.interval_seconds,
              )}
            />
            {task.cron_expression && (
              <Row label="Cron expression" value={task.cron_expression} />
            )}
            {task.interval_seconds !== null && task.interval_seconds !== undefined && (
              <Row label="Interval" value={`${task.interval_seconds}s`} />
            )}
            {task.schedule_time && (
              <Row label="Schedule time" value={fmtDate(task.schedule_time)} />
            )}
            <Row label="Timezone" value={task.task_timezone} />
            <Row
              label="Next run"
              value={
                task.next_run_at
                  ? `${fmtDate(task.next_run_at)} (${relativeTime(task.next_run_at)})`
                  : '—'
              }
            />
            <Row label="Last run" value={fmtDate(task.last_run_at)} />
            <Row label="Run count" value={String(task.run_count)} />
            {task.ends_at && (
              <Row label="Ends at" value={fmtDate(task.ends_at)} />
            )}
            {task.callback_url && (
              <div className="flex items-baseline justify-between gap-4">
                <span className="text-xs text-text-muted whitespace-nowrap">Callback URL</span>
                <div className="flex items-center gap-1.5 min-w-0">
                  <a
                    href={task.callback_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-xs text-accent truncate hover:underline"
                  >
                    {task.callback_url}
                  </a>
                  <a
                    href={task.callback_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="shrink-0 text-text-muted hover:text-text-primary"
                  >
                    <ExternalLink className="h-3 w-3" />
                  </a>
                </div>
              </div>
            )}
          </Section>

          {/* Execution History */}
          <div className="rounded-lg border border-border bg-bg-secondary p-3">
            <p className="text-[11px] font-semibold uppercase tracking-wider text-text-muted mb-3">
              Execution History
            </p>
            {executions.length === 0 ? (
              <p className="text-xs text-text-muted py-4 text-center">No executions recorded yet.</p>
            ) : (
              <>
                <div className="overflow-x-auto">
                  <table className="w-full text-xs">
                    <thead>
                      <tr className="border-b border-border text-text-muted">
                        <th className="pb-2 text-left font-medium pr-3">#</th>
                        <th className="pb-2 text-left font-medium pr-3">Status</th>
                        <th className="pb-2 text-left font-medium pr-3">Started</th>
                        <th className="pb-2 text-left font-medium pr-3">Duration</th>
                        <th className="pb-2 text-left font-medium pr-3">HTTP</th>
                        <th className="pb-2 text-left font-medium pr-3">Retries</th>
                        <th className="pb-2 text-left font-medium">Error</th>
                        <th className="pb-2 w-5"></th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-border">
                      {pagedExecutions.map((exec: TaskExecution) => {
                        const isExpanded = expandedExec === exec.execution_number;
                        const hasDetail = exec.result != null || exec.error_message;
                        return (
                          <>
                            <tr
                              key={exec.execution_number}
                              className={`align-top ${hasDetail ? 'cursor-pointer hover:bg-bg-card transition-colors' : ''}`}
                              onClick={() => hasDetail && setExpandedExec(isExpanded ? null : exec.execution_number)}
                            >
                              <td className="py-2 pr-3 text-text-muted font-mono">
                                {exec.execution_number}
                              </td>
                              <td className="py-2 pr-3">
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
                                  {exec.status}
                                </Badge>
                                {exec.is_retry && (
                                  <Badge variant="orange" className="ml-1">retry</Badge>
                                )}
                              </td>
                              <td className="py-2 pr-3 text-text-muted whitespace-nowrap">
                                {exec.started_at ? relativeTime(exec.started_at) : '—'}
                              </td>
                              <td className="py-2 pr-3 text-text-primary whitespace-nowrap">
                                {exec.duration_seconds !== null ? `${exec.duration_seconds.toFixed(2)}s` : '—'}
                              </td>
                              <td className="py-2 pr-3 text-text-primary">
                                {exec.http_status_code ?? '—'}
                              </td>
                              <td className="py-2 pr-3 text-text-primary">
                                {exec.retry_count}
                              </td>
                              <td className="py-2 text-red-400">
                                {exec.error_type && <span className="font-medium">{exec.error_type}</span>}
                              </td>
                              <td className="py-2 pl-2 text-text-muted">
                                {hasDetail && (
                                  <ChevronDown className={`h-3.5 w-3.5 transition-transform ${isExpanded ? 'rotate-180' : ''}`} />
                                )}
                              </td>
                            </tr>
                            {isExpanded && (
                              <tr key={`${exec.execution_number}-detail`}>
                                <td colSpan={8} className="px-2 pb-3 pt-0">
                                  <div className="rounded-md bg-bg-primary p-3 space-y-2">
                                    {exec.error_message && (
                                      <div>
                                        <p className="text-[11px] text-text-muted mb-1">Error</p>
                                        <pre className="text-xs text-red-400 whitespace-pre-wrap break-all">{exec.error_message}</pre>
                                      </div>
                                    )}
                                    {exec.result != null && (
                                      <JsonBlock label="result" data={exec.result} />
                                    )}
                                  </div>
                                </td>
                              </tr>
                            )}
                          </>
                        );
                      })}
                    </tbody>
                  </table>
                </div>

                {/* Pagination */}
                {totalExecPages > 1 && (
                  <div className="mt-3 flex items-center justify-between text-xs text-text-muted">
                    <span>
                      Page {historyPage} of {totalExecPages} &middot; {executions.length} total
                    </span>
                    <div className="flex items-center gap-1">
                      <button
                        onClick={() => setHistoryPage((p) => Math.max(1, p - 1))}
                        disabled={historyPage === 1}
                        className="rounded border border-border p-1 disabled:opacity-40 hover:bg-bg-card transition-colors"
                      >
                        <ChevronLeft className="h-3.5 w-3.5" />
                      </button>
                      <button
                        onClick={() => setHistoryPage((p) => Math.min(totalExecPages, p + 1))}
                        disabled={historyPage === totalExecPages}
                        className="rounded border border-border p-1 disabled:opacity-40 hover:bg-bg-card transition-colors"
                      >
                        <ChevronRight className="h-3.5 w-3.5" />
                      </button>
                    </div>
                  </div>
                )}
              </>
            )}
          </div>

          {/* Payload */}
          {(task.task_args.length > 0 || Object.keys(task.task_kwargs).length > 0) && (
            <Section title="Payload">
              {task.task_args.length > 0 && (
                <JsonBlock label="args" data={task.task_args} />
              )}
              {Object.keys(task.task_kwargs).length > 0 && (
                <JsonBlock label="kwargs" data={task.task_kwargs} />
              )}
            </Section>
          )}
        </div>

        {/* ── RIGHT (40%) ────────────────────────────────── */}
        <div className="space-y-4 lg:col-span-2">
          {/* Status & Health */}
          <Section title="Status & Health">
            <div className="flex flex-wrap gap-2 mb-2">
              <Badge variant={statusVariant(task.status)}>{task.status}</Badge>
              {task.is_paused && <Badge variant="orange">paused</Badge>}
              {task.is_overdue && (
                <Badge
                  variant="red"
                  title="Overdue: Task should have run but hasn't yet."
                >
                  overdue
                </Badge>
              )}
            </div>
            <Row label="Created" value={fmtDate(task.created_at)} />
            <Row label="Updated" value={fmtDate(task.updated_at)} />
            <Row label="Started" value={fmtDate(task.started_at)} />
            <Row label="Completed" value={fmtDate(task.completed_at)} />
            {task.execution_time !== null && task.execution_time !== undefined && (
              <Row label="Execution time" value={`${task.execution_time.toFixed(2)}s`} />
            )}
          </Section>

          {/* Retry Config */}
          <Section title="Retry Config">
            <Row label="Policy" value={task.retry_policy} />
            {task.retry_policy !== 'none' && (
              <>
                <Row label="Max retries" value={String(task.max_retries)} />
                <Row label="Delay" value={`${task.retry_delay_seconds}s`} />
                <div className="pt-1">
                  <div className="flex items-center justify-between mb-1">
                    <span className="text-xs text-text-muted">Retries used</span>
                    <span className="text-xs text-text-primary">
                      {task.retry_count} / {task.max_retries}
                    </span>
                  </div>
                  <div className="h-1.5 rounded-full bg-bg-primary overflow-hidden">
                    <div
                      className="h-full rounded-full bg-accent transition-all"
                      style={{
                        width:
                          task.max_retries > 0
                            ? `${Math.min(100, (task.retry_count / task.max_retries) * 100)}%`
                            : '0%',
                      }}
                    />
                  </div>
                </div>
              </>
            )}
          </Section>

          {/* Execution Stats */}
          {execStats && (
            <Section title="Execution Stats">
              <div className="grid grid-cols-2 gap-3 mb-3">
                <div className="rounded-md bg-bg-primary p-2.5 text-center">
                  <p className="text-xl font-bold text-emerald-400">
                    {execStats.successRate}%
                  </p>
                  <p className="text-[11px] text-text-muted mt-0.5">Success rate</p>
                </div>
                <div className="rounded-md bg-bg-primary p-2.5 text-center">
                  <p className="text-xl font-bold text-text-primary">
                    {execStats.total}
                  </p>
                  <p className="text-[11px] text-text-muted mt-0.5">Total runs</p>
                </div>
                {execStats.avgDuration !== null && (
                  <div className="rounded-md bg-bg-primary p-2.5 text-center col-span-2">
                    <p className="text-xl font-bold text-text-primary">
                      {execStats.avgDuration.toFixed(2)}s
                    </p>
                    <p className="text-[11px] text-text-muted mt-0.5">Avg duration</p>
                  </div>
                )}
              </div>
              {execStats.lastError && (
                <div className="rounded-md bg-red-500/10 border border-red-500/20 px-2.5 py-2">
                  <p className="text-[11px] text-text-muted mb-0.5">Last error type</p>
                  <p className="text-xs text-red-400 font-medium">{execStats.lastError}</p>
                </div>
              )}
            </Section>
          )}

          {/* Execution Status Chart */}
          {chartData.length > 0 && (
            <div className="rounded-lg border border-border bg-bg-secondary p-3">
              <p className="text-[11px] font-semibold uppercase tracking-wider text-text-muted mb-3">
                Execution Breakdown
              </p>
              <ResponsiveContainer width="100%" height={160}>
                <BarChart data={chartData} margin={{ top: 0, right: 0, left: -20, bottom: 0 }}>
                  <XAxis
                    dataKey="status"
                    tick={{ fontSize: 11, fill: '#a1a1aa' }}
                    axisLine={{ stroke: '#27272a' }}
                    tickLine={false}
                  />
                  <YAxis
                    tick={{ fontSize: 11, fill: '#a1a1aa' }}
                    axisLine={{ stroke: '#27272a' }}
                    tickLine={false}
                    allowDecimals={false}
                  />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: '#18181b',
                      border: '1px solid #27272a',
                      fontSize: 12,
                      borderRadius: 6,
                    }}
                  />
                  <Bar dataKey="count" radius={[4, 4, 0, 0]}>
                    {chartData.map((entry) => (
                      <Cell
                        key={entry.status}
                        fill={statusBarColor(entry.status)}
                      />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
