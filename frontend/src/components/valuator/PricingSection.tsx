import { DollarSign, Factory } from 'lucide-react';
import { Input } from '@/components/ui/input';
import { Slider } from '@/components/ui/slider';
import { Switch } from '@/components/ui/switch';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import type { FormData, MarketData, NiProduct, LiProduct } from '@/types/battery';

interface PricingSectionProps {
  formData: FormData;
  onUpdate: (updates: Partial<FormData>) => void;
  marketData?: MarketData;
}

const primaryMetals = [
  { key: 'ni', label: 'Nickel', symbol: 'Ni' },
  { key: 'co', label: 'Cobalt', symbol: 'Co' },
  { key: 'li', label: 'Lithium', symbol: 'Li' },
] as const;

const secondaryMetals = [
  { key: 'cu', label: 'Copper', symbol: 'Cu' },
  { key: 'al', label: 'Aluminum', symbol: 'Al' },
  { key: 'mn', label: 'Manganese', symbol: 'Mn' },
] as const;

export function PricingSection({
  formData,
  onUpdate,
  marketData,
}: PricingSectionProps) {
  const updatePrice = (key: string, value: number) => {
    onUpdate({
      prices: { ...formData.prices, [key]: value },
    });
  };

  const updatePayable = (key: string, value: number) => {
    onUpdate({
      payables: { ...formData.payables, [key]: value },
    });
  };

  const getMarketPrice = (key: string): number | null => {
    if (!marketData) return null;
    const keyMap: Record<string, keyof MarketData> = {
      ni: 'Ni',
      co: 'Co',
      li: 'Li',
      cu: 'Cu',
      al: 'Al',
      mn: 'Mn',
    };
    const marketKey = keyMap[key];
    if (!marketKey) return null;
    const value = marketData[marketKey];
    return typeof value === 'number' ? value : null;
  };

  const renderMetalRow = ({ key, label, symbol }: { key: string; label: string; symbol: string }) => (
    <div key={key} className="space-y-2 pb-3 border-b border-border last:border-0 last:pb-0">
      {/* Metal name and live price */}
      <div className="flex items-center justify-between">
        <label className="text-sm font-medium text-foreground">
          {label} ({symbol})
        </label>
        {marketData && (
          <span className="text-xs text-primary font-medium">
            Live: ${getMarketPrice(key)?.toFixed(2)}
          </span>
        )}
      </div>
      
      {/* Price and Payable on same row */}
      <div className="grid grid-cols-2 gap-2">
        {/* Price input */}
        <div className="flex items-center gap-1">
          <span className="text-xs text-muted-foreground">$</span>
          <Input
            type="number"
            value={formData.prices[key as keyof typeof formData.prices]}
            onChange={(e) => updatePrice(key, parseFloat(e.target.value) || 0)}
            min={0}
            step={0.1}
            className="font-mono h-8 text-sm"
          />
          <span className="text-xs text-muted-foreground">/kg</span>
        </div>
        
        {/* Payable input */}
        <div className="flex items-center gap-1">
          <Input
            type="number"
            value={formData.payables[key as keyof typeof formData.payables]}
            onChange={(e) => updatePayable(key, Math.min(300, Math.max(0, parseFloat(e.target.value) || 0)))}
            min={0}
            max={300}
            step={1}
            className="font-mono h-8 text-sm"
          />
          <span className="text-xs text-muted-foreground">%</span>
        </div>
      </div>
    </div>
  );

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center gap-2 text-sm font-semibold text-foreground uppercase tracking-wider">
        <DollarSign className="h-4 w-4 text-primary" />
        Metal Pricing & Payables
      </div>

      {/* All metals in two columns */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-x-6 gap-y-0">
        {/* Column headers - left */}
        <div className="grid grid-cols-2 gap-2 text-xs text-muted-foreground font-medium uppercase tracking-wider pb-2 border-b border-border mb-3">
          <span>Price (/kg)</span>
          <span>Payable (%)</span>
        </div>
        {/* Column headers - right */}
        <div className="hidden lg:grid grid-cols-2 gap-2 text-xs text-muted-foreground font-medium uppercase tracking-wider pb-2 border-b border-border mb-3">
          <span>Price (/kg)</span>
          <span>Payable (%)</span>
        </div>
        
        {/* Left column metals */}
        <div className="space-y-3">
          {primaryMetals.map(renderMetalRow)}
        </div>

        {/* Right column metals */}
        <div className="space-y-3 mt-3 lg:mt-0">
          {secondaryMetals.map(renderMetalRow)}
        </div>
      </div>

      {/* Refining Section */}
      <div className="border-t border-border pt-6 space-y-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2 text-sm font-semibold text-foreground uppercase tracking-wider">
            <Factory className="h-4 w-4 text-primary" />
            Refining
          </div>
          <div className="flex items-center gap-2">
            <span className="text-xs text-muted-foreground">
              {formData.refiningEnabled ? 'Enabled' : 'Black Mass Only'}
            </span>
            <Switch
              checked={formData.refiningEnabled}
              onCheckedChange={(checked) => onUpdate({ refiningEnabled: checked })}
            />
          </div>
        </div>

        {formData.refiningEnabled && (
          <div className="space-y-4 animate-in fade-in slide-in-from-top-2 duration-200">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="text-sm font-medium text-muted-foreground block mb-2">
                  Ni/Co Product
                </label>
                <Select
                  value={formData.niProduct}
                  onValueChange={(v) => onUpdate({ niProduct: v as NiProduct })}
                >
                  <SelectTrigger className="h-9">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="Sulphates (Battery Salt)">Sulphates (Battery Salt)</SelectItem>
                    <SelectItem value="MHP (Intermediate)">MHP (Intermediate)</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div>
                <label className="text-sm font-medium text-muted-foreground block mb-2">
                  Li Product
                </label>
                <Select
                  value={formData.liProduct}
                  onValueChange={(v) => onUpdate({ liProduct: v as LiProduct })}
                >
                  <SelectTrigger className="h-9">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="Carbonate (LCE)">Carbonate (LCE)</SelectItem>
                    <SelectItem value="Hydroxide (LiOH)">Hydroxide (LiOH)</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="text-sm font-medium text-muted-foreground block mb-2">
                  Refining OPEX ($/MT BM)
                </label>
                <Input
                  type="number"
                  value={formData.refiningOpex}
                  onChange={(e) => onUpdate({ refiningOpex: parseFloat(e.target.value) || 0 })}
                  min={0}
                  className="font-mono h-9"
                />
              </div>

              <div>
                <div className="flex justify-between mb-2">
                  <label className="text-sm font-medium text-muted-foreground">
                    Hydromet Recovery
                  </label>
                  <span className="text-sm font-semibold text-primary">
                    {formData.hydrometRecovery}%
                  </span>
                </div>
                <Slider
                  value={[formData.hydrometRecovery]}
                  onValueChange={([v]) => onUpdate({ hydrometRecovery: v })}
                  min={80}
                  max={100}
                  step={1}
                  className="w-full"
                />
              </div>
            </div>
          </div>
        )}

        {!formData.refiningEnabled && (
          <p className="text-sm text-muted-foreground bg-muted/50 rounded-lg p-3">
            Refining disabled. Valuation will calculate black mass value only, without downstream processing costs or refined product revenue.
          </p>
        )}
      </div>
    </div>
  );
}
