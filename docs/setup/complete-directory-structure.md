# Complete Directory Structure

Generated on: 2025-06-14 08:12:01

## Tree Structure (DFS Traversal)

```
ai-system/
├── .approved/
├── .claude/
│   ├── claude-code/
│   │   ├── .vscode/
│   │   │   └── extensions.json (155B, 8 lines)
│   │   ├── CHANGELOG.md (7.8K, 252 lines)
│   │   ├── demo.gif (15.6M)
│   │   ├── LICENSE.md (150B, 1 lines)
│   │   ├── package-lock.json (90B, 6 lines)
│   │   ├── README.md (2.1K, 41 lines)
│   │   └── SECURITY.md (693B, 12 lines)
│   └── settings.local.json (8.0K, 67 lines)
├── .vscode/
│   └── settings.json (689B, 24 lines)
├── agents/
│   ├── __init__.py (806B, 31 lines)
│   ├── backend.py (3.5K, 107 lines)
│   ├── coordinator.py (10.0K, 220 lines)
│   ├── doc.py (2.9K, 91 lines)
│   ├── factory.py (19.3K, 445 lines)
│   ├── frontend.py (3.0K, 90 lines)
│   ├── human_agents.py (18.4K, 489 lines)
│   ├── qa.py (19.2K, 499 lines)
│   └── technical.py (3.3K, 103 lines)
├── analytics/
│   ├── results/
│   │   ├── BE-07_analysis_20250611_004345.json (394B, 16 lines)
│   │   └── comprehensive_analysis_analysis_20250611_004337.json (454B, 19 lines)
│   ├── __init__.py (345B, 13 lines)
│   └── analyse_feedback.py (30.1K, 695 lines)
├── api/
│   ├── __init__.py (560B, 23 lines)
│   ├── external_integrations.py (33.3K, 891 lines)
│   ├── hitl_routes.py (53.2K, 1,471 lines)
│   └── webhook_manager.py (25.2K, 610 lines)
├── build/
│   ├── archives/
│   │   ├── cold/
│   │   └── warm/
│   ├── dashboard/
│   │   ├── dashboard/
│   │   ├── docs/
│   │   │   └── sprint/
│   │   │       └── briefings/
│   │   ├── logs/
│   │   ├── notifications/
│   │   ├── reports/
│   │   │   └── execution-summary.csv (100B)
│   │   ├── visualizations/
│   │   ├── agent_status.json (4.4K, 166 lines)
│   │   ├── COMPLETION_SUMMARY.md (2.9K, 64 lines)
│   │   ├── config.py (4.2K, 110 lines)
│   │   ├── enhanced_dashboard_working.js (98.6K, 2,545 lines)
│   │   ├── gantt_api.py (34.7K, 1,029 lines)
│   │   ├── gantt_chart_component.js (42.3K, 1,034 lines)
│   │   ├── gantt_chart_styles.css (13.6K, 763 lines)
│   │   ├── gantt_data.json (87.3K, 3,185 lines)
│   │   ├── hitl_data.json (6.5K, 170 lines)
│   │   ├── hitl_widgets.py (46.5K, 1,008 lines)
│   │   ├── live_execution.json (209B, 8 lines)
│   │   ├── test_charts.html (2.8K, 78 lines)
│   │   ├── test_dashboard.html (3.1K, 85 lines)
│   │   ├── unified_api_server.py (67.2K, 1,659 lines)
│   │   └── unified_dashboard.html (41.9K, 1,239 lines)
│   ├── data/
│   │   └── storage/
│   ├── reports/
│   ├── runtime/
│   │   ├── logs/
│   │   │   ├── daily_cycle/
│   │   │   └── langgraph/
│   │   │       ├── BE-07_qa_results.jsonl (1.7K)
│   │   │       └── BE-07_transitions.jsonl (1.7K)
│   │   ├── outputs/
│   │   └── temp/
│   ├── static/
│   ├── storage/
│   │   ├── cold/
│   │   ├── feedback/
│   │   ├── hitl/
│   │   │   └── audit.jsonl (220.5K)
│   │   ├── hitl_tasks/
│   │   ├── hot/
│   │   │   └── build_test_outputs_test_doc.md_0.dat (184B)
│   │   ├── warm/
│   │   └── storage_metadata.json (2B, 1 lines)
│   ├── templates/
│   │   └── email/
│   └── test_outputs/
├── cli/
│   ├── escalation_cli.py (12.6K, 316 lines)
│   ├── feedback_cli.py (10.3K, 271 lines)
│   ├── hitl_cli.py (25.6K, 665 lines)
│   ├── hitl_kanban_cli.py (13.1K, 439 lines)
│   ├── qa_cli.py (10.0K, 298 lines)
│   ├── qa_execution_cli.py (8.8K, 289 lines)
│   └── quick_hitl_status.py (8.7K, 263 lines)
├── config/
│   ├── schemas/
│   │   └── task.schema.json (4.1K, 90 lines)
│   ├── agents.yaml (4.1K, 122 lines)
│   ├── build_paths.py (2.3K, 82 lines)
│   ├── daily_cycle.json (593B, 24 lines)
│   ├── hitl_policies.yaml (7.2K, 250 lines)
│   ├── qa_thresholds.yaml (5.5K, 224 lines)
│   ├── tools.yaml (1.6K, 79 lines)
│   └── webhook_external_api_config.json (1.7K, 69 lines)
├── dashboard/
│   ├── notifications/
│   ├── __init__.py (596B, 23 lines)
│   ├── agent_status.json (4.4K, 167 lines)
│   ├── hitl_data.json (68.6K, 1,807 lines)
│   ├── hitl_kanban_board.html (21.4K, 667 lines)
│   ├── hitl_kanban_board.py (24.7K, 648 lines)
│   ├── hitl_kanban_demo.py (10.1K, 322 lines)
│   ├── hitl_widgets.py (19.2K, 491 lines)
│   ├── live_execution.json (207B, 8 lines)
│   └── unified_api_server.py (11.8K, 344 lines)
├── data/
│   ├── context/
│   │   ├── backend/
│   │   │   └── api-patterns.md (866B, 42 lines)
│   │   ├── db/
│   │   │   ├── db-schema-summary.md (1.1K, 28 lines)
│   │   │   ├── schema-summary.md (2.2K, 90 lines)
│   │   │   ├── schema.md (2.6K, 101 lines)
│   │   │   └── schema.sql (4.9K, 129 lines)
│   │   ├── design/
│   │   │   └── homepage-wireframe-summary.md (1.0K, 34 lines)
│   │   ├── frontend/
│   │   ├── infra/
│   │   │   ├── supabase-setup-summary.md (918B, 42 lines)
│   │   │   └── supabase-setup.md (2.0K, 86 lines)
│   │   ├── patterns/
│   │   │   ├── api-route-integration.md (2.8K, 110 lines)
│   │   │   ├── error-handling-pattern.md (1.6K, 60 lines)
│   │   │   ├── service-crud-operations.md (3.6K, 153 lines)
│   │   │   ├── service-layer-overview.md (2.2K, 70 lines)
│   │   │   ├── service-layer-pattern-summary.md (2.2K, 90 lines)
│   │   │   ├── service-layer-pattern.md (4.9K, 217 lines)
│   │   │   ├── service-layer-summary.md (753B, 32 lines)
│   │   │   ├── service-layer.md (1.6K, 61 lines)
│   │   │   ├── service-pattern.md (4.9K, 217 lines)
│   │   │   └── service-response-pattern.md (1.5K, 54 lines)
│   │   ├── product/
│   │   ├── sprint/
│   │   │   ├── day2-plan-summary.md (276B, 13 lines)
│   │   │   ├── day2-plan.md (1.8K, 69 lines)
│   │   │   ├── day3-plan.md (1.7K, 70 lines)
│   │   │   ├── day4-plan.md (1.6K, 69 lines)
│   │   │   ├── day5-plan.md (1.8K, 76 lines)
│   │   │   ├── pre_sprint0_tasks.md (33.9K, 672 lines)
│   │   │   ├── sprint-overview.md (1.0K, 34 lines)
│   │   │   ├── sprint-phase0-summary.md (1.2K, 27 lines)
│   │   │   └── sprint0_checklist.md (5.6K, 187 lines)
│   │   ├── technical/
│   │   │   ├── agent-architecture-summary.md (1.5K, 33 lines)
│   │   │   ├── agent-system-architecture.md (2.4K, 62 lines)
│   │   │   ├── knowledge_curation_workflow.md (4.8K, 105 lines)
│   │   │   ├── langgraph-workflow-architecture.md (2.7K, 97 lines)
│   │   │   ├── memory-engine-architecture.md (4.9K, 106 lines)
│   │   │   ├── memory-engine-summary.md (3.3K, 75 lines)
│   │   │   ├── system-overview.md (5.4K, 90 lines)
│   │   │   ├── system_architecture.md (6.8K, 140 lines)
│   │   │   ├── task-orchestration-architecture.md (3.2K, 99 lines)
│   │   │   └── tool-system-architecture.md (2.7K, 109 lines)
│   │   ├── agent-task-assignments.json (4B, 1 lines)
│   │   ├── agent_task_assignments.json (20.3K, 651 lines)
│   │   ├── db-schema.md (2.6K, 101 lines)
│   │   ├── large_files_chunking_audit.md (0B, 0 lines)
│   │   ├── pre_sprint0_tasks.md (33.9K, 672 lines)
│   │   ├── project-overview.md (0B, 0 lines)
│   │   ├── README.md (2.0K, 39 lines)
│   │   ├── service-pattern.md (4.9K, 217 lines)
│   │   ├── sprint0_checklist.md (5.6K, 187 lines)
│   │   └── workflow-patterns.md (0B, 0 lines)
│   ├── sprints/
│   │   ├── audit/
│   │   │   ├── report/
│   │   │   │   ├── code-architecture-quality-audit-completed.md (11.4K, 273 lines)
│   │   │   │   └── testability-audit-completed.md (12.5K, 323 lines)
│   │   │   ├── advanced-enhancements-audit.md (3.1K, 108 lines)
│   │   │   ├── cli-execution-layer-audit.md (3.2K, 109 lines)
│   │   │   ├── code-architecture-quality-audit.md (3.2K, 108 lines)
│   │   │   ├── code-quality-audit-completed.md (12.2K, 330 lines)
│   │   │   ├── code-review-memory-engine.md (22.2K, 142 lines)
│   │   │   ├── crewai-integration-audit.md (3.1K, 92 lines)
│   │   │   ├── external-tool-integration-audit.md (3.0K, 108 lines)
│   │   │   ├── implementation-gap-analysis-audit.md (3.9K, 141 lines)
│   │   │   ├── langgraph-task-orchestration-audit.md (2.4K, 73 lines)
│   │   │   ├── performance-security-audit.md (3.0K, 107 lines)
│   │   │   ├── protocol-alignment-audit.md (3.1K, 106 lines)
│   │   │   ├── technical-audit-summary.md (2.8K, 130 lines)
│   │   │   ├── testability-audit.md (3.1K, 108 lines)
│   │   │   └── testability-recommendations.md (5.6K, 198 lines)
│   │   ├── phase6_implementation_prompt.md (13.0K, 329 lines)
│   │   ├── phase6_technical_roadmap.md (14.1K, 450 lines)
│   │   ├── phase7_implementation_prompt.md (27.6K, 723 lines)
│   │   ├── sprint_phase0_setup.txt (3.6K, 76 lines)
│   │   ├── sprint_phase1_success.txt (3.8K, 71 lines)
│   │   ├── sprint_phase2_success.txt (6.1K, 131 lines)
│   │   ├── sprint_phase3_knowledge.txt (13.5K, 287 lines)
│   │   ├── sprint_phase4_execution.txt (9.4K, 223 lines)
│   │   ├── sprint_phase5_reporting.txt (10.3K, 237 lines)
│   │   ├── sprint_phase6_automation.txt (16.1K, 365 lines)
│   │   ├── sprint_phase7_Human-in-the-Loop.txt (65.7K, 1,408 lines)
│   │   ├── system_implementation.txt (44.5K, 1,637 lines)
│   │   └── technical-audit-tasks.md (13.3K, 296 lines)
│   ├── storage/
│   │   ├── cold/
│   │   │   └── context/
│   │   ├── escalations/
│   │   │   └── escalations.json (63.9K, 2,519 lines)
│   │   ├── hot/
│   │   │   └── context/
│   │   └── warm/
│   │       └── context/
│   └── templates/
│       └── email/
│           ├── eod_report.html (2.1K, 61 lines)
│           └── morning_briefing.html (2.3K, 64 lines)
├── deployment/
│   ├── build/
│   │   ├── archives/
│   │   │   ├── cold/
│   │   │   └── warm/
│   │   ├── dashboard/
│   │   │   ├── dashboard/
│   │   │   ├── docs/
│   │   │   │   └── sprint/
│   │   │   │       └── briefings/
│   │   │   ├── logs/
│   │   │   ├── notifications/
│   │   │   ├── reports/
│   │   │   │   ├── execution-summary.csv (100B)
│   │   │   │   └── execution-summary.csv.backup (100B)
│   │   │   ├── visualizations/
│   │   │   ├── agent_status.json (4.4K, 166 lines)
│   │   │   ├── agent_status.json.backup (4.4K)
│   │   │   ├── COMPLETION_SUMMARY.md (2.9K, 64 lines)
│   │   │   ├── COMPLETION_SUMMARY.md.backup (2.9K)
│   │   │   ├── config.py (4.2K, 110 lines)
│   │   │   ├── config.py.backup (4.2K)
│   │   │   ├── enhanced_dashboard_working.js (98.6K, 2,545 lines)
│   │   │   ├── enhanced_dashboard_working.js.backup (98.6K)
│   │   │   ├── gantt_api.py (34.7K, 1,029 lines)
│   │   │   ├── gantt_api.py.backup (34.7K)
│   │   │   ├── gantt_chart_component.js (42.3K, 1,034 lines)
│   │   │   ├── gantt_chart_component.js.backup (42.3K)
│   │   │   ├── gantt_chart_styles.css (13.6K, 763 lines)
│   │   │   ├── gantt_chart_styles.css.backup (13.6K)
│   │   │   ├── gantt_data.json (87.3K, 3,185 lines)
│   │   │   ├── gantt_data.json.backup (87.3K)
│   │   │   ├── hitl_data.json (6.5K, 170 lines)
│   │   │   ├── hitl_data.json.backup (6.5K)
│   │   │   ├── hitl_widgets.py (46.5K, 1,008 lines)
│   │   │   ├── hitl_widgets.py.backup (46.5K)
│   │   │   ├── live_execution.json (209B, 8 lines)
│   │   │   ├── live_execution.json.backup (209B)
│   │   │   ├── test_charts.html (2.8K, 78 lines)
│   │   │   ├── test_charts.html.backup (2.8K)
│   │   │   ├── test_dashboard.html (3.1K, 85 lines)
│   │   │   ├── test_dashboard.html.backup (3.1K)
│   │   │   ├── unified_api_server.py (67.2K, 1,659 lines)
│   │   │   ├── unified_api_server.py.backup (67.2K)
│   │   │   ├── unified_dashboard.html (41.9K, 1,239 lines)
│   │   │   └── unified_dashboard.html.backup (41.9K)
│   │   ├── data/
│   │   │   └── storage/
│   │   ├── reports/
│   │   ├── runtime/
│   │   │   ├── logs/
│   │   │   │   ├── daily_cycle/
│   │   │   │   └── langgraph/
│   │   │   │       ├── BE-07_qa_results.jsonl (1.7K)
│   │   │   │       ├── BE-07_qa_results.jsonl.backup (1.7K)
│   │   │   │       ├── BE-07_transitions.jsonl (1.7K)
│   │   │   │       └── BE-07_transitions.jsonl.backup (1.7K)
│   │   │   ├── outputs/
│   │   │   └── temp/
│   │   ├── static/
│   │   ├── storage/
│   │   │   ├── cold/
│   │   │   ├── feedback/
│   │   │   ├── hitl/
│   │   │   │   ├── audit.jsonl (220.5K)
│   │   │   │   └── audit.jsonl.backup (220.5K)
│   │   │   ├── hitl_tasks/
│   │   │   ├── hot/
│   │   │   │   ├── build_test_outputs_test_doc.md_0.dat (184B)
│   │   │   │   └── build_test_outputs_test_doc.md_0.dat.backup (184B)
│   │   │   ├── warm/
│   │   │   ├── storage_metadata.json (2B, 1 lines)
│   │   │   └── storage_metadata.json.backup (2B)
│   │   ├── templates/
│   │   │   └── email/
│   │   └── test_outputs/
│   ├── logs/
│   │   ├── daily_cycle/
│   │   └── langgraph/
│   │       ├── BE-07_qa_results.jsonl (5.6K)
│   │       ├── BE-07_qa_results.jsonl.backup (5.6K)
│   │       ├── BE-07_transitions.jsonl (5.5K)
│   │       └── BE-07_transitions.jsonl.backup (5.5K)
│   ├── outputs/
│   ├── reports/
│   │   ├── execution-summary.csv (118.8K)
│   │   └── execution-summary.csv.backup (118.8K)
│   ├── runtime/
│   │   ├── cache/
│   │   │   └── memory_disk_cache/
│   │   │       ├── metadata.json (4.7K, 147 lines)
│   │   │       └── metadata.json.backup (4.7K)
│   │   ├── chroma_db/
│   │   │   ├── chroma.sqlite3 (160.0K)
│   │   │   └── chroma.sqlite3.backup (160.0K)
│   │   ├── logs/
│   │   │   ├── context_usage/
│   │   │   ├── daily_cycle/
│   │   │   └── langgraph/
│   │   ├── outputs/
│   │   ├── progress_reports/
│   │   │   ├── daily_report_2025-04-02.md (408B, 15 lines)
│   │   │   ├── daily_report_2025-04-02.md.backup (408B)
│   │   │   ├── daily_report_2025-04-03.md (407B, 15 lines)
│   │   │   ├── daily_report_2025-04-03.md.backup (407B)
│   │   │   ├── daily_report_2025-05-28.md (560B, 17 lines)
│   │   │   ├── daily_report_2025-05-28.md.backup (560B)
│   │   │   ├── daily_report_2025-05-29.md (958B, 33 lines)
│   │   │   ├── daily_report_2025-05-29.md.backup (958B)
│   │   │   ├── daily_report_2025-05-30.md (405B, 15 lines)
│   │   │   ├── daily_report_2025-05-30.md.backup (405B)
│   │   │   ├── daily_report_2025-05-31.md (407B, 15 lines)
│   │   │   ├── daily_report_2025-05-31.md.backup (407B)
│   │   │   ├── daily_report_2025-06-01.md (804B, 31 lines)
│   │   │   ├── daily_report_2025-06-01.md.backup (804B)
│   │   │   ├── daily_report_2025-06-02.md (804B, 31 lines)
│   │   │   ├── daily_report_2025-06-02.md.backup (804B)
│   │   │   ├── day2_eod_report_2025-04-02.md (3.3K, 108 lines)
│   │   │   ├── day2_eod_report_2025-04-02.md.backup (3.3K)
│   │   │   ├── day2_report_2025-04-02.md (560B, 17 lines)
│   │   │   ├── day2_report_2025-04-02.md.backup (560B)
│   │   │   ├── day3_eod_report_2025-04-03.md (3.3K, 108 lines)
│   │   │   ├── day3_eod_report_2025-04-03.md.backup (3.3K)
│   │   │   ├── day60_eod_report_2025-05-30.md (3.3K, 108 lines)
│   │   │   ├── day60_eod_report_2025-05-30.md.backup (3.3K)
│   │   │   ├── day61_eod_report_2025-05-31.md (3.3K, 108 lines)
│   │   │   ├── day61_eod_report_2025-05-31.md.backup (3.3K)
│   │   │   ├── day62_eod_report_2025-06-01.md (2.9K, 109 lines)
│   │   │   ├── day62_eod_report_2025-06-01.md.backup (2.9K)
│   │   │   ├── summary_report_2025-05-28.md (741B, 30 lines)
│   │   │   └── summary_report_2025-05-28.md.backup (741B)
│   │   ├── reports/
│   │   │   ├── qa/
│   │   │   │   ├── BE-07_qa_report.json (1.2K, 43 lines)
│   │   │   │   └── BE-07_qa_report.json.backup (1.2K)
│   │   │   ├── context-coverage.json (11.3K, 1,166 lines)
│   │   │   ├── context-coverage.json.backup (11.3K)
│   │   │   ├── coverage_dashboard.html (1.5K, 46 lines)
│   │   │   ├── coverage_dashboard.html.backup (1.5K)
│   │   │   ├── execution-summary.csv (679.8K)
│   │   │   ├── execution-summary.csv.backup (679.8K)
│   │   │   ├── step_3_9_demo_coverage.csv (2.0K)
│   │   │   ├── step_3_9_demo_coverage.csv.backup (2.0K)
│   │   │   ├── step_3_9_demo_coverage.html (10.1K, 205 lines)
│   │   │   ├── step_3_9_demo_coverage.html.backup (10.1K)
│   │   │   ├── step_3_9_demo_coverage.json (11.3K, 1,166 lines)
│   │   │   ├── step_3_9_demo_coverage.json.backup (11.3K)
│   │   │   ├── step_3_9_test_coverage.csv (2.0K)
│   │   │   ├── step_3_9_test_coverage.csv.backup (2.0K)
│   │   │   ├── step_3_9_test_coverage.html (10.1K, 206 lines)
│   │   │   ├── step_3_9_test_coverage.html.backup (10.1K)
│   │   │   ├── step_3_9_test_coverage.json (11.3K, 1,166 lines)
│   │   │   ├── step_3_9_test_coverage.json.backup (11.3K)
│   │   │   ├── task_graph.png (505.3K)
│   │   │   └── task_graph.png.backup (505.3K)
│   │   ├── temp/
│   │   │   └── mock-api-key/
│   │   ├── test_logs/
│   │   │   └── daily_cycle/
│   │   └── test_outputs/
│   └── storage/
│       ├── cold/
│       ├── feedback/
│       ├── hitl/
│       ├── hitl_tasks/
│       ├── hot/
│       ├── warm/
│       ├── storage_metadata.json (918B, 28 lines)
│       └── storage_metadata.json.backup (918B)
├── docs/
│   ├── admin/
│   │   ├── CODE_QUALITY_IMPROVEMENTS_SUMMARY.md (7.6K, 207 lines)
│   │   ├── MEMORY_ENGINE_REFACTORING_SUMMARY.md (5.1K, 142 lines)
│   │   ├── test_cleanup_summary.md (3.7K, 104 lines)
│   │   ├── test_results_summary.md (5.0K, 153 lines)
│   │   └── test_structure_fix_summary.md (3.6K, 108 lines)
│   ├── architecture/
│   │   └── modernization-plan.md (31.9K, 916 lines)
│   ├── completions/
│   │   ├── BE-07.json (2.4K, 84 lines)
│   │   ├── BE-07.md (1.7K, 60 lines)
│   │   ├── EXAMPLE-01.md (2.1K, 105 lines)
│   │   └── PHASE7_STEP7.4_COMPLETION_SUMMARY.md (10.5K, 295 lines)
│   ├── optimizations/
│   │   └── PHASE2_COMPLETE_DOCUMENTATION.md (24.9K, 673 lines)
│   ├── setup/
│   │   ├── complete-directory-structure.md (81.4K, 1,523 lines)
│   │   └── directory-structure.md (8.8K, 292 lines)
│   ├── sprint/
│   │   ├── briefings/
│   │   │   ├── day1-morning-briefing.md (2.9K, 70 lines)
│   │   │   ├── day2-morning-briefing.md (537B, 22 lines)
│   │   │   └── day3-morning-briefing.md (2.9K, 69 lines)
│   │   ├── daily_reports/
│   │   │   ├── eod_report_2025-05-29_20250529_005605.markdown (1.2K)
│   │   │   ├── eod_report_2025-05-29_20250529_010208.markdown (1.2K)
│   │   │   ├── eod_report_2025-05-29_20250529_010430.markdown (1.2K)
│   │   │   ├── eod_report_2025-05-29_20250529_013718.markdown (1.2K)
│   │   │   ├── eod_report_2025-05-29_20250529_013926.markdown (1.2K)
│   │   │   ├── eod_report_2025-05-29_20250529_014049.markdown (1.2K)
│   │   │   ├── eod_report_2025-06-01_20250601_135924.markdown (1.2K)
│   │   │   ├── eod_report_2025-06-01_20250601_140644.markdown (1.2K)
│   │   │   ├── eod_report_2025-06-01_20250601_181246.markdown (1.2K)
│   │   │   └── eod_report_2025-06-02_20250602_200441.markdown (1.2K)
│   │   ├── BRIEFING_GENERATOR_API.md (7.8K, 258 lines)
│   │   └── PHASE6_COMPLETION_REPORT.md (4.7K, 121 lines)
│   ├── tools/
│   │   ├── __init__.md (45B, 3 lines)
│   │   ├── base_tool.md (1.3K, 36 lines)
│   │   ├── context_tracker.md (1008B, 22 lines)
│   │   ├── context_visualizer.md (779B, 21 lines)
│   │   ├── coverage_tool.md (1.1K, 30 lines)
│   │   ├── cypress_tool.md (819B, 24 lines)
│   │   ├── design_system_tool.md (146B, 6 lines)
│   │   ├── echo_tool.md (880B, 32 lines)
│   │   ├── fixed_retrieval_qa.md (162B, 6 lines)
│   │   ├── github_tool.md (112B, 6 lines)
│   │   ├── jest_tool.md (494B, 18 lines)
│   │   ├── markdown_tool.md (123B, 6 lines)
│   │   ├── memory_engine.md (744B, 38 lines)
│   │   ├── memory_engine_examples.md (624B, 19 lines)
│   │   ├── qa_cli.md (638B, 16 lines)
│   │   ├── rate_limiter.md (177B, 8 lines)
│   │   ├── retrieval_qa.md (128B, 6 lines)
│   │   ├── supabase_tool.md (649B, 22 lines)
│   │   ├── tailwind_tool.md (127B, 6 lines)
│   │   ├── tool_loader.md (1.2K, 35 lines)
│   │   └── vercel_tool.md (111B, 6 lines)
│   ├── agent_architecture.md (3.6K, 115 lines)
│   ├── agent_builder.md (2.0K, 40 lines)
│   ├── agent_factory_refactoring_summary.md (4.8K, 156 lines)
│   ├── agent_system_overview.md (2.1K, 42 lines)
│   ├── api_reference.md (1.4K, 33 lines)
│   ├── backend_agent.md (1000B, 20 lines)
│   ├── class_dictionary.md (1.3K, 54 lines)
│   ├── configuration_reference.md (1.6K, 35 lines)
│   ├── coordinator_agent.md (917B, 17 lines)
│   ├── COORDINATOR_IMPROVEMENTS.md (7.2K, 181 lines)
│   ├── daily_cycle_orchestrator.md (3.3K, 78 lines)
│   ├── dependency_map.md (1.2K, 37 lines)
│   ├── documentation_agent.md (861B, 20 lines)
│   ├── documentation_completeness.md (507B, 17 lines)
│   ├── documentation_index.md (2.8K, 40 lines)
│   ├── documentation_search_index.md (2.0K, 76 lines)
│   ├── ERROR_HANDLING_IMPROVEMENTS.md (11.0K, 327 lines)
│   ├── error_propagation_strategy.md (9.2K, 257 lines)
│   ├── FILE_ORGANIZATION_IMPROVEMENTS.md (7.5K, 210 lines)
│   ├── frontend_agent.md (912B, 20 lines)
│   ├── function_dictionary.md (1.1K, 38 lines)
│   ├── graph_visualization.md (9.5K, 284 lines)
│   ├── hitl_kanban_dashboard.md (9.3K, 344 lines)
│   ├── INDEX.md (7.3K, 143 lines)
│   ├── INPUT_VALIDATION_IMPLEMENTATION_SUMMARY.md (8.7K, 225 lines)
│   ├── knowledge_curation_workflow.md (4.8K, 105 lines)
│   ├── langgraph_workflow.md (11.2K, 392 lines)
│   ├── main_entry_point.md (3.2K, 66 lines)
│   ├── MASTER_DOCUMENTATION_GUIDE.md (6.0K, 175 lines)
│   ├── memory_engine.md (16.0K, 354 lines)
│   ├── module_dictionary.md (1.3K, 59 lines)
│   ├── phase6_enhanced_eod_reporting_guide.md (15.0K, 498 lines)
│   ├── PHASE6_STEP6.3_COMPLETION_SUMMARY.md (6.5K, 158 lines)
│   ├── PHASE6_STEP6.5_COMPLETION_SUMMARY.md (9.7K, 206 lines)
│   ├── PHASE6_STEP6.6_EMAIL_INTEGRATION_COMPLETION.md (9.2K, 229 lines)
│   ├── PHASE7_STEPS7.2-7.3_COMPLETION_SUMMARY.md (11.6K, 232 lines)
│   ├── qa_agent.md (1.1K, 22 lines)
│   ├── quick_reference_cards.md (1.2K, 36 lines)
│   ├── retrieval_qa_usage.md (5.9K, 190 lines)
│   ├── SCHEMA_UTILITIES_CONSOLIDATION.md (7.5K, 224 lines)
│   ├── symbol_index.md (655B, 11 lines)
│   ├── system_architecture.md (6.8K, 140 lines)
│   ├── task_loader.md (1.2K, 32 lines)
│   ├── task_orchestration.md (16.2K, 474 lines)
│   ├── technical_lead_agent.md (905B, 20 lines)
│   ├── testing_best_practices.md (6.5K, 218 lines)
│   ├── thread_safety_implementation_summary.md (9.6K, 240 lines)
│   ├── tools_system.md (8.6K, 238 lines)
│   ├── visual_documentation.md (1023B, 20 lines)
│   ├── workflow_executor.md (1.6K, 24 lines)
│   ├── workflow_monitoring.md (5.7K, 178 lines)
│   └── workflow_task_system.md (12.1K, 191 lines)
├── examples/
│   ├── agent_output_demo.py (3.3K, 85 lines)
│   ├── agent_summarization_demo.py (13.9K, 420 lines)
│   ├── annotate_context_tags_tasks.py (13.3K, 353 lines)
│   ├── code_extraction_demo.py (4.2K, 150 lines)
│   ├── complete_validation.py (11.9K, 329 lines)
│   ├── context_tracking_functionality.py (10.2K, 301 lines)
│   ├── daily_cycle_demo.py (3.7K, 91 lines)
│   ├── hitl_cli_demo.py (15.6K, 393 lines)
│   ├── human-in-the-Loop_context_review.py (8.5K, 245 lines)
│   ├── langChain_characterTextSplitter.py (5.8K, 145 lines)
│   ├── mcp_context_usage.py (9.2K, 273 lines)
│   ├── qa_execution_demo.py (10.5K, 323 lines)
│   ├── register_agent_output_demo.py (22.9K, 633 lines)
│   ├── task_declaration_preparation.py (13.4K, 385 lines)
│   └── visualise_context_coverage.py (11.1K, 310 lines)
├── graph/
│   ├── auto_generate_graph.py (11.9K, 333 lines)
│   ├── auto_generated_graph.json (1.1K, 67 lines)
│   ├── critical_path.html (993B, 33 lines)
│   ├── critical_path.json (1009B, 44 lines)
│   ├── critical_path.mmd (703B)
│   ├── critical_path.yaml (723B, 32 lines)
│   ├── flow.py (4.0K, 135 lines)
│   ├── graph_builder.py (27.7K, 691 lines)
│   ├── handlers.py (19.9K, 566 lines)
│   ├── interrupt_nodes.py (17.2K, 471 lines)
│   ├── notifications.py (11.0K, 314 lines)
│   ├── resilient_workflow.py (8.0K, 234 lines)
│   └── visualize.py (2.8K, 88 lines)
├── handlers/
│   └── qa_handler.py (1.3K, 46 lines)
├── logs/
│   ├── daily_cycle/
│   └── langgraph/
│       ├── BE-07_qa_results.jsonl (5.6K)
│       └── BE-07_transitions.jsonl (5.5K)
├── memory-bank/
│   ├── activeContext.md (7.5K, 150 lines)
│   ├── productContext.md (4.4K, 96 lines)
│   ├── progress.md (8.7K, 227 lines)
│   ├── projectbrief.md (2.6K, 57 lines)
│   ├── README.md (6.7K, 200 lines)
│   ├── systemPatterns.md (9.5K, 212 lines)
│   └── techContext.md (8.6K, 266 lines)
├── orchestration/
│   ├── __init__.py (586B, 23 lines)
│   ├── automation_health_check.py (16.8K, 431 lines)
│   ├── complete_task.py (24.0K, 645 lines)
│   ├── daily_cycle.py (28.0K, 687 lines)
│   ├── delegation.py (3.8K, 126 lines)
│   ├── documentation_agent.py (27.8K, 768 lines)
│   ├── email_integration.py (22.6K, 561 lines)
│   ├── end_of_day_report.py (25.5K, 595 lines)
│   ├── enhanced_workflow.py (17.5K, 468 lines)
│   ├── error_handling.py (20.7K, 505 lines)
│   ├── execute_graph.py (31.5K, 817 lines)
│   ├── execute_task.py (9.0K, 260 lines)
│   ├── execute_workflow.py (16.9K, 482 lines)
│   ├── extract_code.py (18.4K, 501 lines)
│   ├── gantt_analyzer.py (49.1K, 1,205 lines)
│   ├── generate_briefing.py (35.8K, 886 lines)
│   ├── generate_prompt.py (10.9K, 289 lines)
│   ├── hitl_engine.py (60.9K, 1,430 lines)
│   ├── hitl_task_metadata.py (18.4K, 452 lines)
│   ├── inject_context.py (6.4K, 200 lines)
│   ├── langgraph_qa_integration.py (9.4K, 273 lines)
│   ├── notification_handlers.py (23.4K, 547 lines)
│   ├── plan_execution_manager.py (11.2K, 260 lines)
│   ├── qa_execution.py (14.9K, 440 lines)
│   ├── qa_validation.py (25.5K, 700 lines)
│   ├── register_output.py (22.5K, 589 lines)
│   ├── registry.py (9.4K, 266 lines)
│   ├── review_context.py (7.9K, 222 lines)
│   ├── review_context_simple.py (7.9K, 223 lines)
│   ├── review_task.py (42.1K, 1,075 lines)
│   ├── run_workflow.py (6.9K, 218 lines)
│   ├── scalable_storage.py (7.6K, 233 lines)
│   ├── sprint_visualizer.py (18.4K, 484 lines)
│   ├── states.py (5.9K, 179 lines)
│   ├── summarise_task.py (26.8K, 758 lines)
│   ├── task_declaration.py (29.3K, 756 lines)
│   ├── task_lifecycle.py (19.5K, 525 lines)
│   └── thread_safe_workflow.py (21.3K, 576 lines)
├── outputs/
├── patches/
│   ├── __init__.py (1.3K, 48 lines)
│   ├── chromadb_telemetry_patch.py (1.4K, 46 lines)
│   └── README.md (1.5K, 46 lines)
├── pending_reviews/
├── progress_reports/
├── prompts/
│   ├── backend-agent.md (1.2K, 40 lines)
│   ├── coordinator.md (1.3K, 43 lines)
│   ├── doc-agent.md (1.8K, 71 lines)
│   ├── frontend-agent.md (1.7K, 57 lines)
│   ├── product-manager.md (1.4K, 46 lines)
│   ├── qa-agent.md (2.1K, 70 lines)
│   ├── technical-architect.md (2.5K, 71 lines)
│   ├── utils.py (5.1K, 159 lines)
│   └── ux-designer.md (1.5K, 45 lines)
├── reports/
│   └── execution-summary.csv (118.8K)
├── reviews/
│   ├── qa_BE-07.md (116B, 7 lines)
│   ├── qa_BE-07.md.meta.json (119B, 6 lines)
│   ├── qa_BE-08.md (96B, 7 lines)
│   └── qa_BE-08.md.meta.json (119B, 6 lines)
├── runtime/
│   ├── cache/
│   │   └── memory_disk_cache/
│   │       └── metadata.json (4.7K, 147 lines)
│   ├── chroma_db/
│   │   └── chroma.sqlite3 (160.0K)
│   ├── logs/
│   │   ├── context_usage/
│   │   ├── daily_cycle/
│   │   └── langgraph/
│   ├── outputs/
│   ├── progress_reports/
│   │   ├── daily_report_2025-04-02.md (408B, 15 lines)
│   │   ├── daily_report_2025-04-03.md (407B, 15 lines)
│   │   ├── daily_report_2025-05-28.md (560B, 17 lines)
│   │   ├── daily_report_2025-05-29.md (958B, 33 lines)
│   │   ├── daily_report_2025-05-30.md (405B, 15 lines)
│   │   ├── daily_report_2025-05-31.md (407B, 15 lines)
│   │   ├── daily_report_2025-06-01.md (804B, 31 lines)
│   │   ├── daily_report_2025-06-02.md (804B, 31 lines)
│   │   ├── day2_eod_report_2025-04-02.md (3.3K, 108 lines)
│   │   ├── day2_report_2025-04-02.md (560B, 17 lines)
│   │   ├── day3_eod_report_2025-04-03.md (3.3K, 108 lines)
│   │   ├── day60_eod_report_2025-05-30.md (3.3K, 108 lines)
│   │   ├── day61_eod_report_2025-05-31.md (3.3K, 108 lines)
│   │   ├── day62_eod_report_2025-06-01.md (2.9K, 109 lines)
│   │   └── summary_report_2025-05-28.md (741B, 30 lines)
│   ├── reports/
│   │   ├── qa/
│   │   │   └── BE-07_qa_report.json (1.2K, 43 lines)
│   │   ├── context-coverage.json (11.3K, 1,166 lines)
│   │   ├── coverage_dashboard.html (1.5K, 46 lines)
│   │   ├── execution-summary.csv (679.8K)
│   │   ├── step_3_9_demo_coverage.csv (2.0K)
│   │   ├── step_3_9_demo_coverage.html (10.1K, 205 lines)
│   │   ├── step_3_9_demo_coverage.json (11.3K, 1,166 lines)
│   │   ├── step_3_9_test_coverage.csv (2.0K)
│   │   ├── step_3_9_test_coverage.html (10.1K, 206 lines)
│   │   ├── step_3_9_test_coverage.json (11.3K, 1,166 lines)
│   │   └── task_graph.png (505.3K)
│   ├── temp/
│   │   └── mock-api-key/
│   ├── test_logs/
│   │   └── daily_cycle/
│   └── test_outputs/
├── scripts/
│   ├── validation/
│   │   ├── validate_canvas_height_fix.py (6.5K, 161 lines)
│   │   ├── validate_canvas_height_fix_final.py (6.4K, 161 lines)
│   │   ├── validate_chart_fix.py (11.0K, 269 lines)
│   │   ├── validate_dashboard_final.py (7.8K, 212 lines)
│   │   ├── validate_dashboard_loading_fix.py (7.8K, 189 lines)
│   │   ├── validate_dashboard_stability.py (7.3K, 217 lines)
│   │   ├── validate_hitl_dashboard.py (10.3K, 302 lines)
│   │   └── validate_remaining_loading_fix.py (9.8K, 220 lines)
│   ├── archive_task.py (10.6K, 314 lines)
│   ├── batch_qa_generation.py (5.7K, 170 lines)
│   ├── debug_extraction_patterns.py (5.0K, 195 lines)
│   ├── debug_memory.py (2.2K, 74 lines)
│   ├── end_to_end_test.py (12.6K, 394 lines)
│   ├── generate_complete_tree.py (8.0K, 240 lines)
│   ├── generate_progress_report.py (21.6K, 519 lines)
│   ├── generate_task_report.py (36.8K, 927 lines)
│   ├── github_finalise.py (11.5K, 330 lines)
│   ├── list_pending_reviews.py (2.1K, 67 lines)
│   ├── manage_knowledge_reviews.py (6.3K, 194 lines)
│   ├── mark_review_complete.py (3.1K, 92 lines)
│   ├── mock_dependencies.py (16.1K, 440 lines)
│   ├── monitor_workflow.py (24.1K, 666 lines)
│   ├── patch_dotenv.py (1.7K, 58 lines)
│   ├── run_optimized_tests_enhanced.py (6.8K, 203 lines)
│   ├── setup_context_for_testing.py (9.1K, 346 lines)
│   ├── test_sprint_phases.py (6.3K, 203 lines)
│   ├── update_dashboard.py (13.0K, 316 lines)
│   ├── visualize_directory_tree.py (14.7K, 433 lines)
│   └── visualize_task_graph.py (14.0K, 464 lines)
├── src/
│   ├── core/
│   │   ├── agents/
│   │   │   ├── __init__.py (11.2K, 305 lines)
│   │   │   ├── __init__.py.backup (806B)
│   │   │   ├── backend.py (3.4K, 108 lines)
│   │   │   ├── backend.py.backup (3.5K)
│   │   │   ├── coordinator.py (10.0K, 220 lines)
│   │   │   ├── coordinator.py.backup (10.0K)
│   │   │   ├── doc.py (3.0K, 91 lines)
│   │   │   ├── doc.py.backup (2.9K)
│   │   │   ├── factory.py (19.3K, 444 lines)
│   │   │   ├── factory.py.backup (19.3K)
│   │   │   ├── frontend.py (3.0K, 90 lines)
│   │   │   ├── frontend.py.backup (3.0K)
│   │   │   ├── human_agents.py (18.4K, 489 lines)
│   │   │   ├── human_agents.py.backup (18.4K)
│   │   │   ├── qa.py (19.2K, 499 lines)
│   │   │   ├── qa.py.backup (19.2K)
│   │   │   ├── technical.py (3.4K, 103 lines)
│   │   │   └── technical.py.backup (3.3K)
│   │   ├── states/
│   │   │   └── __init__.py (28B, 1 lines)
│   │   ├── tasks/
│   │   │   ├── backend/
│   │   │   │   ├── __init__.py (28B, 1 lines)
│   │   │   │   ├── BE-07.json (467B, 17 lines)
│   │   │   │   └── BE-07.json.backup (467B)
│   │   │   ├── frontend/
│   │   │   │   └── __init__.py (28B, 1 lines)
│   │   │   ├── general/
│   │   │   │   ├── __init__.py (28B, 1 lines)
│   │   │   │   ├── TEST-07.json (427B, 16 lines)
│   │   │   │   └── TEST-07.json.backup (427B)
│   │   │   ├── qa/
│   │   │   │   └── __init__.py (28B, 1 lines)
│   │   │   ├── technical_lead/
│   │   │   │   └── __init__.py (28B, 1 lines)
│   │   │   ├── __init__.py (28B, 1 lines)
│   │   │   ├── BE-01.yaml (563B, 20 lines)
│   │   │   ├── BE-01.yaml.backup (563B)
│   │   │   ├── BE-02.yaml (396B, 17 lines)
│   │   │   ├── BE-02.yaml.backup (396B)
│   │   │   ├── BE-03.yaml (453B, 18 lines)
│   │   │   ├── BE-03.yaml.backup (453B)
│   │   │   ├── BE-04.yaml (397B, 17 lines)
│   │   │   ├── BE-04.yaml.backup (397B)
│   │   │   ├── BE-05.yaml (463B, 18 lines)
│   │   │   ├── BE-05.yaml.backup (463B)
│   │   │   ├── BE-06.yaml (360B, 15 lines)
│   │   │   ├── BE-06.yaml.backup (360B)
│   │   │   ├── BE-07.yaml (526B, 25 lines)
│   │   │   ├── BE-07.yaml.backup (526B)
│   │   │   ├── BE-08.yaml (453B, 18 lines)
│   │   │   ├── BE-08.yaml.backup (453B)
│   │   │   ├── BE-09.yaml (393B, 18 lines)
│   │   │   ├── BE-09.yaml.backup (393B)
│   │   │   ├── BE-10.yaml (409B, 17 lines)
│   │   │   ├── BE-10.yaml.backup (409B)
│   │   │   ├── BE-11.yaml (407B, 17 lines)
│   │   │   ├── BE-11.yaml.backup (407B)
│   │   │   ├── BE-12.yaml (365B, 16 lines)
│   │   │   ├── BE-12.yaml.backup (365B)
│   │   │   ├── BE-13.yaml (371B, 16 lines)
│   │   │   ├── BE-13.yaml.backup (371B)
│   │   │   ├── BE-14.yaml (435B, 18 lines)
│   │   │   ├── BE-14.yaml.backup (435B)
│   │   │   ├── FE-01.yaml (402B, 17 lines)
│   │   │   ├── FE-01.yaml.backup (402B)
│   │   │   ├── FE-02.yaml (502B, 21 lines)
│   │   │   ├── FE-02.yaml.backup (502B)
│   │   │   ├── FE-03.yaml (404B, 16 lines)
│   │   │   ├── FE-03.yaml.backup (404B)
│   │   │   ├── FE-04.yaml (471B, 19 lines)
│   │   │   ├── FE-04.yaml.backup (471B)
│   │   │   ├── FE-05.yaml (462B, 18 lines)
│   │   │   ├── FE-05.yaml.backup (462B)
│   │   │   ├── FE-06.yaml (366B, 15 lines)
│   │   │   ├── FE-06.yaml.backup (366B)
│   │   │   ├── LC-01.yaml (381B, 13 lines)
│   │   │   ├── LC-01.yaml.backup (381B)
│   │   │   ├── missing_context_topics_report.md (0B, 0 lines)
│   │   │   ├── missing_context_topics_report.md.backup (0B)
│   │   │   ├── PM-01.yaml (350B, 13 lines)
│   │   │   ├── PM-01.yaml.backup (350B)
│   │   │   ├── PM-02.yaml (397B, 15 lines)
│   │   │   ├── PM-02.yaml.backup (397B)
│   │   │   ├── PM-03.yaml (365B, 13 lines)
│   │   │   ├── PM-03.yaml.backup (365B)
│   │   │   ├── PM-04.yaml (379B, 15 lines)
│   │   │   ├── PM-04.yaml.backup (379B)
│   │   │   ├── PM-05.yaml (335B, 14 lines)
│   │   │   ├── PM-05.yaml.backup (335B)
│   │   │   ├── PM-06.yaml (369B, 13 lines)
│   │   │   ├── PM-06.yaml.backup (369B)
│   │   │   ├── PM-07.yaml (380B, 15 lines)
│   │   │   ├── PM-07.yaml.backup (380B)
│   │   │   ├── PM-08.yaml (351B, 13 lines)
│   │   │   ├── PM-08.yaml.backup (351B)
│   │   │   ├── PM-09.yaml (427B, 17 lines)
│   │   │   ├── PM-09.yaml.backup (427B)
│   │   │   ├── PM-10.yaml (360B, 13 lines)
│   │   │   ├── PM-10.yaml.backup (360B)
│   │   │   ├── PM-11.yaml (342B, 13 lines)
│   │   │   ├── PM-11.yaml.backup (342B)
│   │   │   ├── PM-12.yaml (356B, 14 lines)
│   │   │   ├── PM-12.yaml.backup (356B)
│   │   │   ├── QA-01.yaml (356B, 15 lines)
│   │   │   ├── QA-01.yaml.backup (356B)
│   │   │   ├── QA-02.yaml (427B, 19 lines)
│   │   │   ├── QA-02.yaml.backup (427B)
│   │   │   ├── QA-03.yaml (363B, 15 lines)
│   │   │   ├── QA-03.yaml.backup (363B)
│   │   │   ├── task-schema.json (1.9K, 67 lines)
│   │   │   ├── task-schema.json.backup (1.9K)
│   │   │   ├── TL-01.yaml (403B, 15 lines)
│   │   │   ├── TL-01.yaml.backup (403B)
│   │   │   ├── TL-02.yaml (381B, 16 lines)
│   │   │   ├── TL-02.yaml.backup (381B)
│   │   │   ├── TL-03.yaml (490B, 19 lines)
│   │   │   ├── TL-03.yaml.backup (490B)
│   │   │   ├── TL-04.yaml (379B, 16 lines)
│   │   │   ├── TL-04.yaml.backup (379B)
│   │   │   ├── TL-05.yaml (469B, 19 lines)
│   │   │   ├── TL-05.yaml.backup (469B)
│   │   │   ├── TL-06.yaml (373B, 16 lines)
│   │   │   ├── TL-06.yaml.backup (373B)
│   │   │   ├── TL-07.yaml (417B, 17 lines)
│   │   │   ├── TL-07.yaml.backup (417B)
│   │   │   ├── TL-08.yaml (422B, 19 lines)
│   │   │   ├── TL-08.yaml.backup (422B)
│   │   │   ├── TL-09.yaml (564B, 19 lines)
│   │   │   ├── TL-09.yaml.backup (564B)
│   │   │   ├── TL-10.yaml (374B, 16 lines)
│   │   │   ├── TL-10.yaml.backup (374B)
│   │   │   ├── TL-11.yaml (418B, 16 lines)
│   │   │   ├── TL-11.yaml.backup (418B)
│   │   │   ├── TL-12.yaml (376B, 15 lines)
│   │   │   ├── TL-12.yaml.backup (376B)
│   │   │   ├── TL-13.yaml (420B, 19 lines)
│   │   │   ├── TL-13.yaml.backup (420B)
│   │   │   ├── TL-14.yaml (401B, 17 lines)
│   │   │   ├── TL-14.yaml.backup (401B)
│   │   │   ├── TL-15.yaml (471B, 19 lines)
│   │   │   ├── TL-15.yaml.backup (471B)
│   │   │   ├── TL-16.yaml (460B, 20 lines)
│   │   │   ├── TL-16.yaml.backup (460B)
│   │   │   ├── TL-17.yaml (411B, 16 lines)
│   │   │   ├── TL-17.yaml.backup (411B)
│   │   │   ├── TL-18.yaml (445B, 18 lines)
│   │   │   ├── TL-18.yaml.backup (445B)
│   │   │   ├── TL-19.yaml (410B, 17 lines)
│   │   │   ├── TL-19.yaml.backup (410B)
│   │   │   ├── TL-20.yaml (428B, 17 lines)
│   │   │   ├── TL-20.yaml.backup (428B)
│   │   │   ├── TL-21.yaml (418B, 18 lines)
│   │   │   ├── TL-21.yaml.backup (418B)
│   │   │   ├── TL-22.yaml (407B, 18 lines)
│   │   │   ├── TL-22.yaml.backup (407B)
│   │   │   ├── TL-23.yaml (408B, 17 lines)
│   │   │   ├── TL-23.yaml.backup (408B)
│   │   │   ├── TL-24.yaml (375B, 16 lines)
│   │   │   ├── TL-24.yaml.backup (375B)
│   │   │   ├── TL-25.yaml (394B, 16 lines)
│   │   │   ├── TL-25.yaml.backup (394B)
│   │   │   ├── TL-26.yaml (371B, 15 lines)
│   │   │   ├── TL-26.yaml.backup (371B)
│   │   │   ├── TL-27.yaml (395B, 16 lines)
│   │   │   ├── TL-27.yaml.backup (395B)
│   │   │   ├── TL-28.yaml (416B, 18 lines)
│   │   │   ├── TL-28.yaml.backup (416B)
│   │   │   ├── TL-29.yaml (419B, 18 lines)
│   │   │   ├── TL-29.yaml.backup (419B)
│   │   │   ├── TL-30.yaml (357B, 15 lines)
│   │   │   ├── TL-30.yaml.backup (357B)
│   │   │   ├── UX-01.yaml (388B, 14 lines)
│   │   │   ├── UX-01.yaml.backup (388B)
│   │   │   ├── UX-02.yaml (424B, 15 lines)
│   │   │   ├── UX-02.yaml.backup (424B)
│   │   │   ├── UX-03.yaml (420B, 15 lines)
│   │   │   ├── UX-03.yaml.backup (420B)
│   │   │   ├── UX-04.yaml (445B, 16 lines)
│   │   │   ├── UX-04.yaml.backup (445B)
│   │   │   ├── UX-05.yaml (457B, 16 lines)
│   │   │   ├── UX-05.yaml.backup (457B)
│   │   │   ├── UX-06.yaml (374B, 15 lines)
│   │   │   ├── UX-06.yaml.backup (374B)
│   │   │   ├── UX-07.yaml (358B, 15 lines)
│   │   │   ├── UX-07.yaml.backup (358B)
│   │   │   ├── UX-08.yaml (434B, 16 lines)
│   │   │   ├── UX-08.yaml.backup (434B)
│   │   │   ├── UX-09.yaml (416B, 19 lines)
│   │   │   ├── UX-09.yaml.backup (416B)
│   │   │   ├── UX-10.yaml (394B, 16 lines)
│   │   │   ├── UX-10.yaml.backup (394B)
│   │   │   ├── UX-11.yaml (350B, 14 lines)
│   │   │   ├── UX-11.yaml.backup (350B)
│   │   │   ├── UX-12.yaml (441B, 19 lines)
│   │   │   ├── UX-12.yaml.backup (441B)
│   │   │   ├── UX-13.yaml (476B, 25 lines)
│   │   │   ├── UX-13.yaml.backup (476B)
│   │   │   ├── UX-14.yaml (445B, 17 lines)
│   │   │   ├── UX-14.yaml.backup (445B)
│   │   │   ├── UX-15.yaml (411B, 18 lines)
│   │   │   ├── UX-15.yaml.backup (411B)
│   │   │   ├── UX-16.yaml (382B, 18 lines)
│   │   │   ├── UX-16.yaml.backup (382B)
│   │   │   ├── UX-17.yaml (406B, 16 lines)
│   │   │   ├── UX-17.yaml.backup (406B)
│   │   │   ├── UX-18.yaml (393B, 15 lines)
│   │   │   ├── UX-18.yaml.backup (393B)
│   │   │   ├── UX-19.yaml (378B, 15 lines)
│   │   │   ├── UX-19.yaml.backup (378B)
│   │   │   ├── UX-21.yaml (443B, 19 lines)
│   │   │   ├── UX-21.yaml.backup (443B)
│   │   │   ├── UX-21b.yaml (435B, 16 lines)
│   │   │   ├── UX-21b.yaml.backup (435B)
│   │   │   ├── UX-22.yaml (413B, 15 lines)
│   │   │   ├── UX-22.yaml.backup (413B)
│   │   │   ├── UX-23.yaml (368B, 16 lines)
│   │   │   ├── UX-23.yaml.backup (368B)
│   │   │   ├── UX-24.yaml (359B, 14 lines)
│   │   │   ├── UX-24.yaml.backup (359B)
│   │   │   ├── UX-25.yaml (321B, 13 lines)
│   │   │   └── UX-25.yaml.backup (321B)
│   │   ├── workflows/
│   │   │   ├── __init__.py (586B, 23 lines)
│   │   │   ├── automation_health_check.py (16.8K, 431 lines)
│   │   │   ├── automation_health_check.py.backup (16.8K)
│   │   │   ├── complete_task.py (24.0K, 645 lines)
│   │   │   ├── complete_task.py.backup (24.0K)
│   │   │   ├── daily_cycle.py (28.1K, 687 lines)
│   │   │   ├── daily_cycle.py.backup (28.0K)
│   │   │   ├── delegation.py (3.8K, 126 lines)
│   │   │   ├── delegation.py.backup (3.8K)
│   │   │   ├── documentation_agent.py (27.8K, 768 lines)
│   │   │   ├── documentation_agent.py.backup (27.8K)
│   │   │   ├── email_integration.py (22.6K, 561 lines)
│   │   │   ├── email_integration.py.backup (22.6K)
│   │   │   ├── end_of_day_report.py (25.5K, 595 lines)
│   │   │   ├── end_of_day_report.py.backup (25.5K)
│   │   │   ├── enhanced_workflow.py (17.5K, 468 lines)
│   │   │   ├── enhanced_workflow.py.backup (17.5K)
│   │   │   ├── error_handling.py (20.7K, 505 lines)
│   │   │   ├── error_handling.py.backup (20.7K)
│   │   │   ├── execute_graph.py (31.6K, 817 lines)
│   │   │   ├── execute_graph.py.backup (31.5K)
│   │   │   ├── execute_task.py (9.0K, 260 lines)
│   │   │   ├── execute_task.py.backup (9.0K)
│   │   │   ├── execute_workflow.py (16.9K, 482 lines)
│   │   │   ├── execute_workflow.py.backup (16.9K)
│   │   │   ├── extract_code.py (18.4K, 501 lines)
│   │   │   ├── extract_code.py.backup (18.4K)
│   │   │   ├── gantt_analyzer.py (49.1K, 1,205 lines)
│   │   │   ├── gantt_analyzer.py.backup (49.1K)
│   │   │   ├── generate_briefing.py (35.8K, 886 lines)
│   │   │   ├── generate_briefing.py.backup (35.8K)
│   │   │   ├── generate_prompt.py (10.9K, 289 lines)
│   │   │   ├── generate_prompt.py.backup (10.9K)
│   │   │   ├── hitl_engine.py (60.9K, 1,430 lines)
│   │   │   ├── hitl_engine.py.backup (60.9K)
│   │   │   ├── hitl_task_metadata.py (18.4K, 452 lines)
│   │   │   ├── hitl_task_metadata.py.backup (18.4K)
│   │   │   ├── inject_context.py (6.4K, 200 lines)
│   │   │   ├── inject_context.py.backup (6.4K)
│   │   │   ├── langgraph_qa_integration.py (9.4K, 273 lines)
│   │   │   ├── langgraph_qa_integration.py.backup (9.4K)
│   │   │   ├── notification_handlers.py (23.4K, 547 lines)
│   │   │   ├── notification_handlers.py.backup (23.4K)
│   │   │   ├── plan_execution_manager.py (11.5K, 260 lines)
│   │   │   ├── plan_execution_manager.py.backup (11.2K)
│   │   │   ├── qa_execution.py (15.0K, 440 lines)
│   │   │   ├── qa_execution.py.backup (14.9K)
│   │   │   ├── qa_validation.py (25.5K, 700 lines)
│   │   │   ├── qa_validation.py.backup (25.5K)
│   │   │   ├── register_output.py (22.6K, 589 lines)
│   │   │   ├── register_output.py.backup (22.5K)
│   │   │   ├── registry.py (9.4K, 266 lines)
│   │   │   ├── registry.py.backup (9.4K)
│   │   │   ├── review_context.py (7.9K, 222 lines)
│   │   │   ├── review_context.py.backup (7.9K)
│   │   │   ├── review_context_simple.py (7.9K, 223 lines)
│   │   │   ├── review_context_simple.py.backup (7.9K)
│   │   │   ├── review_task.py (42.1K, 1,075 lines)
│   │   │   ├── review_task.py.backup (42.1K)
│   │   │   ├── run_workflow.py (6.9K, 218 lines)
│   │   │   ├── run_workflow.py.backup (6.9K)
│   │   │   ├── scalable_storage.py (7.6K, 233 lines)
│   │   │   ├── scalable_storage.py.backup (7.6K)
│   │   │   ├── sprint_visualizer.py (18.4K, 484 lines)
│   │   │   ├── sprint_visualizer.py.backup (18.4K)
│   │   │   ├── states.py (5.9K, 179 lines)
│   │   │   ├── states.py.backup (5.9K)
│   │   │   ├── summarise_task.py (26.8K, 758 lines)
│   │   │   ├── summarise_task.py.backup (26.8K)
│   │   │   ├── task_declaration.py (29.3K, 756 lines)
│   │   │   ├── task_declaration.py.backup (29.3K)
│   │   │   ├── task_lifecycle.py (19.5K, 525 lines)
│   │   │   ├── task_lifecycle.py.backup (19.5K)
│   │   │   ├── thread_safe_workflow.py (21.3K, 576 lines)
│   │   │   └── thread_safe_workflow.py.backup (21.3K)
│   │   └── __init__.py (348B, 15 lines)
│   ├── integrations/
│   │   ├── analytics/
│   │   │   ├── results/
│   │   │   │   ├── __init__.py (28B, 1 lines)
│   │   │   │   ├── BE-07_analysis_20250611_004345.json (394B, 16 lines)
│   │   │   │   ├── BE-07_analysis_20250611_004345.json.backup (394B)
│   │   │   │   ├── comprehensive_analysis_analysis_20250611_004337.json (454B, 19 lines)
│   │   │   │   └── comprehensive_analysis_analysis_20250611_004337.json.backup (454B)
│   │   │   ├── __init__.py (345B, 13 lines)
│   │   │   ├── __init__.py.backup (345B)
│   │   │   ├── analyse_feedback.py (30.1K, 695 lines)
│   │   │   └── analyse_feedback.py.backup (30.1K)
│   │   ├── external/
│   │   │   └── __init__.py (28B, 1 lines)
│   │   ├── notifications/
│   │   │   └── __init__.py (28B, 1 lines)
│   │   └── __init__.py (321B, 13 lines)
│   ├── interfaces/
│   │   ├── api/
│   │   │   ├── __init__.py (560B, 23 lines)
│   │   │   ├── external_integrations.py (33.3K, 891 lines)
│   │   │   ├── external_integrations.py.backup (33.3K)
│   │   │   ├── hitl_routes.py (53.3K, 1,471 lines)
│   │   │   ├── hitl_routes.py.backup (53.2K)
│   │   │   ├── webhook_manager.py (25.2K, 610 lines)
│   │   │   └── webhook_manager.py.backup (25.2K)
│   │   ├── cli/
│   │   │   ├── __init__.py (28B, 1 lines)
│   │   │   ├── escalation_cli.py (12.6K, 316 lines)
│   │   │   ├── escalation_cli.py.backup (12.6K)
│   │   │   ├── feedback_cli.py (10.3K, 271 lines)
│   │   │   ├── feedback_cli.py.backup (10.3K)
│   │   │   ├── hitl_cli.py (25.6K, 665 lines)
│   │   │   ├── hitl_cli.py.backup (25.6K)
│   │   │   ├── hitl_kanban_cli.py (13.1K, 439 lines)
│   │   │   ├── hitl_kanban_cli.py.backup (13.0K)
│   │   │   ├── qa_cli.py (10.0K, 298 lines)
│   │   │   ├── qa_cli.py.backup (10.0K)
│   │   │   ├── qa_execution_cli.py (8.8K, 289 lines)
│   │   │   ├── qa_execution_cli.py.backup (8.8K)
│   │   │   ├── quick_hitl_status.py (8.7K, 263 lines)
│   │   │   └── quick_hitl_status.py.backup (8.7K)
│   │   ├── dashboard/
│   │   │   ├── api/
│   │   │   │   ├── __init__.py (38B, 1 lines)
│   │   │   │   ├── gantt_api.py (34.7K, 1,029 lines)
│   │   │   │   ├── routes.py (8.8K, 271 lines)
│   │   │   │   └── unified_api_server.py (67.2K, 1,659 lines)
│   │   │   ├── components/
│   │   │   │   ├── __init__.py (45B, 1 lines)
│   │   │   │   ├── hitl_kanban_board.py (24.7K, 648 lines)
│   │   │   │   ├── hitl_kanban_demo.py (10.1K, 322 lines)
│   │   │   │   └── hitl_widgets.py (46.5K, 1,008 lines)
│   │   │   ├── static/
│   │   │   │   └── __init__.py (41B, 1 lines)
│   │   │   ├── templates/
│   │   │   │   └── __init__.py (44B, 1 lines)
│   │   │   ├── __init__.py (596B, 23 lines)
│   │   │   └── config.py (4.2K, 110 lines)
│   │   ├── webhooks/
│   │   │   └── __init__.py (28B, 1 lines)
│   │   └── __init__.py (362B, 15 lines)
│   ├── platform/
│   │   ├── memory/
│   │   │   ├── config/
│   │   │   │   ├── __init__.py (40B, 1 lines)
│   │   │   │   ├── exceptions.py (1.0K, 49 lines)
│   │   │   │   ├── factory.py (4.2K, 151 lines)
│   │   │   │   └── memory_config.py (5.6K, 157 lines)
│   │   │   ├── engines/
│   │   │   │   ├── __init__.py (41B, 1 lines)
│   │   │   │   ├── caching.py (12.0K, 366 lines)
│   │   │   │   ├── chunking.py (12.0K, 347 lines)
│   │   │   │   ├── memory_engine.py (34.1K, 859 lines)
│   │   │   │   └── storage.py (16.7K, 447 lines)
│   │   │   ├── knowledge/
│   │   │   │   ├── __init__.py (43B, 1 lines)
│   │   │   │   ├── active_context.md (7.5K, 150 lines)
│   │   │   │   ├── context_manager.py (2.4K, 70 lines)
│   │   │   │   ├── product_context.md (4.4K, 96 lines)
│   │   │   │   ├── progress.md (8.7K, 227 lines)
│   │   │   │   ├── project_brief.md (2.6K, 57 lines)
│   │   │   │   ├── README.md (6.7K, 200 lines)
│   │   │   │   ├── system_patterns.md (9.5K, 212 lines)
│   │   │   │   └── tech_context.md (8.6K, 266 lines)
│   │   │   ├── security/
│   │   │   │   ├── __init__.py (42B, 1 lines)
│   │   │   │   ├── encryption.py (13.8K, 378 lines)
│   │   │   │   └── thread_safety.py (13.5K, 344 lines)
│   │   │   └── __init__.py (7.5K, 216 lines)
│   │   ├── security/
│   │   │   ├── __init__.py (1.3K, 48 lines)
│   │   │   ├── __init__.py.backup (1.3K)
│   │   │   ├── chromadb_telemetry_patch.py (1.4K, 46 lines)
│   │   │   ├── chromadb_telemetry_patch.py.backup (1.4K)
│   │   │   ├── README.md (1.5K, 46 lines)
│   │   │   └── README.md.backup (1.5K)
│   │   ├── storage/
│   │   │   └── __init__.py (28B, 1 lines)
│   │   ├── tools/
│   │   │   ├── __init__.py (28B, 1 lines)
│   │   │   ├── auto_generate_graph.py (11.9K, 333 lines)
│   │   │   ├── auto_generate_graph.py.backup (11.9K)
│   │   │   ├── auto_generated_graph.json (1.1K, 67 lines)
│   │   │   ├── auto_generated_graph.json.backup (1.1K)
│   │   │   ├── build_json.py (29.9K, 755 lines)
│   │   │   ├── build_json.py.backup (29.9K)
│   │   │   ├── context_tracker.py (9.9K, 312 lines)
│   │   │   ├── critical_path.html (993B, 33 lines)
│   │   │   ├── critical_path.html.backup (993B)
│   │   │   ├── critical_path.json (1009B, 44 lines)
│   │   │   ├── critical_path.json.backup (1009B)
│   │   │   ├── critical_path.mmd (703B)
│   │   │   ├── critical_path.mmd.backup (703B)
│   │   │   ├── critical_path.yaml (723B, 32 lines)
│   │   │   ├── critical_path.yaml.backup (723B)
│   │   │   ├── flow.py (4.1K, 135 lines)
│   │   │   ├── flow.py.backup (4.0K)
│   │   │   ├── graph_builder.py (27.7K, 691 lines)
│   │   │   ├── graph_builder.py.backup (27.7K)
│   │   │   ├── handlers.py (19.9K, 566 lines)
│   │   │   ├── handlers.py.backup (19.9K)
│   │   │   ├── interrupt_nodes.py (17.2K, 471 lines)
│   │   │   ├── interrupt_nodes.py.backup (17.2K)
│   │   │   ├── notifications.py (11.0K, 314 lines)
│   │   │   ├── notifications.py.backup (11.0K)
│   │   │   ├── qa_handler.py (1.3K, 46 lines)
│   │   │   ├── qa_handler.py.backup (1.3K)
│   │   │   ├── resilient_workflow.py (8.0K, 234 lines)
│   │   │   ├── resilient_workflow.py.backup (8.0K)
│   │   │   ├── visualize.py (2.9K, 88 lines)
│   │   │   └── visualize.py.backup (2.8K)
│   │   ├── utils/
│   │   │   ├── __init__.py (28B, 1 lines)
│   │   │   ├── api_validation.py (18.7K, 548 lines)
│   │   │   ├── completion_metrics.py (17.8K, 448 lines)
│   │   │   ├── coverage_analyzer.py (19.0K, 472 lines)
│   │   │   ├── escalation_system.py (37.3K, 893 lines)
│   │   │   ├── execution_monitor.py (29.7K, 801 lines)
│   │   │   ├── feedback_system.py (29.2K, 765 lines)
│   │   │   ├── input_validation.py (23.2K, 640 lines)
│   │   │   ├── integration_analyzer.py (18.6K, 464 lines)
│   │   │   ├── migrate_tasks.py (4.4K, 129 lines)
│   │   │   ├── review.py (4.5K, 173 lines)
│   │   │   ├── schema_manager.py (15.6K, 447 lines)
│   │   │   ├── task_loader.py (7.8K, 274 lines)
│   │   │   └── workflow_recursion_fix.py (3.6K, 110 lines)
│   │   └── __init__.py (353B, 15 lines)
│   ├── __init__.py (506B, 19 lines)
│   └── README.md (2.2K, 66 lines)
├── storage/
│   ├── cold/
│   ├── feedback/
│   ├── hitl/
│   ├── hitl_tasks/
│   ├── hot/
│   ├── warm/
│   └── storage_metadata.json (918B, 28 lines)
├── tasks/
│   ├── backend/
│   │   └── BE-07.json (467B, 17 lines)
│   ├── frontend/
│   ├── general/
│   │   └── TEST-07.json (427B, 16 lines)
│   ├── qa/
│   ├── technical_lead/
│   ├── BE-01.yaml (563B, 20 lines)
│   ├── BE-02.yaml (396B, 17 lines)
│   ├── BE-03.yaml (453B, 18 lines)
│   ├── BE-04.yaml (397B, 17 lines)
│   ├── BE-05.yaml (463B, 18 lines)
│   ├── BE-06.yaml (360B, 15 lines)
│   ├── BE-07.yaml (526B, 25 lines)
│   ├── BE-08.yaml (453B, 18 lines)
│   ├── BE-09.yaml (393B, 18 lines)
│   ├── BE-10.yaml (409B, 17 lines)
│   ├── BE-11.yaml (407B, 17 lines)
│   ├── BE-12.yaml (365B, 16 lines)
│   ├── BE-13.yaml (371B, 16 lines)
│   ├── BE-14.yaml (435B, 18 lines)
│   ├── FE-01.yaml (402B, 17 lines)
│   ├── FE-02.yaml (502B, 21 lines)
│   ├── FE-03.yaml (404B, 16 lines)
│   ├── FE-04.yaml (471B, 19 lines)
│   ├── FE-05.yaml (462B, 18 lines)
│   ├── FE-06.yaml (366B, 15 lines)
│   ├── LC-01.yaml (381B, 13 lines)
│   ├── missing_context_topics_report.md (0B, 0 lines)
│   ├── PM-01.yaml (350B, 13 lines)
│   ├── PM-02.yaml (397B, 15 lines)
│   ├── PM-03.yaml (365B, 13 lines)
│   ├── PM-04.yaml (379B, 15 lines)
│   ├── PM-05.yaml (335B, 14 lines)
│   ├── PM-06.yaml (369B, 13 lines)
│   ├── PM-07.yaml (380B, 15 lines)
│   ├── PM-08.yaml (351B, 13 lines)
│   ├── PM-09.yaml (427B, 17 lines)
│   ├── PM-10.yaml (360B, 13 lines)
│   ├── PM-11.yaml (342B, 13 lines)
│   ├── PM-12.yaml (356B, 14 lines)
│   ├── QA-01.yaml (356B, 15 lines)
│   ├── QA-02.yaml (427B, 19 lines)
│   ├── QA-03.yaml (363B, 15 lines)
│   ├── task-schema.json (1.9K, 67 lines)
│   ├── TL-01.yaml (403B, 15 lines)
│   ├── TL-02.yaml (381B, 16 lines)
│   ├── TL-03.yaml (490B, 19 lines)
│   ├── TL-04.yaml (379B, 16 lines)
│   ├── TL-05.yaml (469B, 19 lines)
│   ├── TL-06.yaml (373B, 16 lines)
│   ├── TL-07.yaml (417B, 17 lines)
│   ├── TL-08.yaml (422B, 19 lines)
│   ├── TL-09.yaml (564B, 19 lines)
│   ├── TL-10.yaml (374B, 16 lines)
│   ├── TL-11.yaml (418B, 16 lines)
│   ├── TL-12.yaml (376B, 15 lines)
│   ├── TL-13.yaml (420B, 19 lines)
│   ├── TL-14.yaml (401B, 17 lines)
│   ├── TL-15.yaml (471B, 19 lines)
│   ├── TL-16.yaml (460B, 20 lines)
│   ├── TL-17.yaml (411B, 16 lines)
│   ├── TL-18.yaml (445B, 18 lines)
│   ├── TL-19.yaml (410B, 17 lines)
│   ├── TL-20.yaml (428B, 17 lines)
│   ├── TL-21.yaml (418B, 18 lines)
│   ├── TL-22.yaml (407B, 18 lines)
│   ├── TL-23.yaml (408B, 17 lines)
│   ├── TL-24.yaml (375B, 16 lines)
│   ├── TL-25.yaml (394B, 16 lines)
│   ├── TL-26.yaml (371B, 15 lines)
│   ├── TL-27.yaml (395B, 16 lines)
│   ├── TL-28.yaml (416B, 18 lines)
│   ├── TL-29.yaml (419B, 18 lines)
│   ├── TL-30.yaml (357B, 15 lines)
│   ├── UX-01.yaml (388B, 14 lines)
│   ├── UX-02.yaml (424B, 15 lines)
│   ├── UX-03.yaml (420B, 15 lines)
│   ├── UX-04.yaml (445B, 16 lines)
│   ├── UX-05.yaml (457B, 16 lines)
│   ├── UX-06.yaml (374B, 15 lines)
│   ├── UX-07.yaml (358B, 15 lines)
│   ├── UX-08.yaml (434B, 16 lines)
│   ├── UX-09.yaml (416B, 19 lines)
│   ├── UX-10.yaml (394B, 16 lines)
│   ├── UX-11.yaml (350B, 14 lines)
│   ├── UX-12.yaml (441B, 19 lines)
│   ├── UX-13.yaml (476B, 25 lines)
│   ├── UX-14.yaml (445B, 17 lines)
│   ├── UX-15.yaml (411B, 18 lines)
│   ├── UX-16.yaml (382B, 18 lines)
│   ├── UX-17.yaml (406B, 16 lines)
│   ├── UX-18.yaml (393B, 15 lines)
│   ├── UX-19.yaml (378B, 15 lines)
│   ├── UX-21.yaml (443B, 19 lines)
│   ├── UX-21b.yaml (435B, 16 lines)
│   ├── UX-22.yaml (413B, 15 lines)
│   ├── UX-23.yaml (368B, 16 lines)
│   ├── UX-24.yaml (359B, 14 lines)
│   └── UX-25.yaml (321B, 13 lines)
├── templates/
│   └── email/
│       ├── eod_report.html (2.1K, 61 lines)
│       └── morning_briefing.html (2.3K, 64 lines)
├── tests/
│   ├── e2e/
│   │   ├── performance/
│   │   │   ├── __init__.py (28B, 1 lines)
│   │   │   ├── integration_enhanced_eod_reporting.py (5.5K, 147 lines)
│   │   │   └── performance_enhanced_eod_reporting.py (11.0K, 310 lines)
│   │   ├── system/
│   │   │   ├── __init__.py (28B, 1 lines)
│   │   │   ├── test_enhanced_qa_agent.py (14.3K, 389 lines)
│   │   │   ├── test_escalation_system.py (23.9K, 661 lines)
│   │   │   └── test_prompt_generation.py (18.0K, 431 lines)
│   │   ├── user_journeys/
│   │   │   └── __init__.py (28B, 1 lines)
│   │   ├── workflows/
│   │   │   ├── __init__.py (28B, 1 lines)
│   │   │   ├── test_phase4_final_validation.py (11.9K, 300 lines)
│   │   │   ├── test_phase6_automation.py (33.5K, 872 lines)
│   │   │   └── test_phase7_hitl.py (27.0K, 728 lines)
│   │   └── __init__.py (32B, 1 lines)
│   ├── fixtures/
│   │   ├── data/
│   │   │   ├── __init__.py (28B, 1 lines)
│   │   │   └── sample_data.py (1.2K, 44 lines)
│   │   ├── factories/
│   │   │   ├── __init__.py (28B, 1 lines)
│   │   │   ├── agent_factory.py (641B, 24 lines)
│   │   │   └── task_factory.py (969B, 30 lines)
│   │   ├── mocks/
│   │   │   ├── __init__.py (291B, 13 lines)
│   │   │   ├── mock_agents.py (1.5K, 56 lines)
│   │   │   ├── mock_api.py (1.2K, 49 lines)
│   │   │   ├── mock_external_deps.py (2.4K, 80 lines)
│   │   │   └── mock_memory.py (1.7K, 51 lines)
│   │   ├── test_data/
│   │   │   └── __init__.py (28B, 1 lines)
│   │   ├── __init__.py (50B, 3 lines)
│   │   ├── fixed_runnable_mock.py (3.6K, 104 lines)
│   │   ├── langchain_fixtures.py (5.7K, 149 lines)
│   │   ├── runnable_mock.py (4.4K, 123 lines)
│   │   ├── test_imports_helper.py (2.3K, 71 lines)
│   │   └── updated_langchain_fixtures.py (5.7K, 150 lines)
│   ├── integration/
│   │   ├── api/
│   │   │   ├── __init__.py (28B, 1 lines)
│   │   │   └── test_api_integration_webhooks.py (11.1K, 296 lines)
│   │   ├── dashboard/
│   │   │   ├── __init__.py (28B, 1 lines)
│   │   │   ├── test_dashboard_integration.py (19.0K, 498 lines)
│   │   │   ├── test_dashboard_routes.py (5.8K, 158 lines)
│   │   │   └── test_dashboard_stability.py (11.7K, 317 lines)
│   │   ├── memory/
│   │   │   └── __init__.py (28B, 1 lines)
│   │   ├── workflows/
│   │   │   ├── __init__.py (28B, 1 lines)
│   │   │   └── test_workflow_integration.py (17.2K, 412 lines)
│   │   ├── __init__.py (0B, 0 lines)
│   │   ├── test_analytics.py (21.7K, 526 lines)
│   │   ├── test_api_integration_webhooks.py (10.7K, 286 lines)
│   │   ├── test_business_endpoints.py (5.6K, 148 lines)
│   │   ├── test_dashboard_integration.py (18.7K, 489 lines)
│   │   ├── test_dashboard_routes.py (5.5K, 148 lines)
│   │   ├── test_dashboard_stability.py (11.3K, 307 lines)
│   │   ├── test_execution_monitor.py (24.3K, 663 lines)
│   │   ├── test_feedback_system.py (26.7K, 740 lines)
│   │   ├── test_hitl_engine_integration.py (17.2K, 408 lines)
│   │   ├── test_phase2_optimizations.py (16.0K, 424 lines)
│   │   ├── test_phase6_step_6_5_visual_progress_charts.py (19.0K, 459 lines)
│   │   ├── test_progress_trend_integration.py (7.6K, 178 lines)
│   │   ├── test_step_4_8_integration.py (2.8K, 78 lines)
│   │   └── test_step_5_4_qa_registration.py (14.4K, 387 lines)
│   ├── test_data/
│   │   ├── context-store/
│   │   │   ├── __init__.py (28B, 1 lines)
│   │   │   └── test_doc.md (675B, 21 lines)
│   │   ├── __init__.py (28B, 1 lines)
│   │   └── test_doc.md (696B, 21 lines)
│   ├── test_outputs/
│   │   └── __init__.py (28B, 1 lines)
│   ├── unit/
│   │   ├── core/
│   │   │   ├── agents/
│   │   │   │   ├── __init__.py (28B, 1 lines)
│   │   │   │   ├── test_agent_orchestration.py (12.5K, 312 lines)
│   │   │   │   ├── test_agent_orchestration_new.py (1.6K, 48 lines)
│   │   │   │   ├── test_agents.py (17.4K, 464 lines)
│   │   │   │   ├── test_documentation_agent.py (11.0K, 319 lines)
│   │   │   │   ├── test_enhanced_qa.py (15.5K, 435 lines)
│   │   │   │   ├── test_enhanced_qa_agent.py (13.9K, 378 lines)
│   │   │   │   ├── test_enhanced_test_generator.py (16.9K, 440 lines)
│   │   │   │   ├── test_human_agents.py (24.6K, 659 lines)
│   │   │   │   ├── test_qa_agent_decisions.py (3.4K, 97 lines)
│   │   │   │   ├── test_qa_execution.py (15.7K, 431 lines)
│   │   │   │   └── test_qa_validation.py (2.2K, 60 lines)
│   │   │   ├── states/
│   │   │   │   └── __init__.py (28B, 1 lines)
│   │   │   ├── tasks/
│   │   │   │   ├── __init__.py (28B, 1 lines)
│   │   │   │   ├── test_summarise_task.py (21.9K, 575 lines)
│   │   │   │   ├── test_task_declaration.py (13.0K, 346 lines)
│   │   │   │   └── test_update_task_status.py (1.4K, 48 lines)
│   │   │   ├── workflows/
│   │   │   │   ├── __init__.py (28B, 1 lines)
│   │   │   │   ├── test_daily_cycle.py (22.8K, 524 lines)
│   │   │   │   ├── test_end_of_day_reporting.py (10.7K, 220 lines)
│   │   │   │   ├── test_enhanced_eod_reporting.py (15.9K, 379 lines)
│   │   │   │   ├── test_enhanced_workflow.py (12.5K, 356 lines)
│   │   │   │   ├── test_execute_graph_comprehensive.py (7.8K, 198 lines)
│   │   │   │   ├── test_extract_code.py (19.6K, 653 lines)
│   │   │   │   ├── test_generate_briefing.py (11.4K, 278 lines)
│   │   │   │   ├── test_generate_briefing_comprehensive.py (20.9K, 537 lines)
│   │   │   │   ├── test_langgraph_workflow.py (4.1K, 119 lines)
│   │   │   │   ├── test_orchestrator.py (1.2K, 37 lines)
│   │   │   │   ├── test_progress_trend_integration.py (7.3K, 168 lines)
│   │   │   │   ├── test_register_output.py (19.0K, 535 lines)
│   │   │   │   ├── test_summarise_task.py (21.6K, 565 lines)
│   │   │   │   ├── test_task_declaration.py (12.6K, 335 lines)
│   │   │   │   ├── test_task_lifecycle.py (23.0K, 619 lines)
│   │   │   │   ├── test_timeline_method.py (1.1K, 40 lines)
│   │   │   │   ├── test_update_task_status.py (1.0K, 35 lines)
│   │   │   │   ├── test_workflow_helpers.py (2.9K, 84 lines)
│   │   │   │   ├── test_workflow_recursion_patch.py (1.2K, 38 lines)
│   │   │   │   └── test_workflow_states.py (17.5K, 421 lines)
│   │   │   ├── __init__.py (32B, 1 lines)
│   │   │   ├── test_agents.py (17.1K, 453 lines)
│   │   │   ├── test_chromadb_patch.py (1.3K, 51 lines)
│   │   │   ├── test_chromadb_patch_optimized.py (2.6K, 91 lines)
│   │   │   ├── test_cleanup_verification.py (4.1K, 125 lines)
│   │   │   ├── test_config_loading.py (658B, 20 lines)
│   │   │   ├── test_coverage.py (725B, 26 lines)
│   │   │   ├── test_daily_cycle.py (23.1K, 535 lines)
│   │   │   ├── test_end_of_day_reporting.py (11.1K, 230 lines)
│   │   │   ├── test_enhanced_eod_reporting.py (16.2K, 389 lines)
│   │   │   ├── test_enhanced_qa.py (15.8K, 446 lines)
│   │   │   ├── test_enhanced_test_generator.py (17.3K, 451 lines)
│   │   │   ├── test_environment.py (5.4K, 165 lines)
│   │   │   ├── test_execute_graph_comprehensive.py (8.2K, 211 lines)
│   │   │   ├── test_extract_code.py (19.9K, 663 lines)
│   │   │   ├── test_generate_briefing.py (11.6K, 283 lines)
│   │   │   ├── test_generate_briefing_comprehensive.py (21.3K, 548 lines)
│   │   │   ├── test_generator.py (31.0K, 809 lines)
│   │   │   ├── test_input_validation.py (14.8K, 417 lines)
│   │   │   ├── test_main.py (13.2K, 361 lines)
│   │   │   ├── test_orchestrator.py (907B, 28 lines)
│   │   │   ├── test_patches.py (11.3K, 292 lines)
│   │   │   ├── test_prompt_generation.py (17.7K, 420 lines)
│   │   │   ├── test_qa_execution.py (16.0K, 441 lines)
│   │   │   ├── test_qa_validation.py (2.5K, 73 lines)
│   │   │   ├── test_register_output.py (19.4K, 545 lines)
│   │   │   ├── test_timeline_method.py (1.4K, 48 lines)
│   │   │   ├── test_updated_retrieval_qa.py (4.4K, 97 lines)
│   │   │   └── test_utils.py (9.1K, 279 lines)
│   │   ├── integrations/
│   │   │   ├── analytics/
│   │   │   │   └── __init__.py (28B, 1 lines)
│   │   │   ├── external/
│   │   │   │   └── __init__.py (28B, 1 lines)
│   │   │   └── __init__.py (32B, 1 lines)
│   │   ├── interfaces/
│   │   │   ├── api/
│   │   │   │   ├── __init__.py (28B, 1 lines)
│   │   │   │   └── test_hitl_api_routes.py (19.6K, 476 lines)
│   │   │   ├── cli/
│   │   │   │   └── __init__.py (28B, 1 lines)
│   │   │   ├── dashboard/
│   │   │   │   ├── __init__.py (28B, 1 lines)
│   │   │   │   ├── test_hitl_api_routes.py (19.4K, 470 lines)
│   │   │   │   ├── test_hitl_cli.py (21.0K, 535 lines)
│   │   │   │   ├── test_hitl_cli_comprehensive.py (33.4K, 859 lines)
│   │   │   │   ├── test_hitl_dashboard_widgets.py (19.6K, 502 lines)
│   │   │   │   └── test_hitl_engine_integration.py (16.8K, 398 lines)
│   │   │   └── __init__.py (32B, 1 lines)
│   │   ├── platform/
│   │   │   ├── memory/
│   │   │   │   ├── __init__.py (28B, 1 lines)
│   │   │   │   ├── test_memory_config.py (2.2K, 65 lines)
│   │   │   │   ├── test_memory_engine.py (7.0K, 179 lines)
│   │   │   │   └── test_memory_functionality.py (11.3K, 313 lines)
│   │   │   ├── security/
│   │   │   │   └── __init__.py (28B, 1 lines)
│   │   │   ├── storage/
│   │   │   │   └── __init__.py (28B, 1 lines)
│   │   │   ├── tools/
│   │   │   │   ├── __init__.py (28B, 1 lines)
│   │   │   │   └── test_tool_loader.py (9.2K, 263 lines)
│   │   │   └── __init__.py (32B, 1 lines)
│   │   └── __init__.py (32B, 1 lines)
│   ├── __init__.py (41B, 3 lines)
│   ├── conftest.py (26.6K, 796 lines)
│   ├── debug_config.py (765B, 28 lines)
│   ├── debug_timeline.py (2.7K, 75 lines)
│   ├── final_validation_complete.py (5.0K, 136 lines)
│   ├── helpers.py (3.4K, 94 lines)
│   ├── mock_environment.py (2.3K, 72 lines)
│   ├── mock_langchain.py (5.2K, 145 lines)
│   ├── mock_memory_engine.py (787B, 27 lines)
│   ├── mock_openai_embeddings.py (2.0K, 55 lines)
│   ├── monkey_patch.py (1.0K, 30 lines)
│   ├── run_optimized_tests.py (4.8K, 153 lines)
│   ├── run_tests.py (23.7K, 674 lines)
│   ├── simple_retrieval_test.py (3.9K, 97 lines)
│   ├── TEST_FIX_SUMMARY.md (2.9K, 97 lines)
│   └── verify_dashboard_fix.py (5.8K, 177 lines)
├── tools/
│   ├── memory/
│   │   ├── __init__.py (3.0K, 102 lines)
│   │   ├── caching.py (11.7K, 355 lines)
│   │   ├── chunking.py (11.7K, 336 lines)
│   │   ├── config.py (3.8K, 115 lines)
│   │   ├── engine.py (33.7K, 849 lines)
│   │   ├── exceptions.py (746B, 38 lines)
│   │   ├── factory.py (3.9K, 140 lines)
│   │   ├── security.py (13.4K, 367 lines)
│   │   ├── storage.py (16.4K, 436 lines)
│   │   └── thread_safe.py (12.9K, 333 lines)
│   ├── __init__.py (655B, 20 lines)
│   ├── base_tool.py (5.1K, 168 lines)
│   ├── context_tracker.py (11.1K, 340 lines)
│   ├── context_visualizer.py (23.6K, 668 lines)
│   ├── coverage_tool.py (18.5K, 481 lines)
│   ├── cypress_tool.py (14.6K, 460 lines)
│   ├── design_system_tool.py (32.1K, 690 lines)
│   ├── echo_tool.py (1.1K, 35 lines)
│   ├── fixed_retrieval_qa.py (284B, 9 lines)
│   ├── github_tool.py (36.4K, 874 lines)
│   ├── jest_tool.py (18.4K, 466 lines)
│   ├── markdown_tool.py (9.6K, 333 lines)
│   ├── qa_cli.py (13.6K, 388 lines)
│   ├── rate_limiter.py (4.0K, 130 lines)
│   ├── retrieval_qa.py (1.8K, 50 lines)
│   ├── retrieval_qa_refactored.py (10.8K, 275 lines)
│   ├── supabase_tool.py (23.0K, 585 lines)
│   ├── tailwind_tool.py (29.2K, 788 lines)
│   ├── tool_loader.py (6.0K, 198 lines)
│   ├── vercel_tool.py (39.8K, 980 lines)
│   └── vercel_tool_refactored.py (17.7K, 465 lines)
├── visualization/
│   └── build_json.py (29.9K, 755 lines)
├── .env.example (642B)
├── ARCHITECTURE_MIGRATION_PLAN.md (8.7K, 255 lines)
├── check_quotes.py (1.2K, 34 lines)
├── check_quotes_detailed.py (2.5K, 68 lines)
├── CLAUDE.md (6.4K, 165 lines)
├── code-quality.ps1 (27.6K, 706 lines)
├── consolidate_dashboard.py (29.9K, 850 lines)
├── consolidate_memory.py (22.8K, 649 lines)
├── CONSOLIDATION_PLAN.md (2.8K, 73 lines)
├── content_ai_system_json.ps1 (15.8K, 386 lines)
├── dashboard_demo.json (1.8K, 72 lines)
├── fix_unicode_escapes.py (1.7K, 55 lines)
├── LICENSE (1.1K)
├── lint.bat (56B, 2 lines)
├── main.py (15.2K, 467 lines)
├── migrate_source_code.py (21.7K, 612 lines)
├── MIGRATION_SUMMARY.md (4.1K, 116 lines)
├── mypy.ini (235B)
├── optimize_tests.py (24.9K, 753 lines)
├── PROPOSED_DIRECTORY_STRUCTURE.md (5.4K, 164 lines)
├── pyproject.toml (519B)
├── pytest-safe.ini (1.0K)
├── pytest.ini (1.3K)
├── README.md (20.6K, 445 lines)
├── requirements-enterprise.txt (320B, 13 lines)
├── requirements.txt (1.1K, 56 lines)
├── setup-code-quality.ps1 (10.5K, 373 lines)
├── test_collection_check.py (3.5K, 115 lines)
└── validate_imports.py (7.5K, 209 lines)
```

