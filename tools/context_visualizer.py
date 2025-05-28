#!/usr/bin/env python3
"""
Step 3.9 Implementation: Visualise Context Coverage

This module implements context coverage visualization as specified in Step 3.9
of the system implementation plan. It creates heatmaps and reports showing
context usage patterns by task and topic frequency.

Features:
- CSV reports showing topic usage frequency by task
- HTML heatmap visualizations with interactive charts
- Context coverage analysis across all tasks
- Integration with Steps 3.7 and 3.8 context tracking data

Usage:
    from tools.context_visualizer import generate_context_coverage_report

    # Generate both CSV and HTML reports
    generate_context_coverage_report()

    # Generate specific format
    generate_context_coverage_report(format="csv")
    generate_context_coverage_report(format="html")

CLI Usage:
    python tools/context_visualizer.py --format csv
    python tools/context_visualizer.py --format html
    python tools/context_visualizer.py --format both
"""

import csv
import json
import logging
import os
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# Import from Step 3.7 context tracking
try:
    from .context_tracker import analyze_context_usage, get_all_context_logs
except ImportError:
    from context_tracker import analyze_context_usage, get_all_context_logs

logger = logging.getLogger(__name__)


def analyze_context_coverage() -> Dict[str, Any]:
    """
    Analyze context coverage patterns across all tasks.

    Returns:
        Dict[str, Any]: Comprehensive coverage analysis
    """
    try:
        # Get all context logs from Step 3.7
        all_logs = get_all_context_logs()

        if not all_logs:
            logger.warning(
                "No context logs found. Run some tasks with context tracking first.")
            return {
                "error": "No context data available",
                "tasks_analyzed": 0,
                "topics": {},
                "coverage_matrix": []
            }

        # Build coverage matrix: task_id -> topic -> usage_count
        coverage_matrix = defaultdict(lambda: defaultdict(int))
        topic_frequency = Counter()
        document_frequency = Counter()
        agent_frequency = Counter()
        task_context_lengths = {}

        for task_id, log_data in all_logs.items():
            agent_role = log_data.get("agent_role", "unknown")
            context_length = log_data.get("context_length", 0)

            task_context_lengths[task_id] = context_length
            agent_frequency[agent_role] += 1

            # Track topic usage for this task
            for topic in log_data.get("context_used", []):
                coverage_matrix[task_id][topic] += 1
                topic_frequency[topic] += 1

            # Track document usage
            for doc_source in log_data.get("document_sources", []):
                source = doc_source.get("source", "unknown")
                document_frequency[source] += 1

        # Get all unique topics across all tasks
        all_topics = set()
        for task_topics in coverage_matrix.values():
            all_topics.update(task_topics.keys())
        all_topics = sorted(list(all_topics))

        # Create normalized coverage matrix
        coverage_data = []
        for task_id in sorted(coverage_matrix.keys()):
            task_row = {
                "task_id": task_id,
                "agent_role": all_logs[task_id].get("agent_role", "unknown"),
                "context_length": task_context_lengths.get(task_id, 0),
                "topics": {}
            }
            for topic in all_topics:
                task_row["topics"][topic] = coverage_matrix[task_id].get(
                    topic, 0)
            coverage_data.append(task_row)

        return {
            "generated_at": datetime.now().isoformat(),
            "step_3_9_implementation": "Visualise Context Coverage",
            "tasks_analyzed": len(all_logs),
            "unique_topics": len(all_topics),
            "unique_documents": len(document_frequency),
            "coverage_matrix": coverage_data,
            "topic_frequency": dict(
                topic_frequency.most_common()),
            "document_frequency": dict(
                document_frequency.most_common(10)),
            "agent_frequency": dict(agent_frequency),
            "all_topics": all_topics,
            "summary_stats": {
                "avg_topics_per_task": sum(
                    len(
                        log.get(
                            "context_used",
                            [])) for log in all_logs.values()) /
                len(all_logs),
                "avg_context_length": sum(
                    task_context_lengths.values()) /
                len(task_context_lengths) if task_context_lengths else 0,
                "most_active_topic": topic_frequency.most_common(1)[0] if topic_frequency else (
                    "none",
                    0),
                "most_active_agent": agent_frequency.most_common(1)[0] if agent_frequency else (
                    "none",
                    0)}}

    except Exception as e:
        logger.error(f"Failed to analyze context coverage: {e}")
        return {
            "error": str(e),
            "tasks_analyzed": 0,
            "topics": {},
            "coverage_matrix": []
        }


