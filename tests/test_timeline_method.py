#!/usr/bin/env python3
"""
Test script to directly call the timeline calculation method.
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent))

from dashboard.unified_api_server import UnifiedDashboardAPI as DashboardAPI

def test_timeline_method():
    """Test the timeline calculation method directly."""
    print("🔍 Testing timeline calculation method...")
    
    try:
        # Create API instance
        api = DashboardAPI()
        
        # Call the timeline calculation method directly
        timeline_data = api._calculate_timeline_data()
        
        print(f"✅ Timeline calculation successful!")
        print(f"   Generated {len(timeline_data)} timeline entries")
        
        if timeline_data:
            print(f"   Sample entry: {timeline_data[0]}")
        
        return timeline_data
        
    except Exception as e:
        print(f"❌ Timeline calculation failed: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    test_timeline_method()
