#!/usr/bin/env python3
"""
Gantt Chart & Critical Path Analyzer - Phase 6 Step 6.7

Advanced Gantt chart generation and critical path analysis system
for project timeline visualization and optimization.
"""

import json
import logging
import os
import sys
from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any, Set
import yaml

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from orchestration.states import TaskStatus
from utils.completion_metrics import CompletionMetricsCalculator


@dataclass
class GanttTask:
    """Represents a task in the Gantt chart."""
    id: str
    name: str
    start_date: datetime
    end_date: datetime
    duration: int  # in days
    progress: float  # 0-100
    dependencies: List[str] = field(default_factory=list)
    assigned_to: str = ""
    priority: str = "medium"  # low, medium, high, critical
    status: str = "pending"
    estimated_effort: int = 1  # story points or hours
    actual_effort: int = 0
    milestone: bool = False
    critical_path: bool = False
    slack_time: int = 0  # float time in days
    resource_allocation: float = 1.0  # 0-1 (percentage of resource time)


@dataclass
class ProjectTimeline:
    """Represents the complete project timeline."""
    start_date: datetime
    end_date: datetime
    total_duration: int
    critical_path_duration: int
    total_tasks: int
    completed_tasks: int
    progress: float
    milestones: List[GanttTask]
    critical_path: List[str]
    resource_utilization: Dict[str, float]


