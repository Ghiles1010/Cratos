import { z } from 'zod';

export const createTaskSchema = z
  .object({
    task_name: z.string().min(1, 'Task name is required').max(255),
    callback_url: z
      .string()
      .url('Must be a valid URL')
      .refine(
        (v) => v.startsWith('http://') || v.startsWith('https://'),
        'Must be HTTP or HTTPS',
      ),
    schedule_type: z.enum(['one_off', 'cron', 'interval']),

    // One-off
    schedule_time: z.string().optional(),

    // Cron
    cron_expression: z.string().optional(),

    // Interval
    interval_seconds: z.coerce.number().int().positive().optional(),

    // Common
    task_timezone: z.string().default('UTC'),
    ends_at: z.string().optional(),

    // Retry
    retry_policy: z.enum(['none', 'fixed', 'linear', 'exponential']).default('none'),
    max_retries: z.coerce.number().int().min(0).default(0),
    retry_delay_seconds: z.coerce.number().int().min(1).default(60),

    // Payload
    task_args_json: z.string().optional(),
    task_kwargs_json: z.string().optional(),
  })
  .superRefine((data, ctx) => {
    if (data.schedule_type === 'cron' && !data.cron_expression) {
      ctx.addIssue({
        code: z.ZodIssueCode.custom,
        message: 'Cron expression is required',
        path: ['cron_expression'],
      });
    }
    if (data.schedule_type === 'interval' && !data.interval_seconds) {
      ctx.addIssue({
        code: z.ZodIssueCode.custom,
        message: 'Interval seconds is required',
        path: ['interval_seconds'],
      });
    }
    if (
      data.retry_policy !== 'none' &&
      (!data.max_retries || data.max_retries === 0)
    ) {
      ctx.addIssue({
        code: z.ZodIssueCode.custom,
        message: 'Must be > 0 when retry policy is set',
        path: ['max_retries'],
      });
    }
    // Validate JSON strings
    if (data.task_args_json) {
      try {
        const parsed = JSON.parse(data.task_args_json);
        if (!Array.isArray(parsed)) {
          ctx.addIssue({
            code: z.ZodIssueCode.custom,
            message: 'Must be a JSON array',
            path: ['task_args_json'],
          });
        }
      } catch {
        ctx.addIssue({
          code: z.ZodIssueCode.custom,
          message: 'Invalid JSON',
          path: ['task_args_json'],
        });
      }
    }
    if (data.task_kwargs_json) {
      try {
        const parsed = JSON.parse(data.task_kwargs_json);
        if (typeof parsed !== 'object' || Array.isArray(parsed)) {
          ctx.addIssue({
            code: z.ZodIssueCode.custom,
            message: 'Must be a JSON object',
            path: ['task_kwargs_json'],
          });
        }
      } catch {
        ctx.addIssue({
          code: z.ZodIssueCode.custom,
          message: 'Invalid JSON',
          path: ['task_kwargs_json'],
        });
      }
    }
  });

export type CreateTaskForm = z.infer<typeof createTaskSchema>;



