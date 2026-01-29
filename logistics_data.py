"""
Logistics and regulatory data for battery waste transportation.
Loads static data from regulatory_db.json and provides structured access.
"""

import json
import os
from typing import Dict, List, Any

# Load regulatory database
_DB_PATH = os.path.join(os.path.dirname(__file__), 'data', 'regulatory_db.json')

def load_regulatory_db() -> Dict[str, Any]:
    """Load the regulatory database from JSON file."""
    with open(_DB_PATH, 'r') as f:
        return json.load(f)

# Load database at module import
_REGULATORY_DB = load_regulatory_db()

# Export key data structures for easy access
WASTE_REGULATIONS = {
    "US": {
        "framework": "RCRA (Resource Conservation and Recovery Act)",
        "competent_authority": "EPA",
        "classification": {
            "lithium_batteries": "Hazardous Waste (D001 Ignitable, D003 Reactive)",
            "black_mass": "Hazardous Waste (if exhibits characteristics)",
            "universal_waste": "40 CFR Part 273 eligible"
        },
        "export_requirements": {
            "notification_system": "WIETS",
            "advance_notice": "60 days",
            "aoc_required": True,
            "aes_filing": True,
            "annual_report_due": "March 1"
        },
        "key_regulations": [
            "40 CFR Part 262 Subpart H (Export)",
            "40 CFR Part 273 (Universal Waste)",
            "40 CFR Part 261 (Hazardous Waste ID)"
        ],
        "links": {
            "epa_faqs": "https://www.epa.gov/hw/lithium-ion-battery-recycling-frequently-asked-questions",
            "wiets": "https://rcrapublic.epa.gov/",
            "export_regs": "https://www.ecfr.gov/current/title-40/part-262/subpart-H"
        }
    },
    "Canada": {
        "framework": "CEPA (Canadian Environmental Protection Act, 1999)",
        "regulation": "SOR/2021-25",
        "competent_authority": "ECCC (Environment and Climate Change Canada)",
        "classification": {
            "hazardous_waste": "Subject to cross-border movement controls",
            "permit_required": "Export, import, transit"
        },
        "export_requirements": {
            "notification_system": "CNMTS",
            "permit_required": True,
            "contract_required": True,
            "liability_insurance": True,
            "record_retention": "5 years"
        },
        "links": {
            "regulations": "https://laws.justice.gc.ca/eng/regulations/SOR-2021-25/",
            "cnmts": "https://ec.ss.ec.gc.ca/"
        }
    },
    "EU": {
        "framework": "EU Battery Regulation 2023/1542",
        "effective_date": "2023-08-17",
        "waste_list_amendment": "EU Commission Decision 2025/934",
        "classification": {
            "black_mass": "Hazardous waste (effective Nov 9, 2026)",
            "waste_code": "191402*",
            "waste_batteries": "Subject to EU Waste Shipment Regulation"
        },
        "export_restrictions": {
            "non_oecd_prohibited": True,
            "effective_date": "2026-11-09",
            "applies_to": ["Waste batteries", "Black mass (waste code 191402*)"]
        },
        "sustainability_requirements": [
            "Carbon footprint declaration",
            "Recycled content minimums",
            "Supply chain due diligence",
            "Battery passport (by 2027)"
        ],
        "links": {
            "regulation": "https://eur-lex.europa.eu/eli/reg/2023/1542/oj"
        }
    },
    "China": {
        "framework": "GACC (General Administration of Customs)",
        "standard": "GB/T 45203-2024",
        "classification": {
            "black_mass": "Non-waste product (industrial intermediate)",
            "hs_code": "3824999996",
            "waste_batteries": "Import restricted, Basel PIC required"
        },
        "import_requirements": {
            "import_license": True,
            "quality_certificate": True,
            "inspection": "Entry-exit inspection and quarantine",
            "facility_approval": "MEE approval required"
        }
    },
    "Basel_Convention": {
        "description": "Multilateral treaty controlling transboundary movements",
        "pic_required": True,
        "key_annexes": {
            "Annex VIII A1170": "Waste batteries with hazardous constituents",
            "Annex IX B1090": "Non-hazardous batteries (limited applicability)"
        },
        "technical_guidelines": "Under development (expected COP-18, 2027)"
    }
}

