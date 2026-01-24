"""
Flask API for Battery Valuator
RESTful endpoints for Lovable frontend integration
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import backend
import logging

app = Flask(__name__)
CORS(app)  # Enable CORS for Lovable to call this API

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Transportation Advisory Data
# Route-based regulatory and documentation requirements
TRANSPORT_ADVISORIES = {
    # Canada to USA
    ("CA", "US"): {
        "route": "Canada → United States",
        "classification": {
            "status": "Regulated",
            "un_number": "UN3480 (Li-ion) or UN3090 (Li metal)",
            "hazard_class": "Class 9 - Miscellaneous Dangerous Goods",
            "notes": "Black mass may be classified as hazardous waste depending on contaminants"
        },
        "checklist": [
            {"item": "EPA Notification", "description": "Submit EPA Form 8700-22 for hazardous waste exports", "required": True},
            {"item": "RCRA Manifest", "description": "Complete hazardous waste manifest if applicable", "required": True},
            {"item": "Canadian Export Permit", "description": "ECCC export permit for hazardous recyclables", "required": True},
            {"item": "Customs Declaration", "description": "HS Code 8549.31 (waste batteries) or 2620.99 (black mass)", "required": True},
            {"item": "Carrier Certification", "description": "Ensure carrier has hazmat certification for Class 9", "required": True},
            {"item": "Emergency Response Info", "description": "Include 24-hour emergency contact and SDS", "required": True},
            {"item": "Insurance Certificate", "description": "Environmental liability coverage recommended", "required": False}
        ],
        "warnings": [
            "Some US states (e.g., California) have additional notification requirements",
            "Transit through certain ports may have restrictions on lithium materials",
            "Processing must occur at EPA-permitted facility"
        ],
        "cost_estimate": {
            "truck": "$150-400 per tonne",
            "rail": "$100-250 per tonne (bulk shipments)",
            "notes": "Costs vary by distance and hazmat surcharges"
        },
        "transit_time": "3-7 business days (truck)",
        "resources": [
            {"name": "EPA Hazardous Waste Exports", "url": "https://www.epa.gov/hwgenerators/hazardous-waste-export-requirements"},
            {"name": "ECCC Export/Import Permits", "url": "https://www.canada.ca/en/environment-climate-change/services/managing-reducing-waste/permit-hazardous-wastes-recyclables.html"}
        ]
    },
    # USA to Canada
    ("US", "CA"): {
        "route": "United States → Canada",
        "classification": {
            "status": "Regulated",
            "un_number": "UN3480 (Li-ion) or UN3090 (Li metal)",
            "hazard_class": "Class 9 - Miscellaneous Dangerous Goods",
            "notes": "TDG regulations apply upon entry to Canada"
        },
        "checklist": [
            {"item": "ECCC Import Notification", "description": "30-day advance notice required for hazardous recyclables", "required": True},
            {"item": "TDG Documentation", "description": "Transport of Dangerous Goods shipping document", "required": True},
            {"item": "EPA Export Notice", "description": "Notify EPA of hazardous waste export", "required": True},
            {"item": "Canadian Receiver Permit", "description": "Receiving facility must hold ECCC permit", "required": True},
            {"item": "Customs Declaration", "description": "CBSA requires accurate HS code classification", "required": True},
            {"item": "Emergency Response Plan", "description": "ERAP may be required for certain quantities", "required": False}
        ],
        "warnings": [
            "Canada requires receiving facility to be pre-authorized",
            "Provincial regulations may add requirements (e.g., Quebec, Ontario)",
            "Winter shipping may face delays at border crossings"
        ],
        "cost_estimate": {
            "truck": "$150-400 per tonne",
            "notes": "Brokerage fees typically $150-300 per shipment"
        },
        "transit_time": "3-7 business days (truck)",
        "resources": [
            {"name": "Transport Canada TDG", "url": "https://tc.canada.ca/en/dangerous-goods"},
            {"name": "ECCC Import Requirements", "url": "https://www.canada.ca/en/environment-climate-change/services/managing-reducing-waste/permit-hazardous-wastes-recyclables.html"}
        ]
    },
    # EU Internal
    ("EU", "EU"): {
        "route": "Within European Union",
        "classification": {
            "status": "Regulated",
            "un_number": "UN3480",
            "hazard_class": "Class 9",
            "notes": "Black mass classified as hazardous waste under EU regulations"
        },
        "checklist": [
            {"item": "ADR Compliance", "description": "European Agreement on Dangerous Goods by Road", "required": True},
            {"item": "Waste Shipment Notification", "description": "Regulation (EC) 1013/2006 - Annex VII or prior notification", "required": True},
            {"item": "Waste Codes", "description": "Use correct EWC/LoW codes (e.g., 16 06 06*)", "required": True},
            {"item": "Carrier Authorization", "description": "Carrier must be registered for hazardous waste transport", "required": True},
            {"item": "Consignee Authorization", "description": "Receiving facility must hold appropriate permits", "required": True},
            {"item": "Financial Guarantee", "description": "May be required for transboundary movements", "required": False}
        ],
        "warnings": [
            "Different member states may have varying interpretation of waste codes",
            "Some countries require translation of shipping documents",
            "COVID/Brexit may affect transit through non-EU territories"
        ],
        "cost_estimate": {
            "truck": "€100-300 per tonne",
            "notes": "Varies significantly by distance and country"
        },
        "transit_time": "2-5 business days",
        "resources": [
            {"name": "EU Waste Shipment Regulation", "url": "https://environment.ec.europa.eu/topics/waste-and-recycling/waste-shipments_en"}
        ]
    },
    # EU to Non-OECD - PROHIBITED
    ("EU", "NON_OECD"): {
        "route": "European Union → Non-OECD Countries",
        "classification": {
            "status": "PROHIBITED",
            "notes": "Export of hazardous waste to non-OECD countries is banned under EU regulations"
        },
        "checklist": [],
        "warnings": [
            "BLACK MASS EXPORT TO NON-OECD COUNTRIES IS PROHIBITED",
            "Battery waste and black mass are classified as hazardous waste under EU law",
            "The Basel Convention and EU Waste Shipment Regulation prohibit this export",
            "Violations can result in criminal penalties and significant fines",
            "This applies even if the destination country is willing to accept the material"
        ],
        "alternatives": [
            "Process material within the EU at authorized facilities",
            "Export to OECD countries (with proper notification procedures)",
            "Check if material can be reclassified as non-hazardous after processing"
        ],
        "resources": [
            {"name": "Basel Convention", "url": "http://www.basel.int/"},
            {"name": "EU Waste Shipment Regulation", "url": "https://environment.ec.europa.eu/topics/waste-and-recycling/waste-shipments_en"}
        ]
    },
    # EU to OECD (non-EU)
    ("EU", "OECD"): {
        "route": "European Union → OECD Countries (non-EU)",
        "classification": {
            "status": "Regulated - Prior Informed Consent",
            "notes": "Requires advance notification and consent from destination country"
        },
        "checklist": [
            {"item": "Prior Notification", "description": "Submit notification to competent authorities (origin, transit, destination)", "required": True},
            {"item": "Written Consent", "description": "Obtain written consent from all competent authorities", "required": True},
            {"item": "Financial Guarantee", "description": "Bond or insurance for shipment and disposal costs", "required": True},
            {"item": "Movement Document", "description": "Annex IB movement document must accompany shipment", "required": True},
            {"item": "Facility Permit", "description": "Destination facility must be authorized for this waste type", "required": True},
            {"item": "Recovery Contract", "description": "Written contract with recovery facility", "required": True}
        ],
        "warnings": [
            "Notification process can take 60-90 days",
            "Some OECD countries have additional restrictions on battery waste",
            "Consent is typically valid for 1 year and limited number of shipments"
        ],
        "cost_estimate": {
            "sea": "$200-600 per tonne",
            "air": "Not recommended for bulk - cost prohibitive",
            "notes": "Includes port fees, handling, and administrative costs"
        },
        "transit_time": "15-45 days (sea freight)",
        "resources": [
            {"name": "OECD Waste Trade", "url": "https://www.oecd.org/environment/waste/"}
        ]
    },
    # Asia to North America
    ("ASIA", "NA"): {
        "route": "Asia → North America",
        "classification": {
            "status": "Regulated",
            "un_number": "UN3480",
            "hazard_class": "Class 9 - IMDG Code applies for sea freight"
        },
        "checklist": [
            {"item": "IMDG Compliance", "description": "International Maritime Dangerous Goods Code requirements", "required": True},
            {"item": "Dangerous Goods Declaration", "description": "Shipper's declaration for dangerous goods", "required": True},
            {"item": "Container Certification", "description": "Proper packaging and container certification", "required": True},
            {"item": "State of Charge (SOC)", "description": "Batteries must be discharged below 30% for air/sea transport", "required": True},
            {"item": "Import Permits", "description": "US EPA / Canada ECCC import notifications if hazardous", "required": True},
            {"item": "Customs Pre-clearance", "description": "FDA and CBP may require additional documentation", "required": False}
        ],
        "warnings": [
            "Some shipping lines have restrictions on lithium battery materials",
            "State of charge requirements are critical - verify before shipping",
            "Port congestion can significantly delay shipments",
            "Consider insurance for cargo damage and environmental liability"
        ],
        "cost_estimate": {
            "sea": "$150-400 per tonne (FCL)",
            "air": "Not recommended - expensive and restricted",
            "notes": "Sea freight preferred for bulk; transit time 20-35 days"
        },
        "transit_time": "20-35 days (sea freight)",
        "resources": [
            {"name": "IMO IMDG Code", "url": "https://www.imo.org/en/OurWork/Safety/Pages/DangerousGoods-default.aspx"}
        ]
    },
    # USA Internal
    ("US", "US"): {
        "route": "Within United States",
        "classification": {
            "status": "Regulated",
            "un_number": "UN3480",
            "hazard_class": "Class 9 (DOT)",
            "notes": "RCRA regulations apply if material is hazardous waste"
        },
        "checklist": [
            {"item": "DOT Hazmat Training", "description": "Shipper and carrier must have hazmat training", "required": True},
            {"item": "Proper Shipping Name", "description": "Use correct DOT shipping name and UN number", "required": True},
            {"item": "Hazardous Waste Manifest", "description": "EPA Form 8700-22 if RCRA hazardous waste", "required": True},
            {"item": "EPA ID Numbers", "description": "Generator and receiver must have EPA ID numbers", "required": True},
            {"item": "State Notifications", "description": "Some states require advance notification", "required": False},
            {"item": "Placarding", "description": "Class 9 placards required for bulk shipments", "required": True}
        ],
        "warnings": [
            "California has strict additional requirements (DTSC)",
            "State-to-state shipments may trigger additional notifications",
            "LTL carriers may refuse lithium battery materials"
        ],
        "cost_estimate": {
            "truck": "$80-200 per tonne",
            "rail": "$50-150 per tonne (bulk only)",
            "notes": "Costs vary significantly by distance"
        },
        "transit_time": "2-7 business days",
        "resources": [
            {"name": "DOT Hazmat", "url": "https://www.phmsa.dot.gov/hazmat"},
            {"name": "EPA RCRA", "url": "https://www.epa.gov/rcra"}
        ]
    },
    # Canada Internal
    ("CA", "CA"): {
        "route": "Within Canada",
        "classification": {
            "status": "Regulated",
            "un_number": "UN3480",
            "hazard_class": "Class 9 (TDG)",
            "notes": "Transport of Dangerous Goods Act applies"
        },
        "checklist": [
            {"item": "TDG Training", "description": "All handlers must have TDG certification", "required": True},
            {"item": "Shipping Document", "description": "TDG-compliant shipping document required", "required": True},
            {"item": "Placards and Labels", "description": "Class 9 labels and placards as required", "required": True},
            {"item": "ERAP", "description": "Emergency Response Assistance Plan if above thresholds", "required": False},
            {"item": "Provincial Permits", "description": "Some provinces require additional permits for hazardous waste", "required": True}
        ],
        "warnings": [
            "Quebec has additional French labeling requirements",
            "Ontario requires generator registration for hazardous waste",
            "Inter-provincial movements may need tracking documentation"
        ],
        "cost_estimate": {
            "truck": "$100-300 per tonne",
            "notes": "Distances in Canada can be significant"
        },
        "transit_time": "2-10 business days",
        "resources": [
            {"name": "Transport Canada TDG", "url": "https://tc.canada.ca/en/dangerous-goods"}
        ]
    }
}

def get_transport_route_key(origin, destination):
    """
    Map country codes to transport advisory keys.
    Handles special cases like EU, OECD, and NON_OECD groupings.
    """
    # EU member states
    eu_countries = ['AT', 'BE', 'BG', 'HR', 'CY', 'CZ', 'DK', 'EE', 'FI', 'FR',
                    'DE', 'GR', 'HU', 'IE', 'IT', 'LV', 'LT', 'LU', 'MT', 'NL',
                    'PL', 'PT', 'RO', 'SK', 'SI', 'ES', 'SE']

    # OECD countries (non-EU)
    oecd_non_eu = ['US', 'CA', 'MX', 'JP', 'KR', 'AU', 'NZ', 'CH', 'NO', 'GB',
                   'IS', 'TR', 'CL', 'CO', 'CR', 'IL']

    # Asian export countries
    asia_countries = ['CN', 'KR', 'JP', 'TH', 'VN', 'ID', 'MY', 'PH', 'SG', 'TW', 'IN']

    # North America
    na_countries = ['US', 'CA', 'MX']

    origin = origin.upper()
    destination = destination.upper()

    # Same country
    if origin == destination:
        if origin in ['US', 'CA']:
            return (origin, origin)
        elif origin in eu_countries:
            return ('EU', 'EU')

    # EU internal
    if origin in eu_countries and destination in eu_countries:
        return ('EU', 'EU')

    # EU to non-OECD
    if origin in eu_countries and destination not in (eu_countries + oecd_non_eu):
        return ('EU', 'NON_OECD')

    # EU to OECD (non-EU)
    if origin in eu_countries and destination in oecd_non_eu:
        return ('EU', 'OECD')

    # Canada-US
    if origin == 'CA' and destination == 'US':
        return ('CA', 'US')
    if origin == 'US' and destination == 'CA':
        return ('US', 'CA')

    # Asia to North America
    if origin in asia_countries and destination in na_countries:
        return ('ASIA', 'NA')

    # Default: return the literal codes (may not have advisory)
    return (origin, destination)

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    import os
    import requests as req
    api_key = os.environ.get('METALS_DEV_API_KEY', '')
    api_key_set = bool(api_key)
    key_preview = f"{api_key[:4]}..." if len(api_key) > 4 else "not set"

    # Test Metals.Dev API
    metals_dev_status = "not tested"
    metals_dev_response = None
    if api_key:
        try:
            url = f"https://api.metals.dev/v1/latest?api_key={api_key}&currency=USD&unit=toz"
            r = req.get(url, timeout=10)
            data = r.json()
            metals_dev_response = data
            if data.get('status') == 'success':
                metals_dev_status = f"working - got {len(data.get('metals', {}))} metals"
            else:
                metals_dev_status = f"error: {data.get('error_message', r.status_code)}"
        except Exception as e:
            metals_dev_status = f"exception: {str(e)}"

    return jsonify({
        'status': 'healthy',
        'service': 'Battery Valuator API',
        'metals_dev_api_key_configured': api_key_set,
        'key_preview': key_preview,
        'metals_dev_api_status': metals_dev_status,
        'metals_dev_sample': metals_dev_response
    })

@app.route('/api/market-data', methods=['GET'])
def get_market_data():
    """
    Get current market data including metal prices and FX rates

    Query params:
        currency: USD, CAD, EUR, or CNY (default: USD)
    """
    try:
        currency = request.args.get('currency', 'USD')
        data = backend.get_market_data(currency)
        return jsonify({
            'success': True,
            'data': data
        })
    except Exception as e:
        logger.error(f"Market data fetch error: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/parse-coa', methods=['POST'])
def parse_coa():
    """
    Parse COA text to extract metal assays

    Request body:
        {
            "coa_text": "Ni: 20.5%\nCo: 6.2%\nLi: 2.5%..."
        }
    """
    try:
        data = request.get_json()
        coa_text = data.get('coa_text', '')

        if not coa_text:
            return jsonify({
                'success': False,
                'error': 'Missing coa_text parameter'
            }), 400

        assays = backend.parse_coa_text(coa_text)

        return jsonify({
            'success': True,
            'data': assays
        })
    except Exception as e:
        logger.error(f"COA parsing error: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/calculate', methods=['POST'])
def calculate_valuation():
    """
    Calculate battery material valuation

    Request body:
        {
            "currency": "USD",
            "gross_weight": 1000,
            "feed_type": "Black Mass (Processed)",
            "yield_pct": 1.0,
            "mech_recovery": 0.95,
            "hydromet_recovery": 0.95,
            "assays": {
                "Nickel": 0.205,
                "Cobalt": 0.062,
                "Lithium": 0.025,
                "Copper": 0.035,
                "Aluminum": 0.012,
                "Manganese": 0.048
            },
            "assay_basis": "Final Powder",
            "metal_prices": {
                "Ni": 16.5,
                "Co": 33.0,
                "Li": 13.5,
                "Cu": 9.2,
                "Al": 2.5,
                "Mn": 1.8
            },
            "payables": {
                "Ni": 0.80,
                "Co": 0.75,
                "Li": 0.30,
                "Cu": 0.80,
                "Al": 0.70,
                "Mn": 0.60
            },
            "shredding_cost_per_ton": 300,
            "elec_surcharge": 150,
            "has_electrolyte": false,
            "refining_opex_base": 1500,
            "ni_product": "Sulphates (Battery Salt)",
            "li_product": "Carbonate (LCE)"
        }
    """
    try:
        input_params = request.get_json()

        # Validate required parameters
        required_params = ['gross_weight', 'assays', 'metal_prices', 'payables']
        for param in required_params:
            if param not in input_params:
                return jsonify({
                    'success': False,
                    'error': f'Missing required parameter: {param}'
                }), 400

        # Calculate valuation
        results = backend.calculate_valuation(input_params)

        return jsonify({
            'success': True,
            'data': results
        })
    except Exception as e:
        logger.error(f"Calculation error: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/validate-assays', methods=['POST'])
def validate_assays():
    """
    Validate assay values against typical ranges

    Request body:
        {
            "bm_grades": {
                "Nickel": 20.5,
                "Cobalt": 6.2,
                "Lithium": 2.5,
                ...
            }
        }
    """
    try:
        data = request.get_json()
        bm_grades = data.get('bm_grades', {})

        warnings = []
        if bm_grades.get('Nickel', 0) > 60:
            warnings.append(f"Nickel grade ({bm_grades['Nickel']:.1f}%) exceeds typical black mass range (10-60%)")
        if bm_grades.get('Cobalt', 0) > 25:
            warnings.append(f"Cobalt grade ({bm_grades['Cobalt']:.1f}%) exceeds typical black mass range (3-25%)")
        if bm_grades.get('Lithium', 0) > 10:
            warnings.append(f"Lithium grade ({bm_grades['Lithium']:.1f}%) exceeds typical black mass range (1-10%)")

        total_grade = sum(bm_grades.values())
        if total_grade > 100:
            warnings.append(f"Total metal content ({total_grade:.1f}%) exceeds 100%")

        return jsonify({
            'success': True,
            'data': {
                'valid': len(warnings) == 0,
                'warnings': warnings
            }
        })
    except Exception as e:
        logger.error(f"Validation error: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/transport-advisory', methods=['POST'])
def get_transport_advisory():
    """
    Get transportation advisory for a specific route.

    Request body:
        {
            "origin_country": "CA",
            "destination_country": "US",
            "material_type": "black_mass"  // optional, defaults to black_mass
        }

    Returns regulatory classification, documentation checklist,
    warnings, cost estimates, and resource links.
    """
    try:
        data = request.get_json()
        origin = data.get('origin_country', '').upper()
        destination = data.get('destination_country', '').upper()
        material_type = data.get('material_type', 'black_mass')

        if not origin or not destination:
            return jsonify({
                'success': False,
                'error': 'Missing origin_country or destination_country'
            }), 400

        # Get the route key
        route_key = get_transport_route_key(origin, destination)

        # Look up advisory
        advisory = TRANSPORT_ADVISORIES.get(route_key)

        if advisory:
            return jsonify({
                'success': True,
                'data': {
                    'origin': origin,
                    'destination': destination,
                    'route_key': f"{route_key[0]} → {route_key[1]}",
                    'advisory': advisory
                }
            })
        else:
            # No specific advisory - return general guidance
            return jsonify({
                'success': True,
                'data': {
                    'origin': origin,
                    'destination': destination,
                    'route_key': f"{origin} → {destination}",
                    'advisory': {
                        'route': f"{origin} → {destination}",
                        'classification': {
                            'status': 'Unknown',
                            'notes': 'No specific advisory available for this route. General dangerous goods regulations apply.'
                        },
                        'checklist': [
                            {"item": "Dangerous Goods Classification", "description": "Verify UN number and proper shipping name", "required": True},
                            {"item": "Local Regulations", "description": "Check origin and destination country regulations", "required": True},
                            {"item": "Carrier Requirements", "description": "Confirm carrier can handle hazardous materials", "required": True}
                        ],
                        'warnings': [
                            "This route does not have specific guidance in our database",
                            "Consult with a freight forwarder or customs broker for detailed requirements",
                            "Battery materials are generally regulated as dangerous goods internationally"
                        ],
                        'resources': [
                            {"name": "UN Dangerous Goods", "url": "https://unece.org/transport/dangerous-goods"}
                        ]
                    }
                }
            })

    except Exception as e:
        logger.error(f"Transport advisory error: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/transport-routes', methods=['GET'])
def list_transport_routes():
    """
    List all available transport advisory routes.
    """
    routes = []
    for key, advisory in TRANSPORT_ADVISORIES.items():
        routes.append({
            'origin': key[0],
            'destination': key[1],
            'route': advisory.get('route', f"{key[0]} → {key[1]}"),
            'status': advisory.get('classification', {}).get('status', 'Unknown')
        })

    return jsonify({
        'success': True,
        'data': routes
    })


@app.route('/api/chemistries', methods=['GET'])
def list_chemistries():
    """
    List supported battery chemistries.
    """
    return jsonify({
        'success': True,
        'data': backend.CHEMISTRIES
    })


@app.route('/api/detect-chemistry', methods=['POST'])
def detect_chemistry():
    """
    Auto-detect battery chemistry from assay profile.

    Request body:
        {
            "assays": {
                "Nickel": 0.205,
                "Cobalt": 0.062,
                "Lithium": 0.025,
                "Iron": 0.0,
                ...
            }
        }
    """
    try:
        data = request.get_json()
        assays = data.get('assays', {})

        if not assays:
            return jsonify({
                'success': False,
                'error': 'Missing assays parameter'
            }), 400

        chemistry = backend.detect_chemistry(assays)
        chemistry_info = backend.CHEMISTRIES.get(chemistry, {})

        return jsonify({
            'success': True,
            'data': {
                'chemistry': chemistry,
                'name': chemistry_info.get('name', 'Unknown'),
                'primary_metals': chemistry_info.get('primary_metals', []),
                'typical_grades': chemistry_info.get('typical_grades', {})
            }
        })

    except Exception as e:
        logger.error(f"Chemistry detection error: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/value-view', methods=['POST'])
def get_value_view():
    """
    Simple Value View for OEMs - shows what their scrap is worth.

    Hides all processing costs, OPEX, and margins.
    Shows only recoverable value and composition.

    Request body:
        {
            "currency": "USD",
            "weight_kg": 1000,
            "assays": {
                "Nickel": 0.205,
                "Cobalt": 0.062,
                "Lithium": 0.025,
                ...
            }
        }

    Returns simplified valuation showing:
    - Material composition
    - Chemistry type (auto-detected)
    - Estimated recoverable value by metal
    - Total estimated value
    """
    try:
        data = request.get_json()

        currency = data.get('currency', 'USD')
        weight_kg = data.get('weight_kg', 0)
        assays = data.get('assays', {})

        if not weight_kg or weight_kg <= 0:
            return jsonify({
                'success': False,
                'error': 'Missing or invalid weight_kg parameter'
            }), 400

        if not assays:
            return jsonify({
                'success': False,
                'error': 'Missing assays parameter'
            }), 400

        # Ensure Iron and Phosphorus exist
        if 'Iron' not in assays:
            assays['Iron'] = 0.0
        if 'Phosphorus' not in assays:
            assays['Phosphorus'] = 0.0

        # Auto-detect chemistry
        chemistry = backend.detect_chemistry(assays)
        chemistry_info = backend.CHEMISTRIES.get(chemistry, {})

        # Get current market prices
        market_data = backend.get_market_data(currency)

        # Define typical recovery rates and payable percentages (industry standard)
        # These represent what a recycler typically pays for contained metal
        recovery_rates = {
            'Nickel': 0.95,
            'Cobalt': 0.95,
            'Lithium': 0.85,
            'Copper': 0.95,
            'Aluminum': 0.90,
            'Manganese': 0.85,
            'Iron': 0.85,
            'Phosphorus': 0.0  # Not recovered separately
        }

        # Typical payable percentages (what recyclers pay for metal content)
        payable_pct = {
            'Nickel': 0.80,
            'Cobalt': 0.75,
            'Lithium': 0.30,
            'Copper': 0.80,
            'Aluminum': 0.70,
            'Manganese': 0.60,
            'Iron': 0.0,  # Typically not paid for
            'Phosphorus': 0.0
        }

        # Metal to price key mapping
        metal_to_price = {
            'Nickel': 'Ni',
            'Cobalt': 'Co',
            'Lithium': 'Li',
            'Copper': 'Cu',
            'Aluminum': 'Al',
            'Manganese': 'Mn',
            'Iron': 'Fe',
            'Phosphorus': 'P'
        }

        # Calculate value for each metal
        metal_values = []
        total_value = 0.0

        for metal, assay in assays.items():
            if assay > 0 and metal in metal_to_price:
                price_key = metal_to_price[metal]
                price_per_kg = market_data.get(price_key, 0.0)

                contained_mass = weight_kg * assay
                recoverable_mass = contained_mass * recovery_rates.get(metal, 0.0)
                estimated_value = recoverable_mass * price_per_kg * payable_pct.get(metal, 0.0)

                if estimated_value > 0:
                    metal_values.append({
                        'metal': metal,
                        'grade_pct': round(assay * 100, 2),
                        'contained_kg': round(contained_mass, 2),
                        'recoverable_kg': round(recoverable_mass, 2),
                        'recovery_rate_pct': round(recovery_rates.get(metal, 0.0) * 100, 0),
                        'estimated_value': round(estimated_value, 2)
                    })
                    total_value += estimated_value

        # Sort by value (highest first)
        metal_values.sort(key=lambda x: x['estimated_value'], reverse=True)

        # Calculate per-tonne value for easy comparison
        per_tonne_value = (total_value / weight_kg) * 1000 if weight_kg > 0 else 0

        return jsonify({
            'success': True,
            'data': {
                'summary': {
                    'weight_kg': weight_kg,
                    'currency': currency,
                    'chemistry': chemistry,
                    'chemistry_name': chemistry_info.get('name', 'Unknown'),
                    'total_estimated_value': round(total_value, 2),
                    'value_per_tonne': round(per_tonne_value, 2),
                    'price_date': market_data.get('timestamp', 'Unknown')
                },
                'metal_breakdown': metal_values,
                'notes': [
                    'Values based on current market prices and typical industry recovery rates',
                    'Actual offers may vary based on material condition, volume, and processor terms',
                    f'Chemistry auto-detected as {chemistry_info.get("name", chemistry)}'
                ]
            }
        })

    except Exception as e:
        logger.error(f"Value view error: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/sensitivity', methods=['POST'])
def calculate_sensitivity():
    """
    Sensitivity analysis - shows how valuation changes with price movements.

    Request body:
        {
            "currency": "USD",
            "weight_kg": 1000,
            "assays": {
                "Nickel": 0.205,
                "Cobalt": 0.062,
                "Lithium": 0.025,
                ...
            },
            "scenarios": [-20, -10, 0, 10, 20]  # Optional: % changes to test
        }

    Returns valuation at each price scenario for each major metal.
    """
    try:
        data = request.get_json()

        currency = data.get('currency', 'USD')
        weight_kg = data.get('weight_kg', 0)
        assays = data.get('assays', {})
        scenarios = data.get('scenarios', [-20, -10, 0, 10, 20])

        if not weight_kg or weight_kg <= 0:
            return jsonify({
                'success': False,
                'error': 'Missing or invalid weight_kg parameter'
            }), 400

        if not assays:
            return jsonify({
                'success': False,
                'error': 'Missing assays parameter'
            }), 400

        # Ensure Iron and Phosphorus exist
        if 'Iron' not in assays:
            assays['Iron'] = 0.0
        if 'Phosphorus' not in assays:
            assays['Phosphorus'] = 0.0

        # Auto-detect chemistry
        chemistry = backend.detect_chemistry(assays)
        chemistry_info = backend.CHEMISTRIES.get(chemistry, {})

        # Get current market prices
        market_data = backend.get_market_data(currency)

        # Standard recovery and payable rates
        recovery_rates = {
            'Nickel': 0.95, 'Cobalt': 0.95, 'Lithium': 0.85,
            'Copper': 0.95, 'Aluminum': 0.90, 'Manganese': 0.85,
            'Iron': 0.85, 'Phosphorus': 0.0
        }
        payable_pct = {
            'Nickel': 0.80, 'Cobalt': 0.75, 'Lithium': 0.30,
            'Copper': 0.80, 'Aluminum': 0.70, 'Manganese': 0.60,
            'Iron': 0.0, 'Phosphorus': 0.0
        }
        metal_to_price = {
            'Nickel': 'Ni', 'Cobalt': 'Co', 'Lithium': 'Li',
            'Copper': 'Cu', 'Aluminum': 'Al', 'Manganese': 'Mn',
            'Iron': 'Fe', 'Phosphorus': 'P'
        }

        # Calculate base value
        def calc_total_value(price_adjustments=None):
            """Calculate total value with optional price adjustments (as multipliers)"""
            if price_adjustments is None:
                price_adjustments = {}

            total = 0.0
            breakdown = {}
            for metal, assay in assays.items():
                if assay > 0 and metal in metal_to_price:
                    price_key = metal_to_price[metal]
                    base_price = market_data.get(price_key, 0.0)
                    adjusted_price = base_price * price_adjustments.get(metal, 1.0)

                    contained = weight_kg * assay
                    recoverable = contained * recovery_rates.get(metal, 0.0)
                    value = recoverable * adjusted_price * payable_pct.get(metal, 0.0)

                    breakdown[metal] = round(value, 2)
                    total += value

            return round(total, 2), breakdown

        # Base case
        base_value, base_breakdown = calc_total_value()

        # Determine which metals to analyze (only those with meaningful value)
        metals_to_analyze = [m for m, v in base_breakdown.items() if v > 0]

        # Build sensitivity matrix
        sensitivity_results = {}

        for metal in metals_to_analyze:
            metal_scenarios = []
            for pct_change in scenarios:
                multiplier = 1.0 + (pct_change / 100.0)
                adjustments = {metal: multiplier}
                scenario_value, _ = calc_total_value(adjustments)
                value_change = scenario_value - base_value
                pct_impact = (value_change / base_value * 100) if base_value > 0 else 0

                metal_scenarios.append({
                    'price_change_pct': pct_change,
                    'total_value': scenario_value,
                    'value_change': round(value_change, 2),
                    'impact_pct': round(pct_impact, 2)
                })

            sensitivity_results[metal] = metal_scenarios

        # Calculate which metal has the biggest impact
        max_impact_metal = None
        max_impact = 0
        for metal, scenarios_data in sensitivity_results.items():
            # Look at the +20% scenario impact
            for s in scenarios_data:
                if s['price_change_pct'] == 20:
                    if abs(s['impact_pct']) > max_impact:
                        max_impact = abs(s['impact_pct'])
                        max_impact_metal = metal

        return jsonify({
            'success': True,
            'data': {
                'summary': {
                    'weight_kg': weight_kg,
                    'currency': currency,
                    'chemistry': chemistry,
                    'chemistry_name': chemistry_info.get('name', 'Unknown'),
                    'base_value': base_value,
                    'value_per_tonne': round((base_value / weight_kg) * 1000, 2) if weight_kg > 0 else 0,
                    'most_sensitive_to': max_impact_metal,
                    'price_date': market_data.get('timestamp', 'Unknown')
                },
                'base_breakdown': base_breakdown,
                'sensitivity': sensitivity_results,
                'scenarios_tested': scenarios,
                'notes': [
                    f'A 20% increase in {max_impact_metal} price would increase value by {max_impact:.1f}%' if max_impact_metal else '',
                    'Sensitivity shows how your material value changes with metal price movements',
                    'Use this to understand your price risk exposure'
                ]
            }
        })

    except Exception as e:
        logger.error(f"Sensitivity analysis error: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/compare-lots', methods=['POST'])
def compare_lots():
    """
    Compare multiple lots of battery material side by side.

    Request body:
        {
            "currency": "USD",
            "lots": [
                {
                    "name": "Lot A - Samsung",
                    "weight_kg": 5000,
                    "assays": {"Nickel": 0.22, "Cobalt": 0.08, "Lithium": 0.04}
                },
                {
                    "name": "Lot B - LG",
                    "weight_kg": 3000,
                    "assays": {"Nickel": 0.18, "Cobalt": 0.05, "Lithium": 0.035}
                }
            ]
        }

    Returns comparison showing value, $/kg, and ranking for each lot.
    """
    try:
        data = request.get_json()

        currency = data.get('currency', 'USD')
        lots = data.get('lots', [])

        if not lots or len(lots) < 2:
            return jsonify({
                'success': False,
                'error': 'At least 2 lots required for comparison'
            }), 400

        if len(lots) > 10:
            return jsonify({
                'success': False,
                'error': 'Maximum 10 lots allowed per comparison'
            }), 400

        # Get current market prices
        market_data = backend.get_market_data(currency)

        # Standard recovery and payable rates
        recovery_rates = {
            'Nickel': 0.95, 'Cobalt': 0.95, 'Lithium': 0.85,
            'Copper': 0.95, 'Aluminum': 0.90, 'Manganese': 0.85,
            'Iron': 0.85, 'Phosphorus': 0.0
        }
        payable_pct = {
            'Nickel': 0.80, 'Cobalt': 0.75, 'Lithium': 0.30,
            'Copper': 0.80, 'Aluminum': 0.70, 'Manganese': 0.60,
            'Iron': 0.0, 'Phosphorus': 0.0
        }
        metal_to_price = {
            'Nickel': 'Ni', 'Cobalt': 'Co', 'Lithium': 'Li',
            'Copper': 'Cu', 'Aluminum': 'Al', 'Manganese': 'Mn',
            'Iron': 'Fe', 'Phosphorus': 'P'
        }

        # Process each lot
        lot_results = []

        for i, lot in enumerate(lots):
            lot_name = lot.get('name', f'Lot {i+1}')
            weight_kg = lot.get('weight_kg', 0)
            assays = lot.get('assays', {})

            if not weight_kg or weight_kg <= 0:
                lot_results.append({
                    'name': lot_name,
                    'error': 'Invalid weight'
                })
                continue

            # Ensure Iron and Phosphorus exist
            if 'Iron' not in assays:
                assays['Iron'] = 0.0
            if 'Phosphorus' not in assays:
                assays['Phosphorus'] = 0.0

            # Detect chemistry
            chemistry = backend.detect_chemistry(assays)

            # Calculate value
            total_value = 0.0
            metal_values = {}

            for metal, assay in assays.items():
                if assay > 0 and metal in metal_to_price:
                    price_key = metal_to_price[metal]
                    price_per_kg = market_data.get(price_key, 0.0)

                    contained = weight_kg * assay
                    recoverable = contained * recovery_rates.get(metal, 0.0)
                    value = recoverable * price_per_kg * payable_pct.get(metal, 0.0)

                    metal_values[metal] = round(value, 2)
                    total_value += value

            value_per_kg = total_value / weight_kg if weight_kg > 0 else 0
            value_per_tonne = value_per_kg * 1000

            lot_results.append({
                'name': lot_name,
                'weight_kg': weight_kg,
                'weight_tonnes': round(weight_kg / 1000, 3),
                'chemistry': chemistry,
                'total_value': round(total_value, 2),
                'value_per_kg': round(value_per_kg, 4),
                'value_per_tonne': round(value_per_tonne, 2),
                'metal_values': metal_values,
                'grades': {k: round(v * 100, 2) for k, v in assays.items() if v > 0}
            })

        # Sort by value per kg (best first) and add ranking
        valid_lots = [l for l in lot_results if 'error' not in l]
        valid_lots.sort(key=lambda x: x['value_per_kg'], reverse=True)

        for rank, lot in enumerate(valid_lots, 1):
            lot['rank'] = rank
            if rank == 1:
                lot['recommendation'] = 'Best value per kg'

        # Calculate comparison stats
        if len(valid_lots) >= 2:
            best = valid_lots[0]
            worst = valid_lots[-1]
            spread_pct = ((best['value_per_kg'] - worst['value_per_kg']) / worst['value_per_kg'] * 100) if worst['value_per_kg'] > 0 else 0

            comparison_stats = {
                'best_lot': best['name'],
                'best_value_per_kg': best['value_per_kg'],
                'worst_lot': worst['name'],
                'worst_value_per_kg': worst['value_per_kg'],
                'spread_pct': round(spread_pct, 1),
                'total_weight_kg': sum(l['weight_kg'] for l in valid_lots),
                'total_value': round(sum(l['total_value'] for l in valid_lots), 2)
            }
        else:
            comparison_stats = {}

        return jsonify({
            'success': True,
            'data': {
                'currency': currency,
                'price_date': market_data.get('timestamp', 'Unknown'),
                'lots': lot_results,
                'comparison': comparison_stats,
                'notes': [
                    'Lots ranked by value per kg (highest = best)',
                    f'Price spread between best and worst: {comparison_stats.get("spread_pct", 0):.1f}%' if comparison_stats else '',
                    'Values based on current market prices and typical recovery rates'
                ]
            }
        })

    except Exception as e:
        logger.error(f"Lot comparison error: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/bid-report', methods=['POST'])
def generate_bid_report():
    """
    Generate a bid report for traders to send to suppliers.

    Includes material value but HIDES internal costs and margins.
    Can be exported/shared with counterparties.

    Request body:
        {
            "currency": "USD",
            "weight_kg": 1000,
            "assays": {...},
            "offered_price_per_kg": 2.50,  # Optional: trader's offered price
            "validity_days": 7,  # Optional: quote validity period
            "transport_origin": "CA",  # Optional: for transport notes
            "transport_destination": "US",  # Optional
            "include_transport_advisory": true,  # Optional
            "include_market_prices": true,  # Optional
            "company_name": "ABC Recycling",  # Optional: for branding
            "reference_number": "Q-2025-001"  # Optional
        }
    """
    try:
        data = request.get_json()

        currency = data.get('currency', 'USD')
        weight_kg = data.get('weight_kg', 0)
        assays = data.get('assays', {})
        offered_price = data.get('offered_price_per_kg', None)
        validity_days = data.get('validity_days', 7)
        include_transport = data.get('include_transport_advisory', False)
        include_prices = data.get('include_market_prices', True)
        company_name = data.get('company_name', None)
        reference = data.get('reference_number', None)

        if not weight_kg or weight_kg <= 0:
            return jsonify({
                'success': False,
                'error': 'Missing or invalid weight_kg parameter'
            }), 400

        if not assays:
            return jsonify({
                'success': False,
                'error': 'Missing assays parameter'
            }), 400

        # Ensure Iron and Phosphorus exist
        if 'Iron' not in assays:
            assays['Iron'] = 0.0
        if 'Phosphorus' not in assays:
            assays['Phosphorus'] = 0.0

        # Auto-detect chemistry
        chemistry = backend.detect_chemistry(assays)
        chemistry_info = backend.CHEMISTRIES.get(chemistry, {})

        # Get market data
        market_data = backend.get_market_data(currency)

        from datetime import datetime, timedelta

        report_date = datetime.now().strftime('%Y-%m-%d')
        valid_until = (datetime.now() + timedelta(days=validity_days)).strftime('%Y-%m-%d')

        # Build composition table
        composition = []
        metal_to_price = {'Nickel': 'Ni', 'Cobalt': 'Co', 'Lithium': 'Li',
                          'Copper': 'Cu', 'Aluminum': 'Al', 'Manganese': 'Mn',
                          'Iron': 'Fe', 'Phosphorus': 'P'}

        for metal, assay in assays.items():
            if assay > 0 and metal in metal_to_price:
                entry = {
                    'metal': metal,
                    'grade_pct': round(assay * 100, 2),
                    'contained_kg': round(weight_kg * assay, 2)
                }
                if include_prices:
                    price_key = metal_to_price[metal]
                    entry['market_price_per_kg'] = round(market_data.get(price_key, 0.0), 2)
                composition.append(entry)

        # Sort by grade (highest first)
        composition.sort(key=lambda x: x['grade_pct'], reverse=True)

        # Calculate offered total if price provided
        offered_total = None
        if offered_price is not None:
            offered_total = round(weight_kg * offered_price, 2)

        # Build report
        report = {
            'report_info': {
                'type': 'Battery Material Purchase Quote',
                'date': report_date,
                'valid_until': valid_until,
                'reference': reference,
                'company': company_name
            },
            'material': {
                'weight_kg': weight_kg,
                'weight_tonnes': round(weight_kg / 1000, 3),
                'chemistry': chemistry,
                'chemistry_name': chemistry_info.get('name', 'Unknown'),
                'composition': composition
            },
            'pricing': {
                'currency': currency
            }
        }

        if include_prices:
            report['pricing']['market_price_date'] = market_data.get('timestamp', 'Unknown')

        if offered_price is not None:
            report['pricing']['offered_price_per_kg'] = offered_price
            report['pricing']['total_offered_value'] = offered_total

        # Add transport advisory if requested
        if include_transport:
            origin = data.get('transport_origin', '').upper()
            destination = data.get('transport_destination', '').upper()

            if origin and destination:
                route_key = get_transport_route_key(origin, destination)
                advisory = TRANSPORT_ADVISORIES.get(route_key)

                if advisory:
                    report['transport'] = {
                        'route': advisory.get('route', f"{origin} → {destination}"),
                        'status': advisory.get('classification', {}).get('status', 'Unknown'),
                        'key_requirements': [item['item'] for item in advisory.get('checklist', [])[:3]],
                        'estimated_cost': advisory.get('cost_estimate', {}).get('truck', 'Contact for quote'),
                        'transit_time': advisory.get('transit_time', 'Varies')
                    }

        # IMPORTANT: These are intentionally NOT included in the report:
        # - Processing costs
        # - Refining OPEX
        # - Trader's margin
        # - Sensitivity analysis
        # - Internal payable rates

        report['disclaimer'] = (
            "This quote is subject to material inspection and verification of specifications. "
            "Final pricing may be adjusted based on actual assay results. "
            f"Quote valid until {valid_until}."
        )

        return jsonify({
            'success': True,
            'data': report
        })

    except Exception as e:
        logger.error(f"Bid report error: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


if __name__ == '__main__':
    # For local development
    app.run(debug=True, host='0.0.0.0', port=5000)
