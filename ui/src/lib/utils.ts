import { clsx, type ClassValue } from 'clsx';
import { twMerge } from 'tailwind-merge';
import { formatDistanceToNow, format } from 'date-fns';

/** Merge Tailwind classes safely (handles conflicts). */
export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

/** Format an ISO date string as relative time ("3 min ago"). */
export function relativeTime(iso: string | null | undefined): string {
  if (!iso) return '—';
  try {
    return formatDistanceToNow(new Date(iso), { addSuffix: true });
  } catch {
    return '—';
  }
}

/** Format an ISO date string for display. */
export function fmtDate(iso: string | null | undefined): string {
  if (!iso) return '—';
  try {
    return format(new Date(iso), 'MMM d, HH:mm:ss');
  } catch {
    return '—';
  }
}

/** Format an ISO date string as full datetime. */
export function fullDate(iso: string | null | undefined): string {
  if (!iso) return '—';
  try {
    return format(new Date(iso), 'MMM d, yyyy HH:mm:ss zzz');
  } catch {
    return '—';
  }
}

/** Read a cookie by name. */
export function getCookie(name: string): string | null {
  const match = document.cookie
    .split('; ')
    .find((row) => row.startsWith(`${name}=`));
  return match ? decodeURIComponent(match.split('=')[1]) : null;
}

/** Human-readable schedule label. */
export function scheduleLabel(
  type: string,
  cron?: string,
  intervalSeconds?: number | null,
): string {
  if (type === 'cron') return cron ? `cron: ${cron}` : 'cron';
  if (type === 'interval')
    return intervalSeconds ? `every ${intervalSeconds}s` : 'interval';
  return 'one-off';
}

/** Truncate a string with ellipsis. */
export function truncate(str: string, len: number): string {
  return str.length > len ? str.slice(0, len) + '…' : str;
}



