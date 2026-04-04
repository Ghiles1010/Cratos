import { useState, useMemo } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  ArrowLeft,
  Copy,
  Loader2,
  ChevronLeft,
  ChevronRight,
  ChevronDown,
} from 'lucide-react';
import { toast } from 'sonner';
import { useTaskDetail } from '@/hooks/useTaskDetail';
import type { TaskExecution } from '@/lib/api';
import { Badge, statusVariant } from '@/components/ui/Badge';
import { JsonBlock, TaskActions, EditTaskForm } from '@/components/task-detail';
import { fmtDate, relativeTime, scheduleLabel } from '@/lib/utils';
import { useUpdateTask } from '@/hooks/useTaskActions';
import type { CreateTaskPayload } from '@/lib/api';

const PAGE_SIZE = 10;

export default function TaskDetail() {
  const { taskId } = useParams<{ taskId: string }>();
  const navigate = useNavigate();
  const { data: task, isLoading } = useTaskDetail(taskId ?? '');

  const [editing, setEditing] = useState(false);
  const [confirmDelete, setConfirmDelete] = useState(false);
  const updateTask = useUpdateTask();
  const [historyPage, setHistoryPage] = useState(1);
  const [expandedExec, setExpandedExec] = useState<number | null>(null);
  const [payloadOpen, setPayloadOpen] = useState(false);

  const executions = task?.execution_history ?? [];
  const totalExecPages = Math.max(1, Math.ceil(executions.length / PAGE_SIZE));
  const pagedExecutions = useMemo(() => {
    const start = (historyPage - 1) * PAGE_SIZE;
    return executions.slice(start, start + PAGE_SIZE);
  }, [executions, historyPage]);

  const hasPayload = task && (task.task_args.length > 0 || Object.keys(task.task_kwargs).length > 0);

  if (isLoading || !task) {
    return (
      <div className="flex items-center justify-center py-40">
        <Loader2 className="h-5 w-5 animate-spin text-text-muted" />
      </div>
    );
  }

  // Build info bar items
  const infoItems = [
    {
      label: 'schedule',
      value: scheduleLabel(task.schedule_type, task.cron_expression, task.interval_seconds),
    },
    {
      label: 'next run',
      value: task.next_run_at ? relativeTime(task.next_run_at) : '—',
      title: task.next_run_at ? fmtDate(task.next_run_at) : undefined,
    },
    {
      label: 'last run',
      value: task.last_run_at ? relativeTime(task.last_run_at) : '—',
      title: task.last_run_at ? fmtDate(task.last_run_at) : undefined,
    },
    { label: 'runs', value: String(task.run_count) },
    {
      label: 'retry',
      value: task.retry_policy === 'none'
        ? 'none'
        : `${task.retry_policy} · ${task.retry_count}/${task.max_retries} · ${task.retry_delay_seconds}s`,
    },
    ...(task.task_timezone !== 'UTC' ? [{ label: 'tz', value: task.task_timezone }] : []),
    ...(task.ends_at ? [{ label: 'ends', value: fmtDate(task.ends_at) }] : []),
  ];

  return (
    <div className="space-y-6">
      {/* Back */}
      <button
        type="button"
        onClick={() => navigate('/')}
        className="inline-flex items-center gap-1.5 font-mono text-xs text-text-muted hover:text-text-primary transition-colors"
      >
        <ArrowLeft className="h-3.5 w-3.5" />
        tasks
      </button>

      {/* Header */}
      <div className="flex items-start justify-between gap-4">
        <div className="min-w-0">
          <div className="flex items-center gap-3 flex-wrap">
            <h1 className="font-mono text-xl font-bold text-text-primary">{task.task_name}</h1>
            <Badge variant={statusVariant(task.status)}>{task.status}</Badge>
            {task.is_paused && <Badge variant="orange">paused</Badge>}
            {task.is_overdue && <Badge variant="red">overdue</Badge>}
          </div>
          <div className="mt-2 flex items-center gap-3">
            <span className="font-mono text-[12px] text-text-muted truncate">
              {task.callback_url}
            </span>
            <button
              onClick={() => {
                void navigator.clipboard.writeText(task.task_id);
                toast.success('Task ID copied');
              }}
              title={task.task_id}
              className="font-mono text-[11px] text-text-muted hover:text-text-primary transition-colors shrink-0"
            >
              <Copy className="h-3 w-3 inline mr-1" />
              {task.task_id.slice(0, 8)}
            </button>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={() => setEditing((e) => !e)}
            className={`font-mono text-xs border border-border px-3 py-1.5 transition-colors ${editing ? 'border-accent text-accent' : 'text-text-muted hover:text-text-primary'}`}
          >
            {editing ? 'Cancel' : 'Edit'}
          </button>
          <TaskActions
            task={task}
            onDelete={() => navigate('/')}
            confirmDelete={confirmDelete}
            onConfirmDelete={setConfirmDelete}
          />
        </div>
      </div>

      {/* Info bar */}
      <div className="flex border border-border divide-x divide-border">
        {infoItems.map(({ label, value, title }) => (
          <div key={label} className="flex-1 px-4 py-2.5 bg-bg-card" title={title}>
            <p className="font-mono text-[10px] text-text-muted uppercase tracking-wider">{label}</p>
            <p className="font-mono text-[13px] text-text-primary mt-0.5">{value}</p>
          </div>
        ))}
      </div>

      {/* Inline edit form */}
      {editing && (
        <div className="border border-border bg-bg-card p-5">
          <p className="font-mono text-[11px] text-text-muted uppercase tracking-wider mb-4">Edit task</p>
          <EditTaskForm
            task={task}
            isSubmitting={updateTask.isPending}
            onCancel={() => setEditing(false)}
            onSubmit={(values: Partial<CreateTaskPayload>) => {
              updateTask.mutate(
                { id: task.task_id, payload: values },
                { onSuccess: () => setEditing(false) },
              );
            }}
          />
        </div>
      )}

      {/* Execution history */}
      <div className="border border-border">
        <div className="border-b border-border px-4 py-2.5 bg-bg-secondary flex items-center justify-between">
          <span className="font-mono text-[11px] text-text-muted uppercase tracking-wider">
            Execution history
            {executions.length > 0 && <span className="ml-2 text-text-primary">{executions.length}</span>}
          </span>
        </div>

        {executions.length === 0 ? (
          <div className="flex items-center justify-center py-12">
            <p className="font-mono text-sm text-text-muted">No executions yet.</p>
          </div>
        ) : (
          <>
            <table className="w-full text-xs">
              <thead>
                <tr className="border-b border-border bg-bg-secondary">
                  {['#', 'Status', 'Started', 'Duration', 'HTTP', 'Retries', 'Error', ''].map((h) => (
                    <th key={h} className="px-4 py-2 text-left font-mono text-[10px] text-text-muted">
                      {h}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody className="divide-y divide-border">
                {pagedExecutions.map((exec: TaskExecution) => {
                  const isExpanded = expandedExec === exec.execution_number;
                  const hasDetail = exec.result != null || !!exec.error_message;
                  return (
                    <>
                      <tr
                        key={exec.execution_number}
                        onClick={() => hasDetail && setExpandedExec(isExpanded ? null : exec.execution_number)}
                        className={`hover:bg-bg-card transition-colors ${hasDetail ? 'cursor-pointer' : ''}`}
                      >
                        <td className="px-4 py-2.5 font-mono text-text-muted">{exec.execution_number}</td>
                        <td className="px-4 py-2.5">
                          <div className="flex items-center gap-1.5">
                            <Badge variant={
                              exec.status === 'success' ? 'green' :
                              exec.status === 'failed' ? 'red' :
                              exec.status === 'running' ? 'yellow' : 'gray'
                            }>
                              {exec.status}
                            </Badge>
                            {exec.is_retry && <Badge variant="orange">retry</Badge>}
                          </div>
                        </td>
                        <td className="px-4 py-2.5 font-mono text-text-muted whitespace-nowrap">
                          {exec.started_at ? relativeTime(exec.started_at) : '—'}
                        </td>
                        <td className="px-4 py-2.5 font-mono text-text-primary tabular-nums">
                          {exec.duration_seconds != null ? `${exec.duration_seconds.toFixed(2)}s` : '—'}
                        </td>
                        <td className="px-4 py-2.5 font-mono text-text-primary tabular-nums">
                          {exec.http_status_code ?? '—'}
                        </td>
                        <td className="px-4 py-2.5 font-mono text-text-muted tabular-nums">
                          {exec.retry_count}
                        </td>
                        <td className="px-4 py-2.5 font-mono text-red-400 text-[11px]">
                          {exec.error_type ?? ''}
                        </td>
                        <td className="px-4 py-2.5 text-text-muted">
                          {hasDetail && (
                            <ChevronDown className={`h-3.5 w-3.5 transition-transform ${isExpanded ? 'rotate-180' : ''}`} />
                          )}
                        </td>
                      </tr>
                      {isExpanded && (
                        <tr key={`${exec.execution_number}-detail`}>
                          <td colSpan={8} className="px-4 pb-3 pt-0">
                            <div className="bg-bg-primary p-3 space-y-2 mt-1">
                              {exec.error_message && (
                                <div>
                                  <p className="font-mono text-[10px] text-text-muted mb-1 uppercase">error</p>
                                  <pre className="font-mono text-xs text-red-400 whitespace-pre-wrap break-all">{exec.error_message}</pre>
                                </div>
                              )}
                              {exec.result != null && <JsonBlock label="result" data={exec.result} />}
                            </div>
                          </td>
                        </tr>
                      )}
                    </>
                  );
                })}
              </tbody>
            </table>

            {totalExecPages > 1 && (
              <div className="flex items-center justify-between border-t border-border px-4 py-2.5">
                <span className="font-mono text-[11px] text-text-muted">
                  {historyPage}/{totalExecPages} · {executions.length} total
                </span>
                <div className="flex items-center gap-1">
                  <button
                    onClick={() => setHistoryPage((p) => Math.max(1, p - 1))}
                    disabled={historyPage === 1}
                    className="border border-border p-1 text-text-muted hover:text-text-primary disabled:opacity-40 transition-colors"
                  >
                    <ChevronLeft className="h-3.5 w-3.5" />
                  </button>
                  <button
                    onClick={() => setHistoryPage((p) => Math.min(totalExecPages, p + 1))}
                    disabled={historyPage === totalExecPages}
                    className="border border-border p-1 text-text-muted hover:text-text-primary disabled:opacity-40 transition-colors"
                  >
                    <ChevronRight className="h-3.5 w-3.5" />
                  </button>
                </div>
              </div>
            )}
          </>
        )}
      </div>

      {/* Payload (collapsible) */}
      {hasPayload && (
        <div className="border border-border">
          <button
            onClick={() => setPayloadOpen((o) => !o)}
            className="w-full flex items-center justify-between px-4 py-2.5 bg-bg-secondary hover:bg-bg-card transition-colors"
          >
            <span className="font-mono text-[11px] text-text-muted uppercase tracking-wider">Payload</span>
            <ChevronDown className={`h-3.5 w-3.5 text-text-muted transition-transform ${payloadOpen ? 'rotate-180' : ''}`} />
          </button>
          {payloadOpen && (
            <div className="p-4 space-y-2">
              {task.task_args.length > 0 && <JsonBlock label="args" data={task.task_args} />}
              {Object.keys(task.task_kwargs).length > 0 && <JsonBlock label="kwargs" data={task.task_kwargs} />}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