class CriticalPathMethod:
    """Implements Enhanced Critical Path Method (CPM) algorithm with resource optimization."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def calculate_critical_path(self, tasks: List[GanttTask]) -> Tuple[List[str], Dict[str, int]]:
        """
        Calculate the critical path using enhanced CPM algorithm.
        
        Returns:
            Tuple of (critical_path_task_ids, slack_times)
        """
        self.logger.info("Calculating critical path for project")
        
        # Build dependency graph
        graph = self._build_dependency_graph(tasks)
        task_dict = {task.id: task for task in tasks}
        
        # Forward pass - calculate earliest start/finish times
        earliest_times = self._forward_pass(graph, task_dict)
        
        # Backward pass - calculate latest start/finish times
        latest_times = self._backward_pass(graph, task_dict, earliest_times)
        
        # Calculate slack times and identify critical path
        slack_times = {}
        critical_path = []
        
        for task_id in graph:
            slack = latest_times[task_id]['finish'] - earliest_times[task_id]['finish']
            slack_times[task_id] = slack
            
            if slack == 0:  # Zero slack = critical path
                critical_path.append(task_id)
                task_dict[task_id].critical_path = True
                task_dict[task_id].slack_time = 0
            else:
                task_dict[task_id].slack_time = slack
        
        # Order critical path tasks
        critical_path = self._order_critical_path(critical_path, graph, task_dict)
        
        # Calculate risk factors for critical path
        self._calculate_risk_factors(critical_path, task_dict)
        
        self.logger.info(f"Critical path identified: {len(critical_path)} tasks")
        return critical_path, slack_times
    
    def _calculate_risk_factors(self, critical_path: List[str], task_dict: Dict[str, GanttTask]):
        """Calculate risk factors for critical path tasks."""
        for task_id in critical_path:
            task = task_dict[task_id]
            
            # Risk factors based on complexity, dependencies, and resource constraints
            risk_score = 0
            
            # Dependency risk (more dependencies = higher risk)
            dependency_risk = min(len(task.dependencies) * 0.1, 0.5)
            risk_score += dependency_risk
            
            # Resource allocation risk (overallocation = higher risk)
            if task.resource_allocation > 0.8:
                risk_score += 0.3
            elif task.resource_allocation > 1.0:
                risk_score += 0.5
            
            # Priority risk (higher priority = higher impact if delayed)
            priority_weights = {"low": 0, "medium": 0.1, "high": 0.2, "critical": 0.3}
            risk_score += priority_weights.get(task.priority, 0)
            
            # Set risk level
            if risk_score >= 0.5:
                task.risk_level = "high"
            elif risk_score >= 0.3:
                task.risk_level = "medium"
            else:
                task.risk_level = "low"
    
    def _build_dependency_graph(self, tasks: List[GanttTask]) -> Dict[str, List[str]]:
        """Build adjacency list representation of task dependencies."""
        graph = defaultdict(list)
        
        for task in tasks:
            if task.id not in graph:
                graph[task.id] = []
            
            for dependency in task.dependencies:
                graph[dependency].append(task.id)
        
        return dict(graph)
    
    def _forward_pass(self, graph: Dict[str, List[str]], task_dict: Dict[str, GanttTask]) -> Dict[str, Dict[str, int]]:
        """Calculate earliest start and finish times."""
        earliest_times = {}
        processed = set()
        
        # Topological sort for processing order
        def dfs(task_id):
            if task_id in processed:
                return
            
            processed.add(task_id)
            task = task_dict[task_id]
            
            # Calculate earliest start time
            earliest_start = 0
            for dep_id in task.dependencies:
                if dep_id in task_dict:
                    dfs(dep_id)
                    dep_finish = earliest_times.get(dep_id, {}).get('finish', 0)
                    earliest_start = max(earliest_start, dep_finish)
            
            earliest_finish = earliest_start + task.duration
            earliest_times[task_id] = {
                'start': earliest_start,
                'finish': earliest_finish
            }
            
            # Process successors
            for successor in graph.get(task_id, []):
                dfs(successor)
        
        # Process all tasks
        for task_id in task_dict:
            dfs(task_id)
        
        return earliest_times
    
    def _backward_pass(self, graph: Dict[str, List[str]], task_dict: Dict[str, GanttTask], 
                      earliest_times: Dict[str, Dict[str, int]]) -> Dict[str, Dict[str, int]]:
        """Calculate latest start and finish times."""
        latest_times = {}
        
        # Find project end time
        project_end = max(times['finish'] for times in earliest_times.values())
        
        # Reverse dependency graph
        reverse_graph = defaultdict(list)
        for task_id, successors in graph.items():
            for successor in successors:
                reverse_graph[successor].append(task_id)
        
        processed = set()
        
        def dfs_backward(task_id):
            if task_id in processed:
                return
            
            processed.add(task_id)
            task = task_dict[task_id]
            
            # Calculate latest finish time
            latest_finish = project_end
            for successor in graph.get(task_id, []):
                if successor in task_dict:
                    dfs_backward(successor)
                    successor_start = latest_times.get(successor, {}).get('start', project_end)
                    latest_finish = min(latest_finish, successor_start)
            
            latest_start = latest_finish - task.duration
            latest_times[task_id] = {
                'start': latest_start,
                'finish': latest_finish
            }
            
            # Process predecessors
            for predecessor in reverse_graph.get(task_id, []):
                dfs_backward(predecessor)
        
        # Process all tasks
        for task_id in task_dict:
            dfs_backward(task_id)
        
        return latest_times
    
    def _order_critical_path(self, critical_tasks: List[str], graph: Dict[str, List[str]], 
                           task_dict: Dict[str, GanttTask]) -> List[str]:
        """Order critical path tasks by dependency sequence."""
        if not critical_tasks:
            return []
        
        # Build subgraph of critical tasks
        critical_graph = {}
        for task_id in critical_tasks:
            critical_graph[task_id] = [
                successor for successor in graph.get(task_id, [])
                if successor in critical_tasks
            ]
        
        # Topological sort of critical tasks
        ordered_path = []
        visited = set()
        
        def dfs(task_id):
            if task_id in visited:
                return
            visited.add(task_id)
            
            for successor in critical_graph.get(task_id, []):
                dfs(successor)
            
            ordered_path.append(task_id)
        
        for task_id in critical_tasks:
            dfs(task_id)
        
        return list(reversed(ordered_path))


class ResourceOptimizer:
    """Analyzes resource allocation and provides optimization recommendations."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def analyze_resource_utilization(self, tasks: List[GanttTask]) -> Dict[str, Any]:
        """Analyze resource utilization and identify bottlenecks."""
        self.logger.info("Analyzing resource utilization")
        
        resource_schedule = defaultdict(list)
        resource_utilization = defaultdict(float)
        
        # Group tasks by assigned resource
        for task in tasks:
            if task.assigned_to:
                resource_schedule[task.assigned_to].append(task)
                resource_utilization[task.assigned_to] += task.resource_allocation
        
        # Identify overallocated resources
        overallocated = {}
        underutilized = {}
        
        for resource, utilization in resource_utilization.items():
            if utilization > 1.0:
                overallocated[resource] = utilization
            elif utilization < 0.7:  # Less than 70% utilization
                underutilized[resource] = utilization
        
        # Calculate resource efficiency metrics
        total_utilization = sum(resource_utilization.values())
        average_utilization = total_utilization / len(resource_utilization) if resource_utilization else 0
        
        # Identify critical resource constraints
        critical_resources = self._identify_critical_resources(resource_schedule, tasks)
        
        return {
            'resource_utilization': dict(resource_utilization),
            'overallocated': overallocated,
            'underutilized': underutilized,
            'average_utilization': average_utilization,
            'critical_resources': critical_resources,
            'optimization_recommendations': self._generate_optimization_recommendations(
                overallocated, underutilized, critical_resources
            )
        }
    
    def _identify_critical_resources(self, resource_schedule: Dict[str, List[GanttTask]], 
                                   tasks: List[GanttTask]) -> List[str]:
        """Identify resources that are critical to project completion."""
        critical_resources = []
        critical_tasks = [task for task in tasks if task.critical_path]
        
        for resource, task_list in resource_schedule.items():
            # Check if resource has critical path tasks
            has_critical_tasks = any(task.critical_path for task in task_list)
            
            # Check if resource has high-priority tasks
            has_high_priority = any(task.priority in ['high', 'critical'] for task in task_list)
            
            if has_critical_tasks or has_high_priority:
                critical_resources.append(resource)
        
        return critical_resources
    
    def _generate_optimization_recommendations(self, overallocated: Dict[str, float], 
                                             underutilized: Dict[str, float],
                                             critical_resources: List[str]) -> List[Dict[str, Any]]:
        """Generate actionable optimization recommendations."""
        recommendations = []
        
        # Recommendations for overallocated resources
        for resource, utilization in overallocated.items():
            recommendations.append({
                'type': 'resource_reallocation',
                'priority': 'high' if resource in critical_resources else 'medium',
                'resource': resource,
                'current_utilization': utilization,
                'message': f'Resource {resource} is overallocated ({utilization:.1%}). Consider redistributing tasks or extending timeline.',
                'suggested_actions': [
                    'Redistribute non-critical tasks to underutilized resources',
                    'Extend task deadlines where possible',
                    'Consider adding additional resources to this role'
                ]
            })
        
        # Recommendations for underutilized resources
        for resource, utilization in underutilized.items():
            recommendations.append({
                'type': 'capacity_optimization',
                'priority': 'low',
                'resource': resource,
                'current_utilization': utilization,
                'message': f'Resource {resource} is underutilized ({utilization:.1%}). Consider additional task assignments.',
                'suggested_actions': [
                    'Assign additional tasks from overallocated resources',
                    'Consider training for additional skill areas',
                    'Evaluate if resource allocation can be reduced'
                ]
            })
        
        # Timeline optimization recommendations
        recommendations.append({
            'type': 'timeline_optimization',
            'priority': 'medium',
            'message': 'Review critical path for potential timeline improvements',
            'suggested_actions': [
                'Parallelize independent tasks where possible',
                'Fast-track critical path activities',
                'Consider overlapping sequential tasks with careful dependency management'
            ]
        })
        
        return recommendations
    
    def generate_resource_leveling_plan(self, tasks: List[GanttTask]) -> Dict[str, Any]:
        """Generate a resource leveling plan to smooth resource usage."""
        self.logger.info("Generating resource leveling plan")
        
        # Group tasks by time period and resource
        time_periods = {}
        for task in tasks:
            current_date = task.start_date
            while current_date <= task.end_date:
                period_key = current_date.strftime("%Y-%m-%d")
                if period_key not in time_periods:
                    time_periods[period_key] = defaultdict(float)
                
                time_periods[period_key][task.assigned_to] += task.resource_allocation
                current_date += timedelta(days=1)
        
        # Identify peaks and valleys in resource usage
        resource_peaks = {}
        resource_valleys = {}
        
        for period, resources in time_periods.items():
            for resource, allocation in resources.items():
                if resource not in resource_peaks:
                    resource_peaks[resource] = 0
                    resource_valleys[resource] = float('inf')
                
                resource_peaks[resource] = max(resource_peaks[resource], allocation)
                resource_valleys[resource] = min(resource_valleys[resource], allocation)
        
        return {
            'time_periods': dict(time_periods),
            'resource_peaks': resource_peaks,
            'resource_valleys': resource_valleys,
            'leveling_recommendations': self._generate_leveling_recommendations(
                time_periods, resource_peaks, resource_valleys
            )
        }
    
    def _generate_leveling_recommendations(self, time_periods: Dict[str, Dict[str, float]], 
                                         resource_peaks: Dict[str, float], 
                                         resource_valleys: Dict[str, float]) -> List[Dict[str, Any]]:
        """Generate specific recommendations for resource leveling."""
        recommendations = []
        
        for resource, peak in resource_peaks.items():
            valley = resource_valleys.get(resource, 0)
            variance = peak - valley
            
            if variance > 0.5:  # High variance in resource usage
                recommendations.append({
                    'resource': resource,
                    'peak_utilization': peak,
                    'valley_utilization': valley,
                    'variance': variance,
                    'recommendation': f'High variance in {resource} utilization. Consider task rescheduling.',
                    'suggested_actions': [
                        'Move non-critical tasks from peak periods to valley periods',
                        'Consider flexible task scheduling',
                        'Evaluate if tasks can be split across multiple periods'
                    ]
                })
        
        return recommendations
    
    def _generate_resource_recommendations(self, resource_schedule: Dict[str, List[GanttTask]], 
                                         overallocated: Dict[str, float], 
                                         underutilized: Dict[str, float]) -> List[str]:
        """Generate resource optimization recommendations."""
        recommendations = []
        
        # Overallocation recommendations
        for resource, utilization in overallocated.items():
            excess = (utilization - 1.0) * 100
            recommendations.append(
                f"⚠️ {resource} is overallocated by {excess:.1f}%. "
                f"Consider redistributing tasks or extending timeline."
            )
        
        # Underutilization recommendations
        for resource, utilization in underutilized.items():
            unused = (1.0 - utilization) * 100
            recommendations.append(
                f"💡 {resource} has {unused:.1f}% unused capacity. "
                f"Consider assigning additional tasks or reducing allocation."
            )
        
        # Cross-resource optimization
        if overallocated and underutilized:
            recommendations.append(
                "🔄 Consider redistributing tasks from overallocated to underutilized resources."
            )
        
        return recommendations
    
    def _calculate_optimization_score(self, resource_utilization: Dict[str, float]) -> float:
        """Calculate resource optimization score (0-100)."""
        if not resource_utilization:
            return 100.0
        
        # Ideal utilization is 80-90%
        target_utilization = 0.85
        total_deviation = 0
        
        for utilization in resource_utilization.values():
            # Calculate deviation from target
            deviation = abs(utilization - target_utilization) / target_utilization
            total_deviation += min(deviation, 1.0)  # Cap at 100% deviation
        
        avg_deviation = total_deviation / len(resource_utilization)
        score = max(0, 100 - (avg_deviation * 100))
        
        return round(score, 1)


