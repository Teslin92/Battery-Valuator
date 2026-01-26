import { Factory } from 'lucide-react';
import { Input } from '@/components/ui/input';
import { Slider } from '@/components/ui/slider';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import type { FormData, NiProduct, LiProduct } from '@/types/battery';

interface RefiningSectionProps {
  formData: FormData;
  onUpdate: (updates: Partial<FormData>) => void;
}

export function RefiningSection({ formData, onUpdate }: RefiningSectionProps) {
  return (
    <div className="space-y-5">
      <div className="flex items-center gap-2 text-sm font-semibold text-foreground uppercase tracking-wider">
        <Factory className="h-4 w-4 text-primary" />
        Refining
      </div>

      <div className="space-y-4">
        <div>
          <label className="text-sm font-medium text-muted-foreground block mb-2">
            Ni/Co Product
          </label>
          <Select
            value={formData.niProduct}
            onValueChange={(v) => onUpdate({ niProduct: v as NiProduct })}
          >
            <SelectTrigger>
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
            <SelectTrigger>
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="Carbonate (LCE)">Carbonate (LCE)</SelectItem>
              <SelectItem value="Hydroxide (LiOH)">Hydroxide (LiOH)</SelectItem>
            </SelectContent>
          </Select>
        </div>

        <div>
          <label className="text-sm font-medium text-muted-foreground block mb-2">
            Refining OPEX ($/MT BM)
          </label>
          <Input
            type="number"
            value={formData.refiningOpex}
            onChange={(e) => onUpdate({ refiningOpex: parseFloat(e.target.value) || 0 })}
            min={0}
            className="font-mono"
          />
        </div>

        <div>
          <div className="flex justify-between mb-1">
            <label className="text-sm font-medium text-muted-foreground">
              Hydromet Recovery
            </label>
            <span className="text-sm font-semibold text-primary">
              {formData.hydrometRecovery}%
            </span>
          </div>
          <p className="text-xs text-muted-foreground mb-2">
            Chemical extraction efficiency of metals from black mass via leaching and precipitation.
          </p>
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
  );
}
