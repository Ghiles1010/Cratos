import { cn } from '@/lib/utils';

interface AutoRefreshToggleProps {
  active: boolean;
  onChange: (v: boolean) => void;
  isFetching: boolean;
}

export function AutoRefreshToggle({
  active,
  onChange,
  isFetching,
}: AutoRefreshToggleProps) {
  return (
    <button
      type="button"
      onClick={() => onChange(!active)}
      title={active ? 'Disable auto-refresh' : 'Enable auto-refresh (10s)'}
      className={cn(
        'flex items-center gap-1.5 rounded-md border px-2.5 py-1.5 text-[11px] font-medium transition-colors',
        active
          ? 'border-emerald-500/30 bg-emerald-500/10 text-emerald-400'
          : 'border-border bg-bg-card text-text-muted hover:text-text-secondary',
      )}
    >
      <span
        className={cn(
          'h-1.5 w-1.5 rounded-full',
          active
            ? isFetching
              ? 'bg-emerald-400 animate-pulse'
              : 'bg-emerald-400'
            : 'bg-text-muted',
        )}
      />
      Auto
    </button>
  );
}

