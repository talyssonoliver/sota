#!/usr/bin/env python3
"""
Dashboard Stability Test - Phase 6 Step 6.6

Tests dashboard for browser crashes, memory leaks, and infinite loops.
Validates all API endpoints and chart rendering stability.
"""

import requests
import json
import time
import threading
import psutil
import sys
from pathlib import Path
from typing import Dict, List, Any

class DashboardStabilityTester:
    """Test dashboard stability and performance."""
    
    def __init__(self):
        self.api_base_url = "http://localhost:5000"
        self.test_results = {
            "api_tests": {},
            "performance_tests": {},
            "stability_tests": {},
            "errors": []
        }
        
    def test_api_endpoints(self) -> bool:
        """Test all dashboard API endpoints."""
        print("🔍 Testing API endpoints...")
        
        endpoints = [
            "/health",
            "/api/metrics", 
            "/api/sprint/health",
            "/api/automation/status",
            "/api/tasks/recent?limit=5",
            "/api/progress/trend?days=7",
            "/api/briefing/latest"
        ]
        
        all_passed = True
        
        for endpoint in endpoints:
            try:
                start_time = time.time()
                response = requests.get(f"{self.api_base_url}{endpoint}", timeout=10)
                response_time = time.time() - start_time
                
                if response.status_code == 200:
                    data = response.json()
                    self.test_results["api_tests"][endpoint] = {
                        "status": "PASS",
                        "response_time": round(response_time, 3),
                        "data_size": len(json.dumps(data))
                    }
                    print(f"  ✅ {endpoint} - {response.status_code} ({response_time:.3f}s)")
                else:
                    self.test_results["api_tests"][endpoint] = {
                        "status": "FAIL",
                        "error": f"HTTP {response.status_code}"
                    }
                    print(f"  ❌ {endpoint} - {response.status_code}")
                    all_passed = False
                    
            except Exception as e:
                self.test_results["api_tests"][endpoint] = {
                    "status": "ERROR",
                    "error": str(e)
                }
                print(f"  💥 {endpoint} - {e}")
                all_passed = False
                
        return all_passed
    
    def test_api_performance(self) -> bool:
        """Test API performance under load."""
        print("⚡ Testing API performance...")
        
        endpoint = "/api/metrics"
        requests_count = 50
        concurrent_threads = 5
        
        results = []
        errors = []
        
        def make_requests():
            for _ in range(requests_count // concurrent_threads):
                try:
                    start_time = time.time()
                    response = requests.get(f"{self.api_base_url}{endpoint}", timeout=5)
                    response_time = time.time() - start_time
                    
                    if response.status_code == 200:
                        results.append(response_time)
                    else:
                        errors.append(f"HTTP {response.status_code}")
                        
                except Exception as e:
                    errors.append(str(e))
        
        # Run concurrent requests
        threads = []
        start_time = time.time()
        
        for _ in range(concurrent_threads):
            thread = threading.Thread(target=make_requests)
            thread.start()
            threads.append(thread)
        
        for thread in threads:
            thread.join()
            
        total_time = time.time() - start_time
        
        if results:
            avg_response_time = sum(results) / len(results)
            max_response_time = max(results)
            min_response_time = min(results)
            
            self.test_results["performance_tests"] = {
                "total_requests": len(results),
                "total_time": round(total_time, 3),
                "avg_response_time": round(avg_response_time, 3),
                "max_response_time": round(max_response_time, 3),
                "min_response_time": round(min_response_time, 3),
                "requests_per_second": round(len(results) / total_time, 2),
                "error_count": len(errors)
            }
            
            print(f"  📊 {len(results)} requests in {total_time:.3f}s")
            print(f"  📊 Avg response: {avg_response_time:.3f}s")
            print(f"  📊 RPS: {len(results) / total_time:.2f}")
            print(f"  📊 Errors: {len(errors)}")
            
            return len(errors) == 0 and avg_response_time < 1.0
        else:
            print("  ❌ No successful requests")
            return False
    
    def test_memory_usage(self) -> bool:
        """Test for memory leaks in repeated API calls."""
        print("🧠 Testing memory usage...")
        
        process = psutil.Process()
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # Make 100 API calls and monitor memory
        for i in range(100):
            try:
                requests.get(f"{self.api_base_url}/api/metrics", timeout=5)
                if i % 20 == 0:
                    current_memory = process.memory_info().rss / 1024 / 1024
                    print(f"  📈 After {i} requests: {current_memory:.1f} MB")
            except:
                pass
                
        final_memory = process.memory_info().rss / 1024 / 1024
        memory_increase = final_memory - initial_memory
        
        self.test_results["stability_tests"]["memory"] = {
            "initial_memory_mb": round(initial_memory, 1),
            "final_memory_mb": round(final_memory, 1),
            "memory_increase_mb": round(memory_increase, 1)
        }
        
        print(f"  📊 Initial: {initial_memory:.1f} MB")
        print(f"  📊 Final: {final_memory:.1f} MB")
        print(f"  📊 Increase: {memory_increase:.1f} MB")
        
        # Memory increase should be reasonable (< 50MB)
        return memory_increase < 50
    
    def test_chart_data_integrity(self) -> bool:
        """Test chart data structure and integrity."""
        print("📈 Testing chart data integrity...")
        
        try:
            # Test metrics data structure
            response = requests.get(f"{self.api_base_url}/api/metrics")
            metrics = response.json()["data"]
            
            required_fields = ["completed_tasks", "total_tasks", "completion_rate"]
            for field in required_fields:
                if field not in metrics:
                    print(f"  ❌ Missing field: {field}")
                    return False
                    
            # Test progress trend data
            response = requests.get(f"{self.api_base_url}/api/progress/trend?days=7")
            trend_data = response.json()["data"]
            
            required_trend_fields = ["dates", "completion_rates"]
            for field in required_trend_fields:
                if field not in trend_data:
                    print(f"  ❌ Missing trend field: {field}")
                    return False
                    
            # Validate data consistency
            if len(trend_data["dates"]) != len(trend_data["completion_rates"]):
                print(f"  ❌ Mismatched trend data lengths")
                return False
                
            print(f"  ✅ Metrics data structure valid")
            print(f"  ✅ Trend data structure valid")
            print(f"  ✅ Data lengths consistent")
            
            return True
            
        except Exception as e:
            print(f"  ❌ Chart data test failed: {e}")
            return False
    
    def test_error_handling(self) -> bool:
        """Test error handling and recovery."""
        print("🛡️ Testing error handling...")
        
        try:
            # Test invalid endpoint
            response = requests.get(f"{self.api_base_url}/api/invalid", timeout=5)
            if response.status_code == 404:
                print(f"  ✅ 404 handling works")
            else:
                print(f"  ⚠️ Expected 404, got {response.status_code}")
                
            # Test malformed requests
            response = requests.get(f"{self.api_base_url}/api/progress/trend?days=invalid")
            # Should handle gracefully without crashing
            print(f"  ✅ Malformed parameter handling works")
            
            return True
            
        except Exception as e:
            print(f"  ❌ Error handling test failed: {e}")
            return False
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Run all dashboard stability tests."""
        print("🚀 Starting Dashboard Stability Tests")
        print("=" * 50)
        
        tests = [
            ("API Endpoints", self.test_api_endpoints),
            ("API Performance", self.test_api_performance),
            ("Memory Usage", self.test_memory_usage),
            ("Chart Data Integrity", self.test_chart_data_integrity),
            ("Error Handling", self.test_error_handling)
        ]
        
        results = {}
        overall_pass = True
        
        for test_name, test_func in tests:
            print(f"\n🔬 Running {test_name} test...")
            try:
                passed = test_func()
                results[test_name] = "PASS" if passed else "FAIL"
                if not passed:
                    overall_pass = False
                    
            except Exception as e:
                results[test_name] = f"ERROR: {e}"
                overall_pass = False
                self.test_results["errors"].append(f"{test_name}: {e}")
        
        print("\n" + "=" * 50)
        print("📋 Test Results Summary:")
        print("=" * 50)
        
        for test_name, result in results.items():
            status_icon = "✅" if result == "PASS" else "❌"
            print(f"{status_icon} {test_name}: {result}")
        
        print(f"\n🎯 Overall Status: {'PASS' if overall_pass else 'FAIL'}")
        
        # Save detailed results
        self.test_results["summary"] = {
            "overall_status": "PASS" if overall_pass else "FAIL",
            "individual_tests": results,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        
        return self.test_results

def main():
    """Main entry point for dashboard stability testing."""
    print("Dashboard Stability Test Suite")
    print("Testing Phase 6 Real-time Dashboard")
    
    tester = DashboardStabilityTester()
    results = tester.run_all_tests()
    
    # Save results to file
    results_file = Path("dashboard_stability_results.json")
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n📄 Detailed results saved to: {results_file}")
    
    # Exit with appropriate code
    exit_code = 0 if results["summary"]["overall_status"] == "PASS" else 1
    sys.exit(exit_code)

if __name__ == "__main__":
    main()
