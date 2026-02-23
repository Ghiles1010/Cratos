import { BarChart3, RefreshCw } from 'lucide-react';
import { cn } from '@/lib/utils';
import { useMetrics } from '@/hooks/useMetrics';
import {
  StatCard,
  ChartCard,
  StatusChart,
  RecentExecutionsTable,
} from '@/components/metrics';

export default function Metrics() {
  const { data, isLoading, isFetching, refetch } = useMetrics();

  const tasksChartData =
    data &&
    Object.entries(data.tasks_by_status).map(([status, count]) => ({
      status,
      count,
    }));

  const executionsChartData =
    data &&
    Object.entries(data.executions_by_status).map(([status, count]) => ({
      status,
      count,
    }));

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-start justify-between">
        <div>
          <h1 className="text-2xl font-bold text-text-primary flex items-center gap-2">
            <BarChart3 className="h-5 w-5 text-accent" />
            Metrics
          </h1>
          <p className="mt-1 text-sm text-text-muted">
            Live insight into scheduled tasks and executions.
          </p>
        </div>
        <button
          type="button"
          onClick={() => void refetch()}
          disabled={isFetching}
          className={cn(
            'inline-flex items-center gap-1.5 rounded-md border border-border bg-bg-card px-3 py-1.5 text-xs font-medium text-text-secondary transition-colors hover:text-text-primary',
            isFetching && 'opacity-70',
          )}
        >
          <RefreshCw
            className={cn(
              'h-3.5 w-3.5',
              (isLoading || isFetching) && 'animate-spin',
            )}
          />
          Refresh
        </button>
      </div>

      {/* Top stats */}
      <div className="grid grid-cols-4 gap-3">
        <StatCard
          label="Tasks"
          value={
            data
              ? Object.values(data.tasks_by_status).reduce(
                  (sum, c) => sum + c,
                  0,
                )
              : 0
          }
          sub="Total tasks (all statuses)"
        />
        <StatCard
          label="Executions"
          value={
            data
              ? Object.values(data.executions_by_status).reduce(
                  (sum, c) => sum + c,
                  0,
                )
              : 0
          }
          sub="All-time executions"
        />
        <StatCard
          label="Overdue"
          value={data?.overdue_tasks ?? 0}
          sub="Tasks past next_run_at"
          alert={(data?.overdue_tasks ?? 0) > 0}
        />
        <StatCard
          label="Avg duration"
          value={data ? data.avg_execution_duration_seconds.toFixed(3) : '0.000'}
          sub="Successful executions (s)"
        />
      </div>

      {/* Charts */}
      <div className="grid grid-cols-2 gap-4">
        <ChartCard title="Tasks by status" empty={!tasksChartData?.length}>
          <StatusChart data={tasksChartData || []} color="#6366f1" />
        </ChartCard>

        <ChartCard title="Executions by status" empty={!executionsChartData?.length}>
          <StatusChart
            data={executionsChartData || []}
            color="#22c55e"
            showLegend
          />
        </ChartCard>
      </div>

      {/* Recent executions list */}
      <RecentExecutionsTable
        executions={data?.recent_executions || []}
        generatedAt={data?.generated_at}
      />
    </div>
  );
}
