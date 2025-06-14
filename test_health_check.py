#!/usr/bin/env python3
"""
Simple test to diagnose the health check issue
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__)))

try:
    from src.interfaces.dashboard.api.unified_api_server import UnifiedDashboardAPI
    
    print("Creating API instance...")
    api = UnifiedDashboardAPI()
    
    print("Getting health status...")
    health = api.health_service.get_system_health()
    
    print(f"Health status: {health.get('status')}")
    print(f"Full health data: {health}")
    
    # Test the actual endpoint
    with api.app.test_client() as client:
        response = client.get('/health')
        print(f"HTTP status code: {response.status_code}")
        print(f"Response data: {response.get_json()}")
        
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
