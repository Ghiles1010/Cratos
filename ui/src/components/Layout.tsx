import { Outlet, NavLink } from 'react-router-dom';
import { useAuth } from '@/contexts/AuthContext';
import {
  CheckSquare,
  Key,
  Activity,
  LogOut,
  Clock,
  BarChart3,
} from 'lucide-react';
import { cn } from '@/lib/utils';

const navItems: Array<{
  to: string;
  icon: typeof CheckSquare;
  label: string;
  end?: boolean;
}> = [
  { to: '/', icon: CheckSquare, label: 'Tasks', end: true },
  { to: '/api-keys', icon: Key, label: 'API Keys' },
  { to: '/health', icon: Activity, label: 'Health' },
  { to: '/metrics', icon: BarChart3, label: 'Metrics' },
];

export default function Layout() {
  const { user, logout } = useAuth();

  return (
    <div className="flex min-h-screen">
      {/* ── Sidebar ─────────────────────────────────────── */}
      <aside className="fixed inset-y-0 left-0 z-50 flex w-[220px] flex-col border-r border-border bg-bg-sidebar">
        {/* Brand */}
        <div className="flex items-center gap-2.5 border-b border-border px-5 py-5">
          <Clock className="h-5 w-5 text-accent" />
          <span className="text-[15px] font-bold tracking-tight text-text-primary">
            Cratos
          </span>
        </div>

        {/* Nav */}
        <nav className="flex-1 flex flex-col gap-0.5 px-3 py-4">
          {navItems.map(({ to, icon: Icon, label, ...rest }) => (
            <NavLink
              key={to}
              to={to}
              end={'end' in rest}
              className={({ isActive }) =>
                cn(
                  'flex items-center gap-2.5 rounded-lg px-3 py-2 text-[13px] font-medium transition-colors',
                  isActive
                    ? 'bg-accent/15 text-accent'
                    : 'text-text-secondary hover:bg-bg-card hover:text-text-primary',
                )
              }
            >
              <Icon className="h-4 w-4 shrink-0" />
              {label}
            </NavLink>
          ))}
        </nav>

        {/* User footer */}
        <div className="flex items-center justify-between border-t border-border px-3 py-3">
          <div className="flex items-center gap-2.5 min-w-0">
            <div className="flex h-7 w-7 shrink-0 items-center justify-center rounded-full bg-accent/15 text-xs font-semibold text-accent">
              {user?.username?.[0]?.toUpperCase() || 'U'}
            </div>
            <div className="min-w-0">
              <p className="truncate text-[13px] font-medium text-text-primary">
                {user?.username ?? 'User'}
              </p>
              <p className="text-[11px] text-text-muted">Admin</p>
            </div>
          </div>
          <button
            type="button"
            onClick={() => void logout()}
            title="Sign out"
            className="rounded-md border border-border p-1.5 text-text-muted transition-colors hover:border-red-500/30 hover:bg-red-500/10 hover:text-red-400"
          >
            <LogOut className="h-3.5 w-3.5" />
          </button>
        </div>
      </aside>

      {/* ── Main ────────────────────────────────────────── */}
      <main className="ml-[220px] flex-1 overflow-y-auto p-8 max-w-[1200px]">
        <Outlet />
      </main>
    </div>
  );
}
