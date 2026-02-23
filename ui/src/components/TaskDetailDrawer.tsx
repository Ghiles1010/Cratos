import { useState } from 'react';
import { Loader2, ExternalLink, Copy } from 'lucide-react';
import { toast } from 'sonner';
import { useTask } from '@/hooks/useTasks';
import { Drawer, DrawerContent } from '@/components/ui/Drawer';
import { Badge, statusVariant } from '@/components/ui/Badge';
import { fmtDate, relativeTime, scheduleLabel } from '@/lib/utils';
import {
  Section,
  Row,
  JsonBlock,
  ExecutionHistoryList,
  TaskActions,
} from '@/components/task-detail';

interface Props {
  taskId: string | null;
  onClose: () => void;
}

export default function TaskDetailDrawer({ taskId, onClose }: Props) {
  const { data: task, isLoading } = useTask(taskId);
  const [confirmDelete, setConfirmDelete] = useState(false);

  const handleCopyId = () => {
    if (task) {
      void navigator.clipboard.writeText(task.task_id);
      toast.success('Task ID copied');
    }
  };

  return (
    <Drawer open={!!taskId} onOpenChange={(open) => !open && onClose()}>
      <DrawerContent title="Task Details">
        {isLoading || !task ? (
          <div className="flex items-center justify-center py-20">
            <Loader2 className="h-5 w-5 animate-spin text-text-muted" />
          </div>
        ) : (
          <div className="space-y-6">
            {/* Header */}
            <div>
              <h3 className="text-lg font-semibold text-text-primary">
                {task.task_name}
              </h3>
              <div className="mt-1 flex items-center gap-2">
                <code className="text-[11px] text-text-muted font-mono">
                  {task.task_id}
                </code>
                <button onClick={handleCopyId} title="Copy ID">
                  <Copy className="h-3 w-3 text-text-muted hover:text-text-primary" />
                </button>
              </div>
              <div className="mt-2 flex items-center gap-2">
                <Badge variant={statusVariant(task.status)}>
                  {task.status}
                </Badge>
                {task.is_paused && <Badge variant="orange">paused</Badge>}
                {task.is_overdue && (
                  <Badge
                    variant="red"
                    title="Overdue: Task should have run but hasn't yet. It will execute when the dispatcher runs."
                  >
                    overdue
                  </Badge>
                )}
              </div>
            </div>

            {/* Actions */}
            <TaskActions
              task={task}
              onDelete={onClose}
              confirmDelete={confirmDelete}
              onConfirmDelete={setConfirmDelete}
            />

            {/* Info grid */}
            <div className="space-y-3">
              <Section title="Schedule">
                <Row
                  label="Type"
                  value={scheduleLabel(
                    task.schedule_type,
                    task.cron_expression,
                    task.interval_seconds,
                  )}
                />
                {typeof task.scheduler_info?.cron_description === 'string' && (
                  <Row
                    label="Description"
                    value={task.scheduler_info.cron_description}
                  />
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
              </Section>

              <Section title="Retry">
                <Row label="Policy" value={task.retry_policy} />
                {task.retry_policy !== 'none' && (
                  <>
                    <Row
                      label="Retries"
                      value={`${task.retry_count} / ${task.max_retries}`}
                    />
                    <Row
                      label="Delay"
                      value={`${task.retry_delay_seconds}s`}
                    />
                  </>
                )}
              </Section>

              <Section title="Callback">
                <div className="flex items-center gap-2">
                  <code className="text-xs text-accent break-all">
                    {task.callback_url}
                  </code>
                  <a
                    href={task.callback_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-text-muted hover:text-text-primary"
                  >
                    <ExternalLink className="h-3 w-3" />
                  </a>
                </div>
              </Section>

              {(task.task_args.length > 0 ||
                Object.keys(task.task_kwargs).length > 0) && (
                <Section title="Payload">
                  {task.task_args.length > 0 && (
                    <JsonBlock label="args" data={task.task_args} />
                  )}
                  {Object.keys(task.task_kwargs).length > 0 && (
                    <JsonBlock label="kwargs" data={task.task_kwargs} />
                  )}
                </Section>
              )}

              {task.result !== null && task.result !== undefined && (
                <Section title="Result">
                  <JsonBlock label="result" data={task.result} />
                </Section>
              )}

              {task.execution_history && task.execution_history.length > 0 && (
                <Section title="Execution History">
                  <ExecutionHistoryList executions={task.execution_history} />
                </Section>
              )}

              <Section title="Timeline">
                <Row label="Created" value={fmtDate(task.created_at)} />
                <Row label="Started" value={fmtDate(task.started_at)} />
                <Row label="Completed" value={fmtDate(task.completed_at)} />
                {task.execution_time !== null && (
                  <Row
                    label="Duration"
                    value={`${task.execution_time.toFixed(2)}s`}
                  />
                )}
              </Section>
            </div>
          </div>
        )}
      </DrawerContent>
    </Drawer>
  );
}
