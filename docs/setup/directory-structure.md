# Directory Structure

Generated on: 2025-08-08 00:24:58

```
ai-system/
├── .claude/
│   └── commands/
├── archives/
│   ├── cold/
│   └── warm/
├── backup_debug_files_20250729_223510/
├── build/
│   ├── dashboard/
│   │   └── notifications/
│   ├── runtime/
│   │   └── logs/
│   ├── storage/
│   │   ├── cold/
│   │   ├── hitl/
│   │   ├── hot/
│   │   └── warm/
│   └── test_outputs/
├── config/
│   └── schemas/
├── dashboard/
├── data/
│   └── storage/
│       ├── cold/
│       │   └── context/
│       ├── escalations/
│       ├── hot/
│       │   └── context/
│       └── warm/
│           └── context/
├── docs/
│   ├── architecture/
│   │   └── improvements/
│   ├── cicd/
│   ├── completions/
│   ├── development/
│   │   ├── debugging/
│   │   ├── generation/
│   │   ├── mocking/
│   │   ├── testing/
│   │   └── visualization/
│   ├── integrations/
│   ├── operations/
│   │   ├── automation/
│   │   ├── monitoring/
│   │   └── workflows/
│   ├── reports/
│   │   ├── memory-engine/
│   │   └── phase7-hitl/
│   ├── security/
│   │   └── validation/
│   ├── setup/
│   ├── sprint/
│   │   ├── briefings/
│   │   └── daily_reports/
│   ├── user-guides/
│   │   └── demos/
│   └── website/
│       ├── blog/
│       │   └── 2021-08-26-welcome/
│       ├── build/
│       │   ├── assets/
│       │   │   ├── css/
│       │   │   └── js/
│       │   ├── docs/
│       │   │   ├── admin/
│       │   │   │   ├── CODE_QUALITY_IMPROVEMENTS_SUMMARY/
│       │   │   │   └── MEMORY_ENGINE_REFACTORING_SUMMARY/
│       │   │   ├── adr/
│       │   │   │   ├── generated_artefact_strategy/
│       │   │   │   └── generated_artefact_strategy_fixed/
│       │   │   ├── api/
│       │   │   │   ├── api_reference/
│       │   │   │   ├── class_dictionary/
│       │   │   │   ├── external_integrations/
│       │   │   │   ├── function_dictionary/
│       │   │   │   ├── hitl_routes/
│       │   │   │   ├── module_dictionary/
│       │   │   │   ├── symbol_index/
│       │   │   │   ├── unified_api_server/
│       │   │   │   └── webhook_manager/
│       │   │   ├── architecture/
│       │   │   │   ├── agent_architecture/
│       │   │   │   ├── agent_system_overview/
│       │   │   │   ├── agents/
│       │   │   │   │   ├── agent_builder/
│       │   │   │   │   ├── agent_factory_refactoring_summary/
│       │   │   │   │   ├── backend/
│       │   │   │   │   ├── backend_agent/
│       │   │   │   │   ├── coordinator/
│       │   │   │   │   ├── coordinator_agent/
│       │   │   │   │   ├── doc/
│       │   │   │   │   ├── documentation_agent/
│       │   │   │   │   ├── factory/
│       │   │   │   │   ├── frontend/
│       │   │   │   │   ├── frontend_agent/
│       │   │   │   │   ├── human_agents/
│       │   │   │   │   ├── qa/
│       │   │   │   │   ├── qa_agent/
│       │   │   │   │   ├── technical/
│       │   │   │   │   └── technical_lead_agent/
│       │   │   │   ├── context_tracking_functionality/
│       │   │   │   ├── COORDINATOR_IMPROVEMENTS/
│       │   │   │   ├── dependency_map/
│       │   │   │   ├── error_handling/
│       │   │   │   ├── ERROR_HANDLING_IMPROVEMENTS/
│       │   │   │   ├── error_propagation_strategy/
│       │   │   │   ├── FILE_ORGANIZATION_IMPROVEMENTS/
│       │   │   │   ├── flow/
│       │   │   │   ├── graph_builder/
│       │   │   │   ├── handlers/
│       │   │   │   ├── hitl_engine/
│       │   │   │   ├── hitl_task_metadata/
│       │   │   │   ├── improvements/
│       │   │   │   ├── inject_context/
│       │   │   │   ├── interrupt_nodes/
│       │   │   │   ├── langgraph_qa_integration/
│       │   │   │   ├── memory_engine/
│       │   │   │   ├── modernization-plan/
│       │   │   │   ├── notification_handlers/
│       │   │   │   ├── notifications/
│       │   │   │   ├── qa_handler/
│       │   │   │   ├── registry/
│       │   │   │   ├── scalable_storage/
│       │   │   │   ├── states/
│       │   │   │   ├── system-architecture-overview/
│       │   │   │   ├── system-overview/
│       │   │   │   ├── system_architecture/
│       │   │   │   ├── task_lifecycle/
│       │   │   │   ├── thread_safe_workflow/
│       │   │   │   ├── thread_safety_implementation_summary/
│       │   │   │   ├── tools_system/
│       │   │   │   └── workflow_task_system/
│       │   │   ├── cicd/
│       │   │   │   └── slack-integration-guide/
│       │   │   ├── development/
│       │   │   │   ├── annotate_context_tags_tasks/
│       │   │   │   ├── automation/
│       │   │   │   ├── build_paths/
│       │   │   │   ├── chromadb_telemetry_patch/
│       │   │   │   ├── CLAUDE_CODE_TEAM_ONBOARDING/
│       │   │   │   ├── configuration_deep_dive/
│       │   │   │   ├── configuration_reference/
│       │   │   │   ├── consolidate_dashboard/
│       │   │   │   ├── debugging/
│       │   │   │   │   ├── analyze_remaining_failures/
│       │   │   │   │   ├── fix_unicode_escapes/
│       │   │   │   │   └── verify_dashboard_fix/
│       │   │   │   ├── ENHANCED_WORKFLOW_GUIDE/
│       │   │   │   ├── generation/
│       │   │   │   │   ├── automated_doc_generator/
│       │   │   │   │   ├── automated_symbol_extraction/
│       │   │   │   │   ├── batch_qa_generation/
│       │   │   │   │   ├── generate_agent/
│       │   │   │   │   ├── generate_briefing/
│       │   │   │   │   ├── generate_progress_report/
│       │   │   │   │   ├── generate_prompt/
│       │   │   │   │   └── generate_task_report/
│       │   │   │   ├── get-pip/
│       │   │   │   ├── helpers/
│       │   │   │   ├── INPUT_VALIDATION_IMPLEMENTATION_SUMMARY/
│       │   │   │   ├── main/
│       │   │   │   ├── main_entry_point/
│       │   │   │   ├── migrate_source_code/
│       │   │   │   ├── mock_memory_engine/
│       │   │   │   ├── mocking/
│       │   │   │   │   ├── mock_dependencies/
│       │   │   │   │   ├── mock_environment/
│       │   │   │   │   ├── mock_langchain/
│       │   │   │   │   └── mock_openai_embeddings/
│       │   │   │   ├── monkey_patch/
│       │   │   │   ├── patch_dotenv/
│       │   │   │   ├── security/
│       │   │   │   ├── setup/
│       │   │   │   ├── testing/
│       │   │   │   │   ├── analyse_feedback/
│       │   │   │   │   ├── complete_validation/
│       │   │   │   │   ├── conftest/
│       │   │   │   │   ├── end_to_end_test/
│       │   │   │   │   ├── final_validation_complete/
│       │   │   │   │   ├── optimize_tests/
│       │   │   │   │   ├── OPTIMIZED_TESTING/
│       │   │   │   │   ├── pytest_simulator/
│       │   │   │   │   ├── run_optimized_tests/
│       │   │   │   │   ├── run_optimized_tests_enhanced/
│       │   │   │   │   ├── run_tests/
│       │   │   │   │   ├── setup_context_for_testing/
│       │   │   │   │   ├── simple_retrieval_test/
│       │   │   │   │   ├── test_collection_check/
│       │   │   │   │   ├── test_sprint_phases/
│       │   │   │   │   ├── test_structure/
│       │   │   │   │   ├── testagent_agent/
│       │   │   │   │   ├── testing_best_practices/
│       │   │   │   │   ├── testvalidation_agent/
│       │   │   │   │   └── validate_imports/
│       │   │   │   ├── troubleshooting/
│       │   │   │   └── visualization/
│       │   │   │       ├── auto_generate_graph/
│       │   │   │       ├── build_json/
│       │   │   │       ├── gantt_analyzer/
│       │   │   │       ├── graph_visualization/
│       │   │   │       ├── sprint_visualizer/
│       │   │   │       ├── visualize/
│       │   │   │       ├── visualize_directory_tree/
│       │   │   │       └── visualize_task_graph/
│       │   │   ├── integrations/
│       │   │   │   └── gemini-cli/
│       │   │   ├── intro/
│       │   │   ├── operations/
│       │   │   │   ├── automation/
│       │   │   │   │   └── automation_health_check/
│       │   │   │   ├── email_integration/
│       │   │   │   ├── list_pending_reviews/
│       │   │   │   ├── manage_knowledge_reviews/
│       │   │   │   ├── mark_review_complete/
│       │   │   │   ├── monitoring/
│       │   │   │   │   ├── monitor_workflow/
│       │   │   │   │   └── workflow_monitoring/
│       │   │   │   ├── update_dashboard/
│       │   │   │   └── workflows/
│       │   │   │       ├── archive_task/
│       │   │   │       ├── complete_task/
│       │   │   │       ├── daily_cycle/
│       │   │   │       ├── daily_cycle_orchestrator/
│       │   │   │       ├── delegation/
│       │   │   │       ├── end_of_day_report/
│       │   │   │       ├── enhanced_workflow/
│       │   │   │       ├── execute_graph/
│       │   │   │       ├── execute_task/
│       │   │   │       ├── execute_workflow/
│       │   │   │       ├── extract_code/
│       │   │   │       ├── knowledge_curation_workflow/
│       │   │   │       ├── langgraph_workflow/
│       │   │   │       ├── plan_execution_manager/
│       │   │   │       ├── qa_execution/
│       │   │   │       ├── qa_validation/
│       │   │   │       ├── register_output/
│       │   │   │       ├── resilient_workflow/
│       │   │   │       ├── review_context/
│       │   │   │       ├── review_context_simple/
│       │   │   │       ├── review_task/
│       │   │   │       ├── run_workflow/
│       │   │   │       ├── summarise_task/
│       │   │   │       ├── task_declaration/
│       │   │   │       ├── task_orchestration/
│       │   │   │       └── workflow_executor/
│       │   │   ├── optimizations/
│       │   │   │   └── PHASE2_COMPLETE_DOCUMENTATION/
│       │   │   ├── reports/
│       │   │   │   ├── import_refactoring_completion_report/
│       │   │   │   ├── memory-engine/
│       │   │   │   │   └── consolidate_memory/
│       │   │   │   └── phase7-hitl/
│       │   │   │       ├── phase6_enhanced_eod_reporting_guide/
│       │   │   │       ├── PHASE6_STEP6.3_COMPLETION_SUMMARY/
│       │   │   │       ├── PHASE6_STEP6.5_COMPLETION_SUMMARY/
│       │   │   │       ├── PHASE6_STEP6.6_EMAIL_INTEGRATION_COMPLETION/
│       │   │   │       └── PHASE7_STEPS7.2-7.3_COMPLETION_SUMMARY/
│       │   │   ├── security/
│       │   │   │   ├── security-overview/
│       │   │   │   └── validation/
│       │   │   │       ├── management_dashboard/
│       │   │   │       └── quality_gates/
│       │   │   ├── setup/
│       │   │   │   ├── complete-directory-structure/
│       │   │   │   ├── directory-structure/
│       │   │   │   ├── requirements/
│       │   │   │   └── requirements-compliance/
│       │   │   ├── sprint/
│       │   │   │   ├── BRIEFING_GENERATOR_API/
│       │   │   │   ├── briefings/
│       │   │   │   │   ├── briefing-2025-05-29/
│       │   │   │   │   ├── briefing-2025-06-01/
│       │   │   │   │   ├── briefing-2025-06-02/
│       │   │   │   │   ├── sprint-day1-briefing/
│       │   │   │   │   ├── sprint-day2-briefing/
│       │   │   │   │   └── sprint-day3-briefing/
│       │   │   │   └── PHASE6_COMPLETION_REPORT/
│       │   │   ├── tools/
│       │   │   │   ├── __init__/
│       │   │   │   ├── base_tool/
│       │   │   │   ├── context_tracker/
│       │   │   │   ├── context_visualizer/
│       │   │   │   ├── coverage_tool/
│       │   │   │   ├── cypress_tool/
│       │   │   │   ├── design_system_tool/
│       │   │   │   ├── echo_tool/
│       │   │   │   ├── fixed_retrieval_qa/
│       │   │   │   ├── github_finalise/
│       │   │   │   ├── github_tool/
│       │   │   │   ├── jest_tool/
│       │   │   │   ├── langChain_characterTextSplitter/
│       │   │   │   ├── markdown_tool/
│       │   │   │   ├── memory_engine/
│       │   │   │   ├── memory_engine_examples/
│       │   │   │   ├── qa_cli/
│       │   │   │   ├── rate_limiter/
│       │   │   │   ├── retrieval_qa/
│       │   │   │   ├── retrieval_qa_refactored/
│       │   │   │   ├── retrieval_qa_usage/
│       │   │   │   ├── supabase_tool/
│       │   │   │   ├── tailwind_tool/
│       │   │   │   ├── task_loader/
│       │   │   │   ├── tool_loader/
│       │   │   │   ├── utilities_catalog/
│       │   │   │   ├── utils/
│       │   │   │   ├── validation/
│       │   │   │   ├── vercel_tool/
│       │   │   │   └── vercel_tool_refactored/
│       │   │   └── user-guides/
│       │   │       ├── demos/
│       │   │       │   ├── agent_output_demo/
│       │   │       │   ├── agent_summarization_demo/
│       │   │       │   ├── code_extraction_demo/
│       │   │       │   ├── hitl_cli_demo/
│       │   │       │   ├── hitl_kanban_demo/
│       │   │       │   ├── human-in-the-Loop_context_review/
│       │   │       │   ├── mcp_context_usage/
│       │   │       │   ├── qa_execution_demo/
│       │   │       │   ├── register_agent_output_demo/
│       │   │       │   ├── task_declaration_preparation/
│       │   │       │   └── visualise_context_coverage/
│       │   │       ├── documentation_completeness/
│       │   │       ├── documentation_index/
│       │   │       ├── documentation_search_index/
│       │   │       ├── escalation_cli/
│       │   │       ├── feedback_cli/
│       │   │       ├── hitl_cli/
│       │   │       ├── hitl_kanban_board/
│       │   │       ├── hitl_kanban_cli/
│       │   │       ├── hitl_kanban_dashboard/
│       │   │       ├── hitl_widgets/
│       │   │       ├── MASTER_DOCUMENTATION_GUIDE/
│       │   │       ├── qa_execution_cli/
│       │   │       ├── quick_hitl_status/
│       │   │       ├── quick_reference_cards/
│       │   │       └── visual_documentation/
│       │   ├── img/
│       │   └── markdown-page/
│       ├── docs/
│       │   ├── admin/
│       │   ├── adr/
│       │   ├── api/
│       │   ├── architecture/
│       │   │   ├── agents/
│       │   │   └── improvements/
│       │   ├── cicd/
│       │   ├── completions/
│       │   ├── development/
│       │   │   ├── debugging/
│       │   │   ├── generation/
│       │   │   ├── mocking/
│       │   │   ├── testing/
│       │   │   └── visualization/
│       │   ├── integrations/
│       │   ├── operations/
│       │   │   ├── automation/
│       │   │   ├── monitoring/
│       │   │   └── workflows/
│       │   ├── optimizations/
│       │   ├── reports/
│       │   │   ├── memory-engine/
│       │   │   └── phase7-hitl/
│       │   ├── security/
│       │   │   └── validation/
│       │   ├── setup/
│       │   ├── sprint/
│       │   │   ├── briefings/
│       │   │   └── daily_reports/
│       │   ├── tools/
│       │   │   └── validation/
│       │   └── user-guides/
│       │       └── demos/
│       ├── src/
│       │   ├── components/
│       │   │   └── HomepageFeatures/
│       │   ├── css/
│       │   └── pages/
│       └── static/
│           └── img/
├── feedback_logs/
├── githooks/
├── investigation_reports/
├── logs/
│   ├── langgraph/
│   └── notifications/
├── outputs/
│   ├── ADVANCED-01/
│   ├── BE-01/
│   ├── BE-02/
│   ├── BE-03/
│   ├── BE-04/
│   ├── BE-05/
│   ├── BE-06/
│   ├── BE-07/
│   ├── BE-08/
│   ├── BE-09/
│   ├── BE-10/
│   ├── BE-11/
│   ├── BE-12/
│   ├── BE-13/
│   ├── BE-14/
│   ├── briefings/
│   ├── CONCURRENT-0/
│   ├── CONCURRENT-1/
│   ├── CONCURRENT-2/
│   ├── CONCURRENT-3/
│   ├── CONCURRENT-4/
│   ├── CONCURRENT-5/
│   ├── CONCURRENT-6/
│   ├── CONCURRENT-7/
│   ├── CONCURRENT-8/
│   ├── CONCURRENT-9/
│   ├── DEPENDENT-01/
│   ├── DOC-01/
│   ├── FE-01/
│   ├── FE-02/
│   ├── FE-03/
│   ├── FE-04/
│   ├── FE-05/
│   ├── FE-06/
│   ├── INTEGRATION-01/
│   ├── LC-01/
│   ├── OUTPUT-01/
│   ├── PERF-0/
│   ├── PERF-1/
│   ├── PERF-10/
│   ├── PERF-11/
│   ├── PERF-12/
│   ├── PERF-13/
│   ├── PERF-14/
│   ├── PERF-15/
│   ├── PERF-16/
│   ├── PERF-17/
│   ├── PERF-18/
│   ├── PERF-19/
│   ├── PERF-2/
│   ├── PERF-20/
│   ├── PERF-21/
│   ├── PERF-22/
│   ├── PERF-23/
│   ├── PERF-24/
│   ├── PERF-25/
│   ├── PERF-26/
│   ├── PERF-27/
│   ├── PERF-28/
│   ├── PERF-29/
│   ├── PERF-3/
│   ├── PERF-30/
│   ├── PERF-31/
│   ├── PERF-32/
│   ├── PERF-33/
│   ├── PERF-34/
│   ├── PERF-35/
│   ├── PERF-36/
│   ├── PERF-37/
│   ├── PERF-38/
│   ├── PERF-39/
│   ├── PERF-4/
│   ├── PERF-40/
│   ├── PERF-41/
│   ├── PERF-42/
│   ├── PERF-43/
│   ├── PERF-44/
│   ├── PERF-45/
│   ├── PERF-46/
│   ├── PERF-47/
│   ├── PERF-48/
│   ├── PERF-49/
│   ├── PERF-5/
│   ├── PERF-50/
│   ├── PERF-51/
│   ├── PERF-52/
│   ├── PERF-53/
│   ├── PERF-54/
│   ├── PERF-55/
│   ├── PERF-56/
│   ├── PERF-57/
│   ├── PERF-58/
│   ├── PERF-59/
│   ├── PERF-6/
│   ├── PERF-60/
│   ├── PERF-61/
│   ├── PERF-62/
│   ├── PERF-63/
│   ├── PERF-64/
│   ├── PERF-65/
│   ├── PERF-66/
│   ├── PERF-67/
│   ├── PERF-68/
│   ├── PERF-69/
│   ├── PERF-7/
│   ├── PERF-70/
│   ├── PERF-71/
│   ├── PERF-72/
│   ├── PERF-73/
│   ├── PERF-74/
│   ├── PERF-75/
│   ├── PERF-76/
│   ├── PERF-77/
│   ├── PERF-78/
│   ├── PERF-79/
│   ├── PERF-8/
│   ├── PERF-80/
│   ├── PERF-81/
│   ├── PERF-82/
│   ├── PERF-83/
│   ├── PERF-84/
│   ├── PERF-85/
│   ├── PERF-86/
│   ├── PERF-87/
│   ├── PERF-88/
│   ├── PERF-89/
│   ├── PERF-9/
│   ├── PERF-90/
│   ├── PERF-91/
│   ├── PERF-92/
│   ├── PERF-93/
│   ├── PERF-94/
│   ├── PERF-95/
│   ├── PERF-96/
│   ├── PERF-97/
│   ├── PERF-98/
│   ├── PERF-99/
│   ├── PM-01/
│   ├── PM-02/
│   ├── PM-03/
│   ├── PM-04/
│   ├── PM-05/
│   ├── PM-06/
│   ├── PM-07/
│   ├── PM-08/
│   ├── PM-09/
│   ├── PM-10/
│   ├── PM-11/
│   ├── PM-12/
│   ├── QA-01/
│   ├── QA-02/
│   ├── QA-03/
│   ├── QA-INTEGRATION-01/
│   ├── step_4_3/
│   │   └── BE-07/
│   ├── TASK#002/
│   ├── TASK-001_special/
│   ├── TASK.004/
│   ├── TASK@003/
│   ├── TEST-01/
│   ├── TEST-backend/
│   ├── TEST-coordinator/
│   ├── TEST-documentation/
│   ├── TEST-frontend/
│   ├── TEST-qa/
│   ├── TL-01/
│   ├── TL-02/
│   ├── TL-03/
│   ├── TL-04/
│   ├── TL-05/
│   ├── TL-06/
│   ├── TL-07/
│   ├── TL-08/
│   ├── TL-09/
│   ├── TL-10/
│   ├── TL-11/
│   ├── TL-12/
│   ├── TL-13/
│   ├── TL-14/
│   ├── TL-15/
│   ├── TL-16/
│   ├── TL-17/
│   ├── TL-18/
│   ├── TL-19/
│   ├── TL-20/
│   ├── TL-21/
│   ├── TL-22/
│   ├── TL-23/
│   ├── TL-24/
│   ├── TL-25/
│   ├── TL-26/
│   ├── TL-27/
│   ├── TL-28/
│   ├── TL-29/
│   ├── TL-30/
│   ├── UX-01/
│   ├── UX-02/
│   ├── UX-03/
│   ├── UX-04/
│   ├── UX-05/
│   ├── UX-06/
│   ├── UX-07/
│   ├── UX-08/
│   ├── UX-09/
│   ├── UX-10/
│   ├── UX-11/
│   ├── UX-12/
│   ├── UX-13/
│   ├── UX-14/
│   ├── UX-15/
│   ├── UX-16/
│   ├── UX-17/
│   ├── UX-18/
│   ├── UX-19/
│   ├── UX-21/
│   ├── UX-21b/
│   ├── UX-22/
│   ├── UX-23/
│   ├── UX-24/
│   └── UX-25/
├── pending_reviews/
├── progress_reports/
├── projects/
│   └── test-project/
├── prompts/
├── reports/
│   └── qa/
├── reviews/
├── runtime/
│   ├── cache/
│   │   └── memory_disk_cache/
│   └── chroma_db/
├── scripts/
│   ├── debug/
│   ├── mocks/
│   │   └── test_data/
│   │       └── context-store/
│   ├── test-runners/
│   └── validation/
├── src/
│   ├── analytics/
│   ├── core/
│   │   ├── abstractions/
│   │   ├── agents/
│   │   ├── configuration/
│   │   ├── dependency_injection/
│   │   ├── domain/
│   │   ├── error_handling/
│   │   ├── outputs/
│   │   ├── security/
│   │   ├── services/
│   │   ├── states/
│   │   ├── tasks/
│   │   │   ├── backend/
│   │   │   ├── frontend/
│   │   │   ├── general/
│   │   │   ├── qa/
│   │   │   └── technical_lead/
│   │   ├── validation/
│   │   └── workflows/
│   │       ├── graph/
│   │       │   └── config/
│   │       └── hitl/
│   ├── docs/
│   │   └── completions/
│   ├── examples/
│   ├── infrastructure/
│   │   ├── .approved/
│   │   ├── config/
│   │   ├── data/
│   │   │   ├── context/
│   │   │   │   ├── backend/
│   │   │   │   ├── db/
│   │   │   │   ├── design/
│   │   │   │   ├── infra/
│   │   │   │   ├── patterns/
│   │   │   │   ├── sprint/
│   │   │   │   └── technical/
│   │   │   ├── sprints/
│   │   │   │   └── audit/
│   │   │   │       └── report/
│   │   │   └── storage/
│   │   │       ├── cold/
│   │   │       │   └── context/
│   │   │       ├── hot/
│   │   │       │   └── context/
│   │   │       └── warm/
│   │   │           └── context/
│   │   ├── memory/
│   │   │   ├── config/
│   │   │   ├── engines/
│   │   │   ├── knowledge/
│   │   │   └── security/
│   │   ├── prompts/
│   │   ├── reviews/
│   │   ├── runtime/
│   │   │   └── chroma_db/
│   │   ├── scripts/
│   │   │   ├── generation/
│   │   │   ├── monitoring/
│   │   │   ├── testing/
│   │   │   │   └── validation/
│   │   │   └── utilities/
│   │   │       └── db/
│   │   ├── security/
│   │   ├── storage/
│   │   │   └── feedback/
│   │   ├── templates/
│   │   │   ├── agent/
│   │   │   └── email/
│   │   ├── tools/
│   │   │   ├── core/
│   │   │   ├── external/
│   │   │   ├── handlers/
│   │   │   ├── memory/
│   │   │   └── validation/
│   │   │       ├── ai/
│   │   │       ├── core/
│   │   │       ├── dashboard/
│   │   │       ├── persistence/
│   │   │       ├── reports/
│   │   │       └── utils/
│   │   └── utils/
│   │       └── security/
│   ├── integrations/
│   │   ├── analytics/
│   │   │   └── results/
│   │   ├── external/
│   │   └── notifications/
│   ├── interfaces/
│   │   ├── api/
│   │   ├── cli/
│   │   ├── dashboard/
│   │   │   ├── api/
│   │   │   │   └── components/
│   │   │   ├── components/
│   │   │   ├── static/
│   │   │   └── templates/
│   │   ├── logs/
│   │   ├── outputs/
│   │   │   └── BE-07/
│   │   ├── visualization/
│   │   └── webhooks/
│   └── platform/
├── storage/
│   ├── feedback/
│   └── hitl_tasks/
├── tasks/
├── templates/
│   └── email/
├── test_outputs/
└── tests/
    ├── components/
    ├── data/
    │   └── storage/
    │       └── escalations/
    ├── docs/
    │   └── sprint/
    │       └── briefings/
    ├── e2e/
    │   ├── dashboard/
    │   ├── performance/
    │   ├── system/
    │   ├── user_journeys/
    │   └── workflows/
    ├── fixtures/
    │   ├── data/
    │   ├── factories/
    │   ├── mocks/
    │   └── test_data/
    ├── integration/
    │   ├── api/
    │   ├── dashboard/
    │   ├── memory/
    │   └── workflows/
    ├── logs/
    │   └── langgraph/
    ├── outputs/
    │   ├── BE-01/
    │   └── QA-INTEGRATION-01/
    ├── runtime/
    │   └── cache/
    ├── storage/
    │   └── feedback/
    ├── tasks/
    ├── templates/
    │   └── email/
    ├── unit/
    │   ├── core/
    │   │   ├── agents/
    │   │   ├── configuration/
    │   │   ├── dependency_injection/
    │   │   ├── error_handling/
    │   │   ├── states/
    │   │   ├── tasks/
    │   │   ├── validation/
    │   │   └── workflows/
    │   ├── infrastructure/
    │   │   ├── security/
    │   │   ├── tools/
    │   │   │   └── validation/
    │   │   └── utils/
    │   ├── integrations/
    │   │   ├── analytics/
    │   │   └── external/
    │   ├── interfaces/
    │   │   ├── api/
    │   │   ├── cli/
    │   │   └── dashboard/
    │   └── scripts/
    ├── utils/
    └── validation/
```

## Summary

- **Total directories**: 798 (directories only - partial view)
- **Generation method**: Depth-First Search (DFS) traversal
- **Tree algorithm**: Recursive directory iteration with ASCII formatting

## Complete Tree Structure

📋 **For the complete tree structure including all files**, see: [`complete-directory-structure.md`](./complete-directory-structure.md)

The complete structure includes:
- **3,491 files** across the entire project
- **798 directories** with full hierarchy
- **373,815 total lines** of code and documentation
- **File sizes** in appropriate units (B/K/M)
- **DFS traversal algorithm** with detailed insights
