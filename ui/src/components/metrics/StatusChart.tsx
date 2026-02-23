import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from 'recharts';

interface StatusChartProps {
  data: Array<{ status: string; count: number }>;
  color?: string;
  showLegend?: boolean;
}

export function StatusChart({
  data,
  color = '#6366f1',
  showLegend = false,
}: StatusChartProps) {
  if (!data || data.length === 0) return null;

  return (
    <ResponsiveContainer width="100%" height={220}>
      <BarChart data={data}>
        <XAxis
          dataKey="status"
          tick={{ fontSize: 11, fill: '#a1a1aa' }}
          axisLine={{ stroke: '#27272a' }}
        />
        <YAxis
          tick={{ fontSize: 11, fill: '#a1a1aa' }}
          axisLine={{ stroke: '#27272a' }}
          allowDecimals={false}
        />
        <Tooltip
          contentStyle={{
            backgroundColor: '#18181b',
            border: '1px solid #27272a',
            fontSize: 12,
          }}
        />
        {showLegend && <Legend />}
        <Bar dataKey="count" fill={color} radius={[4, 4, 0, 0]} />
      </BarChart>
    </ResponsiveContainer>
  );
}

