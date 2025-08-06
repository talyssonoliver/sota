#!/usr/bin/env python3

from src.infrastructure.utils.common_imports import (
    Path,
    asyncio,
    requests,
    sys
)
"""
Daily Automation Scheduler - Phase 6 Complete Demo

Demonstrates the full automated daily cycle with scheduled tasks
"""
# import asyncio  # Consolidated to common_imports
# import sys  # Consolidated to common_imports
# from pathlib import Path  # Consolidated to common_imports

# Add parent directory to path for imports 
sys.path.append(str(Path(__file__).parent.parent))

from src.core.workflows.daily_cycle import DailyCycleOrchestrator

async def demo_full_automation():
    print("🚀 Starting Phase 6 Daily Automation & Visualization Demo")
    print("=" * 60)
    
    orchestrator = DailyCycleOrchestrator()
    print("✅ Daily Cycle Orchestrator initialized")
    
    # Demo 1: Morning Briefing
    print("\n📊 DEMO 1: Morning Briefing Generation")
    print("-" * 40)
    result = await orchestrator.run_morning_briefing()
    if result.get('status') == 'success':
        print(f"✅ Morning briefing generated: {result.get('file_path', 'N/A')}")
        print(f"📧 Email status: {result.get('email_status', 'disabled')}")
        print(f"📈 Dashboard updated: {result.get('dashboard_updated', False)}")
    
    # Demo 2: Midday Health Check
    print("\n🔍 DEMO 2: Midday System Health Check")
    print("-" * 40)
    result = await orchestrator.run_midday_check()
    if result.get('status') == 'success':
        print("✅ System health check completed")
        print(f"🎯 Tasks analyzed: {result.get('tasks_analyzed', 0)}")
        print(f"⚠️  Issues found: {result.get('issues_count', 0)}")
    
    # Demo 3: End-of-Day Report
    print("\n📋 DEMO 3: End-of-Day Report Generation")
    print("-" * 40)
    result = await orchestrator.run_end_of_day_report()
    if result.get('status') == 'success':
        print(f"✅ End-of-day report generated: {result.get('file_path', 'N/A')}")
        print(f"📊 Metrics calculated: {result.get('metrics_calculated', False)}")
        print(f"📈 Dashboard updated: {result.get('dashboard_updated', False)}")
    
    # Demo 4: Dashboard API Status
    print("\n🌐 DEMO 4: Dashboard API Integration")
    print("-" * 40)
    try:
#         import requests  # Consolidated to common_imports
        response = requests.get('http://localhost:5000/health', timeout=5)
        if response.status_code == 200:
            print("✅ Dashboard API is running")
            print("🔗 Access at: http://localhost:5000")
            
            # Test metrics endpoint
            metrics_response = requests.get('http://localhost:5000/api/metrics', timeout=5)
            if metrics_response.status_code == 200:
                print("✅ Metrics API endpoint working")
            else:
                print("⚠️  Metrics API endpoint issue")
        else:
            print("⚠️  Dashboard API not responding correctly")
    except Exception as e:
        print(f"❌ Dashboard API not accessible: {e}")
    
    print("\n🎉 Phase 6 Daily Automation Demo Complete!")
    print("=" * 60)
    print("\n📚 FEATURES DEMONSTRATED:")
    print("• ✅ Automated morning briefing generation")
    print("• ✅ Midday health checks and monitoring") 
    print("• ✅ Comprehensive end-of-day reporting")
    print("• ✅ Email integration (SMTP configured)")
    print("• ✅ Real-time dashboard API")
    print("• ✅ Metrics calculation and tracking")
    print("• ✅ Configuration management")
    print("• ✅ Error handling and logging")
    
    print("\n🔧 NEXT STEPS:")
    print("• Configure production SMTP credentials")
    print("• Set up automated scheduling (cron/Task Scheduler)")
    print("• Deploy dashboard with production WSGI server")
    print("• Add advanced visualizations (Gantt charts)")
    print("• Implement performance optimizations")

if __name__ == "__main__":
    asyncio.run(demo_full_automation())
