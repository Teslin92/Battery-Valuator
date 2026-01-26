export type Currency = 'USD' | 'CAD' | 'EUR' | 'CNY';

export type FeedType = 
  | 'Black Mass (Processed)'
  | 'Cathode Foils'
  | 'Cell Stacks / Jelly Rolls'
  | 'Whole Cells'
  | 'Modules'
  | 'Battery Packs';

export type NiProduct = 'Sulphates (Battery Salt)' | 'MHP (Intermediate)';
export type LiProduct = 'Carbonate (LCE)' | 'Hydroxide (LiOH)';
export type AssayBasis = 'Whole Battery' | 'Final Powder';

export interface MetalPrices {
  Ni: number;
  Co: number;
  Li: number;
  Cu: number;
  Al: number;
  Mn: number;
}

export interface MarketData {
  FX: number;
  fx_fallback_used: boolean;
  timestamp: string;
  Ni: number;
  Co: number;
  Li: number;
  Cu: number;
  Al: number;
  Mn: number;
  NiSO4: number;
  CoSO4: number;
  LCE: number;
  LiOH: number;
}

export interface Assays {
  Nickel: number;
  Cobalt: number;
  Lithium: number;
  Copper: number;
  Aluminum: number;
  Manganese: number;
}

export interface Payables {
  Ni: number;
  Co: number;
  Li: number;
  Cu: number;
  Al: number;
  Mn: number;
}

export interface CalculationRequest {
  currency: Currency;
  gross_weight: number;
  feed_type: FeedType;
  yield_pct: number;
  mech_recovery: number;
  hydromet_recovery: number;
  assays: Assays;
  assay_basis: AssayBasis;
  metal_prices: MetalPrices;
  payables: Payables;
  shredding_cost_per_ton: number;
  elec_surcharge: number;
  has_electrolyte: boolean;
  refining_opex_base: number;
  ni_product: NiProduct;
  li_product: LiProduct;
}

export interface ProductionItem {
  Product: string;
  'Mass (kg)': number;
  Revenue: number;
}

export interface CalculationResult {
  net_bm_weight: number;
  bm_grades: Record<string, number>;
  masses: Record<string, number>;
  costs: Record<string, number>;
  material_cost: number;
  total_pre_treat: number;
  total_refining_cost: number;
  total_opex: number;
  production_data: ProductionItem[];
  total_revenue: number;
  net_profit: number;
  margin_pct: number;
  warnings: string[];
  cost_breakdown: {
    shredding: number;
    electrolyte: number;
    refining: number;
  };
}

export interface FormData {
  currency: Currency;
  fxRate: number;
  fxRateOverridden: boolean;
  grossWeight: number;
  feedType: FeedType;
  yieldPct: number;
  mechRecovery: number;
  hydrometRecovery: number;
  assayBasis: AssayBasis;
  hasElectrolyte: boolean;
  elecSurcharge: number;
  shreddingCost: number;
  refiningOpex: number;
  niProduct: NiProduct;
  liProduct: LiProduct;
  prices: {
    ni: number;
    co: number;
    li: number;
    cu: number;
    al: number;
    mn: number;
  };
  payables: {
    ni: number;
    co: number;
    li: number;
    cu: number;
    al: number;
    mn: number;
  };
  assays: {
    ni: number;
    co: number;
    li: number;
    cu: number;
    al: number;
    mn: number;
  };
  coaText: string;
}

export const FEED_TYPE_YIELDS: Record<FeedType, number> = {
  'Black Mass (Processed)': 100,
  'Cathode Foils': 90,
  'Cell Stacks / Jelly Rolls': 70,
  'Whole Cells': 60,
  'Modules': 50,
  'Battery Packs': 40,
};

export const DEFAULT_PAYABLES = {
  ni: 70,
  co: 70,
  li: 70,
  cu: 0,
  al: 0,
  mn: 0,
};

export const METAL_LABELS: Record<string, string> = {
  ni: 'Nickel',
  co: 'Cobalt',
  li: 'Lithium',
  cu: 'Copper',
  al: 'Aluminum',
  mn: 'Manganese',
};
