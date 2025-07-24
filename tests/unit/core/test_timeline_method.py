"""
test_timeline_method.py - Optimized Test Structure

Migrated from: tests/workflows	est_timeline_method.py
New location: tests/unit\\core	est_timeline_method.py

Part of the optimized test pyramid reorganization:
- Tests now mirror src/ structure
- Proper categorization (unit/integration/e2e)
- Improved mocking and isolation
"""

import sys
import traceback
from pathlib import Path

sys.path.append(str(Path(__file__).parent))
from src.interfaces.dashboard.api.unified_api_server import (
    UnifiedDashboardAPI as DashboardAPI,
)


def test_timeline_method():
    """Test the timeline calculation method directly."""
    print("🔍 Testing timeline calculation method...")
    try:
        api = DashboardAPI()
        timeline_data = api._calculate_timeline_data()
        print("✅ Timeline calculation successful!")
        print(f"   Generated {len(timeline_data)} timeline entries")
        if timeline_data:
            print(f"   Sample entry: {timeline_data[0]}")
        return timeline_data
    except Exception as e:
        print(f"❌ Timeline calculation failed: {e}")
        traceback.print_exc()
        return None


if __name__ == "__main__":
    test_timeline_method()