ROUTE_FEASIBILITY = {
    "US->Canada": {
        "status": "allowed",
        "requirements": ["ECCC permit", "EPA AOC", "RCRA manifest", "DOT packaging"],
        "processing_time_days": "60-90",
        "notes": "Well-established cross-border protocols"
    },
    "Canada->US": {
        "status": "allowed",
        "requirements": ["EPA AOC", "RCRA manifest", "ECCC movement document"],
        "processing_time_days": "60-90",
        "notes": "Common route for recycling services"
    },
    "US->EU": {
        "status": "allowed",
        "requirements": ["EPA AOC", "Basel notification", "EU waste shipment consent"],
        "processing_time_days": "90-120",
        "notes": "Multiple EU competent authorities involved"
    },
    "US->China": {
        "status": "restricted",
        "requirements": ["EPA AOC", "Basel PIC", "China import license", "MEE approval if waste"],
        "processing_time_days": "120-180",
        "notes": "Black mass as product (GB/T 45203) easier than waste classification"
    },
    "Canada->China": {
        "status": "restricted",
        "requirements": ["ECCC permit", "Basel PIC", "China import license"],
        "processing_time_days": "120-180",
        "notes": "Long lead times for approvals"
    },
    "EU->Non-OECD": {
        "status": "allowed_until_nov_2026",
        "status_after": "blocked",
        "reason": "EU Commission Decision 2025/934 classifies black mass as hazardous waste (191402*), prohibiting export to non-OECD per Basel Convention",
        "effective_date": "2026-11-09",
        "current_note": "Currently allowed but restriction takes effect November 9, 2026",
        "applies_to": ["Waste batteries", "Black mass (waste code 191402*)"],
        "legal_basis": "Commission Delegated Decision (EU) 2025/934",
        "notes": "Export to OECD countries will remain allowed after Nov 9, 2026"
    },
    "EU->China": {
        "status": "allowed_until_nov_2026",
        "status_after": "blocked",
        "reason": "EU Commission Decision 2025/934 classifies black mass as hazardous waste, prohibiting export to non-OECD countries including China",
        "effective_date": "2026-11-09",
        "requirements": ["EU waste shipment consent", "Basel PIC", "China import license", "MEE approval"],
        "processing_time_days": "120-180",
        "current_note": "Currently allowed but export of hazardous battery waste to China will be prohibited from November 9, 2026",
        "notes": "China is non-OECD. After Nov 2026, only non-hazardous battery materials can be exported to China."
    },
    "Germany->China": {
        "status": "allowed_until_nov_2026",
        "status_after": "blocked",
        "reason": "EU Commission Decision 2025/934 - same as EU->China",
        "effective_date": "2026-11-09",
        "requirements": ["German Federal Environment Agency approval", "Basel PIC", "China import license"],
        "processing_time_days": "120-180",
        "notes": "Will be prohibited from November 9, 2026 per EU Commission Decision 2025/934"
    },
    "France->China": {
        "status": "allowed_until_nov_2026",
        "status_after": "blocked",
        "reason": "EU Commission Decision 2025/934 - same as EU->China",
        "effective_date": "2026-11-09",
        "requirements": ["French Ministry approval", "Basel PIC", "China import license"],
        "processing_time_days": "120-180",
        "notes": "Will be prohibited from November 9, 2026 per EU Commission Decision 2025/934"
    },
    "US->Mexico": {
        "status": "allowed",
        "requirements": ["EPA AOC", "Mexico SEMARNAT approval", "Basel notification"],
        "processing_time_days": "60-90",
        "notes": "NAFTA/USMCA simplifies some procedures"
    },
    "US->South Korea": {
        "status": "allowed",
        "requirements": ["EPA AOC", "Basel PIC", "Korea MOE approval"],
        "processing_time_days": "90-120",
        "notes": "Strong e-waste recycling infrastructure"
    }
}

