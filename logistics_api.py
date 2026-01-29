"""
API clients for external logistics and regulatory data sources.
Includes caching to minimize API calls and improve performance.
"""

import os
import requests
from functools import lru_cache
from typing import Dict, Any, Optional
from datetime import datetime, timedelta

# API Configuration
EPA_RCRAINFO_BASE_URL = "https://rcrainfo.epa.gov/rcrainfoprod/rest/api/v1"
CHINA_HSCIQ_BASE_URL = "http://www.hsbianma.com/api"  # Example - actual API may vary

# Cache settings
CACHE_TTL_HOURS = 24  # Cache API responses for 24 hours

class EPARCRAInfoClient:
    """
    Client for EPA RCRAInfo API.
    Provides access to handler information, facility data, and waste codes.
    
    Note: Requires API key from EPA. Register at https://rcrainfo.epa.gov/
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize EPA RCRAInfo client.
        
        Args:
            api_key: EPA RCRAInfo API key (defaults to environment variable)
        """
        self.api_key = api_key or os.environ.get('EPA_RCRAINFO_API_KEY')
        self.base_url = EPA_RCRAINFO_BASE_URL
        self.session = requests.Session()
        if self.api_key:
            self.session.headers.update({
                'Authorization': f'Bearer {self.api_key}',
                'Accept': 'application/json'
            })
    
    @lru_cache(maxsize=100)
    def get_handler_info(self, handler_id: str) -> Dict[str, Any]:
        """
        Get information about a hazardous waste handler (generator, TSDF).
        
        Args:
            handler_id: EPA ID number (e.g., 'CAD000000000')
        
        Returns:
            Handler information including permits, waste codes, contact info
        """
        if not self.api_key:
            return {
                "error": "EPA_RCRAINFO_API_KEY not configured",
                "handler_id": handler_id,
                "note": "Set environment variable EPA_RCRAINFO_API_KEY to enable"
            }
        
        try:
            url = f"{self.base_url}/emanifest/handler/{handler_id}"
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {
                "error": str(e),
                "handler_id": handler_id,
                "available": False
            }
    
    @lru_cache(maxsize=50)
    def search_handlers_by_state(self, state_code: str, handler_type: str = "Tsdf") -> Dict[str, Any]:
        """
        Search for hazardous waste handlers in a specific state.
        
        Args:
            state_code: Two-letter state code (e.g., 'CA', 'TX')
            handler_type: Type of handler ('Generator', 'Tsdf', 'Transporter')
        
        Returns:
            List of handlers matching criteria
        """
        if not self.api_key:
            return {
                "error": "EPA_RCRAINFO_API_KEY not configured",
                "note": "Set environment variable EPA_RCRAINFO_API_KEY to enable"
            }
        
        try:
            url = f"{self.base_url}/emanifest/lookup/handler"
            params = {
                'stateCode': state_code,
                'type': handler_type
            }
            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {
                "error": str(e),
                "state": state_code,
                "available": False
            }
    
    @lru_cache(maxsize=20)
    def get_waste_code_info(self, waste_code: str) -> Dict[str, Any]:
        """
        Get information about a specific hazardous waste code.
        
        Args:
            waste_code: EPA hazardous waste code (e.g., 'D001', 'F005')
        
        Returns:
            Description and regulatory information for waste code
        """
        # Common waste codes for batteries (static data since these rarely change)
        waste_codes = {
            "D001": {
                "code": "D001",
                "description": "Ignitable waste",
                "characteristic": "Ignitability",
                "flash_point": "< 140°F (60°C)",
                "applies_to": "Lithium batteries with flammable electrolytes"
            },
            "D003": {
                "code": "D003",
                "description": "Reactive waste",
                "characteristic": "Reactivity",
                "hazards": ["Violent reaction with water", "Generates toxic gases", "Capable of detonation"],
                "applies_to": "Lithium batteries (thermal runaway risk)"
            },
            "D008": {
                "code": "D008",
                "description": "Lead",
                "characteristic": "Toxicity",
                "tclp_limit": "5.0 mg/L",
                "applies_to": "Lead-acid batteries"
            }
        }
        
        return waste_codes.get(waste_code, {
            "code": waste_code,
            "description": "Contact EPA for details",
            "available": False
        })


