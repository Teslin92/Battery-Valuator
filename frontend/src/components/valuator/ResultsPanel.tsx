import { AlertTriangle, TrendingUp, TrendingDown, Minus, Truck, CheckCircle2 } from 'lucide-react';
import { MetricCard } from '@/components/ui/metric-card';
import { ProductTable } from './ProductTable';
import type { CalculationResultWithTransport, FormData } from '@/types/battery';

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
  result: CalculationResultWithTransport | null;
  formData: FormData;
  recoverableBlackMass: number;
  isCalculating: boolean;
}

// Map full metal names to formData price keys
const METAL_TO_PRICE_KEY: Record<string, keyof FormData['prices']> = {
  Nickel: 'ni',
  Cobalt: 'co',
  Lithium: 'li',
  Copper: 'cu',
  Aluminum: 'al',
  Manganese: 'mn',
};

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

  // Compute gross material value (mass * price, no payable discount)
  const computeGrossMaterialValue = () => {
    if (!result?.masses) return 0;
    let total = 0;
    for (const [metal, mass] of Object.entries(result.masses)) {
      const priceKey = METAL_TO_PRICE_KEY[metal];
      if (priceKey) {
        total += mass * formData.prices[priceKey];
      }
    }
    return total;
  };

  const grossMaterialValue = result ? computeGrossMaterialValue() : 0;

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

      {/* Material Value Section */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <MetricCard
          title="Material Value"
          subtitle="Gross value based on metal content and prices"
          value={formatCurrency(grossMaterialValue)}
          variant="default"
          size="md"
        />
        <MetricCard
          title="Material Payable"
          subtitle="Net value after payable deductions"
          value={formatCurrency(result.material_cost)}
          variant="default"
          size="md"
        />
      </div>

      {/* Processing Costs */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <MetricCard
          title="Pre-treatment"
          value={formatCurrency(result.total_pre_treat)}
          variant="default"
          size="sm"
        />
        {formData.refiningEnabled && (
          <MetricCard
            title="Post-treatment"
            value={formatCurrency(result.total_refining_cost)}
            variant="default"
            size="sm"
          />
        )}
        {result.transport_cost !== undefined && result.transport_cost > 0 && (
          <MetricCard
            title="Transportation"
            value={formatCurrency(result.transport_cost)}
            variant="default"
            size="sm"
          />
        )}
      </div>

      {/* Total Cost */}
      <MetricCard
        title="Total Cost"
        subtitle={formData.refiningEnabled 
          ? "Pre-treatment + Post-treatment + Transportation" 
          : "Pre-treatment + Transportation"}
        value={formatCurrency(result.total_opex)}
        variant="cost"
        size="md"
      />

      {/* Transport & Regulatory Summary */}
      {result.route_advisory && (
        <div className="bg-card rounded-xl border border-border p-4 card-shadow">
          <div className="flex items-center gap-2 mb-3">
            <Truck className="h-5 w-5" />
            <h3 className="font-semibold">Logistics Summary</h3>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <p className="text-sm text-muted-foreground mb-1">Route Status</p>
              <div className="flex items-center gap-2">
                {result.route_advisory.allowed ? (
                  <CheckCircle2 className="h-4 w-4 text-profit" />
                ) : (
                  <AlertTriangle className="h-4 w-4 text-destructive" />
                )}
                <span className={`font-medium ${result.route_advisory.allowed ? 'text-profit' : 'text-destructive'}`}>
                  {result.route_advisory.status.toUpperCase()}
                </span>
              </div>
            </div>
            {result.transport_estimate && (
              <div>
                <p className="text-sm text-muted-foreground mb-1">Transport Mode</p>
                <p className="font-medium capitalize">{result.transport_estimate.mode}</p>
              </div>
            )}
          </div>
          
          {/* Vehicle/Container Information */}
          {result.transport_estimate && result.transport_estimate.vehicle_type && (
            <div className="mt-4 p-3 bg-primary/10 border border-primary/30 rounded-lg">
              <p className="text-sm font-medium text-foreground mb-2">
                {result.transport_estimate.vehicle_type}
              </p>
              <div className="grid grid-cols-2 gap-3 text-sm">
                {result.transport_estimate.num_vehicles && (
                  <div>
                    <span className="text-muted-foreground">Quantity:</span>{' '}
                    <span className="font-medium">{result.transport_estimate.num_vehicles}</span>
                  </div>
                )}
                {result.transport_estimate.capacity_per_vehicle_kg && (
                  <div>
                    <span className="text-muted-foreground">Capacity:</span>{' '}
                    <span className="font-medium">{result.transport_estimate.capacity_per_vehicle_kg.toLocaleString()} kg each</span>
                  </div>
                )}
                {result.transport_estimate.utilization_pct !== null && result.transport_estimate.utilization_pct !== undefined && (
                  <div>
                    <span className="text-muted-foreground">Utilization:</span>{' '}
                    <span className="font-medium">{result.transport_estimate.utilization_pct}%</span>
                  </div>
                )}
                {result.transport_estimate.cost_per_kg && (
                  <div>
                    <span className="text-muted-foreground">Cost per kg:</span>{' '}
                    <span className="font-medium">{formatCurrency(result.transport_estimate.cost_per_kg)}</span>
                  </div>
                )}
              </div>
              {result.transport_estimate.sizing_note && (
                <p className="text-xs text-muted-foreground mt-2">
                  {result.transport_estimate.sizing_note}
                </p>
              )}
            </div>
          )}
          
          {result.route_advisory.processing_time && (
            <div className="mt-3 text-sm">
              <span className="text-muted-foreground">Estimated Processing Time:</span>{' '}
              <span className="font-medium">{result.route_advisory.processing_time} days</span>
            </div>
          )}
        </div>
      )}

      {/* Total Revenue with Product Schedule - Only show when refining is enabled */}
      {formData.refiningEnabled && (
        <div className="space-y-4">
          <MetricCard
            title="Total Revenue"
            subtitle="Sum of all product sales (see Product Schedule below)"
            value={formatCurrency(result.total_revenue)}
            variant="default"
            size="md"
          />
          <ProductTable products={result.production_data} currency={formData.currency} />
        </div>
      )}

      {/* Net Profit - Only show when refining is enabled */}
      {formData.refiningEnabled && (
        <MetricCard
          title="Net Profit"
          subtitle="Total Revenue − Material Payable − Total Cost"
          value={result.net_profit >= 0 ? formatCurrency(result.net_profit) : `-${formatCurrency(result.net_profit)}`}
          badge={`${result.margin_pct >= 0 ? '+' : ''}${result.margin_pct.toFixed(1)}% margin`}
          badgeVariant={result.margin_pct > 0 ? 'success' : 'danger'}
          variant={result.net_profit >= 0 ? 'profit' : 'cost'}
          size="lg"
        />
      )}

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
