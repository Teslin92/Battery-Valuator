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


if __name__ == '__main__':
    # For local development
    app.run(debug=True, host='0.0.0.0', port=5000)