# Transport rates based on Freightos Baltic Index
TRANSPORT_RATES = {
    "ocean": {
        "base_rate_usd_per_mt": 85,
        "hazmat_multiplier": 1.8,
        "typical_transit_days": 14,
        "routes": {
            "US->China": {"rate": 95, "days": 14},
            "US->EU": {"rate": 75, "days": 10},
            "Canada->Asia": {"rate": 90, "days": 16}
        }
    },
    "air": {
        "base_rate_usd_per_mt": 4500,
        "hazmat_multiplier": 2.2,
        "typical_transit_days": 2,
        "notes": "DDR (Damaged/Defective/Recalled) batteries prohibited"
    },
    "truck": {
        "base_rate_usd_per_mile": 3.50,
        "hazmat_multiplier": 1.5,
        "typical_distances": {
            "US-Canada border": 500,
            "Cross-country US": 2500,
            "Cross-country Canada": 3000
        }
    }
}

PERMIT_REQUIREMENTS = {
    "US_export": [
        {
            "name": "EPA Acknowledgment of Consent (AOC)",
            "agency": "EPA",
            "required": True,
            "processing_time": "30-90 days",
            "validity": "Up to 1 year (3 years for OECD pre-consented)",
            "application_system": "WIETS",
            "url": "https://rcrapublic.epa.gov/"
        },
        {
            "name": "AES Filing",
            "agency": "Census Bureau",
            "required": True,
            "processing_time": "Immediate",
            "description": "Automated Export System filing",
            "url": "https://www.census.gov/foreign-trade/aes/"
        },
        {
            "name": "EPA Form 8700-22 (Hazardous Waste Manifest)",
            "required": True,
            "submission_deadline": "Within 30 days to e-Manifest",
            "url": "https://www.epa.gov/hwgenerators/uniform-hazardous-waste-manifest"
        }
    ],
    "Canada_export": [
        {
            "name": "ECCC Export Permit",
            "agency": "Environment and Climate Change Canada",
            "required": True,
            "processing_time": "Varies by destination",
            "application_system": "CNMTS",
            "url": "https://ec.ss.ec.gc.ca/"
        },
        {
            "name": "Liability Insurance",
            "required": True,
            "regulation": "Division 7 of SOR/2021-25",
            "purpose": "Cover accidents or incidents during transport"
        }
    ],
    "China_import": [
        {
            "name": "Import License",
            "agency": "Ministry of Commerce (MOFCOM)",
            "required": True,
            "processing_time": "30-60 days"
        },
        {
            "name": "MEE Approval",
            "agency": "Ministry of Ecology and Environment",
            "required": "If classified as waste",
            "processing_time": "60-90 days",
            "notes": "Not required if black mass classified as product per GB/T 45203"
        }
    ],
    "EU_import": [
        {
            "name": "Waste Shipment Notification",
            "agency": "Competent authority of destination country",
            "required": True,
            "processing_time": "30 days",
            "regulation": "EU Waste Shipment Regulation"
        }
    ]
}

PACKAGING_REQUIREMENTS = {
    "lithium_batteries": {
        "un_classification": {
            "un_number": "UN3480 (lithium metal) / UN3481 (contained in equipment)",
            "class": "Class 9 Dangerous Goods",
            "packing_group": "II"
        },
        "regulations": [
            "49 CFR 173.185 (US DOT)",
            "IATA DGR Section 4.11 (Air transport)"
        ],
        "requirements": [
            "Inner packaging prevents short circuits",
            "Outer packaging provides cushioning",
            "Terminals isolated (tape, plastic caps, bags)",
            "Package marked with UN number",
            "Lithium battery handling label",
            "State of charge documentation"
        ]
    },
    "ddr_batteries": {
        "description": "Damaged, Defective, or Recalled batteries",
        "regulation": "49 CFR 173.185(f)",
        "restrictions": {
            "air_transport": "Prohibited",
            "ground_transport": "Allowed with special packaging"
        },
        "special_requirements": [
            "Individual non-conductive inner packaging",
            "Additional cushioning required",
            "Warning labels for damaged/defective status",
            "Separate storage from non-DDR batteries"
        ]
    },
    "black_mass": {
        "classification": "Hazardous material (reactive battery residues)",
        "packaging": [
            "UN-approved drums or IBCs",
            "Sealed to prevent moisture ingress",
            "Proper hazardous waste labeling",
            "SDS (Safety Data Sheet) must accompany"
        ]
    }
}

