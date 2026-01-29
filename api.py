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
        
        # Add transport data if provided
        transport_data = input_params.get('transport_data')
        if transport_data:
            try:
                # Check if user provided a manual override cost
                manual_override = transport_data.get('manual_override', False)
                manual_cost = transport_data.get('manual_cost')
                
                if manual_override and manual_cost is not None:
                    # Use the manually entered cost
                    transport_cost = float(manual_cost)
                    transport_estimate = {
                        'estimated_cost': transport_cost,
                        'mode': transport_data.get('mode', 'ocean'),
                        'weight_kg': input_params['gross_weight'],
                        'note': 'Manual override - user-provided cost',
                        'manual_override': True
                    }
                else:
                    # Get transport estimate from backend
                    transport_estimate = backend.get_transport_estimate(
                        origin=transport_data.get('origin', 'US'),
                        destination=transport_data.get('destination', 'Canada'),
                        mode=transport_data.get('mode', 'ocean'),
                        weight_kg=input_params['gross_weight'],
                        material_type=transport_data.get('material_type', 'black_mass'),
                        is_ddr=transport_data.get('is_ddr', False),
                        distance_miles=transport_data.get('distance_miles')
                    )
                    transport_cost = transport_estimate.get('estimated_cost', 0)
                
                # Check route feasibility
                route_advisory = backend.check_route_feasibility(
                    origin=transport_data.get('origin', 'US'),
                    destination=transport_data.get('destination', 'Canada'),
                    material_type=transport_data.get('material_type', 'black_mass')
                )
                
                # Add transport cost to total OPEX
                results['transport_cost'] = transport_cost
                results['total_opex'] = results['total_opex'] + transport_cost
                
                # Recalculate profit and margin
                results['net_profit'] = results['total_revenue'] - results['material_cost'] - results['total_opex']
                results['margin_pct'] = (results['net_profit'] / results['total_revenue']) * 100 if results['total_revenue'] > 0 else 0
                
                # Add transport and regulatory info
                results['transport_estimate'] = transport_estimate
                results['route_advisory'] = route_advisory
                
                # Update cost breakdown
                if 'cost_breakdown' not in results:
                    results['cost_breakdown'] = {}
                results['cost_breakdown']['transport'] = transport_cost
                
            except Exception as e:
                logger.error(f"Error calculating transport costs: {str(e)}")
                results['transport_error'] = str(e)

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

# ============================================================================
# TRANSPORT AND REGULATORY ENDPOINTS
# ============================================================================

