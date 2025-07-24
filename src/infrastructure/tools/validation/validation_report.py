#!/usr/bin/env python3
"""
Validation Report Generator
Generate reports and trend analysis from validation history.
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict

# Add src to path for proper imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from src.infrastructure.tools.validation.persistence.validation_history import (
    ValidationHistoryTracker,
)


def print_validation_summary(report: Dict[str, Any]):
    """Print validation summary report."""
    summary = report.get("summary", {})

    print(f"📊 VALIDATION REPORT - {report['period'].upper().replace('_', ' ')}")
    print("=" * 60)

    if "message" in report:
        print(f"ℹ️  {report['message']}")
        return

    # Summary statistics
    print("📈 Summary Statistics:")
    print(f"   Total Runs: {summary.get('total_runs', 0)}")
    print(f"   Successful: {summary.get('successful_runs', 0)}")
    print(f"   Failed: {summary.get('failed_runs', 0)}")
    print(f"   Success Rate: {summary.get('success_rate', 0):.1%}")
    print(f"   Avg Duration: {summary.get('average_duration', 0):.1f}s")

    # Trends
    trends = report.get("trends", {}).get("trends", {})
    if trends:
        print("\n📊 Trends:")

        success_trend = trends.get("success_rate", {})
        if success_trend:
            print(
                f"   Success Rate: {success_trend.get('current', 0):.1%} ({success_trend.get('trend', 'stable')})"
            )

        time_trend = trends.get("average_time", {})
        if time_trend:
            print(
                f"   Avg Time: {time_trend.get('current', 0):.1f}s ({time_trend.get('trend', 'stable')})"
            )

        issue_trend = trends.get("issue_count", {})
        if issue_trend:
            print(
                f"   Avg Issues: {issue_trend.get('current', 0):.1f} ({issue_trend.get('trend', 'stable')})"
            )

    # Phase performance
    phase_perf = trends.get("phase_performance", {})
    if phase_perf:
        print("\n⚡ Phase Performance:")
        for phase, stats in phase_perf.items():
            avg_time = stats.get("average_time", 0)
            trend = stats.get("trend", "stable")
            emoji = (
                "📈"
                if trend == "increasing"
                else "📉" if trend == "decreasing" else "➡️"
            )
            print(f"   {phase.title()}: {avg_time:.1f}s {emoji} {trend}")

    # Common issues
    common_issues = trends.get("most_common_issues", [])
    if common_issues:
        print("\n🔍 Most Common Issues:")
        for i, issue_data in enumerate(common_issues[:5], 1):
            issue = issue_data.get("issue", "Unknown")
            freq = issue_data.get("frequency", 0)
            print(f"   {i}. {issue}: {freq} occurrences")

    # Recommendations
    recommendations = report.get("recommendations", [])
    if recommendations:
        print("\n💡 Improvement Suggestions:")
        for i, rec in enumerate(recommendations, 1):
            print(f"   {i}. {rec}")

    print("=" * 60)


def print_detailed_trends(tracker: ValidationHistoryTracker):
    """Print detailed trend analysis."""
    # Load trends data
    trends_data = tracker._load_trends()

    if not trends_data or not trends_data.get("trends"):
        print("📊 No trend data available")
        return

    trends = trends_data["trends"]

    print("📈 DETAILED TREND ANALYSIS")
    print("=" * 60)
    print(f"Data Period: {trends_data.get('data_period', 'Unknown')}")
    print(f"Total Records: {trends_data.get('total_records', 0)}")
    print(f"Last Updated: {trends_data.get('last_updated', 'Unknown')}")

    # Success rate details
    success_rate = trends.get("success_rate", {})
    print("\n✅ Success Rate Analysis:")
    print(f"   Current Rate: {success_rate.get('current', 0):.1%}")
    print(f"   Trend: {success_rate.get('trend', 'stable').title()}")

    # Performance details
    avg_time = trends.get("average_time", {})
    print("\n⏱️  Performance Analysis:")
    print(f"   Average Time: {avg_time.get('current', 0):.1f}s")
    print(f"   Trend: {avg_time.get('trend', 'stable').title()}")

    # Issue analysis
    issue_count = trends.get("issue_count", {})
    print("\n🐛 Issue Analysis:")
    print(f"   Average Issues: {issue_count.get('current', 0):.1f}")
    print(f"   Trend: {issue_count.get('trend', 'stable').title()}")

    # Phase performance breakdown
    phase_perf = trends.get("phase_performance", {})
    if phase_perf:
        print("\n🔧 Phase Performance Breakdown:")
        for phase, stats in sorted(phase_perf.items()):
            avg_time = stats.get("average_time", 0)
            trend = stats.get("trend", "stable")
            print(f"   {phase.title():<15}: {avg_time:>6.1f}s - {trend}")

    # Most common issues
    common_issues = trends.get("most_common_issues", [])
    if common_issues:
        print("\n🔍 Top Issues (by frequency):")
        for i, issue_data in enumerate(common_issues[:10], 1):
            issue = issue_data.get("issue", "Unknown")
            freq = issue_data.get("frequency", 0)
            print(f"   {i:2d}. {issue:<40} ({freq:>3d}x)")

    print("=" * 60)


def print_metrics(tracker: ValidationHistoryTracker):
    """Print aggregated metrics."""
    # Load metrics data
    if tracker.metrics_file.exists():
        try:
            with open(tracker.metrics_file, "r", encoding="utf-8") as f:
                metrics_data = json.load(f)
        except Exception:
            print("❌ Failed to load metrics data")
            return
    else:
        print("📊 No metrics data available")
        return

    metrics = metrics_data.get("metrics", {})

    print("📊 VALIDATION METRICS (ALL TIME)")
    print("=" * 60)
    print(f"Last Updated: {metrics_data.get('last_updated', 'Unknown')}")

    # Overall statistics
    print("\n📈 Overall Statistics:")
    print(f"   Total Validation Runs: {metrics.get('total_validation_runs', 0)}")
    print(f"   Successful Runs: {metrics.get('successful_runs', 0)}")
    print(f"   Overall Success Rate: {metrics.get('success_rate', 0):.1%}")
    print(f"   Average Duration: {metrics.get('average_duration', 0):.1f}s")
    print(f"   Total Issues Found: {metrics.get('total_issues_found', 0)}")

    # Time range
    first_run = metrics.get("first_run")
    last_run = metrics.get("last_run")
    if first_run and last_run:
        print(f"   Data Range: {first_run[:10]} to {last_run[:10]}")

    # Phase statistics
    phase_stats = metrics.get("phase_statistics", {})
    if phase_stats:
        print("\n⚡ Phase Performance (All Time):")
        for phase, stats in sorted(phase_stats.items()):
            avg_time = stats.get("avg_time", 0)
            run_count = stats.get("run_count", 0)
            total_time = stats.get("total_time", 0)
            print(
                f"   {phase.title():<15}: {avg_time:>6.1f}s avg ({run_count} runs, {total_time:.1f}s total)"
            )

    # Issue statistics
    issue_stats = metrics.get("issue_statistics", {})
    if issue_stats:
        by_category = issue_stats.get("by_category", {})
        by_severity = issue_stats.get("by_severity", {})

        if by_category:
            print("\n🐛 Issues by Category:")
            for category, count in sorted(
                by_category.items(), key=lambda x: x[1], reverse=True
            ):
                print(f"   {category.title():<20}: {count:>4d}")

        if by_severity:
            print("\n🚨 Issues by Severity:")
            for severity, count in sorted(
                by_severity.items(), key=lambda x: x[1], reverse=True
            ):
                print(f"   {severity.title():<20}: {count:>4d}")

    # Git statistics
    git_stats = metrics.get("git_statistics", {})
    if git_stats:
        branches = git_stats.get("branches", {})
        authors = git_stats.get("authors", {})

        if branches:
            print("\n🌿 Validation by Branch:")
            for branch, count in sorted(
                branches.items(), key=lambda x: x[1], reverse=True
            )[:5]:
                print(f"   {branch:<20}: {count:>3d} runs")

        if authors:
            print("\n👥 Validation by Author:")
            for author, count in sorted(
                authors.items(), key=lambda x: x[1], reverse=True
            )[:5]:
                print(f"   {author:<20}: {count:>3d} runs")

    print("=" * 60)


def cleanup_old_data(tracker: ValidationHistoryTracker, days: int):
    """Clean up old validation data."""
    print(f"🧹 Cleaning up validation data older than {days} days...")
    tracker.cleanup_old_records(days)
    print("✅ Cleanup completed")


def main():
    """Main entry point for validation reporting."""
    parser = argparse.ArgumentParser(
        description="Generate validation reports and trend analysis",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Show 7-day summary report
  python validation_report.py --summary

  # Show 30-day summary  
  python validation_report.py --summary --days 30

  # Show detailed trends
  python validation_report.py --trends

  # Show all-time metrics
  python validation_report.py --metrics

  # Clean up data older than 90 days
  python validation_report.py --cleanup --days 90
        """,
    )

    parser.add_argument(
        "--summary", "-s", action="store_true", help="Show validation summary report"
    )

    parser.add_argument(
        "--trends", "-t", action="store_true", help="Show detailed trend analysis"
    )

    parser.add_argument(
        "--metrics", "-m", action="store_true", help="Show all-time validation metrics"
    )

    parser.add_argument(
        "--cleanup", "-c", action="store_true", help="Clean up old validation data"
    )

    parser.add_argument(
        "--days",
        "-d",
        type=int,
        default=7,
        help="Number of days for reports (default: 7) or cleanup retention (default: 90)",
    )

    parser.add_argument(
        "--root",
        "-r",
        type=Path,
        default=Path("."),
        help="Root path of the project (default: current directory)",
    )

    args = parser.parse_args()

    # Initialize tracker
    tracker = ValidationHistoryTracker(args.root)

    # Default to summary if no specific action is requested
    if not any([args.summary, args.trends, args.metrics, args.cleanup]):
        args.summary = True

    try:
        if args.cleanup:
            cleanup_days = (
                args.days if args.days != 7 else 90
            )  # Use 90 as default for cleanup
            cleanup_old_data(tracker, cleanup_days)

        if args.summary:
            report = tracker.get_validation_report(args.days)
            print_validation_summary(report)

        if args.trends:
            print_detailed_trends(tracker)

        if args.metrics:
            print_metrics(tracker)

    except KeyboardInterrupt:
        print("\n⚠️  Report generation interrupted")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error generating report: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
