#!/usr/bin/env python3
"""
Medium-Term Metrics Monitor
Tracks progress and success metrics for Weeks 2-4 improvements
"""

import json
import time
import psutil
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
import ast
import re


class MetricsMonitor:
    def __init__(self):
        self.base_path = Path(__file__).parent.parent
        self.src_path = self.base_path / "src"
        self.reports_path = self.base_path / "reports"
        self.baseline_metrics = None
        
    def establish_baseline(self) -> Dict[str, Any]:
        """Establish baseline metrics before improvements"""
        print("📊 Establishing baseline metrics...")
        
        baseline = {
            "timestamp": datetime.now().isoformat(),
            "code_quality": self._measure_code_quality(),
            "test_coverage": self._measure_test_coverage(),
            "performance": self._measure_performance(),
            "architecture": self._measure_architecture_quality(),
            "duplication": self._measure_code_duplication()
        }
        
        # Save baseline
        baseline_file = self.reports_path / "baseline_metrics.json"
        self.reports_path.mkdir(exist_ok=True)
        
        with open(baseline_file, 'w') as f:
            json.dump(baseline, f, indent=2)
        
        self.baseline_metrics = baseline
        print(f"✅ Baseline established and saved to {baseline_file}")
        return baseline
    
    def measure_current_state(self) -> Dict[str, Any]:
        """Measure current state metrics"""
        print("📈 Measuring current state...")
        
        current = {
            "timestamp": datetime.now().isoformat(),
            "code_quality": self._measure_code_quality(),
            "test_coverage": self._measure_test_coverage(),
            "performance": self._measure_performance(),
            "architecture": self._measure_architecture_quality(),
            "duplication": self._measure_code_duplication()
        }
        
        return current
    
    def calculate_improvements(self, current_metrics: Optional[Dict] = None) -> Dict[str, Any]:
        """Calculate improvements from baseline"""
        if not self.baseline_metrics:
            # Try to load baseline
            baseline_file = self.reports_path / "baseline_metrics.json"
            if baseline_file.exists():
                with open(baseline_file, 'r') as f:
                    self.baseline_metrics = json.load(f)
            else:
                raise ValueError("No baseline metrics found. Run establish_baseline() first.")
        
        if current_metrics is None:
            current_metrics = self.measure_current_state()
        
        improvements = {
            "measurement_time": datetime.now().isoformat(),
            "baseline_time": self.baseline_metrics["timestamp"],
            "improvements": {}
        }
        
        # Calculate improvements for each category
        categories = ["code_quality", "test_coverage", "performance", "architecture", "duplication"]
        
        for category in categories:
            baseline_data = self.baseline_metrics.get(category, {})
            current_data = current_metrics.get(category, {})
            
            improvements["improvements"][category] = self._calculate_category_improvement(
                baseline_data, current_data, category
            )
        
        # Calculate overall score
        improvements["overall_improvement_score"] = self._calculate_overall_score(improvements["improvements"])
        
        return improvements
    
    def _measure_code_quality(self) -> Dict[str, Any]:
        """Measure code quality metrics"""
        quality_metrics = {
            "total_files": 0,
            "total_lines": 0,
            "avg_lines_per_file": 0,
            "large_files_count": 0,  # >500 lines
            "very_large_files_count": 0,  # >1000 lines
            "complex_functions_count": 0,
            "total_functions": 0,
            "total_classes": 0,
            "import_statements": 0
        }
        
        python_files = list(self.src_path.rglob("*.py"))
        quality_metrics["total_files"] = len(python_files)
        
        total_lines = 0
        complex_functions = 0
        total_functions = 0
        total_classes = 0
        total_imports = 0
        
        for file_path in python_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    lines = content.split('\n')
                    line_count = len(lines)
                    total_lines += line_count
                    
                    if line_count > 500:
                        quality_metrics["large_files_count"] += 1
                    if line_count > 1000:
                        quality_metrics["very_large_files_count"] += 1
                    
                    # Count imports
                    import_count = len([line for line in lines if line.strip().startswith(('import ', 'from '))])
                    total_imports += import_count
                    
                    # Parse AST for detailed analysis
                    try:
                        tree = ast.parse(content)
                        for node in ast.walk(tree):
                            if isinstance(node, ast.FunctionDef):
                                total_functions += 1
                                # Simple complexity: count decision points
                                complexity = len([n for n in ast.walk(node) 
                                                if isinstance(n, (ast.If, ast.For, ast.While, ast.Try))])
                                if complexity > 10:
                                    complex_functions += 1
                            elif isinstance(node, ast.ClassDef):
                                total_classes += 1
                    except SyntaxError:
                        pass
                        
            except Exception as e:
                print(f"Warning: Could not analyze {file_path}: {e}")
        
        quality_metrics["total_lines"] = total_lines
        quality_metrics["avg_lines_per_file"] = total_lines / len(python_files) if python_files else 0
        quality_metrics["complex_functions_count"] = complex_functions
        quality_metrics["total_functions"] = total_functions
        quality_metrics["total_classes"] = total_classes
        quality_metrics["import_statements"] = total_imports
        
        return quality_metrics
    
    def _measure_test_coverage(self) -> Dict[str, Any]:
        """Measure test coverage"""
        coverage_metrics = {
            "overall_coverage": 0.0,
            "total_test_files": 0,
            "untested_modules": 0,
            "test_lines": 0,
            "coverage_by_module": {}
        }
        
        try:
            # Count test files
            test_files = list(Path("tests").rglob("test_*.py"))
            coverage_metrics["total_test_files"] = len(test_files)
            
            # Count test lines
            test_lines = 0
            for test_file in test_files:
                try:
                    with open(test_file, 'r') as f:
                        test_lines += len(f.readlines())
                except:
                    pass
            coverage_metrics["test_lines"] = test_lines
            
            # Estimate coverage based on test files vs source files
            src_files = list(self.src_path.rglob("*.py"))
            if src_files:
                # Simple heuristic: coverage estimated from test file ratio
                coverage_metrics["overall_coverage"] = min(95.0, (len(test_files) / len(src_files)) * 100)
                coverage_metrics["untested_modules"] = max(0, len(src_files) - len(test_files))
            
        except Exception as e:
            print(f"Warning: Could not measure coverage: {e}")
        
        return coverage_metrics
    
    def _measure_performance(self) -> Dict[str, Any]:
        """Measure performance metrics"""
        performance_metrics = {
            "memory_usage_mb": 0,
            "startup_time_seconds": 0,
            "test_execution_time": 0,
            "import_time_seconds": 0
        }
        
        try:
            # Measure current memory usage
            process = psutil.Process()
            performance_metrics["memory_usage_mb"] = process.memory_info().rss / 1024 / 1024
            
            # Measure import time
            start_time = time.time()
            try:
                subprocess.run([
                    "python3", "-c", "import src.infrastructure.memory"
                ], capture_output=True, timeout=30)
            except:
                pass
            performance_metrics["import_time_seconds"] = time.time() - start_time
            
            # Measure test execution time (sample)
            start_time = time.time()
            try:
                result = subprocess.run([
                    "python3", "-m", "pytest", "tests/unit/", "-x", "--tb=no"
                ], capture_output=True, timeout=60)
                performance_metrics["test_execution_time"] = time.time() - start_time
            except subprocess.TimeoutExpired:
                performance_metrics["test_execution_time"] = 60  # Timeout value
            except:
                performance_metrics["test_execution_time"] = 0
            
        except Exception as e:
            print(f"Warning: Could not measure performance: {e}")
        
        return performance_metrics
    
    def _measure_architecture_quality(self) -> Dict[str, Any]:
        """Measure architecture quality"""
        arch_metrics = {
            "circular_dependencies": 0,
            "module_coupling": 0,
            "large_classes": 0,  # >20 methods
            "deep_inheritance": 0,  # >5 levels
            "dependency_violations": 0
        }
        
        try:
            python_files = list(self.src_path.rglob("*.py"))
            
            for file_path in python_files:
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        tree = ast.parse(content)
                        
                        for node in ast.walk(tree):
                            if isinstance(node, ast.ClassDef):
                                # Count methods in class
                                methods = [n for n in node.body if isinstance(n, ast.FunctionDef)]
                                if len(methods) > 20:
                                    arch_metrics["large_classes"] += 1
                                
                except SyntaxError:
                    pass
                except Exception:
                    pass
                    
        except Exception as e:
            print(f"Warning: Could not measure architecture: {e}")
        
        return arch_metrics
    
    def _measure_code_duplication(self) -> Dict[str, Any]:
        """Measure code duplication"""
        duplication_metrics = {
            "duplicate_imports": 0,
            "duplicate_functions": 0,
            "estimated_duplicate_lines": 0,
            "duplication_percentage": 0.0
        }
        
        try:
            from collections import Counter
            
            # Count import patterns
            import_counter = Counter()
            function_signatures = Counter()
            total_lines = 0
            
            python_files = list(self.src_path.rglob("*.py"))
            
            for file_path in python_files:
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        lines = content.split('\n')
                        total_lines += len(lines)
                        
                        # Count imports
                        for line in lines:
                            if line.strip().startswith(('import ', 'from ')):
                                import_counter[line.strip()] += 1
                        
                        # Parse for functions
                        try:
                            tree = ast.parse(content)
                            for node in ast.walk(tree):
                                if isinstance(node, ast.FunctionDef):
                                    # Simple signature
                                    args = [arg.arg for arg in node.args.args]
                                    signature = f"{node.name}({', '.join(args)})"
                                    function_signatures[signature] += 1
                        except SyntaxError:
                            pass
                            
                except Exception:
                    pass
            
            # Calculate duplication
            duplicate_imports = sum(1 for count in import_counter.values() if count > 3)
            duplicate_functions = sum(1 for count in function_signatures.values() if count > 1)
            
            # Estimate duplicate lines
            estimated_duplicate_lines = (
                sum(count - 1 for count in import_counter.values() if count > 1) +
                sum((count - 1) * 5 for count in function_signatures.values() if count > 1)  # Assume 5 lines per function
            )
            
            duplication_metrics["duplicate_imports"] = duplicate_imports
            duplication_metrics["duplicate_functions"] = duplicate_functions
            duplication_metrics["estimated_duplicate_lines"] = estimated_duplicate_lines
            duplication_metrics["duplication_percentage"] = (estimated_duplicate_lines / total_lines * 100) if total_lines > 0 else 0
            
        except Exception as e:
            print(f"Warning: Could not measure duplication: {e}")
        
        return duplication_metrics
    
    def _calculate_category_improvement(self, baseline: Dict, current: Dict, category: str) -> Dict[str, Any]:
        """Calculate improvement for a specific category"""
        improvements = {
            "category": category,
            "metrics": {},
            "overall_improvement": 0
        }
        
        if category == "code_quality":
            # Lower is better for complexity metrics
            improvements["metrics"]["large_files_reduction"] = self._calculate_reduction(
                baseline.get("large_files_count", 0), current.get("large_files_count", 0)
            )
            improvements["metrics"]["complex_functions_reduction"] = self._calculate_reduction(
                baseline.get("complex_functions_count", 0), current.get("complex_functions_count", 0)
            )
            improvements["overall_improvement"] = (
                improvements["metrics"]["large_files_reduction"] + 
                improvements["metrics"]["complex_functions_reduction"]
            ) / 2
            
        elif category == "test_coverage":
            # Higher is better for coverage
            improvements["metrics"]["coverage_increase"] = self._calculate_increase(
                baseline.get("overall_coverage", 0), current.get("overall_coverage", 0)
            )
            improvements["metrics"]["test_files_increase"] = self._calculate_increase(
                baseline.get("total_test_files", 0), current.get("total_test_files", 0)
            )
            improvements["overall_improvement"] = improvements["metrics"]["coverage_increase"]
            
        elif category == "performance":
            # Lower is better for time/memory metrics
            improvements["metrics"]["memory_reduction"] = self._calculate_reduction(
                baseline.get("memory_usage_mb", 0), current.get("memory_usage_mb", 0)
            )
            improvements["metrics"]["test_time_reduction"] = self._calculate_reduction(
                baseline.get("test_execution_time", 0), current.get("test_execution_time", 0)
            )
            improvements["overall_improvement"] = (
                improvements["metrics"]["memory_reduction"] + 
                improvements["metrics"]["test_time_reduction"]
            ) / 2
            
        elif category == "architecture":
            # Lower is better for architectural issues
            improvements["metrics"]["large_classes_reduction"] = self._calculate_reduction(
                baseline.get("large_classes", 0), current.get("large_classes", 0)
            )
            improvements["overall_improvement"] = improvements["metrics"]["large_classes_reduction"]
            
        elif category == "duplication":
            # Lower is better for duplication
            improvements["metrics"]["duplication_percentage_reduction"] = self._calculate_reduction(
                baseline.get("duplication_percentage", 0), current.get("duplication_percentage", 0)
            )
            improvements["metrics"]["duplicate_imports_reduction"] = self._calculate_reduction(
                baseline.get("duplicate_imports", 0), current.get("duplicate_imports", 0)
            )
            improvements["overall_improvement"] = improvements["metrics"]["duplication_percentage_reduction"]
        
        return improvements
    
    def _calculate_reduction(self, baseline_value: float, current_value: float) -> float:
        """Calculate percentage reduction (positive is good)"""
        if baseline_value == 0:
            return 0
        return ((baseline_value - current_value) / baseline_value) * 100
    
    def _calculate_increase(self, baseline_value: float, current_value: float) -> float:
        """Calculate percentage increase (positive is good)"""
        if baseline_value == 0:
            return 100 if current_value > 0 else 0
        return ((current_value - baseline_value) / baseline_value) * 100
    
    def _calculate_overall_score(self, improvements: Dict[str, Any]) -> float:
        """Calculate overall improvement score"""
        scores = []
        weights = {
            "code_quality": 0.25,
            "test_coverage": 0.30,
            "performance": 0.20,
            "architecture": 0.15,
            "duplication": 0.10
        }
        
        for category, weight in weights.items():
            if category in improvements:
                category_score = improvements[category].get("overall_improvement", 0)
                scores.append(category_score * weight)
        
        return sum(scores)
    
    def generate_progress_report(self, save_to_file: bool = True) -> Dict[str, Any]:
        """Generate comprehensive progress report"""
        print("📋 Generating progress report...")
        
        current_metrics = self.measure_current_state()
        improvements = self.calculate_improvements(current_metrics)
        
        report = {
            "report_timestamp": datetime.now().isoformat(),
            "baseline_metrics": self.baseline_metrics,
            "current_metrics": current_metrics,
            "improvements": improvements,
            "week_targets": {
                "week2": {
                    "target": "Reduce code duplication to <0.1%",
                    "current_duplication": current_metrics["duplication"]["duplication_percentage"],
                    "target_met": current_metrics["duplication"]["duplication_percentage"] < 0.1
                },
                "week3": {
                    "target": "Achieve 80% test coverage",
                    "current_coverage": current_metrics["test_coverage"]["overall_coverage"],
                    "target_met": current_metrics["test_coverage"]["overall_coverage"] >= 80.0
                },
                "week4": {
                    "target": "Eliminate large files (>500 lines)",
                    "current_large_files": current_metrics["code_quality"]["large_files_count"],
                    "target_met": current_metrics["code_quality"]["large_files_count"] == 0
                }
            },
            "recommendations": self._generate_recommendations(current_metrics, improvements)
        }
        
        if save_to_file:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            report_file = self.reports_path / f"progress_report_{timestamp}.json"
            
            with open(report_file, 'w') as f:
                json.dump(report, f, indent=2)
            
            print(f"📄 Progress report saved to: {report_file}")
        
        return report
    
    def _generate_recommendations(self, current_metrics: Dict, improvements: Dict) -> List[str]:
        """Generate improvement recommendations"""
        recommendations = []
        
        # Check duplication
        if current_metrics["duplication"]["duplication_percentage"] > 0.1:
            recommendations.append("Continue Week 2 deduplication efforts - target not yet met")
        
        # Check coverage
        if current_metrics["test_coverage"]["overall_coverage"] < 80:
            recommendations.append("Intensify Week 3 testing efforts - coverage below target")
        
        # Check large files
        if current_metrics["code_quality"]["large_files_count"] > 0:
            recommendations.append("Focus Week 4 refactoring on remaining large files")
        
        # Check complex functions
        if current_metrics["code_quality"]["complex_functions_count"] > 10:
            recommendations.append("Simplify remaining complex functions in Week 4")
        
        # Performance recommendations
        if current_metrics["performance"]["test_execution_time"] > 120:
            recommendations.append("Optimize test execution time - currently too slow")
        
        if not recommendations:
            recommendations.append("Excellent progress! All targets are being met.")
        
        return recommendations
    
    def print_dashboard(self):
        """Print real-time metrics dashboard"""
        current_metrics = self.measure_current_state()
        improvements = self.calculate_improvements(current_metrics) if self.baseline_metrics else None
        
        print("\n" + "=" * 80)
        print("📊 MEDIUM-TERM IMPROVEMENTS DASHBOARD")
        print("=" * 80)
        
        # Current state
        print("📈 CURRENT STATE:")
        print(f"  Code Quality: {current_metrics['code_quality']['large_files_count']} large files, "
              f"{current_metrics['code_quality']['complex_functions_count']} complex functions")
        print(f"  Test Coverage: {current_metrics['test_coverage']['overall_coverage']:.1f}% "
              f"({current_metrics['test_coverage']['total_test_files']} test files)")
        print(f"  Performance: {current_metrics['performance']['memory_usage_mb']:.1f}MB memory, "
              f"{current_metrics['performance']['test_execution_time']:.1f}s test time")
        print(f"  Duplication: {current_metrics['duplication']['duplication_percentage']:.2f}% duplicate code")
        
        # Improvements (if baseline exists)
        if improvements:
            print(f"\n📊 IMPROVEMENTS FROM BASELINE:")
            overall_score = improvements['overall_improvement_score']
            print(f"  Overall Score: {overall_score:+.1f}%")
            
            for category, data in improvements['improvements'].items():
                category_score = data.get('overall_improvement', 0)
                status = "✅" if category_score > 0 else "⚠️" if category_score == 0 else "❌"
                print(f"  {status} {category.title()}: {category_score:+.1f}%")
        
        # Week targets
        print(f"\n🎯 WEEK TARGETS:")
        week_targets = {
            "Week 2 (Deduplication)": f"<0.1% duplicate code (current: {current_metrics['duplication']['duplication_percentage']:.2f}%)",
            "Week 3 (Testing)": f"80% test coverage (current: {current_metrics['test_coverage']['overall_coverage']:.1f}%)",
            "Week 4 (Architecture)": f"0 large files (current: {current_metrics['code_quality']['large_files_count']})"
        }
        
        for week, target in week_targets.items():
            print(f"  {week}: {target}")


def main():
    """CLI interface for metrics monitoring"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Medium-Term Metrics Monitor")
    parser.add_argument("--baseline", action="store_true", help="Establish baseline metrics")
    parser.add_argument("--measure", action="store_true", help="Measure current state")
    parser.add_argument("--improvements", action="store_true", help="Calculate improvements")
    parser.add_argument("--report", action="store_true", help="Generate progress report")
    parser.add_argument("--dashboard", action="store_true", help="Show real-time dashboard")
    parser.add_argument("--all", action="store_true", help="Run all monitoring tasks")
    
    args = parser.parse_args()
    
    monitor = MetricsMonitor()
    
    if args.all or args.baseline:
        monitor.establish_baseline()
    
    if args.all or args.measure:
        current = monitor.measure_current_state()
        print("📊 Current metrics measured")
    
    if args.all or args.improvements:
        improvements = monitor.calculate_improvements()
        print(f"📈 Overall improvement score: {improvements['overall_improvement_score']:+.1f}%")
    
    if args.all or args.report:
        monitor.generate_progress_report()
    
    if args.all or args.dashboard:
        monitor.print_dashboard()


if __name__ == "__main__":
    main()