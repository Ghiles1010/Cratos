import { useState } from 'react';
import { relativeTime } from '@/lib/utils';
import type { TaskExecution } from '@/lib/api';

interface Props {
  executions: TaskExecution[];
}

const statusColor = (status: string) => {
  if (status === 'success') return 'bg-emerald-400';
  if (status === 'failed') return 'bg-red-400';
  if (status === 'running') return 'bg-yellow-400 animate-pulse';
  return 'bg-zinc-600';
};

export function ExecutionTimeline({ executions }: Props) {
  const [tooltip, setTooltip] = useState<{ exec: TaskExecution; x: number; y: number } | null>(null);

  if (executions.length === 0) return null;

  // Show last 60, oldest left → newest right
  const visible = [...executions].reverse().slice(-60);

  return (
    <div className="border border-border bg-bg-card px-4 py-3">
      <p className="font-mono text-[10px] text-text-muted uppercase tracking-wider mb-2">
        Timeline · last {visible.length} runs
      </p>
      <div className="flex items-end gap-0.5 h-8 relative">
        {visible.map((exec) => (
          <div
            key={exec.execution_number}
            className={`flex-1 min-w-[4px] max-w-[16px] rounded-sm cursor-default transition-opacity hover:opacity-70 ${statusColor(exec.status)}`}
            style={{
              height: exec.duration_seconds
                ? `${Math.max(20, Math.min(100, (exec.duration_seconds / 5) * 100))}%`
                : '40%',
            }}
            onMouseEnter={(e) => {
              const rect = e.currentTarget.getBoundingClientRect();
              setTooltip({ exec, x: rect.left, y: rect.top });
            }}
            onMouseLeave={() => setTooltip(null)}
          />
        ))}
      </div>

      {/* Tooltip */}
      {tooltip && (
        <div
          className="fixed z-50 border border-border bg-bg-card px-3 py-2 text-xs pointer-events-none shadow-lg"
          style={{ left: tooltip.x, top: tooltip.y - 80 }}
        >
          <p className={`font-mono font-semibold ${
            tooltip.exec.status === 'success' ? 'text-emerald-400' :
            tooltip.exec.status === 'failed' ? 'text-red-400' : 'text-text-muted'
          }`}>
            {tooltip.exec.status}
            {tooltip.exec.is_retry ? ' · retry' : ''}
          </p>
          <p className="font-mono text-text-muted mt-0.5">
            {tooltip.exec.started_at ? relativeTime(tooltip.exec.started_at) : '—'}
          </p>
          {tooltip.exec.duration_seconds != null && (
            <p className="font-mono text-text-muted">{tooltip.exec.duration_seconds.toFixed(2)}s</p>
          )}
          {tooltip.exec.error_type && (
            <p className="font-mono text-red-400 mt-0.5">{tooltip.exec.error_type}</p>
          )}
        </div>
      )}
    </div>
  );
}
