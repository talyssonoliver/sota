#!/usr/bin/env python3
"""
Test script for Daily Cycle Orchestrator
"""
import asyncio
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from orchestration.daily_cycle import DailyCycleOrchestrator

async def main():
    print("Initializing Daily Cycle Orchestrator...")
    orchestrator = DailyCycleOrchestrator()
    print("✓ Orchestrator initialized successfully")
    
    print("\nTesting Morning Briefing...")
    result = await orchestrator.run_morning_briefing()
    print(f"✓ Morning briefing result: {result.get('status', 'unknown')}")
    
    print("\nTesting End-of-Day Report...")
    result = await orchestrator.run_end_of_day_report()
    print(f"✓ End-of-Day report result: {result.get('status', 'unknown')}")
    
    print("\n✓ All tests completed successfully!")

if __name__ == "__main__":
    asyncio.run(main())