# Material classifications for transport
MATERIAL_CLASSIFICATIONS = {
    "whole_batteries": {
        "description": "Complete lithium-ion battery cells or modules",
        "hazard_class": "Class 9 Dangerous Goods",
        "typical_waste_codes": ["D001", "D003"],
        "universal_waste_eligible": True,
        "basel_annex": "Annex VIII A1170"
    },
    "black_mass": {
        "description": "Shredded battery material (cathode + anode)",
        "hazard_class": "Hazardous waste (if exhibits characteristics)",
        "typical_waste_codes": ["D001", "D003"],
        "universal_waste_eligible": False,
        "basel_annex": "Annex VIII A1170 or product (China GB/T 45203)",
        "notes": "Requires RCRA Part B permit for storage before recycling"
    },
    "processed_metals": {
        "description": "Recovered battery-grade metals (Li, Co, Ni compounds)",
        "hazard_class": "Generally non-hazardous (case-by-case)",
        "basel_annex": "Annex IX B1010 (if non-hazardous)",
        "notes": "May qualify for less restrictive trade if sufficiently processed"
    }
}

# Countries and their regulatory frameworks
COUNTRIES = {
    "US": {
        "name": "United States",
        "competent_authority": "EPA",
        "oecd_member": True,
        "basel_party": True,
        "system": "WIETS"
    },
    "Canada": {
        "name": "Canada",
        "competent_authority": "ECCC",
        "oecd_member": True,
        "basel_party": True,
        "system": "CNMTS"
    },
    "China": {
        "name": "People's Republic of China",
        "competent_authority": "MEE",
        "oecd_member": False,
        "basel_party": True,
        "special_notes": "Black mass can be product (GB/T 45203) or waste"
    },
    "EU": {
        "name": "European Union",
        "competent_authority": "Varies by member state",
        "oecd_member": True,
        "basel_party": True,
        "special_restrictions": "No hazardous battery waste export to non-OECD (from Sept 2026)"
    },
    "Mexico": {
        "name": "Mexico",
        "competent_authority": "SEMARNAT",
        "oecd_member": True,
        "basel_party": True
    },
    "South Korea": {
        "name": "South Korea",
        "competent_authority": "MOE",
        "oecd_member": True,
        "basel_party": True
    }
}

def get_route_key(origin: str, destination: str) -> str:
    """Generate route key from origin and destination."""
    return f"{origin}->{destination}"

def get_route_status(origin: str, destination: str) -> Dict[str, Any]:
    """Get feasibility status for a specific route."""
    route_key = get_route_key(origin, destination)
    return ROUTE_FEASIBILITY.get(route_key, {
        "status": "unknown",
        "notes": "Route not in database. Consult regulatory authorities."
    })

def get_country_regulations(country: str) -> Dict[str, Any]:
    """Get regulatory framework for a specific country."""
    return WASTE_REGULATIONS.get(country, {})

def get_permit_requirements_for_route(origin: str, destination: str) -> List[Dict[str, Any]]:
    """Get all permits required for a specific route."""
    permits = []
    
    # Export permits from origin
    if origin == "US":
        permits.extend(PERMIT_REQUIREMENTS.get("US_export", []))
    elif origin == "Canada":
        permits.extend(PERMIT_REQUIREMENTS.get("Canada_export", []))
    
    # Import permits for destination
    if destination == "China":
        permits.extend(PERMIT_REQUIREMENTS.get("China_import", []))
    elif destination in ["EU", "Germany", "France", "Netherlands"]:
        permits.extend(PERMIT_REQUIREMENTS.get("EU_import", []))
    
    return permits

