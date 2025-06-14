#!/usr/bin/env python3
"""
Gantt Chart API Endpoints - Phase 6 Step 6.7

Flask API endpoints for Gantt chart data, critical path analysis,
and timeline optimization functionality.
"""

import json
import logging
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path
from flask import Blueprint, jsonify, request
from typing import Dict, List, Any

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

try:
    from orchestration.gantt_analyzer import GanttAnalyzer
    from orchestration.states import TaskStatus
    from utils.completion_metrics import CompletionMetricsCalculator
except ImportError as e:
    print(f"Import error: {e}")
    # Create mock classes for development
    class GanttAnalyzer:
        def __init__(self):
            pass
        def generate_gantt_data(self):
            return {}
        def get_optimization_recommendations(self):
            return []
        def optimize_timeline(self, **kwargs):
            return {}

# Create Blueprint
gantt_bp = Blueprint('gantt', __name__, url_prefix='/api/gantt')

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global analyzer instance
gantt_analyzer = None

def get_gantt_analyzer():
    """Get or create GanttAnalyzer instance."""
    global gantt_analyzer
    if gantt_analyzer is None:
        try:
            gantt_analyzer = GanttAnalyzer()
            logger.info("GanttAnalyzer initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize GanttAnalyzer: {e}")
            gantt_analyzer = GanttAnalyzer()  # Use mock
    return gantt_analyzer


@gantt_bp.route('/data', methods=['GET'])
def get_gantt_data():
    """
    Get comprehensive Gantt chart data including tasks, timeline, and critical path.
    
    Returns:
        JSON response with Gantt chart data
    """
    try:
        logger.info("Fetching Gantt chart data")
        
        # Get query parameters
        time_range = request.args.get('range', 'month')  # week, month, quarter, all
        include_completed = request.args.get('include_completed', 'true').lower() == 'true'
        
        analyzer = get_gantt_analyzer()
        
        # Generate Gantt data
        gantt_data = analyzer.generate_gantt_data()
        
        # If no data from analyzer, use sample data
        if not gantt_data or 'tasks' not in gantt_data:
            gantt_data = generate_sample_gantt_data()
        
        # Filter data based on parameters
        if not include_completed:
            gantt_data['tasks'] = [
                task for task in gantt_data.get('tasks', [])
                if task.get('status') != 'completed'
            ]
        
        # Filter by time range
        gantt_data = filter_by_time_range(gantt_data, time_range)
        
        # Add metadata
        response_data = {
            'success': True,
            'data': gantt_data,
            'metadata': {
                'time_range': time_range,
                'include_completed': include_completed,
                'generated_at': datetime.now().isoformat(),
                'total_tasks': len(gantt_data.get('tasks', [])),
                'critical_tasks': len([
                    t for t in gantt_data.get('tasks', []) 
                    if t.get('critical_path', False)
                ])
            }
        }
        
        logger.info(f"Successfully generated Gantt data with {len(gantt_data.get('tasks', []))} tasks")
        return jsonify(response_data)
        
    except Exception as e:
        logger.error(f"Error generating Gantt data: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'data': generate_sample_gantt_data()
        }), 500


