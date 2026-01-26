import { AlertTriangle, TrendingUp, TrendingDown, Minus } from 'lucide-react';
import { MetricCard } from '@/components/ui/metric-card';
import { CostBreakdownChart } from './CostBreakdownChart';
import { ProductTable } from './ProductTable';
import type { CalculationResult, FormData } from '@/types/battery';

// Correct chemical symbols mapping
const METAL_SYMBOLS: Record<string, string> = {
  Nickel: 'Ni',
  Cobalt: 'Co',
  Lithium: 'Li',
  Copper: 'Cu',
  Aluminum: 'Al',
  Manganese: 'Mn',
};

interface ResultsPanelProps {
  result: CalculationResult | null;
  formData: FormData;
  recoverableBlackMass: number;
  isCalculating: boolean;
}

export function ResultsPanel({
  result,
  formData,
  recoverableBlackMass,
  isCalculating,
}: ResultsPanelProps) {
  const formatCurrency = (value: number) => {
    const symbol = formData.currency === 'EUR' ? '€' : formData.currency === 'CNY' ? '¥' : '$';
    return `${symbol}${Math.abs(value).toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
  };

  const isBlackMass = formData.feedType === 'Black Mass (Processed)';

  if (!result) {
    return (
      <div className="flex flex-col items-center justify-center h-full min-h-[400px] text-center px-8">
        <div className="w-24 h-24 rounded-full bg-secondary flex items-center justify-center mb-6">
          <TrendingUp className="h-12 w-12 text-muted-foreground" />
        </div>
        <h2 className="text-2xl font-semibold text-foreground mb-2">
          Ready to Calculate
        </h2>
        <p className="text-muted-foreground max-w-md">
          Configure your inputs in the sidebar and click "Run Valuation" to see your battery material valuation results.
        </p>
      </div>
    );
  }

  const marginIcon = result.margin_pct > 5 ? TrendingUp : result.margin_pct < 0 ? TrendingDown : Minus;
  const MarginIcon = marginIcon;

  return (
    <div className="space-y-6">
      {/* Summary Banner */}
      <div className="bg-card rounded-xl border border-border p-4 card-shadow">
        <div className="flex flex-wrap gap-x-8 gap-y-2 text-sm">
          <div>
            <span className="text-muted-foreground">Material:</span>{' '}
            <span className="font-medium text-foreground">{formData.feedType}</span>
          </div>
          <div>
            <span className="text-muted-foreground">Gross Weight:</span>{' '}
            <span className="font-medium text-foreground">{formData.grossWeight.toLocaleString()} kg</span>
          </div>
          <div>
            <span className="text-muted-foreground">Net Black Mass:</span>{' '}
            <span className="font-medium text-foreground">
              {result.net_bm_weight.toLocaleString(undefined, { maximumFractionDigits: 1 })} kg
            </span>{' '}
            <span className="text-muted-foreground">({formData.yieldPct}% Yield)</span>
          </div>
          <div>
            <span className="text-muted-foreground">Recovery:</span>{' '}
            <span className="font-medium text-foreground">
              {!isBlackMass && `Mech: ${formData.mechRecovery}% | `}Hydro: {formData.hydrometRecovery}%
            </span>
          </div>
        </div>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <MetricCard
          title="Net Profit"
          value={result.net_profit >= 0 ? formatCurrency(result.net_profit) : `-${formatCurrency(result.net_profit)}`}
          badge={`${result.margin_pct >= 0 ? '+' : ''}${result.margin_pct.toFixed(1)}% margin`}
          badgeVariant={result.margin_pct > 0 ? 'success' : 'danger'}
          variant={result.net_profit >= 0 ? 'profit' : 'cost'}
          size="lg"
          className="md:col-span-2"
        />
        <MetricCard
          title="Total Revenue"
          value={formatCurrency(result.total_revenue)}
          variant="default"
          size="md"
        />
        <MetricCard
          title="Material Cost"
          value={formatCurrency(result.material_cost)}
          variant="default"
          size="md"
        />
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <MetricCard
          title="Pre-treatment"
          value={formatCurrency(result.total_pre_treat)}
          variant="default"
          size="sm"
        />
        <MetricCard
          title="Refining Cost"
          value={formatCurrency(result.total_refining_cost)}
          variant="default"
          size="sm"
        />
        <MetricCard
          title="Total OPEX"
          value={formatCurrency(result.total_opex)}
          variant="default"
          size="sm"
        />
      </div>

      {/* Chart and Table */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <CostBreakdownChart result={result} currency={formData.currency} />
        <ProductTable products={result.production_data} currency={formData.currency} />
      </div>

      {/* Warnings */}
      {result.warnings && result.warnings.length > 0 && (
        <div className="p-4 bg-warning/10 border border-warning/30 rounded-xl">
          <div className="flex items-start gap-3">
            <AlertTriangle className="h-5 w-5 text-warning mt-0.5" />
            <div>
              <h4 className="font-semibold text-warning-foreground mb-1">Validation Warnings</h4>
              <ul className="text-sm text-warning-foreground space-y-1">
                {result.warnings.map((warning, idx) => (
                  <li key={idx}>{warning}</li>
                ))}
              </ul>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