## Summary

- **Total files**: 1,248
- **Total directories**: 268
- **Total items**: 1,516
- **Total lines of code**: 226,383
- **Generation method**: Depth-First Search (DFS) traversal
- **Tree algorithm**: Recursive directory iteration with size and line count information
- **Excluded patterns**: .coverage, .git, .log, .mypy_cache, .pytest_cache, .tox, .venv, __pycache__, build/archives, dist, htmlcov, logs/, node_modules, runtime/cache, runtime/logs, runtime/temp, test_logs/

## Tree Traversal Algorithm

This tree structure was generated using a **Depth-First Search (DFS)** algorithm:

1. **Recursive Traversal**: Starting from root, recursively visit each directory
2. **Sorting Strategy**: Directories first, then files (alphabetically)
3. **Size Calculation**: File sizes shown in appropriate units (B/K/M)
4. **Line Counting**: Text files show line counts for code analysis
5. **Exclusion Filtering**: Skip temporary, cache, and build directories
6. **Depth Limiting**: Maximum depth of 8 levels to prevent excessive output

## Architecture Insights

Based on this tree structure with **1,248 files** and **226,383 lines of code**:

- **Modular Organization**: Clear separation of concerns across directories
- **Build Artifacts**: Organized in `build/` with proper segregation  
- **Runtime Data**: Separated in `runtime/` for operational files
- **Configuration**: Centralized in `config/` with schema validation
- **Testing**: Comprehensive test structure in `tests/` with fixtures
- **Documentation**: Well-organized in `docs/` by category
- **Tools & Scripts**: Utility functions properly categorized

This structure demonstrates a **mature software architecture** with clear boundaries and proper file organization.

## File Type Analysis

Based on the line counts, this codebase contains:
- **Python code**: Estimated 158,468 lines (70% of total)
- **Documentation**: Estimated 33,957 lines (15% of total)  
- **Configuration**: Estimated 22,638 lines (10% of total)
- **Other files**: Estimated 11,319 lines (5% of total)

This represents a **substantial codebase** with comprehensive documentation and configuration.
