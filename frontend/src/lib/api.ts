import axios from 'axios';
import type { 
  Currency, 
  MarketData, 
  Assays, 
  CalculationRequest, 
  CalculationResult,
  TransportData,
  RouteAdvisory,
  TransportEstimate,
  RegulatoryRequirementsResponse
} from '@/types/battery';

// Configure base URL for Railway API
const API_BASE_URL = import.meta.env.VITE_API_URL || 'https://web-production-e2d0.up.railway.app';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export interface MarketDataResponse {
  success: boolean;
  data: MarketData;
}

export interface ParseCOAResponse {
  success: boolean;
  data: Assays;
}

export interface CalculateResponse {
  success: boolean;
  data: CalculationResult;
}

export interface ValidateAssaysResponse {
  success: boolean;
  data: {
    valid: boolean;
    warnings: string[];
  };
}

export const fetchMarketData = async (currency: Currency = 'USD'): Promise<MarketDataResponse> => {
  try {
    const response = await api.get<MarketDataResponse>(`/api/market-data?currency=${currency}`);
    return response.data;
  } catch (error) {
    console.error('Failed to fetch market data:', error);
    throw error;
  }
};

export const parseCOA = async (coaText: string): Promise<ParseCOAResponse> => {
  try {
    const response = await api.post<ParseCOAResponse>('/api/parse-coa', {
      coa_text: coaText,
    });
    return response.data;
  } catch (error) {
    console.error('Failed to parse COA:', error);
    throw error;
  }
};

export const calculateValuation = async (request: CalculationRequest): Promise<CalculateResponse> => {
  try {
    const response = await api.post<CalculateResponse>('/api/calculate', request);
    return response.data;
  } catch (error) {
    console.error('Failed to calculate valuation:', error);
    throw error;
  }
};

export const validateAssays = async (bmGrades: Record<string, number>): Promise<ValidateAssaysResponse> => {
  try {
    const response = await api.post<ValidateAssaysResponse>('/api/validate-assays', {
      bm_grades: bmGrades,
    });
    return response.data;
  } catch (error) {
    console.error('Failed to validate assays:', error);
    throw error;
  }
};

// ============================================================================
// TRANSPORT AND REGULATORY API FUNCTIONS
// ============================================================================

export interface RouteCheckResponse {
  success: boolean;
  data: RouteAdvisory;
}

export interface TransportEstimateResponse {
  success: boolean;
  data: TransportEstimate;
  error?: string;
  alternative?: string;
}

export interface RegulatoryRequirementsRequestResponse {
  success: boolean;
  data: RegulatoryRequirementsResponse;
}

export const checkTransportRoute = async (
  origin: string,
  destination: string,
  materialType: string
): Promise<RouteCheckResponse> => {
  try {
    const response = await api.post<RouteCheckResponse>('/api/transport/check-route', {
      origin,
      destination,
      materialType,
    });
    return response.data;
  } catch (error) {
    console.error('Failed to check transport route:', error);
    throw error;
  }
};

export const estimateTransportCost = async (
  transportData: TransportData
): Promise<TransportEstimateResponse> => {
  try {
    const response = await api.post<TransportEstimateResponse>('/api/transport/estimate', {
      origin: transportData.origin,
      destination: transportData.destination,
      mode: transportData.mode,
      weightKg: transportData.weightKg,
      materialType: transportData.materialType,
      isDDR: transportData.isDDR,
      distanceMiles: transportData.distanceMiles,
    });
    return response.data;
  } catch (error) {
    console.error('Failed to estimate transport cost:', error);
    throw error;
  }
};

export const fetchRegulatoryRequirements = async (
  origin: string,
  destination: string,
  material: string
): Promise<RegulatoryRequirementsRequestResponse> => {
  try {
    const response = await api.get<RegulatoryRequirementsRequestResponse>(
      `/api/regulatory/requirements?origin=${origin}&destination=${destination}&material=${material}`
    );
    return response.data;
  } catch (error) {
    console.error('Failed to fetch regulatory requirements:', error);
    throw error;
  }
};
