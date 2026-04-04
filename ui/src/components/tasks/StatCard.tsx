import { cn } from '@/lib/utils';

interface StatBarProps {
  total: number;
  scheduled: number;
  recurring: number;
  failed: number;
}

export function StatBar({ total, scheduled, recurring, failed }: StatBarProps) {
  const items = [
    { label: 'total', value: total },
    { label: 'scheduled', value: scheduled },
    { label: 'recurring', value: recurring },
    { label: 'failed', value: failed, alert: failed > 0 },
  ];

  return (
    <div className="flex items-center gap-0 border border-border divide-x divide-border overflow-hidden rounded">
      {items.map(({ label, value, alert }) => (
        <div key={label} className="flex items-baseline gap-2 px-4 py-2.5 bg-bg-card flex-1">
          <span className={cn('text-xl font-mono font-bold tabular-nums', alert ? 'text-red-400' : 'text-text-primary')}>
            {value}
          </span>
          <span className="text-[11px] text-text-muted uppercase tracking-wider">{label}</span>
        </div>
      ))}
    </div>
  );
}

// Keep StatCard exported to avoid breaking other imports
export function StatCard({ label, value, sub, alert }: { label: string; value: number; sub: string; alert?: boolean }) {
  return (
    <div className="border border-border bg-bg-card p-4 rounded">
      <p className="text-xs text-text-muted">{label}</p>
      <p className={cn('mt-1 text-2xl font-mono font-bold tabular-nums', alert ? 'text-red-400' : 'text-text-primary')}>
        {value}
      </p>
      <p className="text-[11px] text-text-muted">{sub}</p>
    </div>
  );
}
