import { UseFormRegister, FieldErrors } from 'react-hook-form';
import type { CreateTaskForm } from '@/lib/schemas';

interface PayloadFieldsProps {
  register: UseFormRegister<CreateTaskForm>;
  errors: FieldErrors<CreateTaskForm>;
}

export function PayloadFields({ register, errors }: PayloadFieldsProps) {
  return (
    <div className="pt-2 border-t border-border">
      <p className="text-xs font-semibold text-text-muted uppercase tracking-wide mb-3">
        Payload (optional)
      </p>
      <div className="space-y-3">
        <div className="flex flex-col gap-1.5">
          <label className="text-[13px] font-medium text-text-secondary">
            Args (JSON array)
          </label>
          <textarea
            placeholder='["arg1", "arg2"]'
            rows={2}
            className="w-full rounded-md border border-border bg-bg-input px-3 py-2 text-sm text-text-primary font-mono placeholder:text-text-muted outline-none focus:border-accent focus:ring-2 focus:ring-accent/20 resize-none"
            {...register('task_args_json')}
          />
          {errors.task_args_json && (
            <p className="text-xs text-red-400">
              {errors.task_args_json.message}
            </p>
          )}
        </div>
        <div className="flex flex-col gap-1.5">
          <label className="text-[13px] font-medium text-text-secondary">
            Kwargs (JSON object)
          </label>
          <textarea
            placeholder='{"key": "value"}'
            rows={2}
            className="w-full rounded-md border border-border bg-bg-input px-3 py-2 text-sm text-text-primary font-mono placeholder:text-text-muted outline-none focus:border-accent focus:ring-2 focus:ring-accent/20 resize-none"
            {...register('task_kwargs_json')}
          />
          {errors.task_kwargs_json && (
            <p className="text-xs text-red-400">
              {errors.task_kwargs_json.message}
            </p>
          )}
        </div>
      </div>
    </div>
  );
}

