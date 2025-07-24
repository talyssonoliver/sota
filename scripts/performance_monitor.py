#!/usr/bin/env python3
"""
Performance Monitor
Tracks and reports system performance metrics for optimization
"""

import json
import psutil
import subprocess
import time
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Dict, List


@dataclass
class PerformanceMetrics:
    """Performance metrics snapshot."""
    timestamp: str
    command: str
    duration: float
    exit_code: int
    cpu_percent: float
    memory_mb: float
    disk_io_mb: float
    test_count: int = 0
    tests_passed: int = 0
    tests_failed: int = 0


class PerformanceMonitor:
    """Monitors and tracks performance metrics."""
    
    def __init__(self, root_path: Path = None):
        self.root_path = root_path or Path.cwd()
        self.metrics_file = self.root_path / "performance_metrics.json"
        self.colors = {
            'GREEN': '\033[0;32m', 
            'YELLOW': '\033[1;33m',
            'BLUE': '\033[0;34m',
            'RED': '\033[0;31m',
            'NC': '\033[0m'
        }
    
    def print_colored(self, message: str, color: str = 'NC') -> None:
        """Print colored message."""
        print(f"{self.colors.get(color, '')}{message}{self.colors['NC']}")
    
    def get_system_metrics(self) -> Dict[str, float]:
        """Get current system metrics."""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk_io = psutil.disk_io_counters()
            
            return {
                'cpu_percent': cpu_percent,
                'memory_mb': memory.used / (1024 * 1024),
                'disk_io_mb': (disk_io.read_bytes + disk_io.write_bytes) / (1024 * 1024) if disk_io else 0
            }
        except Exception:
            return {'cpu_percent': 0, 'memory_mb': 0, 'disk_io_mb': 0}
    
    def parse_test_output(self, output: str) -> Dict[str, int]:
        """Parse pytest output for test metrics."""
        test_count = 0
        tests_passed = 0
        tests_failed = 0
        
        try:
            lines = output.split('\n')
            for line in lines:
                if 'passed' in line and 'failed' in line:
                    # Look for lines like "5 failed, 23 passed in 2.34s"
                    parts = line.split()
                    for i, part in enumerate(parts):
                        if part == 'passed' and i > 0:
                            tests_passed = int(parts[i-1])
                        elif part == 'failed' and i > 0:
                            tests_failed = int(parts[i-1])
                elif line.strip().endswith(' passed'):
                    # Look for lines like "50 passed in 1.23s"
                    parts = line.split()
                    if len(parts) >= 2 and parts[1] == 'passed':
                        tests_passed = int(parts[0])
        except (ValueError, IndexError):
            pass
        
        test_count = tests_passed + tests_failed
        return {
            'test_count': test_count,
            'tests_passed': tests_passed,
            'tests_failed': tests_failed
        }
    
    def run_with_monitoring(self, command: List[str]) -> PerformanceMetrics:
        """Run a command while monitoring performance."""
        start_metrics = self.get_system_metrics()
        start_time = time.time()
        
        try:
            # Run the command
            result = subprocess.run(
                command,
                cwd=self.root_path,
                capture_output=True,
                text=True,
                timeout=1800  # 30 minute timeout
            )
            
            end_time = time.time()
            end_metrics = self.get_system_metrics()
            
            # Parse test results if it's a pytest command
            test_metrics = {}
            if 'pytest' in ' '.join(command):
                test_metrics = self.parse_test_output(result.stdout + result.stderr)
            
            # Calculate metrics
            metrics = PerformanceMetrics(
                timestamp=datetime.now().isoformat(),
                command=' '.join(command),
                duration=end_time - start_time,
                exit_code=result.returncode,
                cpu_percent=max(start_metrics['cpu_percent'], end_metrics['cpu_percent']),
                memory_mb=max(start_metrics['memory_mb'], end_metrics['memory_mb']),
                disk_io_mb=end_metrics['disk_io_mb'] - start_metrics['disk_io_mb'],
                **test_metrics
            )
            
            return metrics
            
        except subprocess.TimeoutExpired:
            end_time = time.time()
            return PerformanceMetrics(
                timestamp=datetime.now().isoformat(),
                command=' '.join(command),
                duration=end_time - start_time,
                exit_code=-1,
                cpu_percent=0,
                memory_mb=0,
                disk_io_mb=0
            )
    
    def save_metrics(self, metrics: PerformanceMetrics) -> None:
        """Save metrics to file."""
        try:
            # Load existing metrics
            existing_metrics = []
            if self.metrics_file.exists():
                with open(self.metrics_file) as f:
                    existing_metrics = json.load(f)
            
            # Add new metrics
            existing_metrics.append(asdict(metrics))
            
            # Keep only last 100 entries
            if len(existing_metrics) > 100:
                existing_metrics = existing_metrics[-100:]
            
            # Save back to file
            with open(self.metrics_file, 'w') as f:
                json.dump(existing_metrics, f, indent=2)
                
        except Exception as e:
            self.print_colored(f"Warning: Could not save metrics: {e}", 'YELLOW')
    
    def display_metrics(self, metrics: PerformanceMetrics) -> None:
        """Display performance metrics."""
        self.print_colored("\n📊 Performance Metrics:", 'BLUE')
        self.print_colored(f"  ⏱️  Duration: {metrics.duration:.1f}s", 'GREEN' if metrics.duration < 60 else 'YELLOW')
        self.print_colored(f"  🖥️  CPU: {metrics.cpu_percent:.1f}%", 'GREEN' if metrics.cpu_percent < 80 else 'YELLOW')
        self.print_colored(f"  💾  Memory: {metrics.memory_mb:.0f}MB", 'GREEN' if metrics.memory_mb < 2000 else 'YELLOW')
        
        if metrics.test_count > 0:
            success_rate = (metrics.tests_passed / metrics.test_count) * 100
            self.print_colored(f"  🧪  Tests: {metrics.tests_passed}/{metrics.test_count} passed ({success_rate:.1f}%)", 
                             'GREEN' if success_rate == 100 else 'YELLOW')
        
        if metrics.exit_code == 0:
            self.print_colored("  ✅  Status: Success", 'GREEN')
        else:
            self.print_colored(f"  ❌  Status: Failed (exit code: {metrics.exit_code})", 'RED')
    
    def get_performance_trends(self, command_filter: str = None) -> Dict[str, float]:
        """Get performance trends over time."""
        if not self.metrics_file.exists():
            return {}
        
        try:
            with open(self.metrics_file) as f:
                all_metrics = json.load(f)
            
            # Filter by command if specified
            if command_filter:
                filtered_metrics = [m for m in all_metrics if command_filter in m.get('command', '')]
            else:
                filtered_metrics = all_metrics
            
            if len(filtered_metrics) < 2:
                return {}
            
            # Calculate trends (last 10 vs previous 10)
            recent = filtered_metrics[-10:]
            previous = filtered_metrics[-20:-10] if len(filtered_metrics) >= 20 else filtered_metrics[:-10]
            
            if not previous:
                return {}
            
            avg_recent_duration = sum(m['duration'] for m in recent) / len(recent)
            avg_previous_duration = sum(m['duration'] for m in previous) / len(previous)
            
            duration_trend = ((avg_recent_duration - avg_previous_duration) / avg_previous_duration) * 100
            
            return {
                'duration_trend_percent': duration_trend,
                'recent_avg_duration': avg_recent_duration,
                'previous_avg_duration': avg_previous_duration,
                'sample_size': len(filtered_metrics)
            }
            
        except Exception:
            return {}
    
    def display_trends(self, command_filter: str = None) -> None:
        """Display performance trends."""
        trends = self.get_performance_trends(command_filter)
        
        if not trends:
            self.print_colored("📈 No trend data available yet", 'BLUE')
            return
        
        self.print_colored(f"\n📈 Performance Trends (last {trends['sample_size']} runs):", 'BLUE')
        
        duration_trend = trends['duration_trend_percent']
        if abs(duration_trend) < 5:
            trend_color = 'GREEN'
            trend_symbol = "➡️"
            trend_desc = "stable"
        elif duration_trend < 0:
            trend_color = 'GREEN' 
            trend_symbol = "⬇️"
            trend_desc = "improving"
        else:
            trend_color = 'YELLOW'
            trend_symbol = "⬆️"
            trend_desc = "degrading"
        
        self.print_colored(f"  {trend_symbol} Duration: {duration_trend:+.1f}% ({trend_desc})", trend_color)
        self.print_colored(f"  ⏱️  Recent avg: {trends['recent_avg_duration']:.1f}s", 'BLUE')
        self.print_colored(f"  ⏱️  Previous avg: {trends['previous_avg_duration']:.1f}s", 'BLUE')


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Performance monitor for commands")
    parser.add_argument("command", nargs='+', help="Command to run and monitor")
    parser.add_argument("--trends", action="store_true", help="Show performance trends")
    parser.add_argument("--filter", help="Filter trends by command pattern")
    
    args = parser.parse_args()
    
    monitor = PerformanceMonitor()
    
    if args.trends:
        monitor.display_trends(args.filter)
        return
    
    # Run command with monitoring
    monitor.print_colored(f"🚀 Running with performance monitoring: {' '.join(args.command)}", 'BLUE')
    
    metrics = monitor.run_with_monitoring(args.command)
    monitor.display_metrics(metrics)
    monitor.save_metrics(metrics)
    
    # Show trends if we have data
    monitor.display_trends(' '.join(args.command))
    
    # Exit with same code as monitored command
    exit(metrics.exit_code)


if __name__ == "__main__":
    main()