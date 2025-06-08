#!/usr/bin/env python3
"""
Chart.js Canvas Size Explosion Fix Validation
Tests the dashboard stability after fixing critical chart recreation loop
"""
import time
import json
import subprocess
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class DashboardStabilityValidator:
    def __init__(self):
        self.api_base_url = "http://localhost:5000"
        self.dashboard_url = "http://localhost:5000/dashboard/realtime_dashboard.html"
        self.driver = None
        
    def setup_browser(self):
        """Setup Chrome browser with monitoring capabilities"""
        chrome_options = Options()
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        # Enable performance logging
        chrome_options.add_argument("--enable-logging")
        chrome_options.add_argument("--v=1")
        chrome_options.set_capability('goog:loggingPrefs', {'performance': 'ALL'})
        
        self.driver = webdriver.Chrome(options=chrome_options)
        return self.driver
        
    def check_api_server(self):
        """Verify API server is running"""
        try:
            response = requests.get(f"{self.api_base_url}/api/metrics", timeout=5)
            return response.status_code == 200
        except:
            return False
            
    def monitor_canvas_sizes(self, duration_seconds=60):
        """Monitor canvas sizes for explosion issues"""
        results = {
            "timestamp": time.time(),
            "duration": duration_seconds,
            "canvas_sizes": [],
            "console_messages": [],
            "memory_usage": [],
            "chart_instances": [],
            "errors": []
        }
        
        try:
            print(f"🌐 Loading dashboard: {self.dashboard_url}")
            self.driver.get(self.dashboard_url)
            
            # Wait for page load
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "canvas"))
            )
            
            print(f"📊 Monitoring canvas sizes for {duration_seconds} seconds...")
            start_time = time.time()
            
            while time.time() - start_time < duration_seconds:
                # Check canvas dimensions
                canvases = self.driver.find_elements(By.TAG_NAME, "canvas")
                canvas_data = []
                
                for i, canvas in enumerate(canvases):
                    width = canvas.get_attribute("width") or canvas.size["width"]
                    height = canvas.get_attribute("height") or canvas.size["height"]
                    style_height = self.driver.execute_script(
                        "return arguments[0].style.height", canvas
                    )
                    computed_height = self.driver.execute_script(
                        "return window.getComputedStyle(arguments[0]).height", canvas
                    )
                    
                    canvas_info = {
                        "id": canvas.get_attribute("id"),
                        "width": width,
                        "height": height,
                        "style_height": style_height,
                        "computed_height": computed_height,
                        "timestamp": time.time()
                    }
                    canvas_data.append(canvas_info)
                    
                    # Flag if height is exploding
                    if isinstance(height, (int, str)) and int(str(height).replace('px', '')) > 1000:
                        results["errors"].append({
                            "type": "canvas_size_explosion",
                            "canvas_id": canvas.get_attribute("id"),
                            "height": height,
                            "timestamp": time.time()
                        })
                
                results["canvas_sizes"].append(canvas_data)
                
                # Check console messages
                logs = self.driver.get_log('browser')
                for log in logs:
                    if log['level'] in ['SEVERE', 'WARNING']:
                        results["console_messages"].append({
                            "level": log['level'],
                            "message": log['message'],
                            "timestamp": log['timestamp']
                        })
                
                # Check memory usage via JS
                memory_info = self.driver.execute_script("""
                    if (performance.memory) {
                        return {
                            usedJSHeapSize: performance.memory.usedJSHeapSize,
                            totalJSHeapSize: performance.memory.totalJSHeapSize,
                            jsHeapSizeLimit: performance.memory.jsHeapSizeLimit
                        };
                    }
                    return null;
                """)
                
                if memory_info:
                    memory_info["timestamp"] = time.time()
                    results["memory_usage"].append(memory_info)
                
                # Check chart instances
                chart_count = self.driver.execute_script("""
                    if (window.dashboardManager && window.dashboardManager.charts) {
                        return Object.keys(window.dashboardManager.charts).length;
                    }
                    return 0;
                """)
                
                results["chart_instances"].append({
                    "count": chart_count,
                    "timestamp": time.time()
                })
                
                time.sleep(2)  # Check every 2 seconds
                
        except Exception as e:
            results["errors"].append({
                "type": "monitoring_error",
                "message": str(e),
                "timestamp": time.time()
            })
            
        return results
        
    def analyze_results(self, results):
        """Analyze monitoring results for issues"""
        analysis = {
            "status": "HEALTHY",
            "issues": [],
            "recommendations": [],
            "metrics": {}
        }
        
        # Check for canvas size explosions
        max_height = 0
        for canvas_snapshot in results["canvas_sizes"]:
            for canvas in canvas_snapshot:
                height = int(str(canvas["height"]).replace('px', '') if canvas["height"] else 0)
                max_height = max(max_height, height)
                
                if height > 1000:
                    analysis["issues"].append(f"Canvas {canvas['id']} height explosion: {height}px")
                    analysis["status"] = "CRITICAL"
                    
        analysis["metrics"]["max_canvas_height"] = max_height
        
        # Check console message count
        error_count = len([msg for msg in results["console_messages"] if msg["level"] == "SEVERE"])
        warning_count = len([msg for msg in results["console_messages"] if msg["level"] == "WARNING"])
        
        analysis["metrics"]["console_errors"] = error_count
        analysis["metrics"]["console_warnings"] = warning_count
        
        if error_count > 10:
            analysis["issues"].append(f"High console error count: {error_count}")
            analysis["status"] = "DEGRADED"
            
        # Check memory growth
        if results["memory_usage"]:
            initial_memory = results["memory_usage"][0]["usedJSHeapSize"]
            final_memory = results["memory_usage"][-1]["usedJSHeapSize"]
            memory_growth = final_memory - initial_memory
            
            analysis["metrics"]["memory_growth_mb"] = memory_growth / (1024 * 1024)
            
            if memory_growth > 50 * 1024 * 1024:  # 50MB growth
                analysis["issues"].append(f"High memory growth: {memory_growth / (1024 * 1024):.1f}MB")
                analysis["status"] = "DEGRADED"
                
        # Check chart instance stability
        if results["chart_instances"]:
            chart_counts = [instance["count"] for instance in results["chart_instances"]]
            if len(set(chart_counts)) > 2:  # Chart count keeps changing
                analysis["issues"].append("Unstable chart instance count")
                analysis["status"] = "DEGRADED"
                
        return analysis
        
    def run_validation(self):
        """Run complete validation test"""
        print("🚀 Starting Dashboard Stability Validation")
        print("=" * 50)
        
        # Check API server
        if not self.check_api_server():
            print("❌ API server not running on localhost:5000")
            return False
            
        print("✅ API server is responding")
        
        try:
            # Setup browser
            self.setup_browser()
            print("✅ Browser initialized")
            
            # Monitor dashboard
            results = self.monitor_canvas_sizes(duration_seconds=60)
            
            # Analyze results
            analysis = self.analyze_results(results)
            
            # Save results
            timestamp = int(time.time())
            results_file = f"dashboard_stability_validation_{timestamp}.json"
            
            with open(results_file, 'w') as f:
                json.dump({
                    "results": results,
                    "analysis": analysis
                }, f, indent=2)
                
            print(f"\n📊 Validation Results:")
            print(f"Status: {analysis['status']}")
            print(f"Max Canvas Height: {analysis['metrics'].get('max_canvas_height', 0)}px")
            print(f"Console Errors: {analysis['metrics'].get('console_errors', 0)}")
            print(f"Memory Growth: {analysis['metrics'].get('memory_growth_mb', 0):.1f}MB")
            
            if analysis["issues"]:
                print(f"\n⚠️ Issues Found:")
                for issue in analysis["issues"]:
                    print(f"  - {issue}")
            else:
                print(f"\n✅ No critical issues detected!")
                
            print(f"\n📄 Detailed results saved to: {results_file}")
            
            return analysis["status"] == "HEALTHY"
            
        except Exception as e:
            print(f"❌ Validation failed: {e}")
            return False
            
        finally:
            if self.driver:
                self.driver.quit()

if __name__ == "__main__":
    validator = DashboardStabilityValidator()
    success = validator.run_validation()
    exit(0 if success else 1)
