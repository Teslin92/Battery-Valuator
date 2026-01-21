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

if __name__ == '__main__':
    # For local development
    app.run(debug=True, host='0.0.0.0', port=5000)
