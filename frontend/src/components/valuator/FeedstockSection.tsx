import { Package } from 'lucide-react';
import { Input } from '@/components/ui/input';
import { Slider } from '@/components/ui/slider';
import { Checkbox } from '@/components/ui/checkbox';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import type { FeedType, FormData } from '@/types/battery';

interface FeedstockSectionProps {
  formData: FormData;
  onUpdate: (updates: Partial<FormData>) => void;
  onFeedTypeChange: (feedType: FeedType) => void;
  recoverableBlackMass: number;
}

const feedTypes: FeedType[] = [
  'Black Mass (Processed)',
  'Cathode Foils',
  'Cell Stacks / Jelly Rolls',
  'Whole Cells',
  'Modules',
  'Battery Packs',
];

export function FeedstockSection({
  formData,
  onUpdate,
  onFeedTypeChange,
  recoverableBlackMass,
}: FeedstockSectionProps) {
  const isBlackMass = formData.feedType === 'Black Mass (Processed)';

  return (
    <div className="space-y-5">
      <div className="flex items-center gap-2 text-sm font-semibold text-foreground uppercase tracking-wider">
        <Package className="h-4 w-4 text-primary" />
        Feedstock & Pre-treatment
      </div>

      <div className="space-y-4">
        <div>
          <label className="text-sm font-medium text-muted-foreground block mb-2">
            Material Type
          </label>
          <Select value={formData.feedType} onValueChange={(v) => onFeedTypeChange(v as FeedType)}>
            <SelectTrigger>
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              {feedTypes.map((type) => (
                <SelectItem key={type} value={type}>
                  {type}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>

        <div>
          <label className="text-sm font-medium text-muted-foreground block mb-2">
            Total Gross Weight (kg)
          </label>
          <Input
            type="number"
            value={formData.grossWeight}
            onChange={(e) => onUpdate({ grossWeight: parseFloat(e.target.value) || 0 })}
            min={0}
            className="font-mono"
          />
        </div>

        <div>
          <div className="flex justify-between mb-1">
            <label className="text-sm font-medium text-muted-foreground">
              Black Mass Yield
            </label>
            <span className="text-sm font-semibold text-primary">
              {formData.yieldPct}%
            </span>
          </div>
          <p className="text-xs text-muted-foreground mb-2">
            Percentage of input material recovered as black mass after shredding.
          </p>
          <Slider
            value={[formData.yieldPct]}
            onValueChange={([v]) => onUpdate({ yieldPct: v })}
            min={10}
            max={100}
            step={1}
            className="w-full"
          />
        </div>

        {!isBlackMass && (
          <div>
            <div className="flex justify-between mb-1">
              <label className="text-sm font-medium text-muted-foreground">
                Mechanical Recovery
              </label>
              <span className="text-sm font-semibold text-primary">
                {formData.mechRecovery}%
              </span>
            </div>
            <p className="text-xs text-muted-foreground mb-2">
              Efficiency of physical separation (shredding, sieving) before hydromet.
            </p>
            <Slider
              value={[formData.mechRecovery]}
              onValueChange={([v]) => onUpdate({ mechRecovery: v })}
              min={80}
              max={100}
              step={1}
              className="w-full"
            />
          </div>
        )}

        <div className="flex items-center gap-3">
          <Checkbox
            id="hasElectrolyte"
            checked={formData.hasElectrolyte}
            onCheckedChange={(checked) => onUpdate({ hasElectrolyte: !!checked })}
          />
          <label htmlFor="hasElectrolyte" className="text-sm font-medium cursor-pointer">
            Contains Electrolyte
          </label>
        </div>

        {formData.hasElectrolyte && (
          <div>
            <label className="text-sm font-medium text-muted-foreground block mb-2">
              Electrolyte Surcharge ($/MT)
            </label>
            <Input
              type="number"
              value={formData.elecSurcharge}
              onChange={(e) => onUpdate({ elecSurcharge: parseFloat(e.target.value) || 0 })}
              min={0}
              className="font-mono"
            />
          </div>
        )}

        {!isBlackMass && (
          <div>
            <label className="text-sm font-medium text-muted-foreground block mb-2">
              Mechanical/Shred Cost ($/MT)
            </label>
            <Input
              type="number"
              value={formData.shreddingCost}
              onChange={(e) => onUpdate({ shreddingCost: parseFloat(e.target.value) || 0 })}
              min={0}
              className="font-mono"
            />
          </div>
        )}

        <div className="p-4 bg-secondary rounded-lg">
          <div className="text-sm text-muted-foreground">Recoverable Black Mass</div>
          <div className="text-xl font-bold text-foreground">
            {recoverableBlackMass.toLocaleString(undefined, { maximumFractionDigits: 1 })} kg
          </div>
        </div>
      </div>
    </div>
  );
}