def calculate_transport_cost(
    mode: str,
    weight_mt: float,
    is_hazmat: bool = True,
    distance_miles: float = None
) -> dict:
    """
    Calculate realistic transport cost with container/vehicle sizing.
    
    Args:
        mode: 'ocean', 'air', or 'truck'
        weight_mt: Weight in metric tons
        is_hazmat: Whether material is hazardous
        distance_miles: Required for truck transport
    
    Returns:
        dict with cost and sizing information
    """
    import math
    
    weight_kg = weight_mt * 1000
    weight_lbs = weight_kg * 2.205
    
    if mode == "ocean":
        # Ocean freight charged per CONTAINER, not per kg
        # Hazmat limits: 20ft = 18,000 kg, 40ft = 24,000 kg
        
        if weight_kg <= 18000:
            # Fits in 20ft container
            container_type = "20ft Container (TEU)"
            container_capacity_kg = 18000 if is_hazmat else 21000
            num_containers = 1
            base_cost_per_container = 3000
            hazmat_surcharge_per_container = 1000 if is_hazmat else 0
        elif weight_kg <= 24000:
            # Needs 40ft container
            container_type = "40ft Container (FEU)"
            container_capacity_kg = 24000 if is_hazmat else 27000
            num_containers = 1
            base_cost_per_container = 4500
            hazmat_surcharge_per_container = 1500 if is_hazmat else 0
        else:
            # Multiple containers needed
            container_type = "20ft Containers (TEU)"
            container_capacity_kg = 18000 if is_hazmat else 21000
            num_containers = math.ceil(weight_kg / container_capacity_kg)
            base_cost_per_container = 3000
            hazmat_surcharge_per_container = 1000 if is_hazmat else 0
        
        total_cost = num_containers * (base_cost_per_container + hazmat_surcharge_per_container)
        utilization_pct = (weight_kg / (num_containers * container_capacity_kg)) * 100
        
        return {
            'cost': round(total_cost, 2),
            'vehicle_type': container_type,
            'num_vehicles': num_containers,
            'capacity_per_vehicle_kg': container_capacity_kg,
            'total_capacity_kg': num_containers * container_capacity_kg,
            'utilization_pct': round(utilization_pct, 1),
            'cost_per_kg': round(total_cost / weight_kg, 2),
            'base_cost': base_cost_per_container * num_containers,
            'hazmat_surcharge': hazmat_surcharge_per_container * num_containers,
            'note': f"Ocean freight charged per container. Your {weight_kg:,.0f} kg shipment requires {num_containers} × {container_type} (capacity: {container_capacity_kg:,} kg each)."
        }
    
    elif mode == "truck":
        if distance_miles is None:
            return {'cost': 0.0, 'error': 'Distance required for truck transport'}
        
        # Determine FTL vs LTL
        if weight_kg >= 4500:
            # Full Truckload (FTL) - charged per truck, not per kg
            if weight_kg <= 6000:
                vehicle_type = "26ft Box Truck"
                vehicle_capacity_kg = 6000
            elif weight_kg <= 18000:
                vehicle_type = "53ft Semi Trailer"
                vehicle_capacity_kg = 18000 if is_hazmat else 22000
            else:
                # Multiple trucks
                vehicle_type = "53ft Semi Trailers"
                vehicle_capacity_kg = 18000 if is_hazmat else 22000
            
            num_vehicles = math.ceil(weight_kg / vehicle_capacity_kg)
            rate_per_mile = 2.50  # FTL rate per mile per truck
            base_cost = distance_miles * rate_per_mile * num_vehicles
            hazmat_surcharge = 300 * num_vehicles if is_hazmat else 0
            total_cost = base_cost + hazmat_surcharge
            utilization_pct = (weight_kg / (num_vehicles * vehicle_capacity_kg)) * 100
            
            return {
                'cost': round(total_cost, 2),
                'vehicle_type': vehicle_type,
                'num_vehicles': num_vehicles,
                'capacity_per_vehicle_kg': vehicle_capacity_kg,
                'total_capacity_kg': num_vehicles * vehicle_capacity_kg,
                'utilization_pct': round(utilization_pct, 1),
                'cost_per_kg': round(total_cost / weight_kg, 2),
                'base_cost': round(base_cost, 2),
                'hazmat_surcharge': hazmat_surcharge,
                'note': f"Full Truckload: {num_vehicles} × {vehicle_type} (capacity: {vehicle_capacity_kg:,} kg each) for {distance_miles:,.0f} miles."
            }
        
        else:
            # Less Than Truckload (LTL) - charged by weight + freight class
            vehicle_type = "LTL (Partial Truck)"
            
            # LTL pricing by weight
            if is_hazmat:
                rate_per_lb = 0.90  # Hazmat LTL rate
            else:
                rate_per_lb = 0.40
            
            base_cost = weight_lbs * rate_per_lb
            
            # Distance-based multiplier for LTL
            if distance_miles < 500:
                distance_mult = 1.0
            elif distance_miles < 1000:
                distance_mult = 1.3
            else:
                distance_mult = 1.6
            
            base_cost *= distance_mult
            
            # Fuel surcharge (typically 25%)
            fuel_surcharge = base_cost * 0.25
            
            # Hazmat handling fee
            hazmat_fee = 150 if is_hazmat else 0
            
            # Minimum charge
            total_cost = max(base_cost + fuel_surcharge + hazmat_fee, 300)
            
            return {
                'cost': round(total_cost, 2),
                'vehicle_type': vehicle_type,
                'num_vehicles': 1,
                'capacity_per_vehicle_kg': None,  # Shared truck space
                'total_capacity_kg': None,
                'utilization_pct': None,
                'cost_per_kg': round(total_cost / weight_kg, 2),
                'base_cost': round(base_cost, 2),
                'fuel_surcharge': round(fuel_surcharge, 2),
                'hazmat_surcharge': hazmat_fee,
                'note': f"LTL freight: {weight_lbs:,.0f} lbs for {distance_miles:,.0f} miles. Consider FTL (4,500+ kg) for better rates."
            }
    
    elif mode == "air":
        # Air freight - charged by chargeable weight with minimums
        vehicle_type = "Air Cargo"
        
        # Hazmat air freight rates
        rate_per_kg = 12.00 if is_hazmat else 5.00
        
        # Base cost with minimum
        base_cost = max(weight_kg * rate_per_kg, 1000)
        
        # Handling surcharge for hazmat
        handling_surcharge = 500 if is_hazmat else 0
        
        total_cost = base_cost + handling_surcharge
        
        return {
            'cost': round(total_cost, 2),
            'vehicle_type': vehicle_type,
            'num_vehicles': 1,
            'capacity_per_vehicle_kg': None,
            'total_capacity_kg': None,
            'utilization_pct': None,
            'cost_per_kg': round(total_cost / weight_kg, 2),
            'base_cost': round(base_cost, 2),
            'hazmat_surcharge': handling_surcharge,
            'note': f"Air freight: {weight_kg:,.0f} kg @ ${rate_per_kg:.2f}/kg. Minimum charge: $1,000. DDR batteries prohibited."
        }
    
    return {'cost': 0.0, 'error': 'Invalid transport mode'}

def get_packaging_requirements(material_type: str, is_damaged: bool = False) -> Dict[str, Any]:
    """Get packaging requirements for material type."""
    if is_damaged:
        return PACKAGING_REQUIREMENTS.get("ddr_batteries", {})
    
    material_map = {
        "whole_batteries": "lithium_batteries",
        "black_mass": "black_mass",
        "processed": "black_mass"  # Use similar requirements
    }
    
    pkg_key = material_map.get(material_type, "lithium_batteries")
    return PACKAGING_REQUIREMENTS.get(pkg_key, {})

# Access to full database for advanced queries
def get_full_database() -> Dict[str, Any]:
    """Return the complete regulatory database."""
    return _REGULATORY_DB
