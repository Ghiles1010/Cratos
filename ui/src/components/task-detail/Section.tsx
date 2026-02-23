interface SectionProps {
  title: string;
  children: React.ReactNode;
}

export function Section({ title, children }: SectionProps) {
  return (
    <div className="rounded-lg border border-border bg-bg-secondary p-3">
      <p className="text-[11px] font-semibold uppercase tracking-wider text-text-muted mb-2">
        {title}
      </p>
      <div className="space-y-1.5">{children}</div>
    </div>
  );
}