class ChinaHSCIQClient:
    """
    Client for China Harmonized System Commodity Inquiry.
    Provides HS code information and import requirements.
    
    Note: This is a placeholder. Actual API details may vary.
    """
    
    def __init__(self, api_id: Optional[str] = None):
        """
        Initialize China HSCIQ client.
        
        Args:
            api_id: API ID for HSCIQ system
        """
        self.api_id = api_id or os.environ.get('CHINA_HSCIQ_API_ID')
        self.base_url = CHINA_HSCIQ_BASE_URL
    
    @lru_cache(maxsize=50)
    def get_hs_requirements(self, hs_code: str) -> Dict[str, Any]:
        """
        Get import requirements for HS code.
        
        Args:
            hs_code: Harmonized System code (e.g., '3824999996' for black mass)
        
        Returns:
            Import requirements, restrictions, and documentation needed
        """
        # Static data for battery-related HS codes
        hs_codes = {
            "3824999996": {
                "hs_code": "3824999996",
                "description": "Black mass (battery recycling intermediate)",
                "classification": "Non-waste product per GB/T 45203-2024",
                "import_license": "Required",
                "inspection": "Entry-exit inspection required",
                "vat_rate": "13%",
                "required_docs": [
                    "Commercial invoice",
                    "Packing list",
                    "Bill of lading",
                    "Quality certificate",
                    "Non-hazardous certification",
                    "Country of origin certificate"
                ]
            },
            "8548100090": {
                "hs_code": "8548100090",
                "description": "Waste batteries",
                "classification": "Restricted import",
                "import_license": "Required from MEE",
                "basel_pic": "Required",
                "notes": "Subject to strict environmental controls"
            }
        }
        
        return hs_codes.get(hs_code, {
            "hs_code": hs_code,
            "description": "HS code not in database",
            "note": "Consult Chinese customs for details",
            "available": False
        })


class FreightRateAPI:
    """
    Interface for freight rate APIs (Freightos, Xeneta, etc.).
    Currently uses static benchmark rates from logistics_data.py.
    """
    
    def __init__(self):
        """Initialize freight rate API client."""
        # Import here to avoid circular dependency
        from logistics_data import TRANSPORT_RATES
        self.rates = TRANSPORT_RATES
    
    def get_ocean_rate(self, origin: str, destination: str, weight_mt: float) -> Dict[str, Any]:
        """
        Get ocean freight rate estimate.
        
        Args:
            origin: Origin country/port
            destination: Destination country/port
            weight_mt: Weight in metric tons
        
        Returns:
            Rate estimate with breakdown
        """
        ocean_rates = self.rates.get("ocean", {})
        base_rate = ocean_rates.get("base_rate_usd_per_mt", 85)
        hazmat_mult = ocean_rates.get("hazmat_multiplier", 1.8)
        
        # Check for specific route rates
        route_key = f"{origin}->{ destination}"
        route_rates = ocean_rates.get("routes", {})
        if route_key in route_rates:
            base_rate = route_rates[route_key].get("rate", base_rate)
            transit_days = route_rates[route_key].get("days", 14)
        else:
            transit_days = ocean_rates.get("typical_transit_days", 14)
        
        base_cost = base_rate * weight_mt
        hazmat_cost = base_cost * (hazmat_mult - 1)
        total_cost = base_cost * hazmat_mult
        
        return {
            "mode": "ocean",
            "base_rate_per_mt": base_rate,
            "weight_mt": weight_mt,
            "base_cost": round(base_cost, 2),
            "hazmat_surcharge": round(hazmat_cost, 2),
            "total_cost": round(total_cost, 2),
            "estimated_transit_days": transit_days,
            "currency": "USD",
            "note": "Benchmark rate - actual rates vary by carrier, season, volume"
        }
    
    def get_air_rate(self, origin: str, destination: str, weight_mt: float) -> Dict[str, Any]:
        """
        Get air freight rate estimate.
        
        Args:
            origin: Origin airport/country
            destination: Destination airport/country
            weight_mt: Weight in metric tons
        
        Returns:
            Rate estimate with breakdown
        """
        air_rates = self.rates.get("air", {})
        base_rate = air_rates.get("base_rate_usd_per_mt", 4500)
        hazmat_mult = air_rates.get("hazmat_multiplier", 2.2)
        
        base_cost = base_rate * weight_mt
        hazmat_cost = base_cost * (hazmat_mult - 1)
        total_cost = base_cost * hazmat_mult
        
        return {
            "mode": "air",
            "base_rate_per_mt": base_rate,
            "weight_mt": weight_mt,
            "base_cost": round(base_cost, 2),
            "hazmat_surcharge": round(hazmat_cost, 2),
            "total_cost": round(total_cost, 2),
            "estimated_transit_days": 2,
            "currency": "USD",
            "warning": "DDR (Damaged/Defective/Recalled) batteries PROHIBITED by air",
            "note": "Benchmark rate - actual rates vary significantly"
        }
    
    def get_truck_rate(self, distance_miles: float, weight_mt: float) -> Dict[str, Any]:
        """
        Get truck freight rate estimate.
        
        Args:
            distance_miles: Distance in miles
            weight_mt: Weight in metric tons
        
        Returns:
            Rate estimate with breakdown
        """
        truck_rates = self.rates.get("truck", {})
        base_rate_per_mile = truck_rates.get("base_rate_usd_per_mile", 3.50)
        hazmat_mult = truck_rates.get("hazmat_multiplier", 1.5)
        
        base_cost = base_rate_per_mile * distance_miles
        hazmat_cost = base_cost * (hazmat_mult - 1)
        total_cost = base_cost * hazmat_mult
        
        # Estimate transit time (assuming 500 miles/day average)
        transit_days = max(1, int(distance_miles / 500))
        
        return {
            "mode": "truck",
            "base_rate_per_mile": base_rate_per_mile,
            "distance_miles": distance_miles,
            "weight_mt": weight_mt,
            "base_cost": round(base_cost, 2),
            "hazmat_surcharge": round(hazmat_cost, 2),
            "total_cost": round(total_cost, 2),
            "estimated_transit_days": transit_days,
            "currency": "USD",
            "note": "Benchmark rate - actual rates vary by carrier, route, season"
        }


