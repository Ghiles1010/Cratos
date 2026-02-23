interface ChartCardProps {
  title: string;
  empty: boolean;
  children: React.ReactNode;
}

export function ChartCard({ title, empty, children }: ChartCardProps) {
  return (
    <div className="rounded-lg border border-border bg-bg-card p-4">
      <div className="mb-3 flex items-center justify-between">
        <h2 className="text-sm font-semibold text-text-primary">{title}</h2>
        {empty && (
          <span className="text-[11px] text-text-muted">No data yet</span>
        )}
      </div>
      <div className="h-[220px]">
        {empty ? (
          <div className="flex h-full items-center justify-center text-xs text-text-muted">
            Waiting for activity…
          </div>
        ) : (
          children
        )}
      </div>
    </div>
  );
}

