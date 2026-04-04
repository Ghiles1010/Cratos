import { useState } from 'react';
import Secrets from './Secrets';
import AllowedOrigins from './AllowedOrigins';
import Account from './Account';
import Health from './Health';

const TABS = [
  { id: 'secrets', label: 'Secrets' },
  { id: 'origins', label: 'Origins' },
  { id: 'account', label: 'Account' },
  { id: 'health', label: 'Health' },
] as const;

type TabId = typeof TABS[number]['id'];

export default function Settings() {
  const [tab, setTab] = useState<TabId>('secrets');

  return (
    <div className="space-y-6">
      <h1 className="font-mono text-lg font-bold text-text-primary tracking-tight">settings</h1>

      {/* Tab bar */}
      <div className="flex border-b border-border">
        {TABS.map((t) => (
          <button
            key={t.id}
            onClick={() => setTab(t.id)}
            className={`px-4 py-2 text-[12px] font-medium font-mono transition-colors border-b-2 -mb-px ${
              tab === t.id
                ? 'border-accent text-text-primary'
                : 'border-transparent text-text-muted hover:text-text-secondary'
            }`}
          >
            {t.label}
          </button>
        ))}
      </div>

      {/* Tab content — strip the page heading since Settings has its own */}
      <div>
        {tab === 'secrets' && <Secrets />}
        {tab === 'origins' && <AllowedOrigins />}
        {tab === 'account' && <Account />}
        {tab === 'health' && <Health />}
      </div>
    </div>
  );
}
