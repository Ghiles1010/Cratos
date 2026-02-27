import { useState, useEffect } from 'react';
import { apiKeys, webhookSecret } from '@/lib/api';
import { Button } from '@/components/ui/Button';
import { Copy, Eye, EyeOff, RefreshCw, Loader2, AlertCircle, Webhook } from 'lucide-react';
import { toast } from 'sonner';

// ── Reusable credential card ──────────────────────────────────────────────────

interface CredentialCardProps {
  title: string;
  description: string;
  value: string | null;
  isLoading: boolean;
  error: string | null;
  isActing: boolean;
  rotateLabel: string;
  rotateConfirmMessage: string;
  emptyMessage: string;
  onRetry: () => void;
  onCopy: () => void;
  onRotate: () => void;
}

function CredentialCard({
  title,
  description,
  value,
  isLoading,
  error,
  isActing,
  rotateLabel,
  rotateConfirmMessage,
  emptyMessage,
  onRetry,
  onCopy,
  onRotate,
}: CredentialCardProps) {
  const [show, setShow] = useState(false);
  const maskLength = value ? Math.min(value.length, 46) : 40;

  if (isLoading) {
    return (
      <div className="flex items-center justify-center rounded-lg border border-border bg-bg-card py-16">
        <Loader2 className="h-5 w-5 animate-spin text-text-muted" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex flex-col items-center gap-3 rounded-lg border border-red-500/30 bg-red-500/10 py-12">
        <AlertCircle className="h-8 w-8 text-red-400" />
        <p className="text-sm text-red-400">{error}</p>
        <Button variant="secondary" size="sm" onClick={onRetry}>
          Retry
        </Button>
      </div>
    );
  }

  return (
    <div className="rounded-lg border border-border bg-bg-card overflow-hidden">
      <div className="border-b border-border px-5 py-3">
        <h2 className="text-sm font-semibold text-text-primary">{title}</h2>
        <p className="mt-0.5 text-xs text-text-muted">{description}</p>
      </div>
      <div className="p-5 space-y-4">
        {value ? (
          <>
            <div className="flex items-center gap-2 rounded-lg border border-border bg-bg-secondary px-4 py-3">
              <code className="flex-1 text-[13px] font-mono text-text-primary break-all">
                {show ? value : '•'.repeat(maskLength)}
              </code>
              <button
                onClick={() => setShow(!show)}
                className="rounded p-1.5 text-text-muted hover:text-text-primary hover:bg-bg-card-hover transition-colors"
                title={show ? 'Hide' : 'Show'}
              >
                {show ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
              </button>
            </div>
            <div className="flex gap-2">
              <Button variant="secondary" size="sm" onClick={onCopy}>
                <Copy className="h-3.5 w-3.5" /> Copy
              </Button>
              <Button
                variant="danger"
                size="sm"
                onClick={() => {
                  if (!confirm(rotateConfirmMessage)) return;
                  onRotate();
                }}
                disabled={isActing}
              >
                {isActing ? (
                  <Loader2 className="h-3.5 w-3.5 animate-spin" />
                ) : (
                  <RefreshCw className="h-3.5 w-3.5" />
                )}
                {isActing ? 'Rotating…' : rotateLabel}
              </Button>
            </div>
          </>
        ) : (
          <p className="text-center text-sm text-text-muted py-4">{emptyMessage}</p>
        )}
      </div>
    </div>
  );
}

// ── Page ──────────────────────────────────────────────────────────────────────

export default function ApiKeys() {
  const [apiKey, setApiKey] = useState<string | null>(null);
  const [apiKeyLoading, setApiKeyLoading] = useState(true);
  const [apiKeyError, setApiKeyError] = useState<string | null>(null);
  const [apiKeyActing, setApiKeyActing] = useState(false);

  const [secret, setSecret] = useState<string | null>(null);
  const [secretLoading, setSecretLoading] = useState(true);
  const [secretError, setSecretError] = useState<string | null>(null);
  const [secretActing, setSecretActing] = useState(false);

  const loadApiKey = async () => {
    setApiKeyLoading(true);
    setApiKeyError(null);
    try {
      const data = await apiKeys.get();
      setApiKey(data.key);
    } catch (err) {
      setApiKeyError(err instanceof Error ? err.message : 'Failed to load API key');
    } finally {
      setApiKeyLoading(false);
    }
  };

  const loadSecret = async () => {
    setSecretLoading(true);
    setSecretError(null);
    try {
      const data = await webhookSecret.get();
      setSecret(data.secret);
    } catch (err) {
      setSecretError(err instanceof Error ? err.message : 'Failed to load webhook secret');
    } finally {
      setSecretLoading(false);
    }
  };

  useEffect(() => {
    void loadApiKey();
    void loadSecret();
  }, []);

  const handleRegenerateApiKey = async () => {
    setApiKeyActing(true);
    try {
      const data = await apiKeys.regenerate();
      setApiKey(data.key);
      toast.success('API key regenerated');
    } catch (err) {
      toast.error(err instanceof Error ? err.message : 'Failed to regenerate');
    } finally {
      setApiKeyActing(false);
    }
  };

  const handleRotateSecret = async () => {
    setSecretActing(true);
    try {
      const data = await webhookSecret.rotate();
      setSecret(data.secret);
      toast.success('Webhook signing secret rotated');
    } catch (err) {
      toast.error(err instanceof Error ? err.message : 'Failed to rotate');
    } finally {
      setSecretActing(false);
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-text-primary">Secrets</h1>
        <p className="mt-1 text-sm text-text-muted">
          Manage your credentials for programmatic access and webhook verification
        </p>
      </div>

      <CredentialCard
        title="API Key"
        description="Use this key to authenticate SDK and API requests via Authorization: Api-Key <key>"
        value={apiKey}
        isLoading={apiKeyLoading}
        error={apiKeyError}
        isActing={apiKeyActing}
        rotateLabel="Regenerate"
        rotateConfirmMessage="Regenerate API key? The old key will stop working immediately."
        emptyMessage="No API key yet. One will be generated when needed."
        onRetry={() => void loadApiKey()}
        onCopy={() => {
          if (apiKey) {
            void navigator.clipboard.writeText(apiKey);
            toast.success('API key copied to clipboard');
          }
        }}
        onRotate={() => void handleRegenerateApiKey()}
      />

      <div className="space-y-3">
        <div className="flex items-center gap-2">
          <Webhook className="h-4 w-4 text-text-muted" />
          <h2 className="text-base font-semibold text-text-primary">Webhook Signing Secret</h2>
        </div>
        <p className="text-sm text-text-muted">
          Every webhook Cratos sends to your <code className="text-xs bg-bg-secondary px-1 py-0.5 rounded">callback_url</code> is
          signed with this secret using HMAC-SHA256. Verify the{' '}
          <code className="text-xs bg-bg-secondary px-1 py-0.5 rounded">X-Cratos-Signature</code> header in your
          receiver to authenticate incoming requests.
        </p>
        <CredentialCard
          title="Current Signing Secret"
          description="Set CRATOS_WEBHOOK_SECRET in your receiver environment and use verify_webhook() from the SDK."
          value={secret}
          isLoading={secretLoading}
          error={secretError}
          isActing={secretActing}
          rotateLabel="Rotate"
          rotateConfirmMessage="Rotate webhook signing secret? Update your receiver before rotating to avoid verification failures."
          emptyMessage="No signing secret yet. One will be created when your first task fires."
          onRetry={() => void loadSecret()}
          onCopy={() => {
            if (secret) {
              void navigator.clipboard.writeText(secret);
              toast.success('Webhook secret copied to clipboard');
            }
          }}
          onRotate={() => void handleRotateSecret()}
        />
      </div>
    </div>
  );
}
