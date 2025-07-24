"""
Validation History Persistence
Tracks validation results over time for trend analysis and reporting.
"""

import hashlib
import json
import os
import time
from collections import defaultdict
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional


class ValidationHistoryTracker:
    """Tracks and persists validation results for trend analysis."""

    def __init__(self, root_path: Optional[Path] = None):
        """Initialize validation history tracker."""
        self.root_path = root_path or Path(".")
        self.history_dir = self.root_path / ".validation_history"
        self.history_dir.mkdir(exist_ok=True)

        # Main history file
        self.history_file = self.history_dir / "validation_history.jsonl"

        # Summary and trend files
        self.trends_file = self.history_dir / "validation_trends.json"
        self.metrics_file = self.history_dir / "validation_metrics.json"

        # Log rotation settings
        self.max_file_size = 10 * 1024 * 1024  # 10MB max file size
        self.max_backup_files = 5  # Keep 5 rotated files

    def record_validation_result(
        self,
        result: Dict[str, Any],
        phase_timings: Dict[str, float],
        issues: List[Any],
        overall_success: bool,
        git_commit: Optional[str] = None,
    ) -> str:
        """
        Record a validation result for historical tracking.

        Args:
            result: Validation results by category
            phase_timings: Timing data for each validation phase
            issues: List of validation issues found
            overall_success: Whether validation passed overall
            git_commit: Git commit hash if available

        Returns:
            Unique ID for this validation run
        """
        timestamp = datetime.now()
        run_id = self._generate_run_id(timestamp)

        # Get git info if available
        git_info = (
            self._get_git_info() if git_commit is None else {"commit": git_commit}
        )

        # Categorize issues
        issues_by_category = defaultdict(list)
        issues_by_severity = defaultdict(int)

        for issue in issues:
            category = getattr(issue, "category", "unknown")
            severity = getattr(issue, "severity", "unknown")

            # Convert severity to string if it's an enum
            if hasattr(severity, "value"):
                severity_str = severity.value
            else:
                severity_str = str(severity)

            issues_by_category[category].append(
                {
                    "type": str(getattr(issue, "issue_type", "unknown")),
                    "severity": severity_str,
                    "file_path": getattr(issue, "file_path", ""),
                    "line": getattr(issue, "line", 0),
                    "message": getattr(issue, "message", ""),
                }
            )
            issues_by_severity[severity_str] += 1

        # Calculate code metrics
        code_metrics = self._calculate_code_metrics()

        # Create validation record
        validation_record = {
            "run_id": run_id,
            "timestamp": timestamp.isoformat(),
            "overall_success": overall_success,
            "git_info": git_info,
            "phase_results": result,
            "phase_timings": phase_timings,
            "total_time": sum(phase_timings.values()),
            "issues_summary": {
                "total_issues": len(issues),
                "by_severity": dict(issues_by_severity),
                "by_category": {
                    cat: len(issues) for cat, issues in issues_by_category.items()
                },
            },
            "issues_detail": dict(issues_by_category),
            "code_metrics": code_metrics,
            "environment": self._get_environment_info(),
        }

        # Check if rotation is needed before writing
        self._rotate_if_needed()

        # Append to history file (JSONL format for efficient streaming)
        with open(self.history_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(validation_record, default=self._json_serializer) + "\n")

        # Update trends and metrics
        self._update_trends()
        self._update_metrics()

        print(f"📊 Validation result recorded with ID: {run_id}")

        return run_id

    def _generate_run_id(self, timestamp: datetime) -> str:
        """Generate unique run ID."""
        # Create hash from timestamp and some entropy
        hash_input = f"{timestamp.isoformat()}{os.getpid()}{time.time()}"
        return hashlib.md5(hash_input.encode()).hexdigest()[:12]

    def _get_git_info(self) -> Dict[str, Any]:
        """Get git information if available."""
        git_info = {"commit": None, "branch": None, "author": None}

        try:
            import subprocess

            # Get commit hash
            result = subprocess.run(
                ["git", "rev-parse", "HEAD"],
                capture_output=True,
                text=True,
                cwd=self.root_path,
            )
            if result.returncode == 0:
                git_info["commit"] = result.stdout.strip()

            # Get branch name
            result = subprocess.run(
                ["git", "rev-parse", "--abbrev-ref", "HEAD"],
                capture_output=True,
                text=True,
                cwd=self.root_path,
            )
            if result.returncode == 0:
                git_info["branch"] = result.stdout.strip()

            # Get author of last commit
            result = subprocess.run(
                ["git", "log", "-1", "--pretty=format:%an"],
                capture_output=True,
                text=True,
                cwd=self.root_path,
            )
            if result.returncode == 0:
                git_info["author"] = result.stdout.strip()

        except Exception:
            pass

        return git_info

    def _calculate_code_metrics(self) -> Dict[str, Any]:
        """Calculate basic code metrics."""
        metrics = {
            "total_files": 0,
            "total_lines": 0,
            "python_files": 0,
            "python_lines": 0,
        }

        try:
            for file_path in self.root_path.rglob("*"):
                if file_path.is_file() and not any(
                    part.startswith(".") for part in file_path.parts
                ):
                    metrics["total_files"] += 1

                    if file_path.suffix == ".py":
                        metrics["python_files"] += 1
                        try:
                            with open(file_path, "r", encoding="utf-8") as f:
                                lines = f.readlines()
                                metrics["total_lines"] += len(lines)
                                metrics["python_lines"] += len(lines)
                        except Exception:
                            continue
                    else:
                        try:
                            with open(file_path, "r", encoding="utf-8") as f:
                                lines = f.readlines()
                                metrics["total_lines"] += len(lines)
                        except Exception:
                            continue

        except Exception:
            pass

        return metrics

    def _get_environment_info(self) -> Dict[str, Any]:
        """Get environment information."""
        import platform
        import sys

        return {
            "python_version": sys.version,
            "platform": platform.platform(),
            "hostname": platform.node(),
            "user": os.environ.get("USER", os.environ.get("USERNAME", "unknown")),
        }

    def _update_trends(self):
        """Update trend analysis data."""
        trends = self._calculate_trends()

        with open(self.trends_file, "w", encoding="utf-8") as f:
            json.dump(trends, f, indent=2, default=str)

    def _update_metrics(self):
        """Update aggregated metrics."""
        metrics = self._calculate_aggregated_metrics()

        with open(self.metrics_file, "w", encoding="utf-8") as f:
            json.dump(metrics, f, indent=2, default=str)

    def _calculate_trends(self) -> Dict[str, Any]:
        """Calculate trend data from validation history."""
        if not self.history_file.exists():
            return {"trends": {}, "last_updated": datetime.now().isoformat()}

        # Read recent history (last 30 days)
        cutoff_date = datetime.now() - timedelta(days=30)
        recent_records = []

        try:
            with open(self.history_file, "r", encoding="utf-8") as f:
                for line in f:
                    try:
                        record = json.loads(line.strip())
                        record_date = datetime.fromisoformat(record["timestamp"])
                        if record_date >= cutoff_date:
                            recent_records.append(record)
                    except Exception:
                        continue
        except Exception:
            return {"trends": {}, "last_updated": datetime.now().isoformat()}

        if not recent_records:
            return {"trends": {}, "last_updated": datetime.now().isoformat()}

        # Sort by timestamp
        recent_records.sort(key=lambda x: x["timestamp"])

        # Calculate trends
        trends = {
            "success_rate": {"current": 0, "trend": "stable", "data_points": []},
            "average_time": {"current": 0, "trend": "stable", "data_points": []},
            "issue_count": {"current": 0, "trend": "stable", "data_points": []},
            "phase_performance": {},
            "most_common_issues": [],
            "improvement_suggestions": [],
        }

        # Calculate success rate trend
        success_count = sum(1 for r in recent_records if r["overall_success"])
        trends["success_rate"]["current"] = (
            success_count / len(recent_records) if recent_records else 0
        )

        # Calculate average time trend
        total_times = [r["total_time"] for r in recent_records]
        trends["average_time"]["current"] = (
            sum(total_times) / len(total_times) if total_times else 0
        )

        # Calculate issue count trend
        issue_counts = [r["issues_summary"]["total_issues"] for r in recent_records]
        trends["issue_count"]["current"] = (
            sum(issue_counts) / len(issue_counts) if issue_counts else 0
        )

        # Analyze phase performance
        for phase in [
            "syntax",
            "dependencies",
            "structure",
            "performance",
            "ai_patterns",
        ]:
            phase_times = [r["phase_timings"].get(phase, 0) for r in recent_records]
            if phase_times:
                trends["phase_performance"][phase] = {
                    "average_time": sum(phase_times) / len(phase_times),
                    "trend": self._calculate_trend_direction(phase_times),
                }

        # Find most common issues
        issue_frequency = defaultdict(int)
        for record in recent_records:
            for category, issues in record["issues_detail"].items():
                for issue in issues:
                    issue_key = f"{category}:{issue.get('type', 'unknown')}"
                    issue_frequency[issue_key] += 1

        trends["most_common_issues"] = [
            {"issue": issue, "frequency": freq}
            for issue, freq in sorted(
                issue_frequency.items(), key=lambda x: x[1], reverse=True
            )[:10]
        ]

        # Generate improvement suggestions
        trends["improvement_suggestions"] = self._generate_improvement_suggestions(
            recent_records
        )

        return {
            "trends": trends,
            "last_updated": datetime.now().isoformat(),
            "data_period": "last_30_days",
            "total_records": len(recent_records),
        }

    def _calculate_trend_direction(self, data_points: List[float]) -> str:
        """Calculate trend direction from data points."""
        if len(data_points) < 2:
            return "stable"

        # Simple linear trend calculation
        recent_avg = sum(data_points[-5:]) / min(5, len(data_points))
        older_avg = (
            sum(data_points[:-5]) / max(1, len(data_points) - 5)
            if len(data_points) > 5
            else recent_avg
        )

        if recent_avg > older_avg * 1.1:
            return "increasing"
        elif recent_avg < older_avg * 0.9:
            return "decreasing"
        else:
            return "stable"

    def _generate_improvement_suggestions(self, records: List[Dict]) -> List[str]:
        """Generate improvement suggestions based on validation history."""
        suggestions = []

        if not records:
            return suggestions

        # Analyze common failure patterns
        failed_records = [r for r in records if not r["overall_success"]]
        if len(failed_records) > len(records) * 0.3:  # More than 30% failure rate
            suggestions.append("Consider implementing more rigorous pre-commit hooks")

        # Analyze slow phases
        avg_times = defaultdict(list)
        for record in records:
            for phase, time_taken in record["phase_timings"].items():
                avg_times[phase].append(time_taken)

        for phase, times in avg_times.items():
            avg_time = sum(times) / len(times)
            if avg_time > 60:  # More than 1 minute
                suggestions.append(
                    f"Consider optimizing {phase} validation phase (avg: {avg_time:.1f}s)"
                )

        # Analyze issue patterns
        issue_categories = defaultdict(int)
        for record in records:
            for category, count in record["issues_summary"]["by_category"].items():
                issue_categories[category] += count

        if issue_categories.get("dependencies", 0) > len(records) * 5:
            suggestions.append(
                "High dependency issues detected - consider dependency cleanup"
            )

        if issue_categories.get("ai_analysis", 0) > len(records) * 10:
            suggestions.append(
                "Many code quality issues found - consider refactoring effort"
            )

        return suggestions

    def _calculate_aggregated_metrics(self) -> Dict[str, Any]:
        """Calculate aggregated metrics from all validation history."""
        if not self.history_file.exists():
            return {"metrics": {}, "last_updated": datetime.now().isoformat()}

        all_records = []
        try:
            with open(self.history_file, "r", encoding="utf-8") as f:
                for line in f:
                    try:
                        record = json.loads(line.strip())
                        all_records.append(record)
                    except Exception:
                        continue
        except Exception:
            return {"metrics": {}, "last_updated": datetime.now().isoformat()}

        if not all_records:
            return {"metrics": {}, "last_updated": datetime.now().isoformat()}

        # Calculate aggregate metrics
        total_runs = len(all_records)
        successful_runs = sum(1 for r in all_records if r["overall_success"])

        metrics = {
            "total_validation_runs": total_runs,
            "successful_runs": successful_runs,
            "success_rate": successful_runs / total_runs if total_runs > 0 else 0,
            "average_duration": (
                sum(r["total_time"] for r in all_records) / total_runs
                if total_runs > 0
                else 0
            ),
            "total_issues_found": sum(
                r["issues_summary"]["total_issues"] for r in all_records
            ),
            "first_run": (
                min(r["timestamp"] for r in all_records) if all_records else None
            ),
            "last_run": (
                max(r["timestamp"] for r in all_records) if all_records else None
            ),
            "phase_statistics": {},
            "issue_statistics": {},
            "git_statistics": {},
        }

        # Phase statistics
        phase_stats = defaultdict(
            lambda: {"total_time": 0, "run_count": 0, "avg_time": 0}
        )
        for record in all_records:
            for phase, time_taken in record["phase_timings"].items():
                phase_stats[phase]["total_time"] += time_taken
                phase_stats[phase]["run_count"] += 1

        for phase, stats in phase_stats.items():
            stats["avg_time"] = (
                stats["total_time"] / stats["run_count"]
                if stats["run_count"] > 0
                else 0
            )
            metrics["phase_statistics"][phase] = stats

        # Issue statistics
        issue_stats = defaultdict(int)
        severity_stats = defaultdict(int)
        for record in all_records:
            for category, count in record["issues_summary"]["by_category"].items():
                issue_stats[category] += count
            for severity, count in record["issues_summary"]["by_severity"].items():
                severity_stats[severity] += count

        metrics["issue_statistics"] = {
            "by_category": dict(issue_stats),
            "by_severity": dict(severity_stats),
        }

        # Git statistics
        branches = defaultdict(int)
        authors = defaultdict(int)
        for record in all_records:
            git_info = record.get("git_info", {})
            if git_info.get("branch"):
                branches[git_info["branch"]] += 1
            if git_info.get("author"):
                authors[git_info["author"]] += 1

        metrics["git_statistics"] = {
            "branches": dict(branches),
            "authors": dict(authors),
        }

        return {"metrics": metrics, "last_updated": datetime.now().isoformat()}

    def _json_serializer(self, obj):
        """Custom JSON serializer to handle enum types and other non-serializable objects."""
        if hasattr(obj, "value"):  # Handle enum types
            return obj.value
        elif hasattr(obj, "isoformat"):  # Handle datetime objects
            return obj.isoformat()
        elif hasattr(obj, "__dict__"):  # Handle objects with __dict__
            return obj.__dict__
        else:
            return str(obj)  # Fallback to string representation

    def get_validation_report(self, days: int = 7) -> Dict[str, Any]:
        """Generate validation report for specified number of days."""
        cutoff_date = datetime.now() - timedelta(days=days)
        recent_records = []

        if self.history_file.exists():
            try:
                with open(self.history_file, "r", encoding="utf-8") as f:
                    for line in f:
                        try:
                            record = json.loads(line.strip())
                            record_date = datetime.fromisoformat(record["timestamp"])
                            if record_date >= cutoff_date:
                                recent_records.append(record)
                        except Exception:
                            continue
            except Exception:
                pass

        if not recent_records:
            return {
                "period": f"last_{days}_days",
                "message": "No validation data available for this period",
            }

        successful_runs = [r for r in recent_records if r["overall_success"]]
        failed_runs = [r for r in recent_records if not r["overall_success"]]

        return {
            "period": f"last_{days}_days",
            "summary": {
                "total_runs": len(recent_records),
                "successful_runs": len(successful_runs),
                "failed_runs": len(failed_runs),
                "success_rate": (
                    len(successful_runs) / len(recent_records) if recent_records else 0
                ),
                "average_duration": (
                    sum(r["total_time"] for r in recent_records) / len(recent_records)
                    if recent_records
                    else 0
                ),
            },
            "trends": self._load_trends(),
            "recommendations": self._generate_improvement_suggestions(recent_records),
        }

    def _load_trends(self) -> Dict[str, Any]:
        """Load trends data from file."""
        if self.trends_file.exists():
            try:
                with open(self.trends_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        return {}

    def cleanup_old_records(self, days_to_keep: int = 90):
        """Clean up validation records older than specified days."""
        if not self.history_file.exists():
            return

        cutoff_date = datetime.now() - timedelta(days=days_to_keep)
        temp_file = self.history_file.with_suffix(".tmp")

        records_kept = 0
        records_removed = 0

        try:
            with open(self.history_file, "r", encoding="utf-8") as infile:
                with open(temp_file, "w", encoding="utf-8") as outfile:
                    for line in infile:
                        try:
                            record = json.loads(line.strip())
                            record_date = datetime.fromisoformat(record["timestamp"])

                            if record_date >= cutoff_date:
                                outfile.write(line)
                                records_kept += 1
                            else:
                                records_removed += 1
                        except Exception:
                            # Keep malformed records to be safe
                            outfile.write(line)
                            records_kept += 1

            # Replace original file with cleaned version
            temp_file.replace(self.history_file)

            print(
                f"📅 Cleaned validation history: kept {records_kept} records, removed {records_removed} old records"
            )

        except Exception as e:
            print(f"⚠️  Failed to cleanup validation history: {e}")
            # Clean up temp file if it exists
            if temp_file.exists():
                temp_file.unlink()

    def _rotate_if_needed(self):
        """Rotate log files if the current file exceeds size limit."""
        if not self.history_file.exists():
            return

        # Check if rotation is needed
        current_size = self.history_file.stat().st_size
        if current_size < self.max_file_size:
            return

        try:
            print(
                f"📦 Rotating validation history log ({current_size / 1024 / 1024:.1f}MB)"
            )

            # Rotate existing backup files
            for i in range(self.max_backup_files - 1, 0, -1):
                old_backup = self.history_dir / f"validation_history.jsonl.{i}"
                new_backup = self.history_dir / f"validation_history.jsonl.{i + 1}"

                if old_backup.exists():
                    if new_backup.exists():
                        new_backup.unlink()  # Remove oldest backup
                    old_backup.rename(new_backup)

            # Move current file to .1 backup
            backup_file = self.history_dir / "validation_history.jsonl.1"
            if backup_file.exists():
                backup_file.unlink()
            self.history_file.rename(backup_file)

            print(
                "📦 Log rotation complete. Old log saved as validation_history.jsonl.1"
            )

        except Exception as e:
            print(f"⚠️  Failed to rotate validation history: {e}")
