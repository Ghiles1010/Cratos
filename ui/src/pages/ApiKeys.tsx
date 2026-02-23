import { useState, useEffect } from 'react';
import { apiKeys } from '@/lib/api';
import { Button } from '@/components/ui/Button';
import { Copy, Eye, EyeOff, RefreshCw, Loader2, AlertCircle } from 'lucide-react';
import { toast } from 'sonner';

export default function ApiKeys() {
  const [apiKey, setApiKey] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isRegenerating, setIsRegenerating] = useState(false);
  const [showKey, setShowKey] = useState(false);

  const loadKey = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const data = await apiKeys.get();
      setApiKey(data.key);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load API key');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    void loadKey();
  }, []);

  const handleRegenerate = async () => {
    if (!confirm('Regenerate API key? The old key will stop working.')) return;
    setIsRegenerating(true);
    try {
      const data = await apiKeys.regenerate();
      setApiKey(data.key);
      setShowKey(true);
      toast.success('API key regenerated');
    } catch (err) {
      toast.error(err instanceof Error ? err.message : 'Failed to regenerate');
    } finally {
      setIsRegenerating(false);
    }
  };

  const handleCopy = () => {
    if (apiKey) {
      void navigator.clipboard.writeText(apiKey);
      toast.success('API key copied to clipboard');
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-text-primary">API Keys</h1>
        <p className="mt-1 text-sm text-text-muted">
          Manage your API key for programmatic / SDK access
        </p>
      </div>

      {isLoading ? (
        <div className="flex items-center justify-center rounded-lg border border-border bg-bg-card py-16">
          <Loader2 className="h-5 w-5 animate-spin text-text-muted" />
        </div>
      ) : error ? (
        <div className="flex flex-col items-center gap-3 rounded-lg border border-red-500/30 bg-red-500/10 py-12">
          <AlertCircle className="h-8 w-8 text-red-400" />
          <p className="text-sm text-red-400">{error}</p>
          <Button variant="secondary" size="sm" onClick={() => void loadKey()}>
            Retry
          </Button>
        </div>
      ) : (
        <div className="rounded-lg border border-border bg-bg-card overflow-hidden">
          <div className="border-b border-border px-5 py-3">
            <h2 className="text-sm font-semibold text-text-primary">
              Current API Key
            </h2>
          </div>
          <div className="p-5 space-y-4">
            {apiKey ? (
              <>
                {/* Key display */}
                <div className="flex items-center gap-2 rounded-lg border border-border bg-bg-secondary px-4 py-3">
                  <code className="flex-1 text-[13px] font-mono text-text-primary break-all">
                    {showKey ? apiKey : '•'.repeat(40)}
                  </code>
                  <button
                    onClick={() => setShowKey(!showKey)}
                    className="rounded p-1.5 text-text-muted hover:text-text-primary hover:bg-bg-card-hover transition-colors"
                    title={showKey ? 'Hide' : 'Show'}
                  >
                    {showKey ? (
                      <EyeOff className="h-4 w-4" />
                    ) : (
                      <Eye className="h-4 w-4" />
                    )}
                  </button>
                </div>

                {/* Actions */}
                <div className="flex gap-2">
                  <Button variant="secondary" size="sm" onClick={handleCopy}>
                    <Copy className="h-3.5 w-3.5" /> Copy
                  </Button>
                  <Button
                    variant="danger"
                    size="sm"
                    onClick={() => void handleRegenerate()}
                    disabled={isRegenerating}
                  >
                    {isRegenerating ? (
                      <Loader2 className="h-3.5 w-3.5 animate-spin" />
                    ) : (
                      <RefreshCw className="h-3.5 w-3.5" />
                    )}
                    {isRegenerating ? 'Regenerating…' : 'Regenerate'}
                  </Button>
                </div>
              </>
            ) : (
              <p className="text-center text-sm text-text-muted py-4">
                No API key yet. One will be generated when needed.
              </p>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
