import { FlaskConical, Sparkles } from 'lucide-react';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Button } from '@/components/ui/button';
import { RadioGroup, RadioGroupItem } from '@/components/ui/radio-group';
import { Label } from '@/components/ui/label';
import type { FormData, AssayBasis } from '@/types/battery';

interface AssaySectionProps {
  formData: FormData;
  onUpdate: (updates: Partial<FormData>) => void;
  onParseCOA: () => void;
  isParsing: boolean;
}

const metals = [
  { key: 'ni', label: 'Nickel (Ni)' },
  { key: 'co', label: 'Cobalt (Co)' },
  { key: 'li', label: 'Lithium (Li)' },
  { key: 'cu', label: 'Copper (Cu)' },
  { key: 'al', label: 'Aluminum (Al)' },
  { key: 'mn', label: 'Manganese (Mn)' },
] as const;

export function AssaySection({
  formData,
  onUpdate,
  onParseCOA,
  isParsing,
}: AssaySectionProps) {
  const updateAssay = (key: string, value: number) => {
    onUpdate({
      assays: { ...formData.assays, [key]: value },
    });
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-2 text-sm font-semibold text-foreground uppercase tracking-wider">
        <FlaskConical className="h-4 w-4 text-primary" />
        Lab Assay
      </div>

      <div className="space-y-4">
        <div>
          <label className="text-sm font-medium text-muted-foreground block mb-3">
            Sample Source
          </label>
          <RadioGroup
            value={formData.assayBasis}
            onValueChange={(v) => onUpdate({ assayBasis: v as AssayBasis })}
            className="space-y-3"
          >
            <div className="flex items-start space-x-2">
              <RadioGroupItem value="Final Powder" id="final-powder" className="mt-0.5" />
              <div>
                <Label htmlFor="final-powder" className="cursor-pointer font-medium">Final Powder</Label>
                <p className="text-xs text-muted-foreground mt-0.5">
                  Assay taken from processed black mass after shredding/drying.
                </p>
              </div>
            </div>
            <div className="flex items-start space-x-2">
              <RadioGroupItem value="Whole Battery" id="whole-battery" className="mt-0.5" />
              <div>
                <Label htmlFor="whole-battery" className="cursor-pointer font-medium">Whole Battery</Label>
                <p className="text-xs text-muted-foreground mt-0.5">
                  Assay from complete battery cells before any processing (will be adjusted for yield).
                </p>
              </div>
            </div>
          </RadioGroup>
        </div>

        <div>
          <label className="text-sm font-medium text-muted-foreground block mb-2">
            Paste COA Text
          </label>
          <Textarea
            value={formData.coaText}
            onChange={(e) => onUpdate({ coaText: e.target.value })}
            placeholder={`Paste lab results here, e.g.:\nNi: 20.5%\nCo: 6.2%\nLi: 2.5%`}
            rows={4}
            className="font-mono text-sm"
          />
          <Button
            onClick={onParseCOA}
            disabled={isParsing || !formData.coaText.trim()}
            variant="outline"
            size="sm"
            className="mt-2 gap-2"
          >
            <Sparkles className={`h-4 w-4 ${isParsing ? 'animate-pulse' : ''}`} />
            {isParsing ? 'Parsing...' : 'Parse COA'}
          </Button>
        </div>

        <div className="text-xs font-medium text-muted-foreground uppercase tracking-wider">
          Manual Assay Inputs (%)
        </div>
        <div className="grid grid-cols-2 gap-3">
          {metals.map(({ key, label }) => (
            <div key={key}>
              <label className="text-xs font-medium text-muted-foreground block mb-1">
                {label}
              </label>
              <div className="flex items-center gap-1">
                <Input
                  type="number"
                  value={formData.assays[key as keyof typeof formData.assays]}
                  onChange={(e) => updateAssay(key, parseFloat(e.target.value) || 0)}
                  min={0}
                  max={100}
                  step={0.1}
                  className="font-mono text-sm"
                />
                <span className="text-sm text-muted-foreground">%</span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