def generate_csv_report(
        coverage_data: Dict[str, Any], output_path: str = "reports/context-coverage.csv") -> bool:
    """
    Generate CSV report of context usage patterns.

    Args:
        coverage_data (Dict[str, Any]): Coverage analysis data
        output_path (str): Path for CSV output

    Returns:
        bool: True if successful
    """
    try:
        # Create reports directory
        report_file = Path(output_path)
        report_file.parent.mkdir(parents=True, exist_ok=True)

        # Write CSV with topic usage frequency
        with open(report_file, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)

            # Write header
            writer.writerow(
                ['Topic', 'Usage Count', 'Percentage', 'Tasks Using'])

            # Write topic frequency data
            topic_frequency = coverage_data.get("topic_frequency", {})
            total_usage = sum(topic_frequency.values()
                              ) if topic_frequency else 1

            for topic, count in topic_frequency.items():
                percentage = (count / total_usage) * \
                    100 if total_usage > 0 else 0

                # Find tasks using this topic
                tasks_using = []
                for task_data in coverage_data.get("coverage_matrix", []):
                    if task_data.get("topics", {}).get(topic, 0) > 0:
                        tasks_using.append(task_data["task_id"])

                writer.writerow([
                    topic,
                    count,
                    f"{percentage:.1f}%",
                    "; ".join(tasks_using)
                ])

            # Add summary section
            writer.writerow([])  # Empty row
            writer.writerow(['=== SUMMARY ==='])
            writer.writerow(
                ['Total Tasks Analyzed', coverage_data.get("tasks_analyzed", 0)])
            writer.writerow(
                ['Unique Topics', coverage_data.get("unique_topics", 0)])
            writer.writerow(
                ['Unique Documents', coverage_data.get("unique_documents", 0)])

            summary_stats = coverage_data.get("summary_stats", {})
            writer.writerow(
                ['Avg Topics per Task', f"{summary_stats.get('avg_topics_per_task', 0):.1f}"])
            writer.writerow(
                ['Avg Context Length', f"{summary_stats.get('avg_context_length', 0):.0f}"])

            most_active_topic = summary_stats.get(
                'most_active_topic', ('none', 0))
            writer.writerow(
                ['Most Active Topic', f"{most_active_topic[0]} ({most_active_topic[1]} uses)"])

            most_active_agent = summary_stats.get(
                'most_active_agent', ('none', 0))
            writer.writerow(
                ['Most Active Agent', f"{most_active_agent[0]} ({most_active_agent[1]} tasks)"])

        logger.info(f"CSV context coverage report generated: {output_path}")
        return True

    except Exception as e:
        logger.error(f"Failed to generate CSV report: {e}")
        return False


def generate_html_report(
        coverage_data: Dict[str, Any], output_path: str = "reports/context-coverage.html") -> bool:
    """
    Generate interactive HTML heatmap of context usage patterns.

    Args:
        coverage_data (Dict[str, Any]): Coverage analysis data
        output_path (str): Path for HTML output

    Returns:
        bool: True if successful
    """
    try:
        # Create reports directory
        report_file = Path(output_path)
        report_file.parent.mkdir(parents=True, exist_ok=True)

        # Generate HTML content
        html_content = generate_html_content(coverage_data)

        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(html_content)

        logger.info(f"HTML context coverage report generated: {output_path}")
        return True

    except Exception as e:
        logger.error(f"Failed to generate HTML report: {e}")
        return False


