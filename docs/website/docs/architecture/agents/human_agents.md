# agents/human_agents.py

## Classes
- **ReviewerRole** (line 23)
- **ReviewPriority** (line 37)
- **ReviewStatus** (line 46)
- **ReviewAssignment** (line 56)
  - Methods: __post_init__, is_expired, time_remaining, to_dict
- **AssignmentResult** (line 98)
- **WorkloadTracker** (line 105)
  - Methods: __init__, has_capacity, add_assignment, complete_assignment, get_workload_summary
- **HumanReviewerAgent** (line 168)
  - Methods: __init__, can_review, is_available, assign_review, estimate_review_duration, get_active_assignments, get_performance_summary
- **HumanAgentRegistry** (line 269)
  - Methods: __init__, _initialize_default_agents, register_agent, find_best_reviewer, assign_review, complete_assignment, get_registry_status, save_registry_state

## Functions
- **get_human_agent_registry()** (line 445)
- **assign_human_review(task_id, task_context, urgency, preferred_reviewer)** (line 450)
- **complete_human_review(task_id, reviewer_id)** (line 456)
- **get_available_reviewers(task_context)** (line 461)
