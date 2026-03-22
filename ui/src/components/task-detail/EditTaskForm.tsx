import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { Input } from '@/components/ui/Input';
import { Select } from '@/components/ui/Select';
import { Button } from '@/components/ui/Button';
import type { Task } from '@/lib/api';

const editTaskSchema = z.object({
  task_name: z.string().min(1, 'Required').max(255),
  callback_url: z
    .string()
    .url('Must be a valid URL')
    .refine((v) => v.startsWith('http://') || v.startsWith('https://'), 'Must be HTTP or HTTPS'),
  cron_expression: z.string().optional(),
  interval_seconds: z.number().int().positive().optional(),
  task_timezone: z.string().min(1, 'Required'),
  ends_at: z.string().optional(),
  retry_policy: z.enum(['none', 'fixed', 'linear', 'exponential']),
  max_retries: z.number().int().min(0),
  retry_delay_seconds: z.number().int().min(1),
});

type EditTaskFormValues = z.infer<typeof editTaskSchema>;

interface Props {
  task: Task;
  onSubmit: (values: Partial<EditTaskFormValues>) => void;
  onCancel: () => void;
  isSubmitting: boolean;
}

export function EditTaskForm({ task, onSubmit, onCancel, isSubmitting }: Props) {
  const {
    register,
    handleSubmit,
    watch,
    formState: { errors },
  } = useForm<EditTaskFormValues>({
    resolver: zodResolver(editTaskSchema),
    defaultValues: {
      task_name: task.task_name,
      callback_url: task.callback_url,
      cron_expression: task.cron_expression ?? '',
      interval_seconds: task.interval_seconds ?? undefined,
      task_timezone: task.task_timezone,
      ends_at: task.ends_at ?? '',
      retry_policy: task.retry_policy,
      max_retries: task.max_retries,
      retry_delay_seconds: task.retry_delay_seconds,
    },
  });

  const retryPolicy = watch('retry_policy');

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
      <div className="grid grid-cols-2 gap-3">
        <Input
          id="task_name"
          label="Task name"
          error={errors.task_name?.message}
          {...register('task_name')}
        />
        <Input
          id="callback_url"
          label="Callback URL"
          error={errors.callback_url?.message}
          {...register('callback_url')}
        />
      </div>

      {task.schedule_type === 'cron' && (
        <Input
          id="cron_expression"
          label="Cron expression"
          error={errors.cron_expression?.message}
          {...register('cron_expression')}
        />
      )}

      {task.schedule_type === 'interval' && (
        <Input
          id="interval_seconds"
          label="Interval (seconds)"
          type="number"
          min={1}
          error={errors.interval_seconds?.message}
          {...register('interval_seconds')}
        />
      )}

      <div className="grid grid-cols-2 gap-3">
        <Input
          id="task_timezone"
          label="Timezone"
          error={errors.task_timezone?.message}
          {...register('task_timezone')}
        />
        <Input
          id="ends_at"
          label="Ends at (optional)"
          type="datetime-local"
          error={errors.ends_at?.message}
          {...register('ends_at')}
        />
      </div>

      <div className="rounded-md border border-border p-3 space-y-3">
        <p className="text-[11px] font-semibold uppercase tracking-wider text-text-muted">Retry</p>
        <Select
          id="retry_policy"
          label="Policy"
          options={[
            { value: 'none', label: 'No retries' },
            { value: 'fixed', label: 'Fixed delay' },
            { value: 'linear', label: 'Linear backoff' },
            { value: 'exponential', label: 'Exponential backoff' },
          ]}
          {...register('retry_policy')}
        />
        {retryPolicy !== 'none' && (
          <div className="grid grid-cols-2 gap-3">
            <Input
              id="max_retries"
              label="Max retries"
              type="number"
              min={1}
              error={errors.max_retries?.message}
              {...register('max_retries')}
            />
            <Input
              id="retry_delay_seconds"
              label="Delay (seconds)"
              type="number"
              min={1}
              error={errors.retry_delay_seconds?.message}
              {...register('retry_delay_seconds')}
            />
          </div>
        )}
      </div>

      <div className="flex items-center justify-end gap-2 pt-1">
        <Button type="button" variant="secondary" size="sm" onClick={onCancel}>
          Cancel
        </Button>
        <Button type="submit" size="sm" disabled={isSubmitting}>
          {isSubmitting ? 'Saving…' : 'Save changes'}
        </Button>
      </div>
    </form>
  );
}
