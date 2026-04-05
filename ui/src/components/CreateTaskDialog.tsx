import { Dialog, DialogContent } from '@/components/ui/Dialog';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { Select } from '@/components/ui/Select';
import {
  ScheduleFields,
  RetryFields,
  PayloadFields,
  useCreateTaskForm,
} from '@/components/create-task';

const SCHEDULE_TYPES = [
  { value: 'one_off', label: 'One-off' },
  { value: 'cron', label: 'Cron' },
  { value: 'interval', label: 'Interval' },
];

interface Props {
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

export default function CreateTaskDialog({ open, onOpenChange }: Props) {
  const { form, onSubmit, isPending } = useCreateTaskForm(() =>
    onOpenChange(false),
  );

  const {
    register,
    handleSubmit,
    watch,
    formState: { errors },
  } = form;

  const scheduleType = watch('schedule_type');
  const retryPolicy = watch('retry_policy');

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent
        title="Create Task"
        description="Schedule a new task for execution"
        className="max-w-xl"
      >
        <form
          onSubmit={(e) => {
            e.preventDefault();
            void handleSubmit(onSubmit)(e);
          }}
          className="space-y-4 max-h-[65vh] overflow-y-auto pr-1"
        >
          {/* Basic info */}
          <div className="grid grid-cols-2 gap-3">
            <Input
              id="task_name"
              label="Task Name"
              placeholder="my-task"
              error={errors.task_name?.message}
              {...register('task_name')}
            />
            <Input
              id="callback_url"
              label="Callback URL"
              placeholder="https://example.com/webhook"
              error={errors.callback_url?.message}
              {...register('callback_url')}
            />
          </div>

          {/* Schedule type */}
          <Select
            id="schedule_type"
            label="Schedule Type"
            options={SCHEDULE_TYPES}
            error={errors.schedule_type?.message}
            {...register('schedule_type')}
          />

          {/* Dynamic schedule fields */}
          <ScheduleFields
            scheduleType={scheduleType}
            register={register}
            errors={errors}
          />

          {/* Retry policy */}
          <RetryFields
            retryPolicy={retryPolicy}
            register={register}
            errors={errors}
          />

          {/* Payload */}
          <PayloadFields register={register} errors={errors} />

          {/* Submit */}
          <div className="flex justify-end gap-2 pt-3 border-t border-border">
            <Button
              type="button"
              variant="secondary"
              onClick={() => onOpenChange(false)}
            >
              Cancel
            </Button>
            <Button type="submit" disabled={isPending}>
              {isPending ? 'Creating…' : 'Create Task'}
            </Button>
          </div>
        </form>
      </DialogContent>
    </Dialog>
  );
}
