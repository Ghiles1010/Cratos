import { ChevronDown } from 'lucide-react';
import type { TaskStatus } from '@/lib/api';

const STATUS_OPTIONS: { label: string; value: TaskStatus | '' }[] = [
  { label: 'All statuses', value: '' },
  { label: 'Scheduled', value: 'scheduled' },
  { label: 'Running', value: 'running' },
  { label: 'Completed', value: 'completed' },
  { label: 'Failed', value: 'failed' },
  { label: 'Cancelled', value: 'cancelled' },
];

interface StatusFilterProps {
  value: TaskStatus | '';
  onChange: (value: TaskStatus | '') => void;
}

export function StatusFilter({ value, onChange }: StatusFilterProps) {
  return (
    <div className="relative">
      <select
        value={value}
        onChange={(e) => onChange(e.target.value as TaskStatus | '')}
        className="h-7 border border-border bg-bg-input pl-2 pr-7 text-xs text-text-primary font-mono outline-none focus:border-accent appearance-none cursor-pointer"
      >
        {STATUS_OPTIONS.map((o) => (
          <option key={o.value} value={o.value}>
            {o.label}
          </option>
        ))}
      </select>
      <ChevronDown className="pointer-events-none absolute right-2 top-1/2 -translate-y-1/2 h-3 w-3 text-text-muted" />
    </div>
  );
}
