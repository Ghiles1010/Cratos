interface RowProps {
  label: string;
  value: string;
}

export function Row({ label, value }: RowProps) {
  return (
    <div className="flex items-baseline justify-between gap-4">
      <span className="text-xs text-text-muted whitespace-nowrap">{label}</span>
      <span className="text-xs text-text-primary text-right">{value}</span>
    </div>
  );
}

