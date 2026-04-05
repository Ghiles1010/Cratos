import { useForm, type UseFormReturn } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { createTaskSchema, type CreateTaskForm } from '@/lib/schemas';
import { useCreateTask } from '@/hooks/useTaskActions';

export function useCreateTaskForm(onSuccess: () => void) {
  const create = useCreateTask();
  const form: UseFormReturn<CreateTaskForm> = useForm<CreateTaskForm>({
    resolver: zodResolver(createTaskSchema) as any,
    defaultValues: {
      task_name: '',
      callback_url: '',
      schedule_type: 'one_off' as const,
      task_timezone: 'UTC',
      retry_policy: 'none' as const,
      max_retries: 0,
      retry_delay_seconds: 60,
      schedule_time: '',
      cron_expression: '',
      interval_seconds: undefined as number | undefined,
      ends_at: '',
      task_args_json: '',
      task_kwargs_json: '',
    },
  });

  const onSubmit = (data: CreateTaskForm) => {
    const payload: Record<string, unknown> = {
      task_name: data.task_name,
      callback_url: data.callback_url,
      schedule_type: data.schedule_type,
      task_timezone: data.task_timezone,
    };

    if (data.schedule_type === 'one_off' && data.schedule_time)
      payload.schedule_time = data.schedule_time;
    if (data.schedule_type === 'cron')
      payload.cron_expression = data.cron_expression;
    if (data.schedule_type === 'interval')
      payload.interval_seconds = data.interval_seconds;
    if (data.ends_at) payload.ends_at = data.ends_at;

    if (data.retry_policy !== 'none') {
      payload.retry_policy = data.retry_policy;
      payload.max_retries = data.max_retries;
      payload.retry_delay_seconds = data.retry_delay_seconds;
    }

    // Parse JSON args/kwargs
    if (data.task_args_json) {
      try {
        payload.task_args = JSON.parse(data.task_args_json);
      } catch {
        // validated by zod
      }
    }
    if (data.task_kwargs_json) {
      try {
        payload.task_kwargs = JSON.parse(data.task_kwargs_json);
      } catch {
        // validated by zod
      }
    }

    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    create.mutate(payload as any, {
      onSuccess: () => {
        form.reset();
        onSuccess();
      },
    });
  };

  return { form, onSubmit, isPending: create.isPending };
}

