import { Outlet, NavLink } from 'react-router-dom';
import { useAuth } from '@/contexts/AuthContext';
import { CheckSquare, BarChart3, Settings, LogOut } from 'lucide-react';
import { cn } from '@/lib/utils';

const navItems = [
  { to: '/', icon: CheckSquare, label: 'Tasks', end: true },
  { to: '/metrics', icon: BarChart3, label: 'Metrics' },
  { to: '/settings', icon: Settings, label: 'Settings' },
];

export default function Layout() {
  const { user, logout } = useAuth();

  return (
    <div className="min-h-screen flex flex-col">
      {/* ── Top nav ─────────────────────────────────────── */}
      <header className="sticky top-0 z-50 border-b border-border bg-bg-sidebar flex items-center justify-between px-6 h-11">
        {/* Brand */}
        <span className="font-mono text-[15px] font-bold text-text-primary">
          cratos<span className="text-accent">.</span>
        </span>

        {/* Nav */}
        <nav className="flex items-center gap-0">
          {navItems.map(({ to, icon: Icon, label, end }) => (
            <NavLink
              key={to}
              to={to}
              end={end}
              className={({ isActive }) =>
                cn(
                  'flex items-center gap-2 px-4 h-11 text-[13px] font-medium transition-colors border-b-2',
                  isActive
                    ? 'border-accent text-text-primary'
                    : 'border-transparent text-text-muted hover:text-text-primary',
                )
              }
            >
              <Icon className="h-3.5 w-3.5" />
              {label}
            </NavLink>
          ))}
        </nav>

        {/* User */}
        <div className="flex items-center gap-3">
          <span className="font-mono text-[12px] text-text-muted">{user?.username}</span>
          <button
            type="button"
            onClick={() => void logout()}
            title="Sign out"
            className="text-text-muted hover:text-red-400 transition-colors"
          >
            <LogOut className="h-3.5 w-3.5" />
          </button>
        </div>
      </header>

      {/* ── Content ─────────────────────────────────────── */}
      <main className="flex-1 p-8 max-w-[1200px] w-full mx-auto">
        <Outlet />
      </main>
    </div>
  );
}
