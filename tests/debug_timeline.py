#!/usr/bin/env python3
"""
Debug script to test the timeline endpoint specifically.
"""

import requests
import json
from pathlib import Path
import sys

# Add the dashboard directory to path
sys.path.append(str(Path(__file__).parent / "dashboard"))

def test_timeline_endpoint():
    """Test the timeline endpoint and debug any issues."""
    base_url = "http://localhost:5000"
    
    print("🔍 Testing API Server Endpoints...")
    
    # Test if server is running
    try:
        response = requests.get(f"{base_url}/health", timeout=5)
        print(f"✅ Health check: {response.status_code}")
    except Exception as e:
        print(f"❌ Server not running: {e}")
        return
    
    # Test working endpoint
    try:
        response = requests.get(f"{base_url}/api/metrics", timeout=5)
        print(f"✅ Metrics endpoint: {response.status_code}")
    except Exception as e:
        print(f"❌ Metrics endpoint error: {e}")
    
    # Test timeline endpoint
    try:
        response = requests.get(f"{base_url}/api/timeline", timeout=5)
        print(f"📊 Timeline endpoint: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Timeline data received: {len(data.get('data', []))} entries")
            if data.get('data'):
                first_entry = data['data'][0]
                print(f"   Sample entry: {json.dumps(first_entry, indent=2)}")
        else:
            print(f"❌ Timeline endpoint failed: {response.text}")
            
    except Exception as e:
        print(f"❌ Timeline endpoint error: {e}")
    
    # List all available routes by checking Flask app directly
    print("\n🔍 Checking registered routes...")
    try:
        # Ensure the directory containing api_server.py is in sys.path so it can be imported
        api_server_path = Path(__file__).parent / "api_server.py"
        if api_server_path.exists():
            sys.path.append(str(Path(__file__).parent))
            import importlib.util
            spec = importlib.util.spec_from_file_location("api_server", str(api_server_path))
            api_server = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(api_server)
            api = api_server.DashboardAPI()
            
            print("Available routes:")
            for rule in api.app.url_map.iter_rules():
                print(f"  {rule.methods} {rule.rule}")
        else:
            print(f"❌ api_server.py not found at {api_server_path}")
            
    except Exception as e:
        print(f"❌ Error checking routes: {e}")

if __name__ == "__main__":
    test_timeline_endpoint()
