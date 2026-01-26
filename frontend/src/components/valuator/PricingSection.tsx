import { DollarSign } from 'lucide-react';
import { Input } from '@/components/ui/input';
import { Slider } from '@/components/ui/slider';
import type { FormData, MarketData } from '@/types/battery';

interface PricingSectionProps {
  formData: FormData;
  onUpdate: (updates: Partial<FormData>) => void;
  marketData?: MarketData;
}

const metalInfo = [
  { key: 'ni', label: 'Nickel (Ni)', primary: true },
  { key: 'co', label: 'Cobalt (Co)', primary: true },
  { key: 'li', label: 'Lithium (Li)', primary: true },
  { key: 'cu', label: 'Copper (Cu)', primary: false },
  { key: 'al', label: 'Aluminum (Al)', primary: false },
  { key: 'mn', label: 'Manganese (Mn)', primary: false },
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

  return (
    <div className="space-y-5">
      <div className="flex items-center gap-2 text-sm font-semibold text-foreground uppercase tracking-wider">
        <DollarSign className="h-4 w-4 text-primary" />
        Metal Pricing
      </div>

      <div className="space-y-4">
        <div className="text-xs font-medium text-muted-foreground uppercase tracking-wider">
          Primary Metals
        </div>
        {metalInfo.filter(m => m.primary).map(({ key, label }) => (
          <div key={key} className="space-y-2">
            <div className="flex items-center justify-between">
              <label className="text-sm font-medium text-muted-foreground">
                {label}
              </label>
              {marketData && (
                <span className="text-xs text-primary font-medium">
                  Live: ${getMarketPrice(key)?.toFixed(2)}
                </span>
              )}
            </div>
            <div className="flex items-center gap-2">
              <span className="text-sm text-muted-foreground">$</span>
              <Input
                type="number"
                value={formData.prices[key as keyof typeof formData.prices]}
                onChange={(e) => updatePrice(key, parseFloat(e.target.value) || 0)}
                min={0}
                step={0.1}
                className="font-mono"
              />
              <span className="text-sm text-muted-foreground">/kg</span>
            </div>
          </div>
        ))}

        <div className="text-xs font-medium text-muted-foreground uppercase tracking-wider pt-4">
          Secondary Metals
        </div>
        {metalInfo.filter(m => !m.primary).map(({ key, label }) => (
          <div key={key} className="space-y-2">
            <div className="flex items-center justify-between">
              <label className="text-sm font-medium text-muted-foreground">
                {label}
              </label>
              {marketData && (
                <span className="text-xs text-primary font-medium">
                  Live: ${getMarketPrice(key)?.toFixed(2)}
                </span>
              )}
            </div>
            <div className="flex items-center gap-2">
              <span className="text-sm text-muted-foreground">$</span>
              <Input
                type="number"
                value={formData.prices[key as keyof typeof formData.prices]}
                onChange={(e) => updatePrice(key, parseFloat(e.target.value) || 0)}
                min={0}
                step={0.1}
                className="font-mono"
              />
              <span className="text-sm text-muted-foreground">/kg</span>
            </div>
          </div>
        ))}

        <div className="text-xs font-medium text-muted-foreground uppercase tracking-wider pt-4">
          Payables (% of metal price paid)
        </div>
        {metalInfo.map(({ key, label }) => (
          <div key={`payable-${key}`} className="space-y-2">
            <div className="flex justify-between items-center">
              <label className="text-sm font-medium text-muted-foreground">
                {label.split(' ')[0]}
              </label>
              <div className="flex items-center gap-1">
                <Input
                  type="number"
                  value={formData.payables[key as keyof typeof formData.payables]}
                  onChange={(e) => updatePayable(key, Math.min(300, Math.max(0, parseFloat(e.target.value) || 0)))}
                  min={0}
                  max={300}
                  step={1}
                  className="w-20 font-mono text-sm h-8"
                />
                <span className="text-sm text-muted-foreground">%</span>
              </div>
            </div>
            <Slider
              value={[formData.payables[key as keyof typeof formData.payables]]}
              onValueChange={([v]) => updatePayable(key, v)}
              min={0}
              max={300}
              step={1}
              className="w-full"
            />
          </div>
        ))}
      </div>
    </div>
  );
}