class ScenarioPlanner:
    """Advanced scenario planning and what-if analysis for project timelines."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def analyze_timeline_scenarios(self, tasks: List[GanttTask]) -> Dict[str, Any]:
        """Analyze different timeline scenarios and their impact."""
        self.logger.info("Analyzing timeline scenarios")
        
        scenarios = {
            'current': self._analyze_current_scenario(tasks),
            'optimistic': self._analyze_optimistic_scenario(tasks),
            'pessimistic': self._analyze_pessimistic_scenario(tasks),
            'resource_optimized': self._analyze_resource_optimized_scenario(tasks)
        }
        
        return {
            'scenarios': scenarios,
            'recommendations': self._generate_scenario_recommendations(scenarios),
            'risk_analysis': self._analyze_scenario_risks(scenarios)
        }
    
    def _analyze_current_scenario(self, tasks: List[GanttTask]) -> Dict[str, Any]:
        """Analyze the current baseline scenario."""
        total_duration = max(task.end_date for task in tasks) - min(task.start_date for task in tasks)
        completion_rate = sum(1 for task in tasks if task.status == 'completed') / len(tasks)
        
        return {
            'name': 'Current Baseline',
            'duration_days': total_duration.days,
            'completion_rate': completion_rate,
            'risk_level': 'medium',
            'resource_utilization': self._calculate_scenario_resource_utilization(tasks),
            'critical_path_length': len([t for t in tasks if t.critical_path])
        }
    
    def _analyze_optimistic_scenario(self, tasks: List[GanttTask]) -> Dict[str, Any]:
        """Analyze optimistic scenario (80% of estimated durations)."""
        optimistic_tasks = []
        for task in tasks:
            optimistic_task = GanttTask(
                id=task.id,
                name=task.name,
                start_date=task.start_date,
                end_date=task.start_date + timedelta(days=int(task.duration * 0.8)),
                duration=int(task.duration * 0.8),
                progress=task.progress,
                dependencies=task.dependencies,
                assigned_to=task.assigned_to,
                priority=task.priority,
                status=task.status
            )
            optimistic_tasks.append(optimistic_task)
        
        total_duration = max(task.end_date for task in optimistic_tasks) - min(task.start_date for task in optimistic_tasks)
        
        return {
            'name': 'Optimistic (80% duration)',
            'duration_days': total_duration.days,
            'completion_rate': 0.95,  # Assume higher completion rate
            'risk_level': 'low',
            'resource_utilization': self._calculate_scenario_resource_utilization(optimistic_tasks),
            'time_savings': (max(task.end_date for task in tasks) - max(task.end_date for task in optimistic_tasks)).days
        }
    
    def _analyze_pessimistic_scenario(self, tasks: List[GanttTask]) -> Dict[str, Any]:
        """Analyze pessimistic scenario (130% of estimated durations)."""
        pessimistic_tasks = []
        for task in tasks:
            pessimistic_task = GanttTask(
                id=task.id,
                name=task.name,
                start_date=task.start_date,
                end_date=task.start_date + timedelta(days=int(task.duration * 1.3)),
                duration=int(task.duration * 1.3),
                progress=task.progress,
                dependencies=task.dependencies,
                assigned_to=task.assigned_to,
                priority=task.priority,
                status=task.status
            )
            pessimistic_tasks.append(pessimistic_task)
        
        total_duration = max(task.end_date for task in pessimistic_tasks) - min(task.start_date for task in pessimistic_tasks)
        
        return {
            'name': 'Pessimistic (130% duration)',
            'duration_days': total_duration.days,
            'completion_rate': 0.75,  # Assume lower completion rate
            'risk_level': 'high',
            'resource_utilization': self._calculate_scenario_resource_utilization(pessimistic_tasks),
            'additional_time': (max(task.end_date for task in pessimistic_tasks) - max(task.end_date for task in tasks)).days
        }
    
    def _analyze_resource_optimized_scenario(self, tasks: List[GanttTask]) -> Dict[str, Any]:
        """Analyze scenario with optimized resource allocation."""
        # Simulate resource optimization by reducing overallocation
        optimized_tasks = []
        resource_loads = defaultdict(float)
        
        for task in tasks:
            if task.assigned_to:
                resource_loads[task.assigned_to] += task.resource_allocation
        
        for task in tasks:
            optimized_task = GanttTask(
                id=task.id,
                name=task.name,
                start_date=task.start_date,
                end_date=task.end_date,
                duration=task.duration,
                progress=task.progress,
                dependencies=task.dependencies,
                assigned_to=task.assigned_to,
                priority=task.priority,
                status=task.status
            )
            
            # Adjust duration based on resource optimization
            if task.assigned_to and resource_loads[task.assigned_to] > 1.0:
                # Increase duration for overallocated resources
                adjustment_factor = min(resource_loads[task.assigned_to], 1.5)
                optimized_task.duration = int(task.duration * adjustment_factor)
                optimized_task.end_date = task.start_date + timedelta(days=optimized_task.duration)
            
            optimized_tasks.append(optimized_task)
        
        total_duration = max(task.end_date for task in optimized_tasks) - min(task.start_date for task in optimized_tasks)
        
        return {
            'name': 'Resource Optimized',
            'duration_days': total_duration.days,
            'completion_rate': 0.85,
            'risk_level': 'low',
            'resource_utilization': self._calculate_scenario_resource_utilization(optimized_tasks),
            'optimization_benefit': 'Balanced resource allocation reduces risk'
        }
    
    def _calculate_scenario_resource_utilization(self, tasks: List[GanttTask]) -> float:
        """Calculate average resource utilization for a scenario."""
        resource_loads = defaultdict(float)
        
        for task in tasks:
            if task.assigned_to:
                resource_loads[task.assigned_to] += task.resource_allocation
        
        if not resource_loads:
            return 0.0
        
        return sum(resource_loads.values()) / len(resource_loads)
    
    def _generate_scenario_recommendations(self, scenarios: Dict[str, Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generate recommendations based on scenario analysis."""
        recommendations = []
        
        current = scenarios['current']
        optimistic = scenarios['optimistic']
        pessimistic = scenarios['pessimistic']
        
        # Timeline recommendations
        if pessimistic['duration_days'] > current['duration_days'] * 1.2:
            recommendations.append({
                'type': 'timeline_risk',
                'priority': 'high',
                'message': 'High risk of significant timeline extension',
                'details': f"Pessimistic scenario shows {pessimistic['additional_time']} days additional time needed",
                'actions': [
                    'Add buffer time to critical path activities',
                    'Identify and mitigate high-risk tasks',
                    'Consider parallel execution of independent tasks'
                ]
            })
        
        # Resource optimization recommendations
        if scenarios['resource_optimized']['risk_level'] == 'low':
            recommendations.append({
                'type': 'resource_optimization',
                'priority': 'medium',
                'message': 'Resource optimization can reduce project risk',
                'details': 'Balanced resource allocation improves predictability',
                'actions': [
                    'Redistribute tasks to balance resource utilization',
                    'Consider cross-training team members',
                    'Plan for resource flexibility'
                ]
            })
        
        return recommendations
    
    def _analyze_scenario_risks(self, scenarios: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze risks across different scenarios."""
        risk_factors = {
            'timeline_variance': self._calculate_timeline_variance(scenarios),
            'resource_risk': self._calculate_resource_risk(scenarios),
            'completion_risk': self._calculate_completion_risk(scenarios)
        }
        
        overall_risk = sum(risk_factors.values()) / len(risk_factors)
        
        return {
            'risk_factors': risk_factors,
            'overall_risk_score': overall_risk,
            'risk_level': 'high' if overall_risk > 0.7 else 'medium' if overall_risk > 0.4 else 'low'
        }
    
    def _calculate_timeline_variance(self, scenarios: Dict[str, Dict[str, Any]]) -> float:
        """Calculate timeline variance risk."""
        durations = [scenario['duration_days'] for scenario in scenarios.values()]
        variance = (max(durations) - min(durations)) / min(durations)
        return min(variance, 1.0)  # Cap at 100%
    
    def _calculate_resource_risk(self, scenarios: Dict[str, Dict[str, Any]]) -> float:
        """Calculate resource utilization risk."""
        utilizations = [scenario.get('resource_utilization', 0) for scenario in scenarios.values()]
        max_utilization = max(utilizations)
        return min(max(0, (max_utilization - 0.9) / 0.3), 1.0)  # Risk increases above 90% utilization
    
    def _calculate_completion_risk(self, scenarios: Dict[str, Dict[str, Any]]) -> float:
        """Calculate completion rate risk."""
        completion_rates = [scenario.get('completion_rate', 0) for scenario in scenarios.values()]
        min_completion = min(completion_rates)
        return max(0, (0.8 - min_completion) / 0.2)  # Risk increases below 80% completion
    

class GanttAnalyzer:
    """Main Gantt chart analyzer and data generator."""
    
    def __init__(self, tasks_dir: str = "tasks"):
        self.tasks_dir = Path(tasks_dir)
        self.logger = logging.getLogger(__name__)
        self.cpm = CriticalPathMethod()
        self.resource_optimizer = ResourceOptimizer()
        self.scenario_planner = ScenarioPlanner()
        self.metrics_calculator = CompletionMetricsCalculator()
    
    def load_tasks_from_yaml(self) -> List[GanttTask]:
        """Load tasks from YAML files and convert to GanttTask objects."""
        self.logger.info(f"Loading tasks from {self.tasks_dir}")
        
        tasks = []
        yaml_files = list(self.tasks_dir.glob("*.yaml")) + list(self.tasks_dir.glob("*.yml"))
        
        for yaml_file in yaml_files:
            try:
                with open(yaml_file, 'r', encoding='utf-8') as f:
                    task_data = yaml.safe_load(f)
                
                if task_data:
                    gantt_task = self._convert_to_gantt_task(task_data, yaml_file.stem)
                    tasks.append(gantt_task)
                    
            except Exception as e:
                self.logger.warning(f"Error loading task from {yaml_file}: {e}")
        
        self.logger.info(f"Loaded {len(tasks)} tasks for Gantt analysis")
        return tasks
    
    def _convert_to_gantt_task(self, task_data: Dict[str, Any], task_id: str) -> GanttTask:
        """Convert YAML task data to GanttTask object."""
        # Parse dates or use defaults
        base_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        
        # Estimate duration based on task complexity
        estimated_duration = self._estimate_task_duration(task_data)
        
        # Determine task status
        status = self._determine_task_status(task_id)
        
        # Calculate progress
        progress = self._calculate_task_progress(status)
        
        return GanttTask(
            id=task_id,
            name=task_data.get('title', task_id),
            start_date=base_date,
            end_date=base_date + timedelta(days=estimated_duration),
            duration=estimated_duration,
            progress=progress,
            dependencies=task_data.get('dependencies', []),
            assigned_to=task_data.get('assigned_to', task_data.get('agent', 'unassigned')),
            priority=task_data.get('priority', 'medium'),
            status=status,
            estimated_effort=task_data.get('estimated_effort', estimated_duration),
            milestone=task_data.get('milestone', False)
        )
    
    def _estimate_task_duration(self, task_data: Dict[str, Any]) -> int:
        """Estimate task duration based on complexity and type."""
        # Base duration by task type
        task_type = task_data.get('type', 'development')
        base_durations = {
            'setup': 1,
            'analysis': 2,
            'development': 3,
            'testing': 2,
            'documentation': 1,
            'deployment': 1,
            'review': 1
        }
        
        base_duration = base_durations.get(task_type, 3)
        
        # Adjust based on complexity
        complexity = task_data.get('complexity', 'medium')
        complexity_multipliers = {
            'low': 0.5,
            'medium': 1.0,
            'high': 1.5,
            'critical': 2.0
        }
        
        multiplier = complexity_multipliers.get(complexity, 1.0)
        return max(1, round(base_duration * multiplier))
    
    def _determine_task_status(self, task_id: str) -> str:
        """Determine task status from outputs directory."""
        outputs_dir = Path("outputs") / task_id
        
        if not outputs_dir.exists():
            return "pending"
        
        status_file = outputs_dir / "status.json"
        if status_file.exists():
            try:
                with open(status_file, 'r') as f:
                    status_data = json.load(f)
                    return status_data.get('status', 'pending')
            except:
                pass
        
        # Check for completion markers
        if (outputs_dir / "completion_report.md").exists():
            return "completed"
        elif (outputs_dir / "qa_report.json").exists():
            return "testing"
        elif any(outputs_dir.glob("output_*.md")):
            return "in_progress"
        
        return "pending"
    
    def _calculate_task_progress(self, status: str) -> float:
        """Calculate task progress percentage based on status."""
        status_progress = {
            'pending': 0.0,
            'in_progress': 30.0,
            'testing': 70.0,
            'review': 85.0,
            'completed': 100.0,
            'blocked': 0.0
        }
        return status_progress.get(status, 0.0)
    
    def generate_gantt_data(self) -> Dict[str, Any]:
        """Generate comprehensive Gantt chart data."""
        self.logger.info("Generating Gantt chart data")
        
        # Load and process tasks
        tasks = self.load_tasks_from_yaml()
        
        if not tasks:
            self.logger.warning("No tasks found for Gantt chart generation")
            return self._generate_empty_gantt_data()
          # Calculate critical path
        critical_path, slack_times = self.cpm.calculate_critical_path(tasks)
        
        # Analyze resource utilization
        resource_analysis = self.resource_optimizer.analyze_resource_utilization(tasks)
        
        # Perform scenario analysis
        scenario_analysis = self.scenario_planner.analyze_timeline_scenarios(tasks)
        
        # Generate resource leveling plan
        leveling_plan = self.resource_optimizer.generate_resource_leveling_plan(tasks)
        
        # Calculate project timeline
        project_timeline = self._calculate_project_timeline(tasks, critical_path)
        
        # Generate Gantt chart format
        gantt_chart_data = self._format_for_gantt_chart(tasks)
        
        # Generate timeline optimization recommendations
        optimization_recommendations = self._generate_timeline_recommendations(
            tasks, critical_path, resource_analysis
        )
        
        return {
            'project_timeline': project_timeline.__dict__,
            'tasks': [task.__dict__ for task in tasks],
            'critical_path': critical_path,
            'slack_times': slack_times,
            'resource_analysis': resource_analysis,
            'scenario_analysis': scenario_analysis,
            'resource_leveling_plan': leveling_plan,
            'gantt_chart_data': gantt_chart_data,
            'optimization_recommendations': optimization_recommendations,
            'generated_at': datetime.now().isoformat(),
            'total_tasks': len(tasks),
            'completion_rate': project_timeline.progress
        }
    
    def _generate_empty_gantt_data(self) -> Dict[str, Any]:
        """Generate empty Gantt data structure."""
        return {
            'project_timeline': {
                'start_date': datetime.now().isoformat(),
                'end_date': (datetime.now() + timedelta(days=30)).isoformat(),
                'total_duration': 30,
                'critical_path_duration': 0,
                'total_tasks': 0,
                'completed_tasks': 0,
                'progress': 0.0,
                'milestones': [],
                'critical_path': [],
                'resource_utilization': {}
            },
            'tasks': [],
            'critical_path': [],
            'slack_times': {},            'resource_analysis': {
                'resource_utilization': {},
                'overallocated_resources': {},
                'underutilized_resources': {},
                'recommendations': ['No tasks available for analysis'],
                'total_resources': 0,
                'optimization_score': 100.0
            },
            'scenario_analysis': {
                'scenarios': {},
                'recommendations': [],
                'risk_analysis': {'overall_risk_score': 0.0, 'risk_level': 'low'}
            },
            'resource_leveling_plan': {
                'time_periods': {},
                'resource_peaks': {},
                'resource_valleys': {},
                'leveling_recommendations': []
            },
            'gantt_chart_data': {
                'tasks': [],
                'links': [],
                'resources': []
            },
            'optimization_recommendations': [],
            'generated_at': datetime.now().isoformat(),
            'total_tasks': 0,
            'completion_rate': 0.0
        }
    
    def _calculate_project_timeline(self, tasks: List[GanttTask], critical_path: List[str]) -> ProjectTimeline:
        """Calculate overall project timeline metrics."""
        if not tasks:
            return ProjectTimeline(
                start_date=datetime.now(),
                end_date=datetime.now(),
                total_duration=0,
                critical_path_duration=0,
                total_tasks=0,
                completed_tasks=0,
                progress=0.0,
                milestones=[],
                critical_path=[],
                resource_utilization={}
            )
        
        # Calculate project bounds
        start_date = min(task.start_date for task in tasks)
        end_date = max(task.end_date for task in tasks)
        total_duration = (end_date - start_date).days
        
        # Calculate critical path duration
        critical_path_duration = sum(
            next(task.duration for task in tasks if task.id == task_id)
            for task_id in critical_path
        )
        
        # Calculate completion metrics
        completed_tasks = sum(1 for task in tasks if task.status == 'completed')
        total_progress = sum(task.progress for task in tasks) / len(tasks) if tasks else 0
        
        # Identify milestones
        milestones = [task for task in tasks if task.milestone]
        
        # Calculate resource utilization
        resource_utilization = defaultdict(float)
        for task in tasks:
            if task.assigned_to:
                resource_utilization[task.assigned_to] += task.resource_allocation
        
        return ProjectTimeline(
            start_date=start_date,
            end_date=end_date,
            total_duration=total_duration,
            critical_path_duration=critical_path_duration,
            total_tasks=len(tasks),
            completed_tasks=completed_tasks,
            progress=total_progress,
            milestones=milestones,
            critical_path=critical_path,
            resource_utilization=dict(resource_utilization)
        )

    
    def _format_for_gantt_chart(self, tasks: List[GanttTask]) -> Dict[str, Any]:
        """Format task data for Gantt chart libraries."""
        chart_tasks = []
        chart_links = []
        resources = set()
        
        for task in tasks:
            # Format task for chart
            chart_task = {
                'id': task.id,
                'text': task.name,
                'start_date': task.start_date.strftime('%Y-%m-%d'),
                'end_date': task.end_date.strftime('%Y-%m-%d'),
                'duration': task.duration,
                'progress': task.progress / 100,
                'priority': task.priority,
                'owner': task.assigned_to,
                'critical': task.critical_path,
                'milestone': task.milestone,
                'status': task.status,
                'slack': task.slack_time
            }
            chart_tasks.append(chart_task)
            
            # Track resources
            if task.assigned_to:
                resources.add(task.assigned_to)
            
            # Create dependency links
            for dep_id in task.dependencies:
                chart_links.append({
                    'id': f"{dep_id}-{task.id}",
                    'source': dep_id,
                    'target': task.id,
                    'type': 'finish_to_start'
                })
        
        return {
            'tasks': chart_tasks,
            'links': chart_links,
            'resources': list(resources)
        }
    
    def _generate_timeline_recommendations(self, tasks: List[GanttTask], 
                                         critical_path: List[str], 
                                         resource_analysis: Dict[str, Any]) -> List[str]:
        """Generate timeline optimization recommendations."""
        recommendations = []
        
        # Generate different types of recommendations
        recommendations.extend(self._generate_critical_path_recommendations(tasks, critical_path))
        recommendations.extend(resource_analysis.get('recommendations', []))
        recommendations.extend(self._generate_parallelization_recommendations(tasks))
        recommendations.extend(self._generate_milestone_alerts(tasks))
        
        return recommendations
    
    def _generate_critical_path_recommendations(self, tasks: List[GanttTask], 
                                              critical_path: List[str]) -> List[str]:
        """Generate recommendations specific to critical path optimization."""
        recommendations = []
        
        if not critical_path:
            return recommendations
            
        # Primary critical path focus
        task_names = ', '.join(critical_path[:3])
        suffix = '...' if len(critical_path) > 3 else ''
        recommendations.append(f"🎯 Focus on critical path tasks: {task_names}{suffix}")
        
        # Slack time utilization
        high_slack_tasks = [
            task for task in tasks 
            if task.slack_time > 2 and task.id not in critical_path
        ]
        
        if high_slack_tasks:
            slack_task_names = ', '.join(task.name for task in high_slack_tasks[:3])
            recommendations.append(
                f"💡 Tasks with available slack time that could assist critical path: {slack_task_names}"
            )
            
        return recommendations
    
    def _generate_parallelization_recommendations(self, tasks: List[GanttTask]) -> List[str]:
        """Generate recommendations for task parallelization opportunities."""
        recommendations = []
        
        parallelizable_tasks = [
            task for task in tasks 
            if len(task.dependencies) == 0 and task.status == 'pending'
        ]
        
        if len(parallelizable_tasks) > 1:
            recommendations.append(
                f"⚡ {len(parallelizable_tasks)} tasks can start immediately and run in parallel"
            )
            
        return recommendations
    
    def _generate_milestone_alerts(self, tasks: List[GanttTask]) -> List[str]:
        """Generate alerts for upcoming milestones."""
        recommendations = []
        
        milestones = [task for task in tasks if task.milestone]
        for milestone in milestones:
            if milestone.status != 'completed':
                days_to_milestone = (milestone.end_date - datetime.now()).days
                if days_to_milestone < 7:
                    recommendations.append(
                        f"🚨 Milestone '{milestone.name}' due in {days_to_milestone} days"
                    )
                    
        return recommendations

# CLI interface
def main():
    """Main entry point for Gantt analyzer CLI."""
    logging.basicConfig(level=logging.INFO)
    
    import argparse
    parser = argparse.ArgumentParser(description="Generate Gantt chart and critical path analysis")
    parser.add_argument("--tasks-dir", default="tasks", help="Directory containing task YAML files")
    parser.add_argument("--output", default="dashboard/gantt_data.json", help="Output JSON file")
    parser.add_argument("--format", choices=['json', 'mermaid'], default='json', help="Output format")
    
    args = parser.parse_args()
    
    # Initialize analyzer
    analyzer = GanttAnalyzer(args.tasks_dir)
    
    # Generate Gantt data
    gantt_data = analyzer.generate_gantt_data()
    
    # Save output
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    if args.format == 'json':
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(gantt_data, f, indent=2, default=str)
        print(f"Gantt data saved to {output_path}")
    
    elif args.format == 'mermaid':
        mermaid_output = generate_mermaid_gantt(gantt_data)
        mermaid_path = output_path.with_suffix('.mmd')
        with open(mermaid_path, 'w', encoding='utf-8') as f:
            f.write(mermaid_output)
        print(f"Mermaid Gantt diagram saved to {mermaid_path}")
    
    # Print summary
    timeline = gantt_data['project_timeline']
    print(f"\n📊 Project Summary:")
    print(f"   Total Tasks: {timeline['total_tasks']}")
    print(f"   Completion: {timeline['progress']:.1f}%")
    print(f"   Duration: {timeline['total_duration']} days")
    print(f"   Critical Path: {len(gantt_data['critical_path'])} tasks")
    
    if gantt_data['optimization_recommendations']:
        print(f"\n💡 Recommendations:")
        for rec in gantt_data['optimization_recommendations'][:3]:
            print(f"   {rec}")


def generate_mermaid_gantt(gantt_data: Dict[str, Any]) -> str:
    """Generate Mermaid.js Gantt diagram from data."""
    tasks = gantt_data['gantt_chart_data']['tasks']
    
    mermaid_lines = [
        "gantt",
        "    title Project Timeline",
        "    dateFormat YYYY-MM-DD",
        "    axisFormat %m/%d"
    ]
    
    # Group tasks by owner for sections
    sections = defaultdict(list)
    for task in tasks:
        section = task.get('owner', 'Unassigned')
        sections[section].append(task)
    
    for section_name, section_tasks in sections.items():
        if section_tasks:
            mermaid_lines.append(f"    section {section_name}")
            
            for task in section_tasks:
                status = ""
                if task.get('critical'):
                    status = "crit, "
                elif task.get('status') == 'completed':
                    status = "done, "
                elif task.get('status') == 'in_progress':
                    status = "active, "
                
                task_line = f"    {task['text']} :{status}{task['id']}, {task['start_date']}, {task['duration']}d"
                mermaid_lines.append(task_line)
    
    return "\n".join(mermaid_lines)


if __name__ == "__main__":
    main()