# Singleton instances for easy access
epa_client = EPARCRAInfoClient()
china_client = ChinaHSCIQClient()
freight_api = FreightRateAPI()


def get_epa_handler(handler_id: str) -> Dict[str, Any]:
    """Convenience function to get EPA handler info."""
    return epa_client.get_handler_info(handler_id)


def get_china_hs_info(hs_code: str = "3824999996") -> Dict[str, Any]:
    """Convenience function to get China HS code info for black mass."""
    return china_client.get_hs_requirements(hs_code)


def get_freight_estimate(
    mode: str,
    origin: str,
    destination: str,
    weight_mt: float,
    distance_miles: Optional[float] = None
) -> Dict[str, Any]:
    """
    Get freight cost estimate.
    
    Args:
        mode: 'ocean', 'air', or 'truck'
        origin: Origin location
        destination: Destination location
        weight_mt: Weight in metric tons
        distance_miles: Distance in miles (required for truck)
    
    Returns:
        Cost estimate with breakdown
    """
    if mode == "ocean":
        return freight_api.get_ocean_rate(origin, destination, weight_mt)
    elif mode == "air":
        return freight_api.get_air_rate(origin, destination, weight_mt)
    elif mode == "truck":
        if distance_miles is None:
            return {"error": "distance_miles required for truck transport"}
        return freight_api.get_truck_rate(distance_miles, weight_mt)
    else:
        return {"error": f"Unknown transport mode: {mode}"}


# Cache management
def clear_api_cache():
    """Clear all cached API responses."""
    epa_client.get_handler_info.cache_clear()
    epa_client.search_handlers_by_state.cache_clear()
    epa_client.get_waste_code_info.cache_clear()
    china_client.get_hs_requirements.cache_clear()


def get_cache_info() -> Dict[str, Any]:
    """Get information about API cache status."""
    return {
        "epa_handler_cache": epa_client.get_handler_info.cache_info()._asdict(),
        "epa_search_cache": epa_client.search_handlers_by_state.cache_info()._asdict(),
        "china_hs_cache": china_client.get_hs_requirements.cache_info()._asdict(),
        "note": "LRU cache - automatically expires least recently used entries"
    }
