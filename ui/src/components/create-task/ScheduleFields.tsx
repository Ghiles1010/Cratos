import { UseFormRegister, FieldErrors } from 'react-hook-form';
import { Input } from '@/components/ui/Input';
import type { CreateTaskForm } from '@/lib/schemas';

interface ScheduleFieldsProps {
  scheduleType: 'one_off' | 'cron' | 'interval';
  register: UseFormRegister<CreateTaskForm>;
  errors: FieldErrors<CreateTaskForm>;
}

export function ScheduleFields({
  scheduleType,
  register,
  errors,
}: ScheduleFieldsProps) {
  return (
    <>
      {scheduleType === 'one_off' && (
        <Input
          id="schedule_time"
          label="Schedule Time (ISO 8601)"
          type="datetime-local"
          error={errors.schedule_time?.message}
          {...register('schedule_time')}
        />
      )}

      {scheduleType === 'cron' && (
        <Input
          id="cron_expression"
          label="Cron Expression"
          placeholder="*/5 * * * *"
          error={errors.cron_expression?.message}
          {...register('cron_expression')}
        />
      )}

      {scheduleType === 'interval' && (
        <Input
          id="interval_seconds"
          label="Interval (seconds)"
          type="number"
          min={1}
          placeholder="30"
          error={errors.interval_seconds?.message}
          {...register('interval_seconds')}
        />
      )}

      <Input
        id="task_timezone"
        label="Timezone"
        placeholder="UTC"
        error={errors.task_timezone?.message}
        {...register('task_timezone')}
      />
    </>
  );
}

