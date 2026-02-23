import { cva, type VariantProps } from 'class-variance-authority';
import { cn } from '@/lib/utils';

const badgeVariants = cva(
  'inline-flex items-center gap-1 rounded-full px-2.5 py-0.5 text-[11px] font-semibold uppercase tracking-wide',
  {
    variants: {
      variant: {
        blue: 'bg-blue-500/15 text-blue-400',
        green: 'bg-emerald-500/15 text-emerald-400',
        red: 'bg-red-500/15 text-red-400',
        yellow: 'bg-yellow-500/15 text-yellow-400',
        purple: 'bg-purple-500/15 text-purple-400',
        gray: 'bg-zinc-500/15 text-zinc-400',
        orange: 'bg-orange-500/15 text-orange-400',
      },
    },
    defaultVariants: {
      variant: 'gray',
    },
  },
);

interface BadgeProps
  extends React.HTMLAttributes<HTMLSpanElement>,
    VariantProps<typeof badgeVariants> {}

export function Badge({ className, variant, ...props }: BadgeProps) {
  return (
    <span className={cn(badgeVariants({ variant }), className)} {...props} />
  );
}

/** Get the badge variant for a task status. */
export function statusVariant(
  status: string,
): VariantProps<typeof badgeVariants>['variant'] {
  const map: Record<string, VariantProps<typeof badgeVariants>['variant']> = {
    scheduled: 'blue',
    pending: 'blue',
    running: 'yellow',
    completed: 'green',
    failed: 'red',
    cancelled: 'gray',
  };
  return map[status] ?? 'gray';
}



