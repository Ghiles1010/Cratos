import { useState } from 'react';
import { Plus, RefreshCw, Search } from 'lucide-react';
import { useTasks } from '@/hooks/useTasks';
import { Button } from '@/components/ui';
import { cn } from '@/lib/utils';
import type { TaskStatus } from '@/lib/api';
import CreateTaskDialog from '@/components/CreateTaskDialog';
import {
  AutoRefreshToggle,
  TaskTable,
  Pagination,
  StatusFilter,
} from '@/components/tasks';

export default function Tasks() {
  const [page, setPage] = useState(1);
  const [pageSize] = useState(20);
  const [autoRefresh, setAutoRefresh] = useState(false);
  const [statusFilter, setStatusFilter] = useState<TaskStatus | ''>('');
  const [search, setSearch] = useState('');
  const [createOpen, setCreateOpen] = useState(false);

  const { data, isLoading, isFetching, refetch } = useTasks({
    page,
    pageSize,
    autoRefresh,
    search,
    status: statusFilter,
  });

  const tasks = data?.results ?? [];
  const totalCount = data?.count ?? 0;
  const totalPages = Math.ceil(totalCount / pageSize);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <h1 className="font-mono text-lg font-bold text-text-primary tracking-tight">
          tasks
        </h1>
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
            <RefreshCw className={cn('h-3.5 w-3.5', isFetching && 'animate-spin')} />
            Refresh
          </Button>
          <Button size="sm" onClick={() => setCreateOpen(true)}>
            <Plus className="h-3.5 w-3.5" />
            New Task
          </Button>
        </div>
      </div>

      {/* Filters */}
      <div className="flex items-center gap-2">
        <StatusFilter
          value={statusFilter}
          onChange={(v) => { setStatusFilter(v); setPage(1); }}
        />
        <div className="relative">
          <Search className="absolute left-2.5 top-1/2 h-3.5 w-3.5 -translate-y-1/2 text-text-muted" />
          <input
            type="text"
            placeholder="Search tasks…"
            value={search}
            onChange={(e) => { setSearch(e.target.value); setPage(1); }}
            className="h-7 w-52 border border-border bg-bg-input pl-8 pr-3 text-xs text-text-primary placeholder:text-text-muted outline-none focus:border-accent font-mono"
          />
        </div>
      </div>

      {/* Table */}
      <TaskTable tasks={tasks} isLoading={isLoading} />

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

      <CreateTaskDialog open={createOpen} onOpenChange={setCreateOpen} />
    </div>
  );
}
