# orchestration/gantt_analyzer.py

## Classes
- **GanttTask** (line 28)
- **ProjectTimeline** (line 49)
- **CriticalPathMethod** (line 63)
  - Methods: __init__, calculate_critical_path, _calculate_risk_factors, _build_dependency_graph, _forward_pass, _backward_pass, _order_critical_path
- **ResourceOptimizer** (line 273)
  - Methods: __init__, analyze_resource_utilization, _identify_critical_resources, _generate_optimization_recommendations, generate_resource_leveling_plan, _generate_leveling_recommendations, _generate_resource_recommendations, _calculate_optimization_score
- **ScenarioPlanner** (line 502)
  - Methods: __init__, analyze_timeline_scenarios, _analyze_current_scenario, _analyze_optimistic_scenario, _analyze_pessimistic_scenario, _analyze_resource_optimized_scenario, _calculate_scenario_resource_utilization, _generate_scenario_recommendations, _analyze_scenario_risks, _calculate_timeline_variance, _calculate_resource_risk, _calculate_completion_risk
- **GanttAnalyzer** (line 727)
  - Methods: __init__, load_tasks_from_yaml, _convert_to_gantt_task, _estimate_task_duration, _determine_task_status, _calculate_task_progress, generate_gantt_data, _generate_empty_gantt_data, _calculate_project_timeline, _format_for_gantt_chart, _generate_timeline_recommendations, _generate_critical_path_recommendations, _generate_parallelization_recommendations, _generate_milestone_alerts

## Functions
- **main()** (line 1120)
- **generate_mermaid_gantt(gantt_data)** (line 1168)
