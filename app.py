import binascii
import requests
from flask import Flask, jsonify, request
import re
from datetime import datetime
import os

app = Flask(__name__)

def convert_timestamp(release_time):
    return datetime.utcfromtimestamp(release_time).strftime('%Y-%m-%d %H:%M:%S')

def extract_token_from_response(data, region):
    print(f"Extracting token for {region}, response: {data}")
    
    if not isinstance(data, dict):
        return None

    # 1️⃣ IND region
    if region == "IND":
        if data.get('success') or data.get('status') in ['success', 'live']:
            return data.get('BearerAuth') or data.get('token')
    
    # 2️⃣ BR, US, SAC, NA regions
    elif region in ["BR", "US", "SAC", "NA"]:
        if 'BearerAuth' in data:
            return data['BearerAuth']
        elif 'token' in data:
            return data['token']

    # 3️⃣ BD, CIS, ME, SG, EU regions (special handling)
    elif region in ["BD", "CIS", "ME", "SG", "EU"]:
        if data.get('success') and 'BearerAuth' in data:
            return data['BearerAuth']
        elif 'token' in data:
            return data['token']
        elif 'data' in data and 'token' in data['data']:
            return data['data']['token']
    
    # 4️⃣ Default fallback
    else:
        if data.get('success') and 'BearerAuth' in data:
            return data['BearerAuth']
        elif 'token' in data:
            return data['token']
    
    # 🔹 Backup keys check
    for key in ['token', 'access_token', 'auth_token', 'BearerAuth']:
        if key in data:
            return data[key]
    
    return None