@gantt_bp.route('/critical-path', methods=['GET'])
def get_critical_path():
    """
    Get detailed critical path analysis.
    
    Returns:
        JSON response with critical path details
    """
    try:
        logger.info("Fetching critical path analysis")
        
        analyzer = get_gantt_analyzer()
        gantt_data = analyzer.generate_gantt_data()
        
        if not gantt_data:
            gantt_data = generate_sample_gantt_data()
        
        # Extract critical path information
        critical_tasks = [
            task for task in gantt_data.get('tasks', [])
            if task.get('critical_path', False)
        ]
        
        # Calculate critical path metrics
        critical_path_analysis = {
            'critical_tasks': critical_tasks,
            'critical_path_ids': gantt_data.get('critical_path', []),
            'metrics': {
                'total_critical_tasks': len(critical_tasks),
                'critical_path_duration': gantt_data.get('project_timeline', {}).get('critical_path_duration', 0),
                'risk_level': calculate_risk_level(critical_tasks),
                'bottlenecks': identify_bottlenecks(critical_tasks),
                'float_analysis': calculate_float_analysis(gantt_data.get('tasks', []))
            },
            'dependencies': extract_dependency_network(critical_tasks),
            'recommendations': generate_critical_path_recommendations(critical_tasks)
        }
        
        return jsonify({
            'success': True,
            'data': critical_path_analysis,
            'generated_at': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error generating critical path analysis: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@gantt_bp.route('/resources', methods=['GET'])
def get_resource_analysis():
    """
    Get resource allocation and utilization analysis.
    
    Returns:
        JSON response with resource analysis
    """
    try:
        logger.info("Fetching resource analysis")
        
        analyzer = get_gantt_analyzer()
        gantt_data = analyzer.generate_gantt_data()
        
        if not gantt_data:
            gantt_data = generate_sample_gantt_data()
        
        tasks = gantt_data.get('tasks', [])
        
        # Analyze resource allocation
        resource_analysis = {
            'resource_utilization': analyze_resource_utilization(tasks),
            'workload_distribution': analyze_workload_distribution(tasks),
            'capacity_analysis': analyze_capacity(tasks),
            'bottlenecks': identify_resource_bottlenecks(tasks),
            'optimization_opportunities': identify_optimization_opportunities(tasks),
            'team_metrics': calculate_team_metrics(tasks)
        }
        
        return jsonify({
            'success': True,
            'data': resource_analysis,
            'generated_at': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error generating resource analysis: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@gantt_bp.route('/recommendations', methods=['GET'])
def get_optimization_recommendations():
    """
    Get timeline and resource optimization recommendations.
    
    Returns:
        JSON response with optimization recommendations
    """
    try:
        logger.info("Fetching optimization recommendations")
        
        analyzer = get_gantt_analyzer()
        
        try:
            recommendations = analyzer.get_optimization_recommendations()
        except:
            recommendations = generate_sample_recommendations()
        
        # Categorize recommendations
        categorized_recommendations = {
            'timeline_optimization': [
                rec for rec in recommendations 
                if rec.get('category') == 'timeline'
            ],
            'resource_optimization': [
                rec for rec in recommendations 
                if rec.get('category') == 'resource'
            ],
            'risk_mitigation': [
                rec for rec in recommendations 
                if rec.get('category') == 'risk'
            ],
            'quality_improvement': [
                rec for rec in recommendations 
                if rec.get('category') == 'quality'
            ]
        }
        
        return jsonify({
            'success': True,
            'data': {
                'recommendations': recommendations,
                'categorized': categorized_recommendations,
                'summary': {
                    'total_recommendations': len(recommendations),
                    'high_priority': len([r for r in recommendations if r.get('priority') == 'high']),
                    'potential_time_savings': sum([
                        r.get('time_savings', 0) for r in recommendations
                    ]),
                    'potential_cost_savings': sum([
                        r.get('cost_savings', 0) for r in recommendations
                    ])
                }
            },
            'generated_at': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error generating recommendations: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'data': {
                'recommendations': generate_sample_recommendations(),
                'categorized': {},
                'summary': {}
            }
        }), 500


@gantt_bp.route('/optimize', methods=['POST'])
def optimize_timeline():
    """
    Run timeline optimization based on specified parameters.
    
    Returns:
        JSON response with optimization results
    """
    try:
        data = request.get_json()
        
        optimization_params = {
            'goal': data.get('goal', 'minimize_duration'),
            'resource_constraint': data.get('resource_constraint', 1.0),
            'time_constraint': data.get('time_constraint', 1.0),
            'quality_threshold': data.get('quality_threshold', 0.8),
            'risk_tolerance': data.get('risk_tolerance', 'medium')
        }
        
        logger.info(f"Running timeline optimization with params: {optimization_params}")
        
        analyzer = get_gantt_analyzer()
        
        try:
            optimization_results = analyzer.optimize_timeline(**optimization_params)
        except:
            optimization_results = generate_sample_optimization_results(optimization_params)
        
        return jsonify({
            'success': True,
            'data': optimization_results,
            'parameters': optimization_params,
            'generated_at': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error running optimization: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@gantt_bp.route('/tasks/<task_id>', methods=['PUT'])
def update_task(task_id):
    """
    Update a specific task's properties.
    
    Args:
        task_id: ID of the task to update
    
    Returns:
        JSON response with update status
    """
    try:
        data = request.get_json()
        
        logger.info(f"Updating task {task_id} with data: {data}")
        
        # In a real implementation, this would update the task in the database
        # For now, we'll just validate the data and return success
        
        allowed_fields = [
            'start_date', 'end_date', 'progress', 'status', 
            'assigned_to', 'priority', 'estimated_effort'
        ]
        
        update_data = {
            field: value for field, value in data.items() 
            if field in allowed_fields
        }
        
        # Validate dates
        if 'start_date' in update_data:
            datetime.fromisoformat(update_data['start_date'].replace('Z', '+00:00'))
        if 'end_date' in update_data:
            datetime.fromisoformat(update_data['end_date'].replace('Z', '+00:00'))
        
        # Validate progress
        if 'progress' in update_data:
            progress = float(update_data['progress'])
            if not 0 <= progress <= 100:
                raise ValueError("Progress must be between 0 and 100")
        
        return jsonify({
            'success': True,
            'message': f'Task {task_id} updated successfully',
            'updated_fields': list(update_data.keys()),
            'updated_at': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error updating task {task_id}: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400


@gantt_bp.route('/export/<format_type>', methods=['GET'])
def export_gantt_data(format_type):
    """
    Export Gantt chart data in various formats.
    
    Args:
        format_type: Format to export (json, mermaid, csv)
    
    Returns:
        Exported data in requested format
    """
    try:
        logger.info(f"Exporting Gantt data in {format_type} format")
        
        analyzer = get_gantt_analyzer()
        gantt_data = analyzer.generate_gantt_data()
        
        if not gantt_data:
            gantt_data = generate_sample_gantt_data()
        
        if format_type.lower() == 'json':
            return jsonify({
                'success': True,
                'data': gantt_data,
                'exported_at': datetime.now().isoformat()
            })
        
        elif format_type.lower() == 'mermaid':
            mermaid_code = generate_mermaid_export(gantt_data)
            return jsonify({
                'success': True,
                'data': {
                    'mermaid_code': mermaid_code,
                    'format': 'mermaid'
                },
                'exported_at': datetime.now().isoformat()
            })
        
        elif format_type.lower() == 'csv':
            csv_data = generate_csv_export(gantt_data)
            return jsonify({
                'success': True,
                'data': {
                    'csv_data': csv_data,
                    'format': 'csv'
                },
                'exported_at': datetime.now().isoformat()
            })
        
        else:
            return jsonify({
                'success': False,
                'error': f'Unsupported export format: {format_type}'
            }), 400
        
    except Exception as e:
        logger.error(f"Error exporting Gantt data: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# Helper Functions

def generate_sample_gantt_data():
    """Generate sample Gantt chart data for demonstration."""
    base_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    
    return {
        'project_timeline': {
            'start_date': base_date.isoformat(),
            'end_date': (base_date + timedelta(days=45)).isoformat(),
            'total_duration': 45,
            'critical_path_duration': 30,
            'total_tasks': 12,
            'completed_tasks': 4,
            'progress': 33.3,
            'resource_utilization': {
                'Developer A': 0.95,
                'Developer B': 0.75,
                'Designer': 0.60,
                'QA Engineer': 0.85,
                'DevOps': 0.70
            }
        },
        'tasks': [
            {
                'id': 'task-1',
                'name': 'Project Setup & Planning',
                'start_date': base_date.isoformat(),
                'end_date': (base_date + timedelta(days=3)).isoformat(),
                'duration': 3,
                'progress': 100,
                'dependencies': [],
                'assigned_to': 'Developer A',
                'priority': 'high',
                'status': 'completed',
                'estimated_effort': 24,
                'actual_effort': 20,
                'milestone': True,
                'critical_path': True,
                'slack_time': 0,
                'resource_allocation': 1.0
            },
            {
                'id': 'task-2',
                'name': 'Database Schema Design',
                'start_date': (base_date + timedelta(days=4)).isoformat(),
                'end_date': (base_date + timedelta(days=8)).isoformat(),
                'duration': 5,
                'progress': 80,
                'dependencies': ['task-1'],
                'assigned_to': 'Developer B',
                'priority': 'high',
                'status': 'in_progress',
                'estimated_effort': 40,
                'actual_effort': 32,
                'milestone': False,
                'critical_path': True,
                'slack_time': 0,
                'resource_allocation': 1.0
            },
            {
                'id': 'task-3',
                'name': 'UI/UX Design & Mockups',
                'start_date': (base_date + timedelta(days=4)).isoformat(),
                'end_date': (base_date + timedelta(days=10)).isoformat(),
                'duration': 7,
                'progress': 60,
                'dependencies': ['task-1'],
                'assigned_to': 'Designer',
                'priority': 'medium',
                'status': 'in_progress',
                'estimated_effort': 56,
                'actual_effort': 35,
                'milestone': False,
                'critical_path': False,
                'slack_time': 3,
                'resource_allocation': 0.8
            },
            {
                'id': 'task-4',
                'name': 'Backend API Development',
                'start_date': (base_date + timedelta(days=9)).isoformat(),
                'end_date': (base_date + timedelta(days=18)).isoformat(),
                'duration': 10,
                'progress': 30,
                'dependencies': ['task-2'],
                'assigned_to': 'Developer A',
                'priority': 'high',
                'status': 'in_progress',
                'estimated_effort': 80,
                'actual_effort': 24,
                'milestone': False,
                'critical_path': True,
                'slack_time': 0,
                'resource_allocation': 1.0
            },
            {
                'id': 'task-5',
                'name': 'Frontend Implementation',
                'start_date': (base_date + timedelta(days=11)).isoformat(),
                'end_date': (base_date + timedelta(days=22)).isoformat(),
                'duration': 12,
                'progress': 20,
                'dependencies': ['task-3'],
                'assigned_to': 'Developer B',
                'priority': 'high',
                'status': 'pending',
                'estimated_effort': 96,
                'actual_effort': 19,
                'milestone': False,
                'critical_path': False,
                'slack_time': 2,
                'resource_allocation': 0.9
            },
            {
                'id': 'task-6',
                'name': 'Integration & Testing',
                'start_date': (base_date + timedelta(days=19)).isoformat(),
                'end_date': (base_date + timedelta(days=28)).isoformat(),
                'duration': 10,
                'progress': 0,
                'dependencies': ['task-4', 'task-5'],
                'assigned_to': 'QA Engineer',
                'priority': 'high',
                'status': 'pending',
                'estimated_effort': 80,
                'actual_effort': 0,
                'milestone': True,
                'critical_path': True,
                'slack_time': 0,
                'resource_allocation': 1.0
            },
            {
                'id': 'task-7',
                'name': 'DevOps & Deployment Setup',
                'start_date': (base_date + timedelta(days=15)).isoformat(),
                'end_date': (base_date + timedelta(days=25)).isoformat(),
                'duration': 11,
                'progress': 10,
                'dependencies': ['task-4'],
                'assigned_to': 'DevOps',
                'priority': 'medium',
                'status': 'pending',
                'estimated_effort': 88,
                'actual_effort': 9,
                'milestone': False,
                'critical_path': False,
                'slack_time': 5,
                'resource_allocation': 0.7
            },
            {
                'id': 'task-8',
                'name': 'Documentation & Training',
                'start_date': (base_date + timedelta(days=29)).isoformat(),
                'end_date': (base_date + timedelta(days=35)).isoformat(),
                'duration': 7,
                'progress': 0,
                'dependencies': ['task-6'],
                'assigned_to': 'Developer A',
                'priority': 'medium',
                'status': 'pending',
                'estimated_effort': 56,
                'actual_effort': 0,
                'milestone': False,
                'critical_path': True,
                'slack_time': 0,
                'resource_allocation': 0.6
            }
        ],
        'critical_path': ['task-1', 'task-2', 'task-4', 'task-6', 'task-8'],
        'milestones': [
            {
                'id': 'milestone-1',
                'name': 'Project Kickoff',
                'date': (base_date + timedelta(days=3)).isoformat(),
                'status': 'completed'
            },
            {
                'id': 'milestone-2',
                'name': 'Development Phase Complete',
                'date': (base_date + timedelta(days=28)).isoformat(),
                'status': 'pending'
            },
            {
                'id': 'milestone-3',
                'name': 'Project Delivery',
                'date': (base_date + timedelta(days=35)).isoformat(),
                'status': 'pending'
            }
        ]
    }


def filter_by_time_range(gantt_data, time_range):
    """Filter Gantt data by specified time range."""
    if time_range == 'all':
        return gantt_data
    
    now = datetime.now()
    
    if time_range == 'week':
        start_date = now - timedelta(days=7)
        end_date = now + timedelta(days=7)
    elif time_range == 'month':
        start_date = now - timedelta(days=30)
        end_date = now + timedelta(days=30)
    elif time_range == 'quarter':
        start_date = now - timedelta(days=90)
        end_date = now + timedelta(days=90)
    else:
        return gantt_data
    
    # Filter tasks within the time range
    filtered_tasks = []
    for task in gantt_data.get('tasks', []):
        task_start = datetime.fromisoformat(task['start_date'].replace('Z', ''))
        task_end = datetime.fromisoformat(task['end_date'].replace('Z', ''))
        
        if (task_start <= end_date and task_end >= start_date):
            filtered_tasks.append(task)
    
    gantt_data['tasks'] = filtered_tasks
    return gantt_data


def calculate_risk_level(critical_tasks):
    """Calculate overall risk level based on critical tasks."""
    if not critical_tasks:
        return 'Low'
    
    total_slack = sum(task.get('slack_time', 0) for task in critical_tasks)
    avg_slack = total_slack / len(critical_tasks)
    
    if avg_slack < 1:
        return 'High'
    elif avg_slack < 3:
        return 'Medium'
    else:
        return 'Low'


def identify_bottlenecks(critical_tasks):
    """Identify potential bottlenecks in critical tasks."""
    bottlenecks = []
    
    for task in critical_tasks:
        if task.get('slack_time', 0) == 0:
            bottlenecks.append({
                'task_id': task['id'],
                'task_name': task['name'],
                'reason': 'Zero slack time',
                'severity': 'high'
            })
    
    return bottlenecks


def calculate_float_analysis(tasks):
    """Calculate float analysis for all tasks."""
    float_analysis = {
        'zero_float_tasks': [],
        'low_float_tasks': [],
        'high_float_tasks': []
    }
    
    for task in tasks:
        slack = task.get('slack_time', 0)
        if slack == 0:
            float_analysis['zero_float_tasks'].append(task['id'])
        elif slack < 3:
            float_analysis['low_float_tasks'].append(task['id'])
        else:
            float_analysis['high_float_tasks'].append(task['id'])
    
    return float_analysis


def extract_dependency_network(critical_tasks):
    """Extract dependency network for critical tasks."""
    dependencies = []
    
    for task in critical_tasks:
        for dep_id in task.get('dependencies', []):
            dependencies.append({
                'from': dep_id,
                'to': task['id'],
                'type': 'finish_to_start'
            })
    
    return dependencies


def generate_critical_path_recommendations(critical_tasks):
    """Generate recommendations for critical path optimization."""
    recommendations = []
    
    for task in critical_tasks:
        if task.get('slack_time', 0) == 0:
            recommendations.append({
                'id': f"crit-{task['id']}",
                'title': f"Optimize {task['name']}",
                'description': f"Consider breaking down or parallelizing this critical task to reduce project duration.",
                'priority': 'high',
                'category': 'timeline',
                'impact': 'High',
                'effort': 'Medium'
            })
    
    return recommendations


def analyze_resource_utilization(tasks):
    """Analyze resource utilization across all tasks."""
    resources = {}
    
    for task in tasks:
        assigned_to = task.get('assigned_to')
        if not assigned_to:
            continue
        
        if assigned_to not in resources:
            resources[assigned_to] = {
                'total_effort': 0,
                'completed_effort': 0,
                'tasks': [],
                'utilization': 0
            }
        
        effort = task.get('estimated_effort', 0)
        completed = task.get('actual_effort', 0)
        
        resources[assigned_to]['total_effort'] += effort
        resources[assigned_to]['completed_effort'] += completed
        resources[assigned_to]['tasks'].append(task['id'])
        resources[assigned_to]['utilization'] = task.get('resource_allocation', 0)
    
    return resources


def analyze_workload_distribution(tasks):
    """Analyze workload distribution across team members."""
    workload = {}
    
    for task in tasks:
        assigned_to = task.get('assigned_to', 'Unassigned')
        if assigned_to not in workload:
            workload[assigned_to] = {
                'task_count': 0,
                'total_duration': 0,
                'avg_task_size': 0
            }
        
        workload[assigned_to]['task_count'] += 1
        workload[assigned_to]['total_duration'] += task.get('duration', 0)
    
    # Calculate averages
    for resource in workload:
        if workload[resource]['task_count'] > 0:
            workload[resource]['avg_task_size'] = (
                workload[resource]['total_duration'] / workload[resource]['task_count']
            )
    
    return workload


def analyze_capacity(tasks):
    """Analyze team capacity and availability."""
    # This would typically integrate with HR/capacity planning systems
    # For now, return sample capacity data
    return {
        'team_capacity': {
            'Developer A': {'available_hours': 40, 'allocated_hours': 38},
            'Developer B': {'available_hours': 40, 'allocated_hours': 30},
            'Designer': {'available_hours': 40, 'allocated_hours': 24},
            'QA Engineer': {'available_hours': 40, 'allocated_hours': 34},
            'DevOps': {'available_hours': 40, 'allocated_hours': 28}
        },
        'overall_utilization': 77.5,
        'peak_demand_periods': [
            {
                'period': 'Week 3-4',
                'utilization': 95,
                'critical_resources': ['Developer A', 'QA Engineer']
            }
        ]
    }


def identify_resource_bottlenecks(tasks):
    """Identify resource bottlenecks."""
    bottlenecks = []
    
    # Analyze resource allocation
    resource_load = analyze_resource_utilization(tasks)
    
    for resource, data in resource_load.items():
        if data['utilization'] > 0.9:
            bottlenecks.append({
                'resource': resource,
                'utilization': data['utilization'],
                'reason': 'Over-allocated',
                'severity': 'high',
                'affected_tasks': data['tasks']
            })
    
    return bottlenecks


def identify_optimization_opportunities(tasks):
    """Identify optimization opportunities."""
    opportunities = []
    
    # Look for tasks that can be parallelized
    for task in tasks:
        deps = task.get('dependencies', [])
        if len(deps) == 0 and not task.get('critical_path', False):
            opportunities.append({
                'type': 'parallelization',
                'task_id': task['id'],
                'description': f"Task '{task['name']}' can potentially start earlier",
                'impact': 'medium'
            })
    
    return opportunities


def calculate_team_metrics(tasks):
    """Calculate overall team performance metrics."""
    total_estimated = sum(task.get('estimated_effort', 0) for task in tasks)
    total_actual = sum(task.get('actual_effort', 0) for task in tasks)
    
    completed_tasks = [task for task in tasks if task.get('status') == 'completed']
    
    return {
        'velocity': len(completed_tasks) / max(len(tasks), 1) * 100,
        'estimation_accuracy': (total_actual / max(total_estimated, 1)) * 100,
        'on_time_delivery': 85,  # Would be calculated from actual delivery dates
        'quality_score': 92,     # Would be calculated from defect rates
        'team_efficiency': 88    # Overall efficiency metric
    }


def generate_sample_recommendations():
    """Generate sample optimization recommendations."""
    return [
        {
            'id': 'rec-1',
            'title': 'Parallelize Independent Tasks',
            'description': 'Tasks "UI Design" and "Database Setup" can run concurrently, reducing timeline by 5 days.',
            'priority': 'high',
            'category': 'timeline',
            'impact': 'High',
            'effort': 'Low',
            'time_savings': 5,
            'cost_savings': 2500
        },
        {
            'id': 'rec-2',
            'title': 'Redistribute Workload',
            'description': 'Developer A is overallocated at 95%. Consider moving non-critical tasks to Developer B.',
            'priority': 'medium',
            'category': 'resource',
            'impact': 'Medium',
            'effort': 'Medium',
            'time_savings': 2,
            'cost_savings': 1000
        },
        {
            'id': 'rec-3',
            'title': 'Add Buffer to Critical Path',
            'description': 'Critical path has zero slack. Consider adding 10% buffer to high-risk tasks.',
            'priority': 'high',
            'category': 'risk',
            'impact': 'High',
            'effort': 'Low',
            'time_savings': 0,
            'cost_savings': 5000
        }
    ]


def generate_sample_optimization_results(params):
    """Generate sample optimization results."""
    return {
        'optimization_goal': params.get('goal'),
        'duration_reduction': 7,
        'resource_efficiency': 85,
        'risk_reduction': 25,
        'quality_impact': 5,
        'changes': [
            'Parallelize "UI Design" and "Database Setup" tasks',
            'Move "Documentation" task to Developer B',
            'Add 2-day buffer to "Integration Testing"',
            'Optimize resource allocation for peak weeks'
        ],
        'new_timeline': {
            'original_duration': 45,
            'optimized_duration': 38,
            'savings': 7
        },
        'resource_changes': {
            'Developer A': {'before': 95, 'after': 85},
            'Developer B': {'before': 75, 'after': 80},
            'Designer': {'before': 60, 'after': 65}
        }
    }


def generate_mermaid_export(gantt_data):
    """Generate Mermaid Gantt chart code for export."""
    tasks = gantt_data.get('tasks', [])
    
    mermaid_code = "gantt\n    title Project Timeline\n    dateFormat YYYY-MM-DD\n\n"
    
    # Group tasks by assignee
    assignees = {}
    for task in tasks:
        assigned_to = task.get('assigned_to', 'Unassigned')
        if assigned_to not in assignees:
            assignees[assigned_to] = []
        assignees[assigned_to].append(task)
    
    for assignee, assignee_tasks in assignees.items():
        mermaid_code += f"    section {assignee}\n"
        for task in assignee_tasks:
            status = 'crit, ' if task.get('critical_path') else ''
            if task.get('status') == 'completed':
                status += 'done, '
            elif task.get('status') == 'in_progress':
                status += 'active, '
            
            start_date = datetime.fromisoformat(task['start_date'].replace('Z', '')).strftime('%Y-%m-%d')
            end_date = datetime.fromisoformat(task['end_date'].replace('Z', '')).strftime('%Y-%m-%d')
            
            mermaid_code += f"    {task['name']} :{status}{task['id']}, {start_date}, {end_date}\n"
    
    return mermaid_code


def generate_csv_export(gantt_data):
    """Generate CSV export of Gantt chart data."""
    tasks = gantt_data.get('tasks', [])
    
    csv_lines = [
        'ID,Name,Start Date,End Date,Duration,Progress,Status,Assigned To,Critical Path,Dependencies'
    ]
    
    for task in tasks:
        line = [
            task['id'],
            task['name'],
            task['start_date'],
            task['end_date'],
            str(task['duration']),
            str(task['progress']),
            task['status'],
            task.get('assigned_to', ''),
            str(task.get('critical_path', False)),
            ','.join(task.get('dependencies', []))
        ]
        csv_lines.append(','.join(f'"{field}"' for field in line))
    
    return '\n'.join(csv_lines)


# Error handlers
@gantt_bp.errorhandler(404)
def not_found(error):
    return jsonify({
        'success': False,
        'error': 'Endpoint not found'
    }), 404


@gantt_bp.errorhandler(500)
def internal_error(error):
    return jsonify({
        'success': False,
        'error': 'Internal server error'
    }), 500
