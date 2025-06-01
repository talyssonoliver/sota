#!/usr/bin/env python3
"""
Test improved configuration loading
"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from orchestration.daily_cycle import DailyCycleOrchestrator

try:
    orchestrator = DailyCycleOrchestrator()
    print("✅ Configuration loaded successfully")
    print(f"Config sections: {list(orchestrator.config.keys())}")
    print(f"Paths section: {orchestrator.config.get('paths', {})}")
    print(f"Email enabled: {orchestrator.config.get('email', {}).get('enabled', False)}")
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