def get_jwt_token_sync(region):
    endpoints = {
    "IND": "https://akiru-jwt-2-mocha.vercel.app/api/get_jwt?guest_uid=4638641253&guest_password=CZY-YCJOFDHGT-NEXU",
    "BR": "https://akiru-jwt-2-mocha.vercel.app/api/get_jwt?guest_uid=4638643094&guest_password=CZY-GA6QEQHOT-NEXU",
    "US": "https://akiru-jwt-2-mocha.vercel.app/api/get_jwt?guest_uid=4638644139&guest_password=CZY-ARQB8QRDQ-NEXU",
    "SAC": "https://akiru-jwt-2-mocha.vercel.app/api/get_jwt?guest_uid=4638645221&guest_password=CZY-PMS9CAHTP-NEXU",
    "NA": "https://akiru-jwt-2-mocha.vercel.app/api/get_jwt?guest_uid=4638657581&guest_password=CZY-CUIDCZBVM-NEXU",
    "EU": "https://akiru-jwt-2-mocha.vercel.app/api/get_jwt?guest_uid=4638646180&guest_password=CZY-TBT48ZAFT-NEXU",
    "ME": "https://akiru-jwt-2-mocha.vercel.app/api/get_jwt?guest_uid=4638655446&guest_password=CZY-HUVV4A0CQ-NEXU",
    "ID": "https://akiru-jwt-2-mocha.vercel.app/api/get_jwt?guest_uid=4638647579&guest_password=CZY-VJCBAX93P-NEXU",
    "SG": "https://akiru-jwt-2-mocha.vercel.app/api/get_jwt?guest_uid=4638651552&guest_password=CZY-43BCHWQML-NEXU",
    "CIS": "https://akiru-jwt-2-mocha.vercel.app/api/get_jwt?guest_uid=4638653923&guest_password=CZY-E5T3H399W-NEXU",
    "BD": "https://akiru-jwt-2-mocha.vercel.app/api/get_jwt?guest_uid=4638638671&guest_password=CZY-EJIOHRVN2-NEXU"
}
    
    url = endpoints.get(region, endpoints["IND"])
    print(f"Fetching JWT token for {region} from: {url}")
    
    try:
        response = requests.get(url, timeout=15)
        print(f"JWT API response status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"JWT API response data: {data}")
            
            token = extract_token_from_response(data, region)
            if token:
                print(f"JWT Token for {region} fetched successfully: {token[:50]}...")
                return token
            else:
                print(f"Failed to extract token from response for {region}")
                # Alternative extraction attempts
                if isinstance(data, dict):
                    for key in ['token', 'access_token', 'auth_token']:
                        if key in data:
                            print(f"Found alternative token key: {key}")
                            return data[key]
        else:
            print(f"Failed to get JWT token for {region}: HTTP {response.status_code}")
            print(f"Response text: {response.text}")
    except Exception as e:
        print(f"Request error for {region}: {e}")
    
    return None

def get_api_endpoint(region):
    endpoints = {
        "IND": "https://client.ind.freefiremobile.com/LoginGetSplash",
        "BR": "https://client.us.freefiremobile.com/LoginGetSplash",
        "US": "https://client.us.freefiremobile.com/LoginGetSplash",
        "SAC": "https://client.us.freefiremobile.com/LoginGetSplash",
        "NA": "https://client.us.freefiremobile.com/LoginGetSplash",
        "ID": "https://clientbp.ggblueshark.com/LoginGetSplash",
        "ME": "https://clientbp.ggblueshark.com/LoginGetSplash",
        "EU": "https://clientbp.ggblueshark.com/LoginGetSplash",
        "CIS": "https://clientbp.ggblueshark.com/LoginGetSplash",
        "SG": "https://clientbp.ggblueshark.com/LoginGetSplash",
        "BD": "https://clientbp.ggblueshark.com/LoginGetSplash"
    }
    return endpoints.get(region, endpoints["IND"])

def apis(idd, region):
    token = get_jwt_token_sync(region)
    if not token:
        raise Exception(f"Failed to get JWT token for region {region}")    
    
    endpoint = get_api_endpoint(region)
    print(f"Using API endpoint: {endpoint} for region: {region}")
    
    headers = {
        'User-Agent': 'Dalvik/2.1.0 (Linux; U; Android 9; ASUS_Z01QD Build/PI)',
        'Connection': 'Keep-Alive',
        'Expect': '100-continue',
        'Authorization': f'Bearer {token}',
        'X-Unity-Version': '2018.4.11f1',
        'X-GA': 'v1 1',
        'ReleaseVersion': 'OB52',
        'Content-Type': 'application/x-www-form-urlencoded',
    }
    
    region_data = {
        "IND": "03f7f38095daae1bf887928b4f2c0eb4",
        "BR": "9223af2eab91b7a150d528f657731074",  # Added default for missing regions
        "US": "9223af2eab91b7a150d528f657731074",
        "SAC": "9223af2eab91b7a150d528f657731074",
        "NA": "9223af2eab91b7a150d528f657731074",
        "ID": "5b 27 f0 86 9e 37 f9 2b 6f 84 c3 a7 39 34 7d b1",
        "BD": "9223af2eab91b7a150d528f657731074",
        "ME": "9223af2eab91b7a150d528f657731074",
        "EU": "9223af2eab91b7a150d528f657731074",
        "CIS": "9223af2eab91b7a150d528f657731074",  # Fixed: spaces removed
        "SG": "9223af2eab91b7a150d528f657731074"
    }
    
    data_hex = region_data.get(region, region_data["IND"])  # Default to IND if region not found
    print(f"Using data hex for {region}: {data_hex}")
    
    try:
        data = bytes.fromhex(data_hex)
        response = requests.post(
            endpoint,
            headers=headers,
            data=data,
            timeout=15
        )
        print(f"API response status: {response.status_code}")
        
        response.raise_for_status()
        return response.content.hex()
    except requests.exceptions.RequestException as e:
        print(f"API request to {endpoint} failed: {e}")
        print(f"Response content: {getattr(e.response, 'content', 'No response')}")
        raise

@app.route('/eventes', methods=['GET'])
def get_player_info():
    try:
        region = request.args.get('region', 'IND').upper()
        key = request.args.get('key')

        # 🔒 Key check: sirf PARRAHEX allowed
        if key != "PARRAHEX":
            return jsonify({"error": "Invalid key"}), 403

        print(f"Request received for region: {region}, key: {key}")
        
        response_hex = apis(key, region)
        if not response_hex:
            return jsonify({"error": "Failed to get response from API"}), 500
        
        response_text = binascii.unhexlify(response_hex).decode('utf-8', errors='ignore')
        print(f"Decoded response length: {len(response_text)}")
        
        # Multiple patterns to find image URLs
        url_patterns = [
            r'https?://[^\s]+\.png',
            r'https?://[^\s]+\.jpg',
            r'https?://[^\s]+\.jpeg',
            r'https?://[^\s]+\.webp'
        ]
        
        urls = []
        for pattern in url_patterns:
            found_urls = re.findall(pattern, response_text)
            urls.extend(found_urls)
        
        current_date = datetime.now().strftime("%Y-%m-%d")
        current_time = datetime.now().strftime("%H:%M:%S")
        
        results = []
        for url in urls:
            clean_url = url.strip().rstrip('"').rstrip("'")
            event_name = clean_url.split('/')[-1]
            event_name = event_name.replace('_880x520_BR_pt.png', '')
            event_name = event_name.replace('_880x520.png', '')
            event_name = event_name.replace('_', ' ')
            event_name = event_name.replace('.png', '')
            event_name = event_name.replace('.jpg', '')
            event_name = event_name.replace('.jpeg', '')
            event_name = event_name.replace('.webp', '')
            event_name = event_name.title()
            
            results.append({
                "title": event_name,
                "image_url": clean_url
            })
        
        response_data = {
            "status": "success",
            "events": results,
            "count": len(results),
            "date": current_date,
            "time": current_time,
            "region": region
        }
        
        print(f"Returning {len(results)} events for region {region}")
        return jsonify(response_data)
        
    except Exception as e:
        print(f"Error in get_player_info: {str(e)}")
        return jsonify({"error": str(e), "region": request.args.get('region', 'IND')}), 500

@app.route('/')
def home():
    return jsonify({
        "message": "FreeFire Events API",
        "endpoints": {
            "events": "/api/eventes?region=IND&key=your_key",
            "available_regions": ["IND", "BR", "US", "SAC", "NA", "ME", "CIS", "SG", "BD"]
        }
    })

@app.route('/favicon.ico')
def favicon():
    return '', 404

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
