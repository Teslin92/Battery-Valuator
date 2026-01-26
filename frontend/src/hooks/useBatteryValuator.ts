import { useState, useCallback, useEffect } from 'react';
import { useQuery, useMutation } from '@tanstack/react-query';
import { fetchMarketData, parseCOA, calculateValuation } from '@/lib/api';
import type { 
  Currency, 
  FormData, 
  CalculationResult, 
  MarketData,
  FeedType,
  FEED_TYPE_YIELDS,
  DEFAULT_PAYABLES
} from '@/types/battery';

const initialFormData: FormData = {
  currency: 'USD',
  fxRate: 1,
  fxRateOverridden: false,
  grossWeight: 1000,
  feedType: 'Black Mass (Processed)',
  yieldPct: 100,
  mechRecovery: 95,
  hydrometRecovery: 95,
  assayBasis: 'Final Powder',
  hasElectrolyte: false,
  elecSurcharge: 150,
  // Black Mass (default) requires no pre-treatment, so shredding cost starts at 0
  shreddingCost: 0,
  refiningOpex: 1500,
  niProduct: 'Sulphates (Battery Salt)',
  liProduct: 'Carbonate (LCE)',
  prices: {
    ni: 16.5,
    co: 33.0,
    li: 13.5,
    cu: 9.2,
    al: 2.5,
    mn: 1.8,
  },
  payables: {
    ni: 70,
    co: 70,
    li: 70,
    cu: 0,
    al: 0,
    mn: 0,
  },
  assays: {
    ni: 20.5,
    co: 6.2,
    li: 2.5,
    cu: 3.5,
    al: 1.2,
    mn: 4.8,
  },
  coaText: '',
};

export function useBatteryValuator() {
  const [formData, setFormData] = useState<FormData>(initialFormData);
  const [result, setResult] = useState<CalculationResult | null>(null);

  // Fetch market data
  const { 
    data: marketData, 
    isLoading: isLoadingMarket, 
    refetch: refetchMarket,
    error: marketError 
  } = useQuery({
    queryKey: ['marketData', formData.currency],
    queryFn: () => fetchMarketData(formData.currency),
    staleTime: 5 * 60 * 1000, // 5 minutes
  });

  // Update prices and FX rate when market data changes
  useEffect(() => {
    if (marketData?.data) {
      const data = marketData.data;
      setFormData(prev => ({
        ...prev,
        prices: {
          ni: parseFloat(data.Ni.toFixed(2)),
          co: parseFloat(data.Co.toFixed(2)),
          li: parseFloat(data.Li.toFixed(2)),
          cu: parseFloat(data.Cu.toFixed(2)),
          al: parseFloat(data.Al.toFixed(2)),
          mn: parseFloat(data.Mn.toFixed(2)),
        },
        // Only update FX rate if not manually overridden
        ...(prev.fxRateOverridden ? {} : { fxRate: parseFloat(data.FX.toFixed(2)) }),
      }));
    }
  }, [marketData]);

  // Parse COA mutation
  const coaMutation = useMutation({
    mutationFn: parseCOA,
    onSuccess: (response) => {
      if (response.success && response.data) {
        const data = response.data;
        setFormData(prev => ({
          ...prev,
          assays: {
            ni: (data.Nickel || 0) * 100,
            co: (data.Cobalt || 0) * 100,
            li: (data.Lithium || 0) * 100,
            cu: (data.Copper || 0) * 100,
            al: (data.Aluminum || 0) * 100,
            mn: (data.Manganese || 0) * 100,
          },
        }));
      }
    },
  });

  // Calculate valuation mutation
  const calcMutation = useMutation({
    mutationFn: calculateValuation,
    onSuccess: (response) => {
      if (response.success && response.data) {
        setResult(response.data);
      }
    },
  });

  const updateFormData = useCallback((updates: Partial<FormData>) => {
    setFormData(prev => ({ ...prev, ...updates }));
  }, []);

  const updateFxRate = useCallback((rate: number) => {
    setFormData(prev => ({
      ...prev,
      fxRate: rate,
      fxRateOverridden: true,
    }));
  }, []);

  const resetFxRate = useCallback(() => {
    if (marketData?.data) {
      setFormData(prev => ({
        ...prev,
        fxRate: parseFloat(marketData.data.FX.toFixed(2)),
        fxRateOverridden: false,
      }));
    }
  }, [marketData]);

  const updateFeedType = useCallback((feedType: FeedType) => {
    const yields: Record<FeedType, number> = {
      'Black Mass (Processed)': 100,
      'Cathode Foils': 90,
      'Cell Stacks / Jelly Rolls': 70,
      'Whole Cells': 60,
      'Modules': 50,
      'Battery Packs': 40,
    };
    const isBlackMass = feedType === 'Black Mass (Processed)';
    setFormData(prev => ({
      ...prev,
      feedType,
      yieldPct: yields[feedType],
      // Black Mass requires no pre-treatment; other types default to 300
      shreddingCost: isBlackMass ? 0 : 300,
    }));
  }, []);

  const handleParseCOA = useCallback(() => {
    if (formData.coaText.trim()) {
      coaMutation.mutate(formData.coaText);
    }
  }, [formData.coaText, coaMutation]);

  const handleCalculate = useCallback(() => {
    const request = {
      currency: formData.currency,
      gross_weight: formData.grossWeight,
      feed_type: formData.feedType,
      yield_pct: formData.yieldPct / 100,
      mech_recovery: formData.mechRecovery / 100,
      hydromet_recovery: formData.hydrometRecovery / 100,
      assays: {
        Nickel: formData.assays.ni / 100,
        Cobalt: formData.assays.co / 100,
        Lithium: formData.assays.li / 100,
        Copper: formData.assays.cu / 100,
        Aluminum: formData.assays.al / 100,
        Manganese: formData.assays.mn / 100,
      },
      assay_basis: formData.assayBasis,
      metal_prices: {
        Ni: formData.prices.ni,
        Co: formData.prices.co,
        Li: formData.prices.li,
        Cu: formData.prices.cu,
        Al: formData.prices.al,
        Mn: formData.prices.mn,
      },
      payables: {
        Ni: formData.payables.ni / 100,
        Co: formData.payables.co / 100,
        Li: formData.payables.li / 100,
        Cu: formData.payables.cu / 100,
        Al: formData.payables.al / 100,
        Mn: formData.payables.mn / 100,
      },
      // Black Mass requires no pre-treatment, so shredding cost is 0
      shredding_cost_per_ton: formData.feedType === 'Black Mass (Processed)' ? 0 : formData.shreddingCost,
      elec_surcharge: formData.hasElectrolyte ? formData.elecSurcharge : 0,
      has_electrolyte: formData.hasElectrolyte,
      refining_opex_base: formData.refiningOpex,
      ni_product: formData.niProduct,
      li_product: formData.liProduct,
    };
    calcMutation.mutate(request);
  }, [formData, calcMutation]);

  const recoverableBlackMass = (formData.grossWeight * formData.yieldPct / 100);

  return {
    formData,
    updateFormData,
    updateFeedType,
    updateFxRate,
    resetFxRate,
    result,
    marketData: marketData?.data,
    isLoadingMarket,
    marketError,
    refetchMarket,
    handleParseCOA,
    isParsingCOA: coaMutation.isPending,
    handleCalculate,
    isCalculating: calcMutation.isPending,
    calculationError: calcMutation.error,
    recoverableBlackMass,
  };
}
