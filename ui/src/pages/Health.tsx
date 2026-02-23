import { useEffect, useState } from 'react';
import { health } from '@/lib/api';
import { Button } from '@/components/ui/Button';
import { RefreshCw, Loader2 } from 'lucide-react';
import { cn } from '@/lib/utils';

export default function Health() {
  const [data, setData] = useState<{ status: string; service: string } | null>(
    null,
  );
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(false);

  const check = async () => {
    setIsLoading(true);
    setError(false);
    try {
      const result = await health.check();
      setData(result);
    } catch {
      setError(true);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    void check();
  }, []);

  const isHealthy = data && !error;

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-text-primary">Health</h1>

      <div className="flex items-center justify-between rounded-lg border border-border bg-bg-card p-5">
        <div className="flex items-center gap-3">
          {isLoading ? (
            <Loader2 className="h-4 w-4 animate-spin text-text-muted" />
          ) : (
            <span
              className={cn(
                'h-3 w-3 rounded-full',
                isHealthy
                  ? 'bg-emerald-400 shadow-[0_0_8px_rgba(34,197,94,0.5)]'
                  : 'bg-red-400 shadow-[0_0_8px_rgba(239,68,68,0.5)]',
              )}
            />
          )}
          <span className="text-sm font-medium text-text-primary">
            {isLoading
              ? 'Checking…'
              : isHealthy
                ? `${data.service} — ${data.status}`
                : 'Unreachable'}
          </span>
        </div>
        <Button
          variant="secondary"
          size="sm"
          onClick={() => void check()}
          disabled={isLoading}
        >
          <RefreshCw
            className={cn('h-3.5 w-3.5', isLoading && 'animate-spin')}
          />
          Refresh
        </Button>
      </div>
    </div>
  );
}



