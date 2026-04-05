import { Outlet, NavLink, useNavigate } from 'react-router-dom';
import { useAuth } from '@/contexts/AuthContext';
import { LogOut } from 'lucide-react';
import { cn } from '@/lib/utils';

const navItems = [
  { to: '/', label: 'Tasks', end: true },
  { to: '/settings', label: 'Settings' },
];

export default function Layout() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  return (
    <div className="min-h-screen flex flex-col">
      <header className="sticky top-0 z-50 border-b border-border bg-bg-sidebar flex items-center justify-between px-6 h-11">
        <button
          onClick={() => navigate('/')}
          className="font-mono text-[15px] font-bold text-text-primary hover:text-accent transition-colors"
        >
          cratos<span className="text-accent">.</span>
        </button>

        <nav className="flex items-center gap-0">
          {navItems.map(({ to, label, end }) => (
            <NavLink
              key={to}
              to={to}
              end={end}
              className={({ isActive }) =>
                cn(
                  'px-4 h-11 flex items-center text-[13px] font-medium transition-colors border-b-2',
                  isActive
                    ? 'border-accent text-text-primary'
                    : 'border-transparent text-text-muted hover:text-text-primary',
                )
              }
            >
              {label}
            </NavLink>
          ))}
        </nav>

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

      <main className="flex-1 p-8 max-w-[1200px] w-full mx-auto">
        <Outlet />
      </main>
    </div>
  );
}
