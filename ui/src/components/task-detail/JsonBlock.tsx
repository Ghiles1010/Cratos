interface JsonBlockProps {
  label: string;
  data: unknown;
}

export function JsonBlock({ label, data }: JsonBlockProps) {
  return (
    <div>
      <p className="text-[11px] text-text-muted mb-1">{label}</p>
      <pre className="rounded border border-border bg-bg-primary p-2 text-[11px] text-accent overflow-x-auto font-mono">
        {String(JSON.stringify(data, null, 2))}
      </pre>
    </div>
  );
}

