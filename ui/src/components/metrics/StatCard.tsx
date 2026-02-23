import { cn } from '@/lib/utils';

interface StatCardProps {
  label: string;
  value: number | string;
  sub: string;
  alert?: boolean;
}

export function StatCard({ label, value, sub, alert }: StatCardProps) {
  return (
    <div className="rounded-lg border border-border bg-bg-card p-4">
      <p className="text-[11px] font-medium text-text-muted">{label}</p>
      <p
        className={cn(
          'mt-1 text-2xl font-bold tabular-nums',
          alert ? 'text-red-400' : 'text-text-primary',
        )}
      >
        {value}
      </p>
      <p className="text-[11px] text-text-muted">{sub}</p>
    </div>
  );
}

