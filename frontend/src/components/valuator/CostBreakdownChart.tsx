import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  Cell,
} from 'recharts';
import type { CalculationResultWithTransport } from '@/types/battery';

interface CostBreakdownChartProps {
  result: CalculationResultWithTransport;
  currency: string;
}

export function CostBreakdownChart({ result, currency }: CostBreakdownChartProps) {
  const data = [
    {
      name: 'Pre-treatment',
      value: result.total_pre_treat,
      color: 'hsl(4, 70%, 50%)',
    },
    {
      name: 'Post-treatment',
      value: result.total_refining_cost,
      color: 'hsl(4, 60%, 65%)',
    },
    {
      name: 'Transportation',
      value: result.transport_cost ?? 0,
      color: 'hsl(210, 60%, 50%)',
    },
    {
      name: 'Total OPEX',
      value: result.total_opex,
      color: 'hsl(4, 70%, 35%)',
    },
  ].filter(item => item.value > 0);

  const formatCurrency = (value: number) => {
    const symbol = currency === 'EUR' ? '€' : currency === 'CNY' ? '¥' : '$';
    return `${symbol}${value.toLocaleString(undefined, { maximumFractionDigits: 0 })}`;
  };

  return (
    <div className="bg-card rounded-xl border border-border p-6 card-shadow">
      <h3 className="text-sm font-semibold text-foreground uppercase tracking-wider mb-4">
        Cost Breakdown
      </h3>
      <div className="h-64">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart
            data={data}
            layout="vertical"
            margin={{ top: 5, right: 30, left: 80, bottom: 5 }}
          >
            <XAxis
              type="number"
              tickFormatter={formatCurrency}
              axisLine={false}
              tickLine={false}
              tick={{ fill: 'hsl(var(--muted-foreground))', fontSize: 12 }}
            />
            <YAxis
              type="category"
              dataKey="name"
              axisLine={false}
              tickLine={false}
              tick={{ fill: 'hsl(var(--foreground))', fontSize: 13, fontWeight: 500 }}
            />
            <Tooltip
              formatter={(value: number) => [formatCurrency(value), 'Amount']}
              contentStyle={{
                backgroundColor: 'hsl(var(--card))',
                border: '1px solid hsl(var(--border))',
                borderRadius: '8px',
                boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)',
              }}
              labelStyle={{ color: 'hsl(var(--foreground))' }}
            />
            <Bar dataKey="value" radius={[0, 6, 6, 0]}>
              {data.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={entry.color} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