def generate_html_content(coverage_data: Dict[str, Any]) -> str:
    """Generate HTML content for context coverage visualization."""

    # Prepare data for JavaScript
    coverage_matrix = coverage_data.get("coverage_matrix", [])
    all_topics = coverage_data.get("all_topics", [])
    topic_frequency = coverage_data.get("topic_frequency", {})
    summary_stats = coverage_data.get("summary_stats", {})

    # Create heatmap data
    heatmap_data = []
    for i, task_data in enumerate(coverage_matrix):
        for j, topic in enumerate(all_topics):
            usage_count = task_data.get("topics", {}).get(topic, 0)
            if usage_count > 0:
                heatmap_data.append([j, i, usage_count])

    # Create bar chart data for topic frequency
    topic_labels = list(topic_frequency.keys())
    topic_values = list(topic_frequency.values())

    html_template = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Context Coverage Analysis - Step 3.9</title>
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            padding: 30px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        .header {{
            text-align: center;
            margin-bottom: 30px;
            padding-bottom: 20px;
            border-bottom: 2px solid #e0e0e0;
        }}
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin: 30px 0;
        }}
        .stat-card {{
            background: #f8f9fa;
            padding: 20px;
            border-radius: 6px;
            text-align: center;
            border-left: 4px solid #007bff;
        }}
        .stat-value {{
            font-size: 2em;
            font-weight: bold;
            color: #007bff;
        }}
        .stat-label {{
            color: #666;
            margin-top: 5px;
        }}
        .chart-container {{
            margin: 30px 0;
            padding: 20px;
            background: #fafafa;
            border-radius: 6px;
        }}
        .chart-title {{
            font-size: 1.2em;
            font-weight: bold;
            margin-bottom: 15px;
            color: #333;
        }}
        .footer {{
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid #e0e0e0;
            text-align: center;
            color: #666;
            font-size: 0.9em;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Context Coverage Analysis</h1>
            <h2>Step 3.9: Visualise Context Coverage</h2>
            <p>Generated at: {coverage_data.get('generated_at', 'unknown')}</p>
        </div>

        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-value">{coverage_data.get('tasks_analyzed', 0)}</div>
                <div class="stat-label">Tasks Analyzed</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{coverage_data.get('unique_topics', 0)}</div>
                <div class="stat-label">Unique Topics</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{summary_stats.get('avg_topics_per_task', 0):.1f}</div>
                <div class="stat-label">Avg Topics/Task</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{summary_stats.get('avg_context_length', 0):.0f}</div>
                <div class="stat-label">Avg Context Length</div>
            </div>
        </div>

        <div class="chart-container">
            <div class="chart-title">Context Usage Heatmap (Task vs Topic)</div>
            <div id="heatmap" style="height: 500px;"></div>
        </div>

        <div class="chart-container">
            <div class="chart-title">Topic Usage Frequency</div>
            <div id="topicChart" style="height: 400px;"></div>
        </div>

        <div class="chart-container">
            <div class="chart-title">Agent Usage Distribution</div>
            <div id="agentChart" style="height: 300px;"></div>
        </div>

        <div class="footer">
            <p>AI System - Phase 3 Knowledge Context Implementation</p>
            <p>Context coverage analysis based on Steps 3.7 and 3.8 tracking data</p>
        </div>
    </div>

    <script>
        // Heatmap data
        const heatmapData = [{json.dumps(heatmap_data)}];
        const taskLabels = {json.dumps([task["task_id"] for task in coverage_matrix])};
        const topicLabels = {json.dumps(all_topics)};

        // Create heatmap
        const heatmapTrace = {{
            z: heatmapData.map(d => d[2]),
            x: heatmapData.map(d => topicLabels[d[0]]),
            y: heatmapData.map(d => taskLabels[d[1]]),
            type: 'scatter',
            mode: 'markers',
            marker: {{
                size: heatmapData.map(d => Math.max(10, d[2] * 20)),
                color: heatmapData.map(d => d[2]),
                colorscale: 'Blues',
                showscale: true,
                colorbar: {{
                    title: 'Usage Count'
                }}
            }},
            text: heatmapData.map(d => `Task: ${{taskLabels[d[1]]}}\\nTopic: ${{topicLabels[d[0]]}}\\nUsage: ${{d[2]}}`),
            hovertemplate: '%{{text}}<extra></extra>'
        }};

        const heatmapLayout = {{
            xaxis: {{
                title: 'Context Topics',
                tickangle: -45
            }},
            yaxis: {{
                title: 'Tasks'
            }},
            margin: {{ t: 50, l: 100, r: 50, b: 150 }}
        }};

        Plotly.newPlot('heatmap', [heatmapTrace], heatmapLayout);

        // Topic frequency bar chart
        const topicTrace = {{
            x: {json.dumps(topic_labels)},
            y: {json.dumps(topic_values)},
            type: 'bar',
            marker: {{
                color: 'rgba(0, 123, 255, 0.7)',
                line: {{
                    color: 'rgba(0, 123, 255, 1)',
                    width: 1
                }}
            }}
        }};

        const topicLayout = {{
            xaxis: {{
                title: 'Context Topics',
                tickangle: -45
            }},
            yaxis: {{
                title: 'Usage Count'
            }},
            margin: {{ t: 30, l: 50, r: 30, b: 120 }}
        }};

        Plotly.newPlot('topicChart', [topicTrace], topicLayout);

        // Agent distribution pie chart
        const agentData = {json.dumps(coverage_data.get("agent_frequency", {}))};
        const agentTrace = {{
            labels: Object.keys(agentData),
            values: Object.values(agentData),
            type: 'pie',
            marker: {{
                colors: ['#007bff', '#28a745', '#ffc107', '#dc3545', '#6f42c1', '#20c997']
            }}
        }};

        const agentLayout = {{
            margin: {{ t: 30, l: 30, r: 30, b: 30 }}
        }};

        Plotly.newPlot('agentChart', [agentTrace], agentLayout);
    </script>
</body>
</html>
"""

    return html_template


def generate_json_report(coverage_data: dict, output_path: str) -> bool:
    """Generate a JSON file with all stats and chart data for dynamic HTML reports."""
    try:
        # Prepare the JSON structure expected by the dynamic HTML
        json_data = {
            "generated_at": coverage_data.get(
                "generated_at",
                datetime.now().isoformat()),
            "stats": {
                "tasks_analyzed": coverage_data.get(
                    "tasks_analyzed",
                    0),
                "unique_topics": coverage_data.get(
                    "unique_topics",
                    0),
                "avg_topics_per_task": coverage_data.get(
                    "summary_stats",
                    {}).get(
                    "avg_topics_per_task",
                    0),
                "avg_context_length": coverage_data.get(
                    "summary_stats",
                    {}).get(
                    "avg_context_length",
                    0),
            },
            "heatmapData": [],
            "taskLabels": [],
            "topicLabels": [],
            "topicFrequency": {
                "labels": [],
                "values": []},
            "agentDistribution": coverage_data.get(
                "agent_frequency",
                {})}
        # Heatmap data
        coverage_matrix = coverage_data.get("coverage_matrix", [])
        all_topics = coverage_data.get("all_topics", [])
        json_data["taskLabels"] = [task["task_id"] for task in coverage_matrix]
        json_data["topicLabels"] = all_topics
        for i, task_data in enumerate(coverage_matrix):
            for j, topic in enumerate(all_topics):
                usage_count = task_data.get("topics", {}).get(topic, 0)
                if usage_count > 0:
                    json_data["heatmapData"].append([j, i, usage_count])
        # Topic frequency
        topic_frequency = coverage_data.get("topic_frequency", {})
        json_data["topicFrequency"]["labels"] = list(topic_frequency.keys())
        json_data["topicFrequency"]["values"] = list(topic_frequency.values())
        # Write JSON file
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(json_data, f, indent=2)
        logger.info(f"JSON context coverage data generated: {output_path}")
        return True
    except Exception as e:
        logger.error(f"Failed to generate JSON report: {e}")
        return False


def generate_context_coverage_report(
        format: str = "both",
        csv_path: str = "reports/context-coverage.csv",
        html_path: str = "reports/context-coverage.html",
        json_path: str = None) -> bool:
    """
    Generate context coverage visualization reports.
    Now also generates a JSON file for dynamic HTML reports.
    """
    try:
        logger.info(
            f"Generating context coverage report(s) in {format} format...")

        # Analyze context coverage using Step 3.7 data
        coverage_data = analyze_context_coverage()

        if "error" in coverage_data:
            logger.error(
                f"Context coverage analysis failed: {coverage_data['error']}")
            return False

        success = True

        if format in ["csv", "both"]:
            csv_success = generate_csv_report(coverage_data, csv_path)
            success = success and csv_success

        if format in ["html", "both"]:
            html_success = generate_html_report(coverage_data, html_path)
            success = success and html_success

        # Always generate JSON for dynamic HTML
        if not json_path:
            # Default: same as HTML but .json
            json_path = os.path.splitext(html_path)[0] + ".json"
        json_success = generate_json_report(coverage_data, json_path)
        success = success and json_success

        if success:
            logger.info(
                f"✅ Step 3.9 context coverage visualization completed successfully!")
            print(f"\n📊 Context Coverage Analysis Summary:")
            print(f"   Tasks analyzed: {coverage_data['tasks_analyzed']}")
            print(f"   Unique topics: {coverage_data['unique_topics']}")
            print(f"   Unique documents: {coverage_data['unique_documents']}")

            summary_stats = coverage_data.get("summary_stats", {})
            print(
                f"   Avg topics per task: {
                    summary_stats.get(
                        'avg_topics_per_task',
                        0):.1f}")
            print(
                f"   Most active topic: {
                    summary_stats.get(
                        'most_active_topic', ('none', 0))[0]}")

            if format in ["csv", "both"]:
                print(f"   📄 CSV report: {csv_path}")
            if format in ["html", "both"]:
                print(f"   🌐 HTML report: {html_path}")
            print(f"   📦 JSON data: {json_path}")

        return success

    except Exception as e:
        logger.error(f"Failed to generate context coverage report: {e}")
        return False


# CLI interface for Step 3.9 context coverage visualization
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Step 3.9 Context Coverage Visualization")
    parser.add_argument(
        "--format",
        choices=[
            "csv",
            "html",
            "both"],
        default="both",
        help="Output format for the report")
    parser.add_argument("--csv-path", default="reports/context-coverage.csv",
                        help="Output path for CSV report")
    parser.add_argument("--html-path", default="reports/context-coverage.html",
                        help="Output path for HTML report")
    parser.add_argument("--verbose", "-v", action="store_true",
                        help="Enable verbose logging")

    args = parser.parse_args()

    # Setup logging
    if args.verbose:
        logging.basicConfig(level=logging.INFO,
                            format='%(levelname)s: %(message)s')

    print("🎯 Step 3.9: Visualise Context Coverage")
    print("=" * 50)

    success = generate_context_coverage_report(
        format=args.format,
        csv_path=args.csv_path,
        html_path=args.html_path
    )

    if success:
        print("\n✅ Context coverage visualization completed successfully!")
    else:
        print("\n❌ Context coverage visualization failed!")
        exit(1)
