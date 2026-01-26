import { RefreshCw, AlertTriangle, RotateCcw } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import type { Currency, MarketData } from '@/types/battery';

interface GlobalSettingsProps {
  currency: Currency;
  onCurrencyChange: (currency: Currency) => void;
  fxRate: number;
  fxRateOverridden: boolean;
  onFxRateChange: (rate: number) => void;
  onResetFxRate: () => void;
  marketData?: MarketData;
  isLoading: boolean;
  onRefresh: () => void;
  error?: Error | null;
}

export function GlobalSettings({
  currency,
  onCurrencyChange,
  fxRate,
  fxRateOverridden,
  onFxRateChange,
  onResetFxRate,
  marketData,
  isLoading,
  onRefresh,
  error,
}: GlobalSettingsProps) {
  const apiFxRate = marketData?.FX ?? 1;
  const isUSD = currency === 'USD';

  return (
    <div className="p-4 bg-card rounded-xl border border-border card-shadow">
      <div className="flex flex-col sm:flex-row items-start sm:items-center gap-4">
        <div className="flex-1">
          <label className="text-sm font-medium text-muted-foreground block mb-2">
            Currency
          </label>
          <Select value={currency} onValueChange={(v) => onCurrencyChange(v as Currency)}>
            <SelectTrigger className="w-32">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="USD">USD</SelectItem>
              <SelectItem value="CAD">CAD</SelectItem>
              <SelectItem value="EUR">EUR</SelectItem>
              <SelectItem value="CNY">CNY</SelectItem>
            </SelectContent>
          </Select>
        </div>

        <div className="flex-1">
          <label className="text-sm font-medium text-muted-foreground block mb-2">
            FX Rate (1 USD =)
          </label>
          <div className="flex items-center gap-2">
            <Input
              type="number"
              step="0.01"
              min="0"
              value={isUSD ? 1 : fxRate}
              onChange={(e) => onFxRateChange(parseFloat(e.target.value) || 0)}
              disabled={isUSD}
              className="w-24"
            />
            <span className="text-sm text-muted-foreground">{currency}</span>
            {!isUSD && fxRateOverridden && (
              <Button
                variant="ghost"
                size="icon"
                onClick={onResetFxRate}
                className="h-8 w-8"
                title={`Reset to API rate (${apiFxRate.toFixed(2)})`}
              >
                <RotateCcw className="h-4 w-4" />
              </Button>
            )}
          </div>
          {!isUSD && (
            <span className="text-xs text-muted-foreground mt-1 block">
              {fxRateOverridden 
                ? `API rate: ${apiFxRate.toFixed(2)}` 
                : marketData?.fx_fallback_used 
                  ? '(fallback rate)' 
                  : '(live rate)'}
            </span>
          )}
        </div>

        <div className="flex-1">
          {marketData?.timestamp && (
            <div className="text-sm text-muted-foreground">
              <span className="block font-medium">Last Updated</span>
              <span className="text-xs">{marketData.timestamp}</span>
            </div>
          )}
        </div>

        <Button
          variant="outline"
          size="sm"
          onClick={() => onRefresh()}
          disabled={isLoading}
          className="gap-2"
        >
          <RefreshCw className={`h-4 w-4 ${isLoading ? 'animate-spin' : ''}`} />
          Refresh Prices
        </Button>
      </div>

      {error && (
        <div className="mt-3 p-3 bg-warning/10 border border-warning/30 rounded-lg flex items-center gap-2 text-sm">
          <AlertTriangle className="h-4 w-4 text-warning" />
          <span className="text-warning-foreground">
            Unable to fetch live prices. Using fallback values.
          </span>
        </div>
      )}

      {marketData?.fx_fallback_used && !error && (
        <div className="mt-3 p-3 bg-warning/10 border border-warning/30 rounded-lg flex items-center gap-2 text-sm">
          <AlertTriangle className="h-4 w-4 text-warning" />
          <span className="text-warning-foreground">
            Using fallback exchange rates.
          </span>
        </div>
      )}
    </div>
  );
}
