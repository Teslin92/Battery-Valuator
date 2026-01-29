import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Label } from '@/components/ui/label';
import { Input } from '@/components/ui/input';
import { Checkbox } from '@/components/ui/checkbox';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { AlertCircle, Info, Truck, Ship, Plane, DollarSign } from 'lucide-react';
import {
  TransportData,
  TransportMode,
  MaterialType,
  COUNTRIES,
  MATERIAL_TYPE_LABELS,
  TRANSPORT_MODE_LABELS,
} from '@/types/battery';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { estimateTransportCost } from '@/lib/api';

interface TransportationSectionProps {
  transportData: TransportData;
  onTransportDataChange: (data: TransportData) => void;
  weightKg: number;
}

export const TransportationSection = ({
  transportData,
  onTransportDataChange,
  weightKg,
}: TransportationSectionProps) => {
  const [showDistanceInput, setShowDistanceInput] = useState(transportData.mode === 'truck');
  const [transportEstimate, setTransportEstimate] = useState<any>(null);
  const [isLoadingEstimate, setIsLoadingEstimate] = useState(false);

  useEffect(() => {
    setShowDistanceInput(transportData.mode === 'truck');
  }, [transportData.mode]);

  // Fetch transport estimate when relevant fields change
  useEffect(() => {
    const fetchEstimate = async () => {
      // Only fetch if we have required data
      if (!transportData.origin || !transportData.destination) {
        setTransportEstimate(null);
        return;
      }
      if (transportData.mode === 'truck' && !transportData.distanceMiles) {
        setTransportEstimate(null);
        return;
      }
      
      setIsLoadingEstimate(true);
      try {
        const response = await estimateTransportCost({
          ...transportData,
          weightKg: weightKg  // Use the current weightKg prop
        });
        if (response.success) {
          setTransportEstimate(response.data);
        } else {
          setTransportEstimate(null);
        }
      } catch (error) {
        console.error('Failed to fetch transport estimate:', error);
        setTransportEstimate(null);
      } finally {
        setIsLoadingEstimate(false);
      }
    };

    // Small delay to debounce rapid changes
    const timeoutId = setTimeout(() => {
      fetchEstimate();
    }, 300);

    return () => clearTimeout(timeoutId);
  }, [transportData.origin, transportData.destination, transportData.mode, transportData.materialType, transportData.distanceMiles, transportData.isDDR, weightKg]);

  const handleChange = (field: keyof TransportData, value: any) => {
    const updated = { ...transportData, [field]: value };
    
    // Update weight if it changes
    if (field !== 'weightKg') {
      updated.weightKg = weightKg;
    }
    
    onTransportDataChange(updated);
  };

  const getModeIcon = (mode: TransportMode) => {
    switch (mode) {
      case 'ocean':
        return <Ship className="h-4 w-4" />;
      case 'air':
        return <Plane className="h-4 w-4" />;
      case 'truck':
        return <Truck className="h-4 w-4" />;
    }
  };

  return (
    <Card className="bg-card rounded-xl border-border card-shadow">
      <CardHeader className="pb-4">
        <div className="flex items-center gap-2 text-sm font-semibold text-foreground uppercase tracking-wider">
          <Truck className="h-4 w-4 text-primary" />
          Transportation & Logistics
        </div>
      </CardHeader>
      <CardContent className="space-y-6">
        {/* Origin & Destination */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="space-y-2">
            <Label htmlFor="origin">Origin Country</Label>
            <Select
              value={transportData.origin}
              onValueChange={(value) => handleChange('origin', value)}
            >
              <SelectTrigger id="origin">
                <SelectValue placeholder="Select origin" />
              </SelectTrigger>
              <SelectContent>
                {COUNTRIES.map((country) => (
                  <SelectItem key={country.code} value={country.code}>
                    {country.name} {country.oecd && '(OECD)'}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          <div className="space-y-2">
            <Label htmlFor="destination">Destination Country</Label>
            <Select
              value={transportData.destination}
              onValueChange={(value) => handleChange('destination', value)}
            >
              <SelectTrigger id="destination">
                <SelectValue placeholder="Select destination" />
              </SelectTrigger>
              <SelectContent>
                {COUNTRIES.map((country) => (
                  <SelectItem key={country.code} value={country.code}>
                    {country.name} {country.oecd && '(OECD)'}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
        </div>

        {/* Material Type */}
        <div className="space-y-2">
          <Label htmlFor="materialType">Material Classification</Label>
          <Select
            value={transportData.materialType}
            onValueChange={(value) => handleChange('materialType', value as MaterialType)}
          >
            <SelectTrigger id="materialType">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              {Object.entries(MATERIAL_TYPE_LABELS).map(([value, label]) => (
                <SelectItem key={value} value={value}>
                  {label}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
          <p className="text-xs text-muted-foreground">
            Determines regulatory classification and requirements
          </p>
        </div>

        {/* Transport Mode */}
        <div className="space-y-2">
          <Label>Transport Mode</Label>
          <div className="grid grid-cols-3 gap-2">
            {Object.entries(TRANSPORT_MODE_LABELS).map(([mode, label]) => (
              <button
                key={mode}
                type="button"
                onClick={() => handleChange('mode', mode as TransportMode)}
                className={`
                  flex items-center justify-center gap-2 p-3 rounded-lg border-2 transition-all
                  ${
                    transportData.mode === mode
                      ? 'border-primary bg-primary/5 text-primary'
                      : 'border-border hover:border-primary/50'
                  }
                `}
              >
                {getModeIcon(mode as TransportMode)}
                <span className="text-sm font-medium">{label}</span>
              </button>
            ))}
          </div>
        </div>

        {/* Distance input for truck mode */}
        {showDistanceInput && (
          <div className="space-y-2">
            <Label htmlFor="distanceMiles">Distance (miles)</Label>
            <Input
              id="distanceMiles"
              type="number"
              value={transportData.distanceMiles || ''}
              onChange={(e) => handleChange('distanceMiles', parseFloat(e.target.value) || undefined)}
              placeholder="Enter distance in miles"
            />
            <p className="text-xs text-muted-foreground">
              Required for truck transport cost calculation
            </p>
          </div>
        )}

        {/* Weight display */}
        <div className="space-y-2">
          <Label>Shipment Weight</Label>
          <div className="p-3 bg-muted rounded-lg">
            <p className="text-sm">
              <span className="font-semibold">{weightKg.toLocaleString()}</span> kg (
              {(weightKg / 1000).toFixed(2)} metric tons)
            </p>
          </div>
        </div>

        {/* DDR Checkbox */}
        <div className="flex items-start space-x-3 p-4 bg-warning/10 border border-warning/30 rounded-lg">
          <Checkbox
            id="isDDR"
            checked={transportData.isDDR}
            onCheckedChange={(checked) => handleChange('isDDR', checked === true)}
          />
          <div className="space-y-1">
            <Label
              htmlFor="isDDR"
              className="text-sm font-medium leading-none cursor-pointer"
            >
              DDR Batteries (Damaged, Defective, or Recalled)
            </Label>
            <p className="text-xs text-muted-foreground">
              Special packaging and restrictions apply. Air transport prohibited.
            </p>
          </div>
        </div>

        {/* DDR Air Transport Warning */}
        {transportData.isDDR && transportData.mode === 'air' && (
          <Alert variant="destructive">
            <AlertCircle className="h-4 w-4" />
            <AlertDescription>
              DDR batteries cannot be transported by air. Please select ocean or truck transport.
            </AlertDescription>
          </Alert>
        )}

        {/* Transport Cost Estimate */}
        {transportEstimate && !transportData.manualOverride && (
          <div className="p-4 bg-profit/10 border border-profit/30 rounded-lg">
            <div className="flex items-center justify-between mb-2">
              <div className="flex items-center gap-2">
                <DollarSign className="h-5 w-5 text-profit" />
                <span className="font-semibold text-foreground">Estimated Transport Cost</span>
              </div>
              <span className="text-2xl font-bold text-profit">
                ${transportEstimate.estimated_cost?.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
              </span>
            </div>
            
            {transportEstimate.vehicle_type && (
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Vehicle/Container:</span>
                  <span className="font-medium text-foreground">{transportEstimate.vehicle_type}</span>
                </div>
                {transportEstimate.num_vehicles && (
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Quantity:</span>
                    <span className="font-medium text-foreground">{transportEstimate.num_vehicles}</span>
                  </div>
                )}
                {transportEstimate.capacity_per_vehicle_kg && (
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Capacity:</span>
                    <span className="font-medium text-foreground">{transportEstimate.capacity_per_vehicle_kg.toLocaleString()} kg each</span>
                  </div>
                )}
                {transportEstimate.utilization_pct !== null && transportEstimate.utilization_pct !== undefined && (
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Utilization:</span>
                    <span className="font-medium text-foreground">{transportEstimate.utilization_pct}%</span>
                  </div>
                )}
                {transportEstimate.cost_per_kg && (
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Cost per kg:</span>
                    <span className="font-medium text-foreground">${transportEstimate.cost_per_kg.toFixed(2)}/kg</span>
                  </div>
                )}
              </div>
            )}
            
            {/* Show the correct note based on actual data */}
            {transportEstimate.sizing_note && (
              <p className="text-xs text-muted-foreground mt-3 pt-3 border-t border-profit/30">
                {transportEstimate.sizing_note}
              </p>
            )}
          </div>
        )}
        
        {/* Loading indicator */}
        {isLoadingEstimate && (
          <div className="p-4 bg-primary/10 border border-primary/30 rounded-lg">
            <div className="flex items-center gap-2">
              <div className="animate-spin h-4 w-4 border-2 border-primary border-t-transparent rounded-full"></div>
              <span className="text-sm text-foreground">Calculating transport cost...</span>
            </div>
          </div>
        )}

        {/* Manual Override */}
        <div className="space-y-3 pt-4 border-t border-border">
          <div className="flex items-center space-x-3">
            <Checkbox
              id="manualOverride"
              checked={transportData.manualOverride}
              onCheckedChange={(checked) => handleChange('manualOverride', checked === true)}
            />
            <Label htmlFor="manualOverride" className="cursor-pointer">
              Manual Cost Override
            </Label>
          </div>

          {transportData.manualOverride && (
            <div className="space-y-2">
              <Label htmlFor="manualCost">Custom Transport Cost (USD)</Label>
              <Input
                id="manualCost"
                type="number"
                value={transportData.manualCost || ''}
                onChange={(e) => handleChange('manualCost', parseFloat(e.target.value) || undefined)}
                placeholder="Enter custom cost"
              />
              <p className="text-xs text-muted-foreground">
                Override the estimated cost with actual quoted rates
              </p>
            </div>
          )}
        </div>

        {/* Info Alert */}
        <Alert>
          <Info className="h-4 w-4" />
          <AlertDescription className="text-xs">
            Transport costs are benchmark estimates based on realistic container/vehicle pricing. Actual
            costs vary by carrier, season, and volume. Use manual override for precise quotes.
          </AlertDescription>
        </Alert>
      </CardContent>
    </Card>
  );
};
