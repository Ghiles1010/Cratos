import { UseFormRegister, FieldErrors } from 'react-hook-form';
import { Input } from '@/components/ui/Input';
import { Select } from '@/components/ui/Select';
import type { CreateTaskForm } from '@/lib/schemas';

const RETRY_POLICIES = [
  { value: 'none', label: 'No retries' },
  { value: 'fixed', label: 'Fixed delay' },
  { value: 'linear', label: 'Linear backoff' },
  { value: 'exponential', label: 'Exponential backoff' },
];

interface RetryFieldsProps {
  retryPolicy: 'none' | 'fixed' | 'linear' | 'exponential';
  register: UseFormRegister<CreateTaskForm>;
  errors: FieldErrors<CreateTaskForm>;
}

export function RetryFields({
  retryPolicy,
  register,
  errors,
}: RetryFieldsProps) {
  return (
    <div className="pt-2 border-t border-border">
      <p className="text-xs font-semibold text-text-muted uppercase tracking-wide mb-3">
        Retry Configuration
      </p>
      <Select
        id="retry_policy"
        label="Retry Policy"
        options={RETRY_POLICIES}
        error={errors.retry_policy?.message}
        {...register('retry_policy')}
      />
      {retryPolicy !== 'none' && (
        <div className="grid grid-cols-2 gap-3 mt-3">
          <Input
            id="max_retries"
            label="Max Retries"
            type="number"
            min={1}
            placeholder="3"
            error={errors.max_retries?.message}
            {...register('max_retries')}
          />
          <Input
            id="retry_delay_seconds"
            label="Retry Delay (sec)"
            type="number"
            min={1}
            placeholder="60"
            error={errors.retry_delay_seconds?.message}
            {...register('retry_delay_seconds')}
          />
        </div>
      )}
    </div>
  );
}

