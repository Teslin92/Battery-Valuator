import { Factory } from 'lucide-react';
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
import type { FormData, NiProduct, LiProduct } from '@/types/battery';

interface PostTreatmentSectionProps {
  formData: FormData;
  onUpdate: (updates: Partial<FormData>) => void;
}

export function PostTreatmentSection({
  formData,
  onUpdate,
}: PostTreatmentSectionProps) {
  return (
    <div className="space-y-6">
      {/* Header with toggle */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2 text-sm font-semibold text-foreground uppercase tracking-wider">
          <Factory className="h-4 w-4 text-primary" />
          Post-Treatment
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
          Post-treatment disabled. Valuation will calculate black mass value only, without downstream processing costs or refined product revenue.
        </p>
      )}
    </div>
  );
}
