import { useState, useEffect } from 'react';
import { allowedOrigins, type AllowedOrigin } from '@/lib/api';
import { Button } from '@/components/ui/Button';
import { Plus, Trash2, Loader2, AlertCircle, ShieldCheck } from 'lucide-react';
import { toast } from 'sonner';

export default function AllowedOrigins() {
  const [origins, setOrigins] = useState<AllowedOrigin[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [deleting, setDeleting] = useState<number | null>(null);

  const [scheme, setScheme] = useState('https');
  const [host, setHost] = useState('');
  const [port, setPort] = useState('443');
  const [adding, setAdding] = useState(false);

  const load = async () => {
    setLoading(true);
    setError(null);
    try {
      setOrigins(await allowedOrigins.list());
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { void load(); }, []);

  const handleAdd = async (e: React.FormEvent) => {
    e.preventDefault();
    const portNum = parseInt(port, 10);
    if (!host.trim() || isNaN(portNum)) return;
    setAdding(true);
    try {
      const created = await allowedOrigins.create({ scheme, host: host.trim(), port: portNum });
      setOrigins(prev => [...prev, created]);
      setHost('');
      toast.success('Origin added');
    } catch (err) {
      toast.error(err instanceof Error ? err.message : 'Failed to add origin');
    } finally {
      setAdding(false);
    }
  };

  const handleDelete = async (id: number) => {
    if (!confirm('Remove this allowed origin?')) return;
    setDeleting(id);
    try {
      await allowedOrigins.delete(id);
      setOrigins(prev => prev.filter(o => o.id !== id));
      toast.success('Origin removed');
    } catch (err) {
      toast.error(err instanceof Error ? err.message : 'Failed to remove');
    } finally {
      setDeleting(null);
    }
  };

  // Auto-set default port when scheme changes
  const handleSchemeChange = (val: string) => {
    setScheme(val);
    if (val === 'https') setPort('443');
    else if (val === 'http') setPort('80');
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="font-mono text-lg font-bold text-text-primary tracking-tight">Allowed Origins</h1>
        <p className="mt-1 text-sm text-text-muted">
          Callback URLs must match one of these origins. This prevents SSRF attacks.
        </p>
      </div>

      {/* Docker hint */}
      <div className="border border-accent/30 bg-accent/5 px-4 py-3 text-sm text-text-secondary font-mono">
        <strong>Running inside Docker?</strong> Use{' '}
        <code className="bg-accent/10 px-1 py-0.5 font-mono text-xs text-accent">host.docker.internal</code>{' '}
        instead of{' '}
        <code className="bg-accent/10 px-1 py-0.5 font-mono text-xs text-accent">localhost</code> — Cratos
        runs in a container where <code className="bg-accent/10 px-1 py-0.5 font-mono text-xs text-accent">localhost</code> refers
        to the container itself, not your machine.
      </div>

      {/* Add form */}
      <div className="border border-border bg-bg-card overflow-hidden">
        <div className="border-b border-border px-5 py-3">
          <h2 className="text-sm font-semibold text-text-primary">Add Origin</h2>
        </div>
        <form onSubmit={(e) => void handleAdd(e)} className="p-5">
          <div className="flex gap-2 flex-wrap">
            <select
              value={scheme}
              onChange={e => handleSchemeChange(e.target.value)}
              className="border border-border bg-bg-secondary px-3 py-2 text-sm font-mono text-text-primary outline-none focus:border-accent"
            >
              <option value="https">https</option>
              <option value="http">http</option>
            </select>
            <input
              type="text"
              placeholder="your-service.com"
              value={host}
              onChange={e => setHost(e.target.value)}
              required
              className="flex-1 min-w-[180px] border border-border bg-bg-secondary px-3 py-2 text-sm font-mono text-text-primary placeholder:text-text-muted outline-none focus:border-accent"
            />
            <input
              type="number"
              placeholder="Port"
              value={port}
              onChange={e => setPort(e.target.value)}
              required
              min={1}
              max={65535}
              className="w-24 border border-border bg-bg-secondary px-3 py-2 text-sm font-mono text-text-primary outline-none focus:border-accent"
            />
            <Button type="submit" variant="primary" size="sm" disabled={adding}>
              {adding ? <Loader2 className="h-3.5 w-3.5 animate-spin" /> : <Plus className="h-3.5 w-3.5" />}
              Add
            </Button>
          </div>
        </form>
      </div>

      {/* List */}
      <div className="border border-border bg-bg-card overflow-hidden">
        <div className="border-b border-border px-5 py-3">
          <h2 className="text-sm font-semibold text-text-primary">Whitelisted Origins</h2>
        </div>

        {loading ? (
          <div className="flex items-center justify-center py-16">
            <Loader2 className="h-5 w-5 animate-spin text-text-muted" />
          </div>
        ) : error ? (
          <div className="flex flex-col items-center gap-3 py-12">
            <AlertCircle className="h-8 w-8 text-red-400" />
            <p className="text-sm text-red-400">{error}</p>
            <Button variant="secondary" size="sm" onClick={() => void load()}>Retry</Button>
          </div>
        ) : origins.length === 0 ? (
          <div className="flex flex-col items-center gap-3 py-16 text-text-muted">
            <ShieldCheck className="h-8 w-8" />
            <p className="text-sm">No origins whitelisted yet. Add one above.</p>
          </div>
        ) : (
          <ul className="divide-y divide-border">
            {origins.map(origin => (
              <li key={origin.id} className="flex items-center justify-between px-5 py-3">
                <code className="text-sm text-text-primary font-mono">
                  {origin.scheme}://{origin.host}:{origin.port}
                </code>
                <button
                  onClick={() => void handleDelete(origin.id)}
                  disabled={deleting === origin.id}
                  className="rounded p-1.5 text-text-muted hover:text-red-400 hover:bg-red-500/10 transition-colors disabled:opacity-50"
                  title="Remove"
                >
                  {deleting === origin.id
                    ? <Loader2 className="h-4 w-4 animate-spin" />
                    : <Trash2 className="h-4 w-4" />}
                </button>
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
}
