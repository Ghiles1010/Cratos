import { useState, useMemo } from 'react';
import { Plus, RefreshCw, Search } from 'lucide-react';
import { useTasks } from '@/hooks/useTasks';
import { Button } from '@/components/ui';
import { cn } from '@/lib/utils';
import type { TaskStatus } from '@/lib/api';
import CreateTaskDialog from '@/components/CreateTaskDialog';
import TaskDetailDrawer from '@/components/TaskDetailDrawer';
import {
  StatCard,
  AutoRefreshToggle,
  TaskTable,
  Pagination,
  StatusFilter,
} from '@/components/tasks';

export default function Tasks() {
  const [page, setPage] = useState(1);
  const [pageSize] = useState(20);
  const [autoRefresh, setAutoRefresh] = useState(false);
  const [statusFilter, setStatusFilter] = useState<TaskStatus | 'all'>('all');
  const [search, setSearch] = useState('');
  const [createOpen, setCreateOpen] = useState(false);
  const [selectedTaskId, setSelectedTaskId] = useState<string | null>(null);

  const { data, isLoading, isFetching, refetch } = useTasks({
    page,
    pageSize,
    autoRefresh,
  });

  const tasks = data?.results ?? [];
  const totalCount = data?.count ?? 0;
  const totalPages = Math.ceil(totalCount / pageSize);

  // Client-side filtering (on top of server pagination)
  const filtered = useMemo(() => {
    let list = tasks;
    if (statusFilter !== 'all') {
      list = list.filter((t) => t.status === statusFilter);
    }
    if (search) {
      const q = search.toLowerCase();
      list = list.filter(
        (t) =>
          t.task_name.toLowerCase().includes(q) ||
          t.task_id.toLowerCase().includes(q),
      );
    }
    return list;
  }, [tasks, statusFilter, search]);

  // Stats from current page
  const stats = useMemo(() => {
    const s = { total: totalCount, scheduled: 0, recurring: 0, failed: 0 };
    tasks.forEach((t) => {
      if (t.status === 'scheduled') s.scheduled++;
      if (t.schedule_type !== 'one_off') s.recurring++;
      if (t.status === 'failed') s.failed++;
    });
    return s;
  }, [tasks, totalCount]);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-start justify-between">
        <div>
          <h1 className="text-2xl font-bold text-text-primary">
            Scheduled Tasks
          </h1>
          <p className="mt-1 text-sm text-text-muted">
            Manage one-off, cron, and interval tasks
          </p>
        </div>
        <div className="flex items-center gap-2">
          <AutoRefreshToggle
            active={autoRefresh}
            onChange={setAutoRefresh}
            isFetching={isFetching}
          />
          <Button
            variant="secondary"
            size="sm"
            onClick={() => void refetch()}
            disabled={isFetching}
          >
            <RefreshCw
              className={cn('h-3.5 w-3.5', isFetching && 'animate-spin')}
            />
            Refresh
          </Button>
          <Button size="sm" onClick={() => setCreateOpen(true)}>
            <Plus className="h-3.5 w-3.5" />
            New Task
          </Button>
        </div>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-4 gap-3">
        <StatCard label="Total" value={stats.total} sub="All tasks" />
        <StatCard label="Scheduled" value={stats.scheduled} sub="Awaiting" />
        <StatCard label="Recurring" value={stats.recurring} sub="Cron / Interval" />
        <StatCard
          label="Failed"
          value={stats.failed}
          sub="Needs attention"
          alert={stats.failed > 0}
        />
      </div>

      {/* Filters */}
      <div className="flex items-center justify-between gap-4">
        <StatusFilter value={statusFilter} onChange={setStatusFilter} />
        <div className="relative">
          <Search className="absolute left-2.5 top-1/2 h-3.5 w-3.5 -translate-y-1/2 text-text-muted" />
          <input
            type="text"
            placeholder="Search tasks…"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="h-8 w-56 rounded-md border border-border bg-bg-input pl-8 pr-3 text-xs text-text-primary placeholder:text-text-muted outline-none focus:border-accent focus:ring-2 focus:ring-accent/20"
          />
        </div>
      </div>

      {/* Table */}
      <TaskTable
        tasks={filtered}
        isLoading={isLoading}
        onSelect={setSelectedTaskId}
      />

      {/* Pagination */}
      {totalPages > 1 && (
        <Pagination
          page={page}
          totalPages={totalPages}
          totalCount={totalCount}
          pageSize={pageSize}
          onPageChange={setPage}
        />
      )}

      {/* Dialogs */}
      <CreateTaskDialog open={createOpen} onOpenChange={setCreateOpen} />
      <TaskDetailDrawer
        taskId={selectedTaskId}
        onClose={() => setSelectedTaskId(null)}
      />
    </div>
  );
}
