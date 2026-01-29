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
  refining_enabled: boolean;
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
  refiningEnabled: boolean;
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

// ============================================================================
// TRANSPORT AND REGULATORY TYPES
// ============================================================================

export type TransportMode = 'ocean' | 'air' | 'truck';
export type MaterialType = 'whole_batteries' | 'black_mass' | 'processed';
export type RouteStatus = 'allowed' | 'restricted' | 'blocked' | 'unknown';

export interface TransportData {
  origin: string;
  destination: string;
  mode: TransportMode;
  materialType: MaterialType;
  isDDR: boolean; // Damaged/Defective/Recalled
  weightKg: number;
  distanceMiles?: number; // Required for truck mode
  manualOverride?: boolean;
  manualCost?: number;
}

export interface TransportEstimate {
  estimated_cost: number;
  mode: TransportMode;
  weight_mt: number;
  weight_kg: number;
  is_hazmat: boolean;
  is_ddr: boolean;
  breakdown: {
    base_cost: number;
    hazmat_surcharge: number;
    total: number;
  };
  currency: string;
  note: string;
  manual_override_allowed: boolean;
  error?: string;
  alternative?: string;
}

export interface RouteAdvisory {
  allowed: boolean;
  status: RouteStatus;
  requirements: string[];
  warnings: string[];
  processing_time?: string;
  origin_regulations: {
    framework?: string;
    authority?: string;
  };
  destination_regulations: {
    framework?: string;
    authority?: string;
  };
}

export interface PermitItem {
  name: string;
  agency: string;
  required: boolean | string;
  processing_time?: string;
  validity?: string;
  application_system?: string;
  url?: string;
  description?: string;
}

export interface PackagingRequirement {
  un_classification?: {
    un_number: string;
    class: string;
    packing_group: string;
  };
  regulations?: string[];
  requirements?: string[];
  restrictions?: {
    air_transport?: string;
    ground_transport?: string;
  };
  special_requirements?: string[];
}

export interface WasteRegulatoryInfo {
  material_classification: {
    type: MaterialType;
    description?: string;
    hazard_class?: string;
    waste_codes?: string[];
    basel_annex?: string;
  };
  origin: {
    country: string;
    framework?: string;
    authority?: string;
    classification?: Record<string, any>;
    export_requirements?: Record<string, any>;
    key_regulations?: string[];
    links?: Record<string, string>;
  };
  destination: {
    country: string;
    framework?: string;
    authority?: string;
    classification?: Record<string, any>;
    import_requirements?: Record<string, any>;
    links?: Record<string, string>;
  };
}

export interface RegulatoryChecklist {
  export_permits: PermitItem[];
  basel_convention: Array<{
    name: string;
    description: string;
    regulation?: string;
    applies_to?: string;
    required: boolean;
  }>;
  packaging: PackagingRequirement;
  documentation: Array<{
    name: string;
    required: boolean | string;
    description: string;
  }>;
}

export interface RegulatoryRequirementsResponse {
  checklist: RegulatoryChecklist;
  regulations: WasteRegulatoryInfo;
}

// Extended calculation result with transport data
export interface CalculationResultWithTransport extends CalculationResult {
  transport_cost?: number;
  transport_estimate?: TransportEstimate;
  route_advisory?: RouteAdvisory;
  transport_error?: string;
}

// Country options for dropdowns
export const COUNTRIES = [
  { code: 'US', name: 'United States', oecd: true },
  { code: 'Canada', name: 'Canada', oecd: true },
  { code: 'China', name: 'China', oecd: false },
  { code: 'EU', name: 'European Union', oecd: true },
  { code: 'Mexico', name: 'Mexico', oecd: true },
  { code: 'South Korea', name: 'South Korea', oecd: true },
] as const;

export const MATERIAL_TYPE_LABELS: Record<MaterialType, string> = {
  whole_batteries: 'Whole Batteries (Assembled Cells with Electrolyte)',
  black_mass: 'Black Mass (Electrode Scrap, Foils, Jelly Rolls, Shredded Material)',
  processed: 'Processed Metals (Refined Products)',
};

export const TRANSPORT_MODE_LABELS: Record<TransportMode, string> = {
  ocean: 'Ocean Freight',
  air: 'Air Freight',
  truck: 'Ground/Truck',
};
