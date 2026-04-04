/**
 * API client for the Cratos backend.
 * Session-based auth (cookies) for the UI.
 */

import { getCookie } from './utils';

// Empty string = relative URLs, proxied through nginx (default for Docker deployments)
// Set VITE_SCHEDULER_API_URL to override (e.g. for local dev without Docker)
const BASE = import.meta.env.VITE_SCHEDULER_API_URL || '';

// ── Request helpers ──────────────────────────────────────────────────────────

function opts(method = 'GET', body?: unknown): RequestInit {
  const headers: Record<string, string> = { 'Content-Type': 'application/json' };
  if (method !== 'GET') {
    const csrf = getCookie('csrftoken');
    if (csrf) headers['X-CSRFToken'] = csrf;
  }
  const init: RequestInit = { method, headers, credentials: 'include' };
  if (body !== undefined) init.body = JSON.stringify(body);
  return init;
}

async function request<T>(url: string, init?: RequestInit): Promise<T> {
  const res = await fetch(url, init);
  if (!res.ok) {
    const data = await res.json().catch(() => null);
    throw new Error(data?.detail || data?.error || `HTTP ${res.status}`);
  }
  if (res.status === 204) return undefined as T;
  return res.json();
}

// ── Types ────────────────────────────────────────────────────────────────────

export type TaskStatus = 'scheduled' | 'pending' | 'running' | 'completed' | 'failed' | 'cancelled';
export type ScheduleType = 'one_off' | 'cron' | 'interval';
export type RetryPolicy = 'none' | 'fixed' | 'linear' | 'exponential';

export interface TaskExecution {
  execution_number: number;
  status: string;
  started_at: string | null;
  completed_at: string | null;
  duration_seconds: number | null;
  http_status_code: number | null;
  http_response_body: string | null;
  error_type: string | null;
  error_message: string | null;
  retry_count: number;
  is_retry: boolean;
  result: Record<string, unknown> | null;
}

export interface Task {
  task_id: string;
  task_name: string;
  status: TaskStatus;
  schedule_type: ScheduleType;
  schedule_time: string | null;
  cron_expression: string;
  interval_seconds: number | null;
  ends_at: string | null;
  task_timezone: string;
  next_run_at: string | null;
  last_run_at: string | null;
  run_count: number;
  is_paused: boolean;
  retry_policy: RetryPolicy;
  max_retries: number;
  retry_delay_seconds: number;
  retry_count: number;
  callback_url: string;
  task_args: unknown[];
  task_kwargs: Record<string, unknown>;
  user: string;
  created_at: string;
  updated_at: string;
  started_at: string | null;
  completed_at: string | null;
  execution_time: number | null;
  is_overdue: boolean;
  is_recurring: boolean;
  scheduler_info: Record<string, unknown> | null;
  execution_history?: TaskExecution[];
}

export interface TaskListResponse {
  count: number;
  next: string | null;
  previous: string | null;
  results: Task[];
}

export interface UserInfo {
  id: number;
  username: string;
  email: string;
  is_staff: boolean;
}

export interface CreateTaskPayload {
  task_name: string;
  callback_url: string;
  schedule_type: ScheduleType;
  schedule_time?: string;
  cron_expression?: string;
  interval_seconds?: number;
  ends_at?: string;
  task_timezone?: string;
  retry_policy?: RetryPolicy;
  max_retries?: number;
  retry_delay_seconds?: number;
  task_args?: unknown[];
  task_kwargs?: Record<string, unknown>;
}

// ── Auth ─────────────────────────────────────────────────────────────────────

export const auth = {
  fetchCsrf: () => fetch(`${BASE}/api/auth/csrf/`, { credentials: 'include' }),
  login: async (username: string, password: string): Promise<UserInfo> => {
    await auth.fetchCsrf();
    const data = await request<{ user: UserInfo }>(
      `${BASE}/api/auth/login/`,
      opts('POST', { username, password }),
    );
    return data.user;
  },
  logout: () => request<void>(`${BASE}/api/auth/logout/`, opts('POST')),
  me: () => request<UserInfo>(`${BASE}/api/auth/me/`, opts()),
};

// ── Tasks ────────────────────────────────────────────────────────────────────

export const tasks = {
  list: (page = 1, pageSize = 20, search = '') => {
    const params = new URLSearchParams({ page: String(page), page_size: String(pageSize) });
    if (search) params.set('search', search);
    return request<TaskListResponse>(`${BASE}/api/tasks/?${params}`, opts());
  },
  get: (id: string) => request<Task>(`${BASE}/api/tasks/${id}/`, opts()),
  create: (payload: CreateTaskPayload) =>
    request<Task>(`${BASE}/api/tasks/`, opts('POST', payload)),
  update: (id: string, payload: Partial<CreateTaskPayload>) =>
    request<Task>(`${BASE}/api/tasks/${id}/`, opts('PATCH', payload)),
  delete: (id: string) => request<void>(`${BASE}/api/tasks/${id}/`, opts('DELETE')),
  cancel: (id: string) => request<Task>(`${BASE}/api/tasks/${id}/cancel/`, opts('POST')),
  pause: (id: string) => request<Task>(`${BASE}/api/tasks/${id}/pause/`, opts('POST')),
  resume: (id: string) => request<Task>(`${BASE}/api/tasks/${id}/resume/`, opts('POST')),
  retry: (id: string) => request<Task>(`${BASE}/api/tasks/${id}/retry/`, opts('POST')),
};

// ── API Keys ─────────────────────────────────────────────────────────────────

export const apiKeys = {
  get: () => request<{ key: string }>(`${BASE}/api/keys/`, opts()),
  regenerate: () => request<{ key: string }>(`${BASE}/api/keys/`, opts('POST')),
};

// ── Webhook Signing Secret ────────────────────────────────────────────────────

export const webhookSecret = {
  get: () => request<{ secret: string }>(`${BASE}/api/webhooks/signing-key/`, opts()),
  rotate: () => request<{ secret: string; rotated: boolean }>(`${BASE}/api/webhooks/signing-key/`, opts('POST')),
};

// ── Account ──────────────────────────────────────────────────────────────────

export const account = {
  changePassword: (current_password: string, new_password: string) =>
    request<{ detail: string }>(`${BASE}/api/auth/change-password/`, opts('POST', { current_password, new_password })),
  changeUsername: (password: string, new_username: string) =>
    request<{ detail: string; username: string }>(`${BASE}/api/auth/change-username/`, opts('POST', { password, new_username })),
};

// ── Allowed Origins ──────────────────────────────────────────────────────────

export interface AllowedOrigin {
  id: number;
  scheme: string;
  host: string;
  port: number;
}

export const allowedOrigins = {
  list: () => request<AllowedOrigin[]>(`${BASE}/api/webhooks/allowed-origins/`, opts()),
  create: (data: Omit<AllowedOrigin, 'id'>) =>
    request<AllowedOrigin>(`${BASE}/api/webhooks/allowed-origins/`, opts('POST', data)),
  delete: (id: number) =>
    request<void>(`${BASE}/api/webhooks/allowed-origins/${id}/`, opts('DELETE')),
};

// ── Health ───────────────────────────────────────────────────────────────────

export const health = {
  check: () => request<{ status: string; service: string }>(`${BASE}/health/`),
};