@app.route('/api/transport/check-route', methods=['POST'])
def check_transport_route():
    """
    Check feasibility of transport route based on regulations.
    
    Request body:
        {
            "origin": "US",
            "destination": "Canada",
            "materialType": "black_mass"
        }
    
    Response:
        {
            "success": true,
            "data": {
                "allowed": true,
                "status": "allowed",
                "requirements": ["ECCC permit", "EPA AOC"],
                "warnings": [],
                "processing_time": "60-90 days"
            }
        }
    """
    try:
        data = request.get_json()
        origin = data.get('origin')
        destination = data.get('destination')
        material_type = data.get('materialType', 'black_mass')
        
        if not origin or not destination:
            return jsonify({
                'success': False,
                'error': 'origin and destination are required'
            }), 400
        
        result = backend.check_route_feasibility(origin, destination, material_type)
        
        return jsonify({
            'success': True,
            'data': result
        })
    except Exception as e:
        logger.error(f"Route check error: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/transport/estimate', methods=['POST'])
def get_transport_estimate():
    """
    Get transportation cost estimate.
    
    Request body:
        {
            "origin": "US",
            "destination": "China",
            "mode": "ocean",
            "weightKg": 1000,
            "materialType": "black_mass",
            "isDDR": false,
            "distanceMiles": null  // required for truck mode
        }
    
    Response:
        {
            "success": true,
            "data": {
                "estimated_cost": 153.00,
                "mode": "ocean",
                "breakdown": {...}
            }
        }
    """
    try:
        data = request.get_json()
        origin = data.get('origin')
        destination = data.get('destination')
        mode = data.get('mode', 'ocean')
        weight_kg = float(data.get('weightKg', 0))
        material_type = data.get('materialType', 'black_mass')
        is_ddr = data.get('isDDR', False)
        distance_miles = data.get('distanceMiles')
        
        if not origin or not destination:
            return jsonify({
                'success': False,
                'error': 'origin and destination are required'
            }), 400
        
        if weight_kg <= 0:
            return jsonify({
                'success': False,
                'error': 'weightKg must be greater than 0'
            }), 400
        
        result = backend.get_transport_estimate(
            origin, destination, mode, weight_kg,
            material_type, is_ddr, distance_miles
        )
        
        # Check for errors in result
        if 'error' in result:
            return jsonify({
                'success': False,
                'error': result['error'],
                'alternative': result.get('alternative')
            }), 400
        
        return jsonify({
            'success': True,
            'data': result
        })
    except Exception as e:
        logger.error(f"Transport estimate error: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/regulatory/requirements', methods=['GET'])
def get_regulatory_requirements():
    """
    Get regulatory requirements for a specific route and material.
    
    Query params:
        origin: Origin country code
        destination: Destination country code
        material: Material type (whole_batteries, black_mass, processed)
    
    Response:
        {
            "success": true,
            "data": {
                "permits": [...],
                "basel_requirements": [...],
                "packaging": {...},
                "documentation": [...]
            }
        }
    """
    try:
        origin = request.args.get('origin')
        destination = request.args.get('destination')
        material = request.args.get('material', 'black_mass')
        
        if not origin or not destination:
            return jsonify({
                'success': False,
                'error': 'origin and destination query parameters are required'
            }), 400
        
        # Get permit checklist
        checklist = backend.get_permit_checklist(origin, destination, material)
        
        # Get regulatory details
        regulations = backend.get_waste_regulations(origin, destination, material)
        
        return jsonify({
            'success': True,
            'data': {
                'checklist': checklist,
                'regulations': regulations
            }
        })
    except Exception as e:
        logger.error(f"Regulatory requirements error: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/regulatory/status', methods=['GET'])
def get_regulatory_database_status():
    """
    Get status of regulatory database (last updated, freshness).
    
    Response:
        {
            "success": true,
            "data": {
                "last_updated": "2026-01-27",
                "next_refresh": "2027-01-27",
                "age_days": 0,
                "status": "fresh",
                "sources": [...]
            }
        }
    """
    try:
        from logistics_data import get_full_database
        import sys
        import os
        
        # Import regulatory_refresh to check freshness
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        import regulatory_refresh
        
        db = get_full_database()
        metadata = db.get('metadata', {})
        
        freshness = regulatory_refresh.check_database_freshness()
        
        return jsonify({
            'success': True,
            'data': {
                'last_updated': metadata.get('last_updated'),
                'next_refresh': metadata.get('next_refresh'),
                'version': metadata.get('version'),
                'sources': metadata.get('sources', []),
                'freshness': freshness
            }
        })
    except Exception as e:
        logger.error(f"Database status error: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/admin/refresh-regulatory', methods=['POST'])
def trigger_regulatory_refresh():
    """
    Manually trigger regulatory database refresh (admin only).
    
    Request body:
        {
            "source": "epa_faqs"  // optional, refresh specific source only
        }
    
    Response:
        {
            "success": true,
            "message": "Refresh instructions returned",
            "instructions": "..."
        }
    """
    try:
        # For security, this should check authentication in production
        # For now, just return refresh instructions
        
        import sys
        import os
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        import regulatory_refresh
        
        # Get manual refresh instructions
        from io import StringIO
        import contextlib
        
        f = StringIO()
        with contextlib.redirect_stdout(f):
            regulatory_refresh.manual_refresh_instructions()
        instructions = f.getvalue()
        
        return jsonify({
            'success': True,
            'message': 'Manual refresh required - see instructions',
            'instructions': instructions,
            'note': 'Use Cursor with CallMcpTool and firecrawl_scrape to refresh data'
        })
    except Exception as e:
        logger.error(f"Refresh trigger error: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


if __name__ == '__main__':
    # For local development
    app.run(debug=True, host='0.0.0.0', port=5000)
