# Complete Directory Structure

Generated on: 2025-07-21 19:16:35

## Tree Structure (DFS Traversal)

```
ai-system/
├── .claude/
│   ├── commands/
│   │   ├── agent-status.md (3.7K, 120 lines)
│   │   ├── check.md (1.6K, 64 lines)
│   │   ├── commit-fast.md (1.6K, 67 lines)
│   │   ├── create-backup.md (772B, 26 lines)
│   │   ├── create-pr.md (4.1K, 151 lines)
│   │   ├── generate-checklist.md (8.6K, 223 lines)
│   │   ├── investigate-file.md (16.9K, 415 lines)
│   │   ├── parallel-investigate.md (14.3K, 385 lines)
│   │   ├── parallel-orchestrator.md (20.4K, 568 lines)
│   │   ├── parallel-safe-fix.md (25.4K, 643 lines)
│   │   ├── run-task.md (1.9K, 76 lines)
│   │   ├── safe-auto-fix.md (18.7K, 472 lines)
│   │   ├── setup-dev.md (4.2K, 153 lines)
│   │   └── test-quick.md (1.3K, 50 lines)
│   ├── hooks.json (14B, 1 lines)
│   ├── hooks.json.backup (8.6K)
│   ├── MCP_SETUP.md (2.1K, 68 lines)
│   ├── README.md (5.7K, 178 lines)
│   └── settings.local.json (18.7K, 120 lines)
├── .vscode/
│   ├── snippets/
│   │   └── python.json (490B, 17 lines)
│   ├── extensions.json (143B, 8 lines)
│   ├── launch.json (200B, 12 lines)
│   ├── settings.json (3.3K, 119 lines)
│   └── tasks.json (5.4K, 216 lines)
├── archives/
│   ├── cold/
│   ├── warm/
│   │   └── BE-08_20250708.tar.gz (681B)
│   └── archive_metadata.json (339B, 12 lines)
├── build/
│   ├── dashboard/
│   │   └── notifications/
│   ├── runtime/
│   │   └── logs/
│   ├── storage/
│   │   ├── cold/
│   │   ├── hitl/
│   │   ├── hot/
│   │   │   └── TEST-02.dat (313B)
│   │   └── warm/
│   └── test_outputs/
├── config/
│   ├── schemas/
│   │   └── task.schema.json (4.1K, 90 lines)
│   ├── __init__.py (979B, 37 lines)
│   ├── agent_generator.yaml (86B, 4 lines)
│   ├── agents.yaml (4.3K, 166 lines)
│   ├── auto_generated_graph.json (1.1K, 67 lines)
│   ├── build_paths.py (2.4K, 84 lines)
│   ├── config_manager.py (9.6K, 278 lines)
│   ├── critical_path.yaml (723B, 32 lines)
│   ├── daily_cycle.json (661B, 26 lines)
│   ├── gemini_config.json (1.4K, 39 lines)
│   ├── hitl_policies.yaml (7.2K, 249 lines)
│   ├── memory_config.py (139B, 5 lines)
│   ├── prometheus.yml (92B, 4 lines)
│   ├── qa_thresholds.yaml (5.5K, 224 lines)
│   ├── redis.conf (34B)
│   ├── tools.yaml (2.0K, 95 lines)
│   ├── validation_config.json (4.3K, 183 lines)
│   └── webhook_external_api_config.json (1.7K, 69 lines)
├── dashboard/
│   ├── agent_status.json (154B, 9 lines)
│   ├── hitl_data.json (67.9K, 1,807 lines)
│   └── live_execution.json (119B, 6 lines)
├── data/
│   └── storage/
│       └── escalations/
│           ├── corrupted_escalation.json (19B, 1 lines)
│           └── escalations.json (4.4K, 183 lines)
├── docs/
│   ├── admin/
│   │   ├── CODE_QUALITY_IMPROVEMENTS_SUMMARY.md (7.6K, 207 lines)
│   │   ├── MEMORY_ENGINE_REFACTORING_SUMMARY.md (5.1K, 142 lines)
│   │   ├── test_results_summary.md (5.0K, 153 lines)
│   │   └── test_structure_fix_summary.md (3.6K, 108 lines)
│   ├── api/
│   │   ├── api_reference.md (1.4K, 33 lines)
│   │   ├── class_dictionary.md (1.3K, 54 lines)
│   │   ├── external_integrations.md (592B, 17 lines)
│   │   ├── function_dictionary.md (1.1K, 38 lines)
│   │   ├── hitl_routes.md (1.7K, 42 lines)
│   │   ├── module_dictionary.md (1.3K, 59 lines)
│   │   ├── README.md (10.3K, 409 lines)
│   │   ├── symbol_index.md (655B, 11 lines)
│   │   ├── unified_api_server.md (447B, 16 lines)
│   │   └── webhook_manager.md (1017B, 19 lines)
│   ├── architecture/
│   │   ├── agents/
│   │   │   ├── agent_builder.md (2.0K, 40 lines)
│   │   │   ├── agent_factory_refactoring_summary.md (4.8K, 156 lines)
│   │   │   ├── backend.md (249B, 6 lines)
│   │   │   ├── backend_agent.md (1000B, 20 lines)
│   │   │   ├── coordinator.md (250B, 6 lines)
│   │   │   ├── coordinator_agent.md (917B, 17 lines)
│   │   │   ├── doc.md (228B, 6 lines)
│   │   │   ├── documentation_agent.md (667B, 12 lines)
│   │   │   ├── factory.md (609B, 15 lines)
│   │   │   ├── frontend.md (247B, 6 lines)
│   │   │   ├── frontend_agent.md (912B, 20 lines)
│   │   │   ├── human_agents.md (1021B, 21 lines)
│   │   │   ├── qa.md (610B, 11 lines)
│   │   │   ├── qa_agent.md (1.1K, 22 lines)
│   │   │   ├── technical.md (334B, 7 lines)
│   │   │   └── technical_lead_agent.md (905B, 20 lines)
│   │   ├── agent_architecture.md (3.6K, 115 lines)
│   │   ├── agent_system_overview.md (2.1K, 42 lines)
│   │   ├── ARCHITECTURE.md (18.0K, 438 lines)
│   │   ├── context_tracking_functionality.md (308B, 9 lines)
│   │   ├── COORDINATOR_IMPROVEMENTS.md (7.2K, 181 lines)
│   │   ├── dependency_map.md (1.2K, 37 lines)
│   │   ├── error_handling.md (837B, 19 lines)
│   │   ├── ERROR_HANDLING_IMPROVEMENTS.md (11.0K, 327 lines)
│   │   ├── error_propagation_strategy.md (9.2K, 257 lines)
│   │   ├── FILE_ORGANIZATION_IMPROVEMENTS.md (7.5K, 210 lines)
│   │   ├── flow.md (195B, 7 lines)
│   │   ├── graph_builder.md (264B, 8 lines)
│   │   ├── handlers.md (395B, 11 lines)
│   │   ├── hitl_engine.md (1.5K, 20 lines)
│   │   ├── hitl_task_metadata.md (721B, 11 lines)
│   │   ├── inject_context.md (338B, 10 lines)
│   │   ├── interrupt_nodes.md (927B, 18 lines)
│   │   ├── langgraph_qa_integration.md (330B, 9 lines)
│   │   ├── memory_engine.md (16.0K, 354 lines)
│   │   ├── modernization-plan.md (31.9K, 916 lines)
│   │   ├── notification_handlers.md (701B, 11 lines)
│   │   ├── notifications.md (352B, 9 lines)
│   │   ├── qa_handler.md (71B, 4 lines)
│   │   ├── README.md (60.8K, 1,954 lines)
│   │   ├── registry.md (498B, 14 lines)
│   │   ├── scalable_storage.md (374B, 10 lines)
│   │   ├── states.md (281B, 10 lines)
│   │   ├── system_architecture.md (6.8K, 140 lines)
│   │   ├── task_lifecycle.md (468B, 10 lines)
│   │   ├── thread_safe_workflow.md (641B, 11 lines)
│   │   ├── thread_safety_implementation_summary.md (9.6K, 240 lines)
│   │   ├── tools_system.md (8.7K, 238 lines)
│   │   └── workflow_task_system.md (12.1K, 191 lines)
│   ├── cicd/
│   │   └── slack-integration-guide.md (5.2K, 174 lines)
│   ├── completions/
│   │   ├── BE-07.json (2.4K, 84 lines)
│   │   ├── BE-07.md (1.7K, 60 lines)
│   │   ├── EXAMPLE-01.md (2.1K, 105 lines)
│   │   └── PHASE7_STEP7.4_COMPLETION_SUMMARY.md (10.5K, 295 lines)
│   ├── development/
│   │   ├── debugging/
│   │   │   ├── analyze_remaining_failures.md (119B, 5 lines)
│   │   │   ├── debug_terminal_crash.md (132B, 5 lines)
│   │   │   ├── fix_unicode_escapes.md (116B, 5 lines)
│   │   │   └── verify_dashboard_fix.md (206B, 7 lines)
│   │   ├── generation/
│   │   │   ├── automated_doc_generator.md (177B, 6 lines)
│   │   │   ├── automated_symbol_extraction.md (698B, 13 lines)
│   │   │   ├── batch_qa_generation.md (284B, 8 lines)
│   │   │   ├── generate_agent.md (297B, 9 lines)
│   │   │   ├── generate_briefing.md (958B, 8 lines)
│   │   │   ├── generate_progress_report.md (512B, 8 lines)
│   │   │   ├── generate_prompt.md (179B, 6 lines)
│   │   │   └── generate_task_report.md (1.7K, 30 lines)
│   │   ├── mocking/
│   │   │   ├── mock_dependencies.md (557B, 17 lines)
│   │   │   ├── mock_environment.md (83B, 4 lines)
│   │   │   ├── mock_langchain.md (80B, 4 lines)
│   │   │   └── mock_openai_embeddings.md (248B, 8 lines)
│   │   ├── testing/
│   │   │   ├── analyse_feedback.md (778B, 8 lines)
│   │   │   ├── complete_validation.md (255B, 8 lines)
│   │   │   ├── conftest.md (1.4K, 37 lines)
│   │   │   ├── end_to_end_test.md (237B, 7 lines)
│   │   │   ├── final_validation_complete.md (158B, 6 lines)
│   │   │   ├── optimize_tests.md (891B, 22 lines)
│   │   │   ├── OPTIMIZED_TESTING.md (7.5K, 258 lines)
│   │   │   ├── pytest_simulator.md (146B, 6 lines)
│   │   │   ├── run_optimized_tests.md (153B, 6 lines)
│   │   │   ├── run_optimized_tests_enhanced.md (134B, 5 lines)
│   │   │   ├── run_tests.md (357B, 11 lines)
│   │   │   ├── setup_context_for_testing.md (138B, 5 lines)
│   │   │   ├── simple_retrieval_test.md (142B, 5 lines)
│   │   │   ├── test_collection_check.md (136B, 6 lines)
│   │   │   ├── test_sprint_phases.md (184B, 7 lines)
│   │   │   ├── test_structure.md (1.7K, 37 lines)
│   │   │   ├── testagent_agent.md (197B, 13 lines)
│   │   │   ├── testing_best_practices.md (6.5K, 218 lines)
│   │   │   ├── testvalidation_agent.md (216B, 13 lines)
│   │   │   └── validate_imports.md (227B, 8 lines)
│   │   ├── visualization/
│   │   │   ├── auto_generate_graph.md (274B, 8 lines)
│   │   │   ├── build_json.md (740B, 8 lines)
│   │   │   ├── gantt_analyzer.md (1.5K, 17 lines)
│   │   │   ├── graph_visualization.md (9.5K, 284 lines)
│   │   │   ├── sprint_visualizer.md (359B, 5 lines)
│   │   │   ├── visualize.md (121B, 5 lines)
│   │   │   ├── visualize_directory_tree.md (6.2K, 146 lines)
│   │   │   └── visualize_task_graph.md (408B, 11 lines)
│   │   ├── annotate_context_tags_tasks.md (296B, 8 lines)
│   │   ├── automation.md (6.2K, 244 lines)
│   │   ├── build_paths.md (81B, 4 lines)
│   │   ├── chromadb_telemetry_patch.md (82B, 4 lines)
│   │   ├── configuration_deep_dive.md (1.4K, 35 lines)
│   │   ├── configuration_reference.md (1.6K, 35 lines)
│   │   ├── consolidate_dashboard.md (493B, 12 lines)
│   │   ├── ENHANCED_WORKFLOW_GUIDE.md (8.5K, 358 lines)
│   │   ├── get-pip.md (258B, 9 lines)
│   │   ├── helpers.md (185B, 7 lines)
│   │   ├── INPUT_VALIDATION_IMPLEMENTATION_SUMMARY.md (8.7K, 225 lines)
│   │   ├── main.md (345B, 11 lines)
│   │   ├── main_entry_point.md (3.2K, 66 lines)
│   │   ├── migrate_source_code.md (642B, 16 lines)
│   │   ├── mock_memory_engine.md (133B, 5 lines)
│   │   ├── monkey_patch.md (80B, 4 lines)
│   │   ├── patch_dotenv.md (71B, 4 lines)
│   │   ├── README.md (4.0K, 94 lines)
│   │   ├── security.md (4.1K, 130 lines)
│   │   ├── setup.md (1.9K, 86 lines)
│   │   └── troubleshooting.md (10.8K, 556 lines)
│   ├── integrations/
│   │   └── gemini-cli.md (7.9K, 272 lines)
│   ├── operations/
│   │   ├── automation/
│   │   │   └── automation_health_check.md (263B, 5 lines)
│   │   ├── monitoring/
│   │   │   ├── monitor_workflow.md (492B, 14 lines)
│   │   │   └── workflow_monitoring.md (5.7K, 178 lines)
│   │   ├── workflows/
│   │   │   ├── archive_task.md (217B, 8 lines)
│   │   │   ├── complete_task.md (644B, 12 lines)
│   │   │   ├── daily_cycle.md (331B, 8 lines)
│   │   │   ├── daily_cycle_orchestrator.md (3.3K, 78 lines)
│   │   │   ├── delegation.md (249B, 6 lines)
│   │   │   ├── end_of_day_report.md (1.3K, 5 lines)
│   │   │   ├── enhanced_workflow.md (312B, 8 lines)
│   │   │   ├── execute_graph.md (279B, 7 lines)
│   │   │   ├── execute_task.md (244B, 7 lines)
│   │   │   ├── execute_workflow.md (382B, 9 lines)
│   │   │   ├── extract_code.md (350B, 9 lines)
│   │   │   ├── knowledge_curation_workflow.md (4.8K, 105 lines)
│   │   │   ├── langgraph_workflow.md (11.2K, 392 lines)
│   │   │   ├── plan_execution_manager.md (159B, 5 lines)
│   │   │   ├── qa_execution.md (381B, 8 lines)
│   │   │   ├── qa_validation.md (774B, 11 lines)
│   │   │   ├── register_output.md (403B, 9 lines)
│   │   │   ├── resilient_workflow.md (271B, 7 lines)
│   │   │   ├── review_context.md (182B, 8 lines)
│   │   │   ├── review_context_simple.md (189B, 8 lines)
│   │   │   ├── review_task.md (1.1K, 13 lines)
│   │   │   ├── run_workflow.md (273B, 7 lines)
│   │   │   ├── summarise_task.md (583B, 12 lines)
│   │   │   ├── task_declaration.md (645B, 11 lines)
│   │   │   ├── task_orchestration.md (16.2K, 474 lines)
│   │   │   └── workflow_executor.md (1.6K, 24 lines)
│   │   ├── email_integration.md (384B, 5 lines)
│   │   ├── list_pending_reviews.md (135B, 5 lines)
│   │   ├── manage_knowledge_reviews.md (296B, 8 lines)
│   │   ├── mark_review_complete.md (151B, 5 lines)
│   │   ├── README.md (28.1K, 993 lines)
│   │   └── update_dashboard.md (439B, 8 lines)
│   ├── optimizations/
│   │   └── PHASE2_COMPLETE_DOCUMENTATION.md (24.9K, 673 lines)
│   ├── reports/
│   │   ├── memory-engine/
│   │   │   ├── consolidate_memory.md (477B, 13 lines)
│   │   │   └── debug_memory.md (77B, 4 lines)
│   │   ├── phase7-hitl/
│   │   │   ├── phase6_enhanced_eod_reporting_guide.md (15.0K, 498 lines)
│   │   │   ├── PHASE6_STEP6.3_COMPLETION_SUMMARY.md (6.5K, 158 lines)
│   │   │   ├── PHASE6_STEP6.5_COMPLETION_SUMMARY.md (9.7K, 206 lines)
│   │   │   ├── PHASE6_STEP6.6_EMAIL_INTEGRATION_COMPLETION.md (9.2K, 229 lines)
│   │   │   └── PHASE7_STEPS7.2-7.3_COMPLETION_SUMMARY.md (11.6K, 232 lines)
│   │   ├── import_refactoring_completion_report.md (6.9K, 161 lines)
│   │   └── README.md (2.2K, 57 lines)
│   ├── security/
│   │   ├── validation/
│   │   │   ├── management_dashboard.md (16.3K, 599 lines)
│   │   │   ├── quality_gates.md (18.6K, 644 lines)
│   │   │   └── README.md (14.0K, 439 lines)
│   │   ├── README.md (8.7K, 245 lines)
│   │   └── SECURITY.md (13.6K, 444 lines)
│   ├── setup/
│   │   ├── complete-directory-structure.md (103.4K, 1,692 lines)
│   │   └── directory-structure.md (8.9K, 317 lines)
│   ├── sprint/
│   │   ├── briefings/
│   │   │   ├── day1-morning-briefing.md (2.9K, 70 lines)
│   │   │   ├── day2-morning-briefing.md (545B, 21 lines)
│   │   │   └── day3-morning-briefing.md (2.9K, 69 lines)
│   │   ├── daily_reports/
│   │   ├── BRIEFING_GENERATOR_API.md (7.8K, 258 lines)
│   │   └── PHASE6_COMPLETION_REPORT.md (4.7K, 121 lines)
│   ├── tools/
│   │   ├── validation/
│   │   │   └── README.md (14.2K, 482 lines)
│   │   ├── base_tool.md (1.3K, 36 lines)
│   │   ├── context_tracker.md (1008B, 22 lines)
│   │   ├── context_visualizer.md (779B, 21 lines)
│   │   ├── coverage_tool.md (1.1K, 30 lines)
│   │   ├── cypress_tool.md (819B, 24 lines)
│   │   ├── design_system_tool.md (146B, 6 lines)
│   │   ├── echo_tool.md (880B, 32 lines)
│   │   ├── fixed_retrieval_qa.md (162B, 6 lines)
│   │   ├── github_finalise.md (291B, 8 lines)
│   │   ├── github_tool.md (112B, 6 lines)
│   │   ├── jest_tool.md (494B, 18 lines)
│   │   ├── langChain_characterTextSplitter.md (101B, 4 lines)
│   │   ├── markdown_tool.md (123B, 6 lines)
│   │   ├── memory_engine_examples.md (624B, 19 lines)
│   │   ├── qa_cli.md (638B, 16 lines)
│   │   ├── rate_limiter.md (177B, 8 lines)
│   │   ├── retrieval_qa.md (128B, 6 lines)
│   │   ├── retrieval_qa_refactored.md (450B, 8 lines)
│   │   ├── retrieval_qa_usage.md (5.9K, 190 lines)
│   │   ├── supabase_tool.md (649B, 22 lines)
│   │   ├── tailwind_tool.md (127B, 6 lines)
│   │   ├── task_loader.md (1.2K, 32 lines)
│   │   ├── tool_loader.md (1.2K, 35 lines)
│   │   ├── utilities_catalog.md (1.2K, 24 lines)
│   │   ├── utils.md (431B, 10 lines)
│   │   ├── vercel_tool.md (111B, 6 lines)
│   │   └── vercel_tool_refactored.md (877B, 19 lines)
│   ├── user-guides/
│   │   ├── demos/
│   │   │   ├── agent_output_demo.md (85B, 4 lines)
│   │   │   ├── agent_summarization_demo.md (138B, 5 lines)
│   │   │   ├── code_extraction_demo.md (88B, 4 lines)
│   │   │   ├── hitl_cli_demo.md (272B, 5 lines)
│   │   │   ├── hitl_kanban_demo.md (311B, 12 lines)
│   │   │   ├── human-in-the-Loop_context_review.md (315B, 9 lines)
│   │   │   ├── mcp_context_usage.md (377B, 10 lines)
│   │   │   ├── qa_execution_demo.md (227B, 8 lines)
│   │   │   ├── register_agent_output_demo.md (296B, 9 lines)
│   │   │   ├── task_declaration_preparation.md (566B, 14 lines)
│   │   │   └── visualise_context_coverage.md (312B, 9 lines)
│   │   ├── documentation_completeness.md (507B, 17 lines)
│   │   ├── documentation_index.md (2.8K, 40 lines)
│   │   ├── documentation_search_index.md (2.0K, 76 lines)
│   │   ├── escalation_cli.md (427B, 11 lines)
│   │   ├── feedback_cli.md (226B, 8 lines)
│   │   ├── hitl_cli.md (671B, 17 lines)
│   │   ├── hitl_kanban_board.md (519B, 10 lines)
│   │   ├── hitl_kanban_cli.md (406B, 10 lines)
│   │   ├── hitl_kanban_dashboard.md (9.3K, 344 lines)
│   │   ├── hitl_widgets.md (944B, 20 lines)
│   │   ├── MASTER_DOCUMENTATION_GUIDE.md (6.1K, 177 lines)
│   │   ├── qa_execution_cli.md (294B, 8 lines)
│   │   ├── quick_hitl_status.md (309B, 10 lines)
│   │   ├── quick_reference_cards.md (1.2K, 36 lines)
│   │   ├── README.md (6.0K, 190 lines)
│   │   └── visual_documentation.md (1023B, 20 lines)
│   ├── INDEX.md (7.7K, 147 lines)
│   ├── README.md (9.6K, 230 lines)
│   └── sonarqube-community-setup.md (2.9K, 91 lines)
├── fix_tracking/
│   ├── phase1/
│   │   ├── add_auth_to_apis.py (3.0K, 87 lines)
│   │   ├── add_input_validation.py (6.8K, 192 lines)
│   │   ├── authentication_fix_report.md (3.0K, 94 lines)
│   │   ├── batch_add_validation_hitl.py (4.5K, 99 lines)
│   │   ├── check_input_validation_coverage.py (8.0K, 206 lines)
│   │   ├── enable_encryption_system.py (12.9K, 384 lines)
│   │   └── input_validation_completion_report.md (7.6K, 223 lines)
│   ├── phase2/
│   ├── phase3/
│   ├── phase4/
│   ├── analyze_issues.py (3.5K, 90 lines)
│   ├── file_priority_analysis.txt (84B, 3 lines)
│   ├── master_checklist.md (11.0K, 277 lines)
│   ├── priority_execution_plan.md (6.2K, 166 lines)
│   └── README.md (4.0K, 130 lines)
├── investigation_reports/
│   ├── phase1_critical/
│   │   ├── encryption_investigation.md (3.2K, 117 lines)
│   │   └── nfr_investigation.md (1.4K, 45 lines)
│   ├── phase2_imports/
│   ├── phase3_quality/
│   ├── phase4_docs/
│   ├── __init___parallel_investigation.json (1.4K, 51 lines)
│   ├── core_agents_action_items.json (4.3K, 143 lines)
│   ├── core_agents_parallel_investigation.md (4.9K, 119 lines)
│   ├── infrastructure_progress.json (4.4K, 147 lines)
│   ├── main_parallel_investigation.json (2.1K, 62 lines)
│   ├── memory__init___parallel_investigation.json (1.7K, 55 lines)
│   ├── memory_security__init___parallel_investigation.json (1.6K, 52 lines)
│   └── security__init___parallel_investigation.json (1.8K, 57 lines)
├── outputs/
│   ├── BE-01/
│   │   ├── qa_report.json (267B, 11 lines)
│   │   └── task_declaration.json (908B, 31 lines)
│   ├── BE-02/
│   │   └── task_declaration.json (748B, 31 lines)
│   ├── BE-03/
│   │   └── task_declaration.json (807B, 32 lines)
│   ├── BE-04/
│   │   ├── prompt_backend.md (785B, 29 lines)
│   │   └── task_declaration.json (1.9K, 47 lines)
│   ├── BE-05/
│   │   └── task_declaration.json (817B, 32 lines)
│   ├── BE-06/
│   │   └── task_declaration.json (703B, 28 lines)
│   ├── BE-07/
│   │   └── task_declaration.json (780B, 30 lines)
│   ├── BE-08/
│   │   └── task_declaration.json (807B, 32 lines)
│   ├── BE-09/
│   │   └── task_declaration.json (747B, 32 lines)
│   ├── BE-10/
│   │   └── task_declaration.json (761B, 31 lines)
│   ├── BE-11/
│   │   └── task_declaration.json (759B, 31 lines)
│   ├── BE-12/
│   │   └── task_declaration.json (715B, 30 lines)
│   ├── BE-13/
│   │   └── task_declaration.json (721B, 30 lines)
│   ├── BE-14/
│   │   └── task_declaration.json (789B, 32 lines)
│   ├── briefings/
│   ├── DEPENDENT-01/
│   │   └── task_declaration.json (593B, 25 lines)
│   ├── FE-01/
│   │   └── task_declaration.json (754B, 31 lines)
│   ├── FE-02/
│   │   └── task_declaration.json (862B, 35 lines)
│   ├── FE-03/
│   │   └── task_declaration.json (754B, 30 lines)
│   ├── FE-04/
│   │   └── task_declaration.json (827B, 33 lines)
│   ├── FE-05/
│   │   ├── lifecycle_tracking.json (178B, 7 lines)
│   │   └── task_declaration.json (816B, 32 lines)
│   ├── FE-06/
│   │   └── task_declaration.json (709B, 28 lines)
│   ├── INTEGRATION-01/
│   │   ├── prompt_backend.md (739B, 30 lines)
│   │   └── task_declaration.json (1.7K, 36 lines)
│   ├── LC-01/
│   │   └── task_declaration.json (720B, 26 lines)
│   ├── PM-01/
│   │   └── task_declaration.json (689B, 26 lines)
│   ├── PM-02/
│   │   └── task_declaration.json (745B, 29 lines)
│   ├── PM-03/
│   │   └── task_declaration.json (704B, 26 lines)
│   ├── PM-04/
│   │   └── task_declaration.json (727B, 29 lines)
│   ├── PM-05/
│   │   └── task_declaration.json (681B, 28 lines)
│   ├── PM-06/
│   │   └── task_declaration.json (708B, 26 lines)
│   ├── PM-07/
│   │   └── task_declaration.json (728B, 29 lines)
│   ├── PM-08/
│   │   └── task_declaration.json (690B, 26 lines)
│   ├── PM-09/
│   │   └── task_declaration.json (779B, 31 lines)
│   ├── PM-10/
│   │   └── task_declaration.json (699B, 26 lines)
│   ├── PM-11/
│   │   └── task_declaration.json (681B, 26 lines)
│   ├── PM-12/
│   │   └── task_declaration.json (702B, 28 lines)
│   ├── QA-01/
│   │   └── task_declaration.json (699B, 28 lines)
│   ├── QA-02/
│   │   └── task_declaration.json (783B, 33 lines)
│   ├── QA-03/
│   │   └── task_declaration.json (706B, 28 lines)
│   ├── QA-INTEGRATION-01/
│   │   └── qa_report.json (279B, 11 lines)
│   ├── TL-01/
│   │   └── task_declaration.json (746B, 28 lines)
│   ├── TL-02/
│   │   └── task_declaration.json (731B, 30 lines)
│   ├── TL-03/
│   │   └── task_declaration.json (846B, 33 lines)
│   ├── TL-04/
│   │   └── task_declaration.json (729B, 30 lines)
│   ├── TL-05/
│   │   └── task_declaration.json (825B, 33 lines)
│   ├── TL-06/
│   │   └── task_declaration.json (723B, 30 lines)
│   ├── TL-07/
│   │   └── task_declaration.json (769B, 31 lines)
│   ├── TL-08/
│   │   └── task_declaration.json (778B, 33 lines)
│   ├── TL-09/
│   │   └── task_declaration.json (902B, 29 lines)
│   ├── TL-10/
│   │   └── task_declaration.json (724B, 30 lines)
│   ├── TL-11/
│   │   └── task_declaration.json (763B, 29 lines)
│   ├── TL-12/
│   │   └── task_declaration.json (719B, 28 lines)
│   ├── TL-13/
│   │   └── task_declaration.json (776B, 33 lines)
│   ├── TL-14/
│   │   └── task_declaration.json (753B, 31 lines)
│   ├── TL-15/
│   │   └── task_declaration.json (827B, 33 lines)
│   ├── TL-16/
│   │   └── task_declaration.json (818B, 34 lines)
│   ├── TL-17/
│   │   └── task_declaration.json (756B, 29 lines)
│   ├── TL-18/
│   │   └── task_declaration.json (799B, 32 lines)
│   ├── TL-19/
│   │   └── task_declaration.json (762B, 31 lines)
│   ├── TL-20/
│   │   └── task_declaration.json (780B, 31 lines)
│   ├── TL-21/
│   │   └── task_declaration.json (772B, 32 lines)
│   ├── TL-22/
│   │   └── task_declaration.json (761B, 32 lines)
│   ├── TL-23/
│   │   └── task_declaration.json (760B, 31 lines)
│   ├── TL-24/
│   │   └── task_declaration.json (725B, 30 lines)
│   ├── TL-25/
│   │   └── task_declaration.json (739B, 29 lines)
│   ├── TL-26/
│   │   └── task_declaration.json (714B, 28 lines)
│   ├── TL-27/
│   │   └── task_declaration.json (745B, 30 lines)
│   ├── TL-28/
│   │   └── task_declaration.json (770B, 32 lines)
│   ├── TL-29/
│   │   └── task_declaration.json (773B, 32 lines)
│   ├── TL-30/
│   │   └── task_declaration.json (700B, 28 lines)
│   ├── UX-01/
│   │   └── task_declaration.json (729B, 27 lines)
│   ├── UX-02/
│   │   └── task_declaration.json (772B, 29 lines)
│   ├── UX-03/
│   │   └── task_declaration.json (768B, 29 lines)
│   ├── UX-04/
│   │   └── task_declaration.json (795B, 30 lines)
│   ├── UX-05/
│   │   └── task_declaration.json (807B, 30 lines)
│   ├── UX-06/
│   │   └── task_declaration.json (717B, 28 lines)
│   ├── UX-07/
│   │   └── task_declaration.json (706B, 29 lines)
│   ├── UX-08/
│   │   └── task_declaration.json (784B, 30 lines)
│   ├── UX-09/
│   │   └── task_declaration.json (772B, 33 lines)
│   ├── UX-10/
│   │   └── task_declaration.json (744B, 30 lines)
│   ├── UX-11/
│   │   └── task_declaration.json (691B, 27 lines)
│   ├── UX-12/
│   │   └── task_declaration.json (797B, 33 lines)
│   ├── UX-13/
│   │   └── task_declaration.json (844B, 39 lines)
│   ├── UX-14/
│   │   └── task_declaration.json (797B, 31 lines)
│   ├── UX-15/
│   │   └── task_declaration.json (765B, 32 lines)
│   ├── UX-16/
│   │   └── task_declaration.json (736B, 32 lines)
│   ├── UX-17/
│   │   └── task_declaration.json (756B, 30 lines)
│   ├── UX-18/
│   │   └── task_declaration.json (741B, 29 lines)
│   ├── UX-19/
│   │   └── task_declaration.json (726B, 29 lines)
│   ├── UX-21/
│   │   └── task_declaration.json (799B, 33 lines)
│   ├── UX-21b/
│   │   └── task_declaration.json (785B, 30 lines)
│   ├── UX-22/
│   │   └── task_declaration.json (761B, 29 lines)
│   ├── UX-23/
│   │   └── task_declaration.json (718B, 30 lines)
│   ├── UX-24/
│   │   └── task_declaration.json (705B, 28 lines)
│   └── UX-25/
│       └── task_declaration.json (660B, 26 lines)
├── progress_reports/
│   ├── day100_eod_report_2025-07-09.md (1.1K, 52 lines)
│   ├── day101_eod_report_2025-07-10.md (1.1K, 52 lines)
│   └── day99_eod_report_2025-07-08.md (1.1K, 52 lines)
├── reports/
│   ├── qa/
│   ├── continued_quality_improvements_report.md (9.4K, 237 lines)
│   ├── final_consolidation_summary.txt (37B, 1 lines)
│   ├── final_quality_report.md (7.1K, 148 lines)
│   ├── nfr_report.json (13.4K, 493 lines)
│   ├── owasp_compliance_report.json (3.0K, 136 lines)
│   ├── parallel_safe_fix_completion_report.md (5.4K, 120 lines)
│   ├── parallel_safe_fix_consolidation_report.json (6.2K, 172 lines)
│   ├── parallel_validation_execution_report.json (761B, 34 lines)
│   ├── parallel_validation_final_report.json (0B, 0 lines)
│   ├── phase5_coverage_report.md (7.7K, 179 lines)
│   ├── quality_gates_report.json (6.1K, 209 lines)
│   ├── validation_report.json (41.0K, 1,386 lines)
│   └── vv_report.json (2.1K, 71 lines)
├── scripts/
│   ├── clean_coverage.sh (676B, 29 lines)
│   ├── cleanup_generated_files.py (8.0K, 214 lines)
│   ├── cleanup_hitl_storage.py (9.5K, 251 lines)
│   ├── generate_encryption_keys.py (2.0K, 71 lines)
│   ├── setup-sonarqube-local.ps1 (3.6K, 87 lines)
│   ├── setup-sonarqube-local.sh (2.4K, 69 lines)
│   └── setup_sonarqube_integration.py (16.1K, 497 lines)
├── src/
│   ├── core/
│   │   ├── agents/
│   │   │   ├── __init__.py (1.3K, 60 lines)
│   │   │   ├── agent_cache.py (1.1K, 43 lines)
│   │   │   ├── backend.py (4.2K, 133 lines)
│   │   │   ├── coordinator.py (2.9K, 93 lines)
│   │   │   ├── doc.py (4.4K, 131 lines)
│   │   │   ├── factory.py (9.3K, 301 lines)
│   │   │   ├── frontend.py (4.4K, 129 lines)
│   │   │   ├── human_agents.py (1.2K, 48 lines)
│   │   │   ├── qa.py (39.9K, 1,125 lines)
│   │   │   └── technical.py (4.4K, 132 lines)
│   │   ├── domain/
│   │   │   ├── __init__.py (660B, 23 lines)
│   │   │   ├── business_rules.py (15.1K, 457 lines)
│   │   │   └── entities.py (13.4K, 392 lines)
│   │   ├── services/
│   │   │   ├── __init__.py (435B, 17 lines)
│   │   │   ├── checkpoint_service.py (16.4K, 459 lines)
│   │   │   └── workflow_service.py (14.2K, 419 lines)
│   │   ├── states/
│   │   │   └── __init__.py (28B, 1 lines)
│   │   ├── tasks/
│   │   │   ├── backend/
│   │   │   │   └── __init__.py (28B, 1 lines)
│   │   │   ├── frontend/
│   │   │   │   └── __init__.py (28B, 1 lines)
│   │   │   ├── general/
│   │   │   │   └── __init__.py (28B, 1 lines)
│   │   │   ├── qa/
│   │   │   │   └── __init__.py (28B, 1 lines)
│   │   │   ├── technical_lead/
│   │   │   │   └── __init__.py (28B, 1 lines)
│   │   │   ├── __init__.py (28B, 1 lines)
│   │   │   ├── BE-01.yaml (563B, 20 lines)
│   │   │   ├── BE-02.yaml (396B, 17 lines)
│   │   │   ├── BE-03.yaml (453B, 18 lines)
│   │   │   ├── BE-04.yaml (397B, 17 lines)
│   │   │   ├── BE-05.yaml (463B, 18 lines)
│   │   │   ├── BE-06.yaml (360B, 15 lines)
│   │   │   ├── BE-07.yaml (526B, 25 lines)
│   │   │   ├── BE-08.yaml (453B, 18 lines)
│   │   │   ├── BE-09.yaml (393B, 18 lines)
│   │   │   ├── BE-10.yaml (409B, 17 lines)
│   │   │   ├── BE-11.yaml (407B, 17 lines)
│   │   │   ├── BE-12.yaml (365B, 16 lines)
│   │   │   ├── BE-13.yaml (371B, 16 lines)
│   │   │   ├── BE-14.yaml (435B, 18 lines)
│   │   │   ├── FE-01.yaml (402B, 17 lines)
│   │   │   ├── FE-02.yaml (502B, 21 lines)
│   │   │   ├── FE-03.yaml (404B, 16 lines)
│   │   │   ├── FE-04.yaml (471B, 19 lines)
│   │   │   ├── FE-05.yaml (462B, 18 lines)
│   │   │   ├── FE-06.yaml (366B, 15 lines)
│   │   │   ├── LC-01.yaml (381B, 13 lines)
│   │   │   ├── PM-01.yaml (350B, 13 lines)
│   │   │   ├── PM-02.yaml (397B, 15 lines)
│   │   │   ├── PM-03.yaml (365B, 13 lines)
│   │   │   ├── PM-04.yaml (379B, 15 lines)
│   │   │   ├── PM-05.yaml (335B, 14 lines)
│   │   │   ├── PM-06.yaml (369B, 13 lines)
│   │   │   ├── PM-07.yaml (380B, 15 lines)
│   │   │   ├── PM-08.yaml (351B, 13 lines)
│   │   │   ├── PM-09.yaml (427B, 17 lines)
│   │   │   ├── PM-10.yaml (360B, 13 lines)
│   │   │   ├── PM-11.yaml (342B, 13 lines)
│   │   │   ├── PM-12.yaml (356B, 14 lines)
│   │   │   ├── QA-01.yaml (356B, 15 lines)
│   │   │   ├── QA-02.yaml (427B, 19 lines)
│   │   │   ├── QA-03.yaml (363B, 15 lines)
│   │   │   ├── task-schema.json (1.9K, 67 lines)
│   │   │   ├── TL-01.yaml (403B, 15 lines)
│   │   │   ├── TL-02.yaml (381B, 16 lines)
│   │   │   ├── TL-03.yaml (490B, 19 lines)
│   │   │   ├── TL-04.yaml (379B, 16 lines)
│   │   │   ├── TL-05.yaml (469B, 19 lines)
│   │   │   ├── TL-06.yaml (373B, 16 lines)
│   │   │   ├── TL-07.yaml (417B, 17 lines)
│   │   │   ├── TL-08.yaml (422B, 19 lines)
│   │   │   ├── TL-09.yaml (564B, 19 lines)
│   │   │   ├── TL-10.yaml (374B, 16 lines)
│   │   │   ├── TL-11.yaml (418B, 16 lines)
│   │   │   ├── TL-12.yaml (376B, 15 lines)
│   │   │   ├── TL-13.yaml (420B, 19 lines)
│   │   │   ├── TL-14.yaml (401B, 17 lines)
│   │   │   ├── TL-15.yaml (471B, 19 lines)
│   │   │   ├── TL-16.yaml (460B, 20 lines)
│   │   │   ├── TL-17.yaml (411B, 16 lines)
│   │   │   ├── TL-18.yaml (445B, 18 lines)
│   │   │   ├── TL-19.yaml (410B, 17 lines)
│   │   │   ├── TL-20.yaml (428B, 17 lines)
│   │   │   ├── TL-21.yaml (418B, 18 lines)
│   │   │   ├── TL-22.yaml (407B, 18 lines)
│   │   │   ├── TL-23.yaml (408B, 17 lines)
│   │   │   ├── TL-24.yaml (375B, 16 lines)
│   │   │   ├── TL-25.yaml (394B, 16 lines)
│   │   │   ├── TL-26.yaml (371B, 15 lines)
│   │   │   ├── TL-27.yaml (395B, 16 lines)
│   │   │   ├── TL-28.yaml (416B, 18 lines)
│   │   │   ├── TL-29.yaml (419B, 18 lines)
│   │   │   ├── TL-30.yaml (357B, 15 lines)
│   │   │   ├── UX-01.yaml (388B, 14 lines)
│   │   │   ├── UX-02.yaml (424B, 15 lines)
│   │   │   ├── UX-03.yaml (420B, 15 lines)
│   │   │   ├── UX-04.yaml (445B, 16 lines)
│   │   │   ├── UX-05.yaml (457B, 16 lines)
│   │   │   ├── UX-06.yaml (374B, 15 lines)
│   │   │   ├── UX-07.yaml (358B, 15 lines)
│   │   │   ├── UX-08.yaml (434B, 16 lines)
│   │   │   ├── UX-09.yaml (416B, 19 lines)
│   │   │   ├── UX-10.yaml (394B, 16 lines)
│   │   │   ├── UX-11.yaml (350B, 14 lines)
│   │   │   ├── UX-12.yaml (441B, 19 lines)
│   │   │   ├── UX-13.yaml (476B, 25 lines)
│   │   │   ├── UX-14.yaml (445B, 17 lines)
│   │   │   ├── UX-15.yaml (411B, 18 lines)
│   │   │   ├── UX-16.yaml (382B, 18 lines)
│   │   │   ├── UX-17.yaml (406B, 16 lines)
│   │   │   ├── UX-18.yaml (393B, 15 lines)
│   │   │   ├── UX-19.yaml (378B, 15 lines)
│   │   │   ├── UX-21.yaml (443B, 19 lines)
│   │   │   ├── UX-21b.yaml (435B, 16 lines)
│   │   │   ├── UX-22.yaml (413B, 15 lines)
│   │   │   ├── UX-23.yaml (368B, 16 lines)
│   │   │   ├── UX-24.yaml (359B, 14 lines)
│   │   │   └── UX-25.yaml (321B, 13 lines)
│   │   ├── workflows/
│   │   │   ├── graph/
│   │   │   │   ├── config/
│   │   │   │   │   ├── critical_path.html (993B, 33 lines)
│   │   │   │   │   └── critical_path.mmd (703B)
│   │   │   │   ├── __init__.py (26B, 1 lines)
│   │   │   │   ├── auto_generate_graph.py (15.1K, 450 lines)
│   │   │   │   ├── flow.py (4.3K, 144 lines)
│   │   │   │   ├── graph_builder.py (30.5K, 819 lines)
│   │   │   │   ├── handlers.py (20.1K, 613 lines)
│   │   │   │   ├── interrupt_nodes.py (16.4K, 487 lines)
│   │   │   │   ├── notifications.py (10.6K, 331 lines)
│   │   │   │   ├── resilient_workflow.py (8.0K, 261 lines)
│   │   │   │   └── visualize.py (3.3K, 115 lines)
│   │   │   ├── hitl/
│   │   │   │   ├── __init__.py (622B, 24 lines)
│   │   │   │   ├── core_engine.py (197B, 10 lines)
│   │   │   │   ├── models.py (5.2K, 166 lines)
│   │   │   │   ├── policy_engine.py (14.6K, 438 lines)
│   │   │   │   └── types.py (923B, 46 lines)
│   │   │   ├── __init__.py (1.1K, 46 lines)
│   │   │   ├── automation_health_check.py (16.2K, 456 lines)
│   │   │   ├── complete_task.py (26.0K, 739 lines)
│   │   │   ├── daily_cycle.py (33.0K, 906 lines)
│   │   │   ├── delegation.py (3.8K, 128 lines)
│   │   │   ├── documentation_agent.py (27.3K, 784 lines)
│   │   │   ├── email_integration.py (22.4K, 626 lines)
│   │   │   ├── end_of_day_report.py (27.0K, 675 lines)
│   │   │   ├── enhanced_workflow.py (18.6K, 549 lines)
│   │   │   ├── error_handling.py (22.4K, 648 lines)
│   │   │   ├── execute_graph.py (33.0K, 963 lines)
│   │   │   ├── execute_task.py (11.2K, 338 lines)
│   │   │   ├── execute_workflow.py (19.0K, 574 lines)
│   │   │   ├── extract_code.py (17.2K, 494 lines)
│   │   │   ├── gantt_analyzer.py (174B, 9 lines)
│   │   │   ├── generate_briefing.py (31.3K, 955 lines)
│   │   │   ├── generate_prompt.py (1.2K, 51 lines)
│   │   │   ├── hitl_engine.py (57.6K, 1,556 lines)
│   │   │   ├── hitl_task_metadata.py (17.9K, 506 lines)
│   │   │   ├── inject_context.py (735B, 26 lines)
│   │   │   ├── langgraph_qa_integration.py (9.5K, 291 lines)
│   │   │   ├── notification_handlers.py (25.0K, 700 lines)
│   │   │   ├── plan_execution_manager.py (11.8K, 308 lines)
│   │   │   ├── qa_execution.py (15.1K, 474 lines)
│   │   │   ├── qa_validation.py (24.8K, 695 lines)
│   │   │   ├── README.md (2.5K, 78 lines)
│   │   │   ├── register_output.py (3.7K, 114 lines)
│   │   │   ├── registry.py (2.4K, 90 lines)
│   │   │   ├── review_context.py (173B, 9 lines)
│   │   │   ├── review_context_simple.py (208B, 9 lines)
│   │   │   ├── review_task.py (177B, 9 lines)
│   │   │   ├── run_workflow.py (6.9K, 249 lines)
│   │   │   ├── scalable_storage.py (7.3K, 232 lines)
│   │   │   ├── sprint_visualizer.py (207B, 9 lines)
│   │   │   ├── states.py (2.9K, 109 lines)
│   │   │   ├── summarise_task.py (26.3K, 778 lines)
│   │   │   ├── task_declaration.py (29.2K, 803 lines)
│   │   │   ├── task_lifecycle.py (19.3K, 561 lines)
│   │   │   └── thread_safe_workflow.py (439B, 24 lines)
│   │   └── __init__.py (337B, 9 lines)
│   ├── examples/
│   │   ├── __init__.py (29B, 1 lines)
│   │   ├── agent_output_demo.py (3.3K, 88 lines)
│   │   ├── agent_summarization_demo.py (13.4K, 458 lines)
│   │   ├── annotate_context_tags_tasks.py (13.1K, 358 lines)
│   │   ├── code_extraction_demo.py (4.1K, 153 lines)
│   │   ├── complete_validation.py (11.9K, 338 lines)
│   │   ├── context_tracking_functionality.py (9.9K, 303 lines)
│   │   ├── daily_cycle_demo.py (3.6K, 99 lines)
│   │   ├── hitl_cli_demo.py (15.3K, 430 lines)
│   │   ├── human-in-the-_loop_context_review.py (8.7K, 274 lines)
│   │   ├── lang_chain_character_text_splitter.py (6.9K, 191 lines)
│   │   ├── mcp_context_usage.py (9.0K, 280 lines)
│   │   ├── qa_execution_demo.py (10.3K, 340 lines)
│   │   ├── register_agent_output_demo.py (21.8K, 698 lines)
│   │   ├── task_declaration_preparation.py (13.4K, 393 lines)
│   │   └── visualise_context_coverage.py (10.7K, 317 lines)
│   ├── infrastructure/
│   │   ├── .approved/
│   │   ├── data/
│   │   │   ├── context/
│   │   │   │   ├── backend/
│   │   │   │   │   └── api-patterns.md (866B, 42 lines)
│   │   │   │   ├── db/
│   │   │   │   │   ├── db-schema-summary.md (1.1K, 28 lines)
│   │   │   │   │   ├── schema-summary.md (2.2K, 90 lines)
│   │   │   │   │   ├── schema.md (2.6K, 101 lines)
│   │   │   │   │   └── schema.sql (4.9K, 129 lines)
│   │   │   │   ├── design/
│   │   │   │   │   └── homepage-wireframe-summary.md (1.0K, 34 lines)
│   │   │   │   ├── infra/
│   │   │   │   │   ├── supabase-setup-summary.md (918B, 42 lines)
│   │   │   │   │   └── supabase-setup.md (2.0K, 86 lines)
│   │   │   │   ├── patterns/
│   │   │   │   │   ├── api-route-integration.md (2.8K, 110 lines)
│   │   │   │   │   ├── error-handling-pattern.md (1.6K, 60 lines)
│   │   │   │   │   ├── service-crud-operations.md (3.6K, 153 lines)
│   │   │   │   │   ├── service-layer-overview.md (2.2K, 70 lines)
│   │   │   │   │   ├── service-layer-pattern-summary.md (2.2K, 90 lines)
│   │   │   │   │   ├── service-layer-pattern.md (4.9K, 217 lines)
│   │   │   │   │   ├── service-layer-summary.md (753B, 32 lines)
│   │   │   │   │   ├── service-layer.md (1.6K, 61 lines)
│   │   │   │   │   ├── service-pattern.md (4.9K, 217 lines)
│   │   │   │   │   └── service-response-pattern.md (1.5K, 54 lines)
│   │   │   │   ├── sprint/
│   │   │   │   │   ├── day2-plan-summary.md (276B, 13 lines)
│   │   │   │   │   ├── day2-plan.md (1.8K, 69 lines)
│   │   │   │   │   ├── day3-plan.md (1.7K, 70 lines)
│   │   │   │   │   ├── day4-plan.md (1.6K, 69 lines)
│   │   │   │   │   ├── day5-plan.md (1.8K, 76 lines)
│   │   │   │   │   ├── pre_sprint0_tasks.md (33.9K, 672 lines)
│   │   │   │   │   ├── sprint-overview.md (1.0K, 34 lines)
│   │   │   │   │   ├── sprint-phase0-summary.md (1.2K, 27 lines)
│   │   │   │   │   └── sprint0_checklist.md (5.6K, 187 lines)
│   │   │   │   ├── technical/
│   │   │   │   │   ├── agent-architecture-summary.md (1.5K, 33 lines)
│   │   │   │   │   ├── agent-system-architecture.md (2.4K, 62 lines)
│   │   │   │   │   ├── knowledge_curation_workflow.md (4.8K, 105 lines)
│   │   │   │   │   ├── langgraph-workflow-architecture.md (2.7K, 97 lines)
│   │   │   │   │   ├── memory-engine-architecture.md (4.9K, 106 lines)
│   │   │   │   │   ├── memory-engine-summary.md (3.3K, 75 lines)
│   │   │   │   │   ├── system-overview.md (5.4K, 90 lines)
│   │   │   │   │   ├── system_architecture.md (6.8K, 140 lines)
│   │   │   │   │   ├── task-orchestration-architecture.md (3.2K, 99 lines)
│   │   │   │   │   └── tool-system-architecture.md (2.7K, 109 lines)
│   │   │   │   ├── agent-task-assignments.json (4B, 1 lines)
│   │   │   │   ├── agent_task_assignments.json (20.3K, 651 lines)
│   │   │   │   ├── db-schema.md (2.6K, 101 lines)
│   │   │   │   ├── pre_sprint0_tasks.md (33.9K, 672 lines)
│   │   │   │   ├── README.md (2.0K, 39 lines)
│   │   │   │   ├── service-pattern.md (4.9K, 217 lines)
│   │   │   │   └── sprint0_checklist.md (5.6K, 187 lines)
│   │   │   ├── sprints/
│   │   │   │   ├── audit/
│   │   │   │   │   ├── report/
│   │   │   │   │   │   ├── code-architecture-quality-audit-completed.md (11.4K, 273 lines)
│   │   │   │   │   │   └── testability-audit-completed.md (12.5K, 323 lines)
│   │   │   │   │   ├── advanced-enhancements-audit.md (3.1K, 108 lines)
│   │   │   │   │   ├── cli-execution-layer-audit.md (3.2K, 109 lines)
│   │   │   │   │   ├── code-architecture-quality-audit.md (3.2K, 108 lines)
│   │   │   │   │   ├── code-quality-audit-completed.md (12.2K, 330 lines)
│   │   │   │   │   ├── code-review-memory-engine.md (22.2K, 142 lines)
│   │   │   │   │   ├── crewai-integration-audit.md (3.1K, 92 lines)
│   │   │   │   │   ├── external-tool-integration-audit.md (3.0K, 108 lines)
│   │   │   │   │   ├── implementation-gap-analysis-audit.md (3.9K, 141 lines)
│   │   │   │   │   ├── langgraph-task-orchestration-audit.md (2.4K, 73 lines)
│   │   │   │   │   ├── performance-security-audit.md (3.0K, 107 lines)
│   │   │   │   │   ├── protocol-alignment-audit.md (3.1K, 106 lines)
│   │   │   │   │   ├── technical-audit-summary.md (2.8K, 130 lines)
│   │   │   │   │   ├── testability-audit.md (3.1K, 108 lines)
│   │   │   │   │   └── testability-recommendations.md (5.6K, 198 lines)
│   │   │   │   ├── phase6_implementation_prompt.md (13.0K, 329 lines)
│   │   │   │   ├── phase6_technical_roadmap.md (14.1K, 450 lines)
│   │   │   │   ├── phase7_implementation_prompt.md (27.6K, 723 lines)
│   │   │   │   ├── sprint_phase0_setup.txt (3.6K, 76 lines)
│   │   │   │   ├── sprint_phase1_success.txt (3.8K, 71 lines)
│   │   │   │   ├── sprint_phase2_success.txt (6.1K, 131 lines)
│   │   │   │   ├── sprint_phase3_knowledge.txt (13.5K, 287 lines)
│   │   │   │   ├── sprint_phase4_execution.txt (9.4K, 223 lines)
│   │   │   │   ├── sprint_phase5_reporting.txt (10.3K, 237 lines)
│   │   │   │   ├── sprint_phase6_automation.txt (16.1K, 365 lines)
│   │   │   │   ├── sprint_phase7_Human-in-the-Loop.txt (65.7K, 1,408 lines)
│   │   │   │   ├── system_implementation.txt (44.5K, 1,637 lines)
│   │   │   │   └── technical-audit-tasks.md (13.3K, 296 lines)
│   │   │   └── storage/
│   │   │       ├── cold/
│   │   │       │   └── context/
│   │   │       ├── hot/
│   │   │       │   └── context/
│   │   │       └── warm/
│   │   │           └── context/
│   │   ├── memory/
│   │   │   ├── config/
│   │   │   │   ├── __init__.py (415B, 21 lines)
│   │   │   │   ├── config.py (1.4K, 65 lines)
│   │   │   │   ├── factory.py (3.8K, 141 lines)
│   │   │   │   └── memory_config.py (5.7K, 184 lines)
│   │   │   ├── engines/
│   │   │   │   ├── __init__.py (329B, 11 lines)
│   │   │   │   ├── caching.py (349B, 19 lines)
│   │   │   │   ├── chunking.py (1.1K, 37 lines)
│   │   │   │   ├── memory_engine.py (40.6K, 1,145 lines)
│   │   │   │   └── storage.py (755B, 30 lines)
│   │   │   ├── knowledge/
│   │   │   │   ├── __init__.py (43B, 1 lines)
│   │   │   │   ├── active_context.md (7.5K, 150 lines)
│   │   │   │   ├── context_manager.py (2.5K, 77 lines)
│   │   │   │   ├── product_context.md (4.4K, 96 lines)
│   │   │   │   ├── progress.md (8.7K, 227 lines)
│   │   │   │   ├── project_brief.md (2.6K, 57 lines)
│   │   │   │   ├── README.md (6.7K, 200 lines)
│   │   │   │   ├── system_patterns.md (9.5K, 212 lines)
│   │   │   │   └── tech_context.md (8.6K, 266 lines)
│   │   │   ├── security/
│   │   │   │   ├── __init__.py (1.2K, 47 lines)
│   │   │   │   ├── encryption.py (13.5K, 396 lines)
│   │   │   │   ├── security_manager.py (5.3K, 195 lines)
│   │   │   │   └── thread_safety.py (13.4K, 401 lines)
│   │   │   ├── __init__.py (3.2K, 122 lines)
│   │   │   ├── caching.py (5.0K, 184 lines)
│   │   │   ├── chunking.py (10.9K, 365 lines)
│   │   │   ├── exceptions.py (993B, 57 lines)
│   │   │   └── storage.py (17.0K, 519 lines)
│   │   ├── prompts/
│   │   │   ├── __init__.py (28B, 1 lines)
│   │   │   ├── backend-agent.md (1.2K, 40 lines)
│   │   │   ├── coordinator.md (1.3K, 43 lines)
│   │   │   ├── doc-agent.md (1.8K, 71 lines)
│   │   │   ├── frontend-agent.md (1.7K, 57 lines)
│   │   │   ├── product-manager.md (1.4K, 46 lines)
│   │   │   ├── qa-agent.md (2.1K, 70 lines)
│   │   │   ├── technical-architect.md (2.5K, 71 lines)
│   │   │   ├── utils.py (5.0K, 170 lines)
│   │   │   └── ux-designer.md (1.5K, 45 lines)
│   │   ├── reviews/
│   │   │   ├── __init__.py (37B, 1 lines)
│   │   │   ├── qa_BE-07.md (122B, 7 lines)
│   │   │   ├── qa_BE-07.md.meta.json (124B, 6 lines)
│   │   │   ├── qa_BE-08.md (102B, 7 lines)
│   │   │   ├── qa_BE-08.md.meta.json (124B, 6 lines)
│   │   │   ├── qa_QA-01.md (123B, 7 lines)
│   │   │   └── qa_QA-01.md.meta.json (124B, 6 lines)
│   │   ├── runtime/
│   │   │   └── chroma_db/
│   │   ├── scripts/
│   │   │   ├── generation/
│   │   │   │   ├── __init__.py (34B, 1 lines)
│   │   │   │   ├── automated_doc_generator.py (2.6K, 90 lines)
│   │   │   │   ├── batch_qa_generation.py (5.5K, 180 lines)
│   │   │   │   ├── generate_agent.py (4.9K, 175 lines)
│   │   │   │   ├── generate_memory_key.py (3.9K, 122 lines)
│   │   │   │   ├── generate_progress_report.py (15.4K, 431 lines)
│   │   │   │   └── generate_task_report.py (36.8K, 1,060 lines)
│   │   │   ├── monitoring/
│   │   │   │   ├── __init__.py (34B, 1 lines)
│   │   │   │   ├── benchmark_agents.py (201B, 13 lines)
│   │   │   │   ├── monitor_workflow.py (25.0K, 784 lines)
│   │   │   │   ├── update_dashboard.py (13.8K, 378 lines)
│   │   │   │   ├── visualize_directory_tree.py (15.4K, 506 lines)
│   │   │   │   └── visualize_task_graph.py (13.5K, 482 lines)
│   │   │   ├── testing/
│   │   │   │   ├── validation/
│   │   │   │   │   ├── __init__.py (39B, 1 lines)
│   │   │   │   │   ├── analyze_dependencies.py (16.7K, 440 lines)
│   │   │   │   │   ├── validate_canvas_height_fix.py (6.4K, 166 lines)
│   │   │   │   │   ├── validate_chart_fix.py (10.9K, 288 lines)
│   │   │   │   │   ├── validate_dashboard_loading_fix.py (7.7K, 194 lines)
│   │   │   │   │   ├── validate_dashboard_stability.py (7.2K, 216 lines)
│   │   │   │   │   ├── validate_hitl_dashboard.py (10.3K, 308 lines)
│   │   │   │   │   ├── validate_imports.py (28.0K, 729 lines)
│   │   │   │   │   └── validate_remaining_loading_fix.py (9.7K, 225 lines)
│   │   │   │   ├── __init__.py (31B, 1 lines)
│   │   │   │   ├── end_to_end_test.py (11.8K, 376 lines)
│   │   │   │   ├── health_check.py (13.3K, 433 lines)
│   │   │   │   ├── run_optimized_tests_enhanced.py (6.7K, 206 lines)
│   │   │   │   ├── setup_context_for_testing.py (8.9K, 360 lines)
│   │   │   │   ├── test_notebook_dependencies.py (3.3K, 121 lines)
│   │   │   │   ├── test_workflows.py (195B, 13 lines)
│   │   │   │   ├── test_zero_vulnerabilities.py (4.5K, 154 lines)
│   │   │   │   ├── validate_mock_fixes.py (5.1K, 137 lines)
│   │   │   │   ├── validate_workflow.py (3.9K, 127 lines)
│   │   │   │   └── validate_workflows.py (199B, 12 lines)
│   │   │   ├── utilities/
│   │   │   │   ├── db/
│   │   │   │   │   └── init.sql (107B, 5 lines)
│   │   │   │   ├── __init__.py (33B, 1 lines)
│   │   │   │   ├── archive_task.py (10.1K, 320 lines)
│   │   │   │   ├── debug_extraction_patterns.py (4.9K, 198 lines)
│   │   │   │   ├── debug_memory.py (2.1K, 73 lines)
│   │   │   │   ├── dev.sh (11.2K, 328 lines)
│   │   │   │   ├── fix_imports.py (6.7K, 192 lines)
│   │   │   │   ├── fix_mock_specs.py (3.1K, 97 lines)
│   │   │   │   ├── github_finalise.py (13.1K, 419 lines)
│   │   │   │   ├── health-check.sh (120B, 7 lines)
│   │   │   │   ├── list_pending_reviews.py (2.1K, 74 lines)
│   │   │   │   ├── manage_knowledge_reviews.py (6.3K, 201 lines)
│   │   │   │   ├── mark_review_complete.py (3.7K, 114 lines)
│   │   │   │   ├── patch_dotenv.py (1.4K, 51 lines)
│   │   │   │   ├── revert_and_fix_syntax.py (14.0K, 341 lines)
│   │   │   │   ├── setup_gemini_cli.py (7.4K, 246 lines)
│   │   │   │   ├── test-watch.sh (274B, 11 lines)
│   │   │   │   ├── utils.sh (159B, 8 lines)
│   │   │   │   └── verify_security.py (6.8K, 211 lines)
│   │   │   └── __init__.py (36B, 3 lines)
│   │   ├── security/
│   │   │   ├── __init__.py (1.3K, 44 lines)
│   │   │   ├── audit_imports.py (16.3K, 477 lines)
│   │   │   ├── auth_middleware.py (4.8K, 161 lines)
│   │   │   ├── chromadb_telemetry_patch.py (2.2K, 58 lines)
│   │   │   ├── encryption.py (276B, 14 lines)
│   │   │   ├── import_security.py (14.5K, 422 lines)
│   │   │   ├── input_validator.py (6.9K, 215 lines)
│   │   │   ├── README.md (1.5K, 46 lines)
│   │   │   └── system_encryption.py (6.1K, 198 lines)
│   │   ├── storage/
│   │   │   ├── feedback/
│   │   │   │   ├── feedback_064d1e70-51d0-487e-9757-ab73cca3ec2f.json (510B, 22 lines)
│   │   │   │   ├── feedback_1873db85-0bc2-4166-a64a-5264c688e84e.json (535B, 24 lines)
│   │   │   │   └── feedback_bb5227fc-2605-4c28-926c-cd64973b5653.json (381B, 16 lines)
│   │   │   ├── __init__.py (28B, 1 lines)
│   │   │   └── storage_metadata.json (354B, 15 lines)
│   │   ├── templates/
│   │   │   ├── agent/
│   │   │   │   ├── agent.py.j2 (690B)
│   │   │   │   ├── doc.md.j2 (223B)
│   │   │   │   └── test_agent.py.j2 (162B)
│   │   │   └── email/
│   │   │       ├── eod_report.html (2.1K, 61 lines)
│   │   │       └── morning_briefing.html (2.3K, 64 lines)
│   │   ├── tools/
│   │   │   ├── core/
│   │   │   │   ├── base_tool.py (7.1K, 245 lines)
│   │   │   │   ├── echo_tool.py (1.8K, 62 lines)
│   │   │   │   ├── retrieval_qa.py (3.8K, 132 lines)
│   │   │   │   └── tool_loader.py (388B, 19 lines)
│   │   │   ├── external/
│   │   │   │   └── supabase_tool.py (24.9K, 689 lines)
│   │   │   ├── handlers/
│   │   │   │   ├── __init__.py (150B, 8 lines)
│   │   │   │   ├── handlers.py (3.5K, 141 lines)
│   │   │   │   └── qa_handler.py (1.9K, 79 lines)
│   │   │   ├── validation/
│   │   │   │   ├── ai/
│   │   │   │   │   ├── __init__.py (383B, 18 lines)
│   │   │   │   │   ├── business_logic_protector.py (22.3K, 577 lines)
│   │   │   │   │   └── pattern_detector.py (37.0K, 954 lines)
│   │   │   │   ├── core/
│   │   │   │   │   ├── __init__.py (660B, 24 lines)
│   │   │   │   │   ├── auto_fixer.py (15.4K, 426 lines)
│   │   │   │   │   ├── base_validator.py (12.3K, 343 lines)
│   │   │   │   │   ├── comprehensive_validator.py (48B, 1 lines)
│   │   │   │   │   ├── dependency_validator.py (37.5K, 995 lines)
│   │   │   │   │   ├── incremental_analyzer.py (19.8K, 568 lines)
│   │   │   │   │   ├── issue_model.py (3.2K, 103 lines)
│   │   │   │   │   ├── nfr_validator.py (47.8K, 1,325 lines)
│   │   │   │   │   ├── performance_validator.py (13.5K, 346 lines)
│   │   │   │   │   ├── quality_gates.py (31.6K, 856 lines)
│   │   │   │   │   ├── shared_file_collector.py (5.4K, 179 lines)
│   │   │   │   │   ├── structure_validator.py (15.7K, 379 lines)
│   │   │   │   │   ├── syntax_validator.py (15.8K, 417 lines)
│   │   │   │   │   ├── tool_installer.py (9.0K, 268 lines)
│   │   │   │   │   ├── unified_validator.py (48B, 1 lines)
│   │   │   │   │   ├── validation_cli.py (21.4K, 617 lines)
│   │   │   │   │   ├── validator.py (34.4K, 903 lines)
│   │   │   │   │   └── vv_validator.py (39.0K, 1,010 lines)
│   │   │   │   ├── dashboard/
│   │   │   │   │   └── management_dashboard.py (35.4K, 942 lines)
│   │   │   │   ├── persistence/
│   │   │   │   │   ├── __init__.py (209B, 8 lines)
│   │   │   │   │   ├── README.md (7.8K, 290 lines)
│   │   │   │   │   └── validation_history.py (23.3K, 643 lines)
│   │   │   │   ├── __init__.py (991B, 32 lines)
│   │   │   │   ├── CLEANUP_SUMMARY.md (47B, 1 lines)
│   │   │   │   ├── fast_precommit_validator.py (5.1K, 165 lines)
│   │   │   │   ├── MIGRATION_GUIDE.md (47B, 1 lines)
│   │   │   │   ├── README.md (10.5K, 368 lines)
│   │   │   │   ├── sonarqube_integrator.py (17.3K, 488 lines)
│   │   │   │   ├── validate.py (702B, 31 lines)
│   │   │   │   ├── validation_report.py (11.0K, 339 lines)
│   │   │   │   └── VERIFICATION_REPORT.md (47B, 1 lines)
│   │   │   ├── __init__.py (139B, 8 lines)
│   │   │   ├── context_tracker.py (11.2K, 340 lines)
│   │   │   ├── context_visualizer.py (24.3K, 723 lines)
│   │   │   └── resilient_workflow.py (10.0K, 303 lines)
│   │   ├── utils/
│   │   │   ├── security/
│   │   │   │   ├── __init__.py (40B, 3 lines)
│   │   │   │   ├── encryption.py (276B, 14 lines)
│   │   │   │   └── thread_safety.py (336B, 20 lines)
│   │   │   ├── __init__.py (816B, 32 lines)
│   │   │   ├── api_validation.py (18.5K, 593 lines)
│   │   │   ├── completion_metrics.py (5.9K, 179 lines)
│   │   │   ├── coverage_analyzer.py (20.0K, 529 lines)
│   │   │   ├── escalation_system.py (38.3K, 1,048 lines)
│   │   │   ├── execution_monitor.py (14.0K, 414 lines)
│   │   │   ├── feedback_system.py (27.9K, 838 lines)
│   │   │   ├── input_validation.py (23.6K, 745 lines)
│   │   │   ├── integration_analyzer.py (19.1K, 517 lines)
│   │   │   ├── migrate_tasks.py (4.6K, 152 lines)
│   │   │   ├── mock_dotenv.py (128B, 9 lines)
│   │   │   ├── review.py (4.3K, 169 lines)
│   │   │   ├── scheduler.py (271B, 16 lines)
│   │   │   ├── schema_manager.py (15.2K, 465 lines)
│   │   │   ├── task_loader.py (5.3K, 184 lines)
│   │   │   └── workflow_recursion_fix.py (142B, 4 lines)
│   │   └── __init__.py (578B, 26 lines)
│   ├── integrations/
│   │   ├── analytics/
│   │   │   ├── results/
│   │   │   │   ├── __init__.py (28B, 1 lines)
│   │   │   │   └── BE-07_analysis_20250611_004345.json (394B, 16 lines)
│   │   │   ├── __init__.py (43B, 3 lines)
│   │   │   └── analyse_feedback.py (33.0K, 887 lines)
│   │   ├── external/
│   │   │   └── __init__.py (28B, 1 lines)
│   │   ├── notifications/
│   │   │   └── __init__.py (28B, 1 lines)
│   │   └── __init__.py (362B, 16 lines)
│   ├── interfaces/
│   │   ├── api/
│   │   │   ├── __init__.py (43B, 3 lines)
│   │   │   ├── external_integrations.py (31.8K, 942 lines)
│   │   │   ├── hitl_routes.py (65.9K, 2,011 lines)
│   │   │   └── webhook_manager.py (25.8K, 739 lines)
│   │   ├── cli/
│   │   │   ├── __init__.py (43B, 3 lines)
│   │   │   ├── escalation_cli.py (12.1K, 346 lines)
│   │   │   ├── feedback_cli.py (10.0K, 294 lines)
│   │   │   ├── gemini_cli.py (19.5K, 577 lines)
│   │   │   ├── hitl_cli.py (29.9K, 861 lines)
│   │   │   ├── hitl_kanban_cli.py (13.4K, 497 lines)
│   │   │   ├── qa_cli.py (9.6K, 306 lines)
│   │   │   ├── qa_execution_cli.py (8.6K, 294 lines)
│   │   │   └── quick_hitl_status.py (9.0K, 313 lines)
│   │   ├── dashboard/
│   │   │   ├── api/
│   │   │   │   ├── components/
│   │   │   │   │   ├── __init__.py (276B, 12 lines)
│   │   │   │   │   └── hitl_widgets.py (883B, 33 lines)
│   │   │   │   ├── __init__.py (43B, 3 lines)
│   │   │   │   ├── gantt_api.py (34.8K, 1,098 lines)
│   │   │   │   ├── routes.py (9.2K, 324 lines)
│   │   │   │   └── unified_api_server.py (70.2K, 1,913 lines)
│   │   │   ├── components/
│   │   │   │   ├── __init__.py (43B, 3 lines)
│   │   │   │   ├── hitl_kanban_board.py (24.7K, 720 lines)
│   │   │   │   ├── hitl_kanban_demo.py (10.3K, 365 lines)
│   │   │   │   └── hitl_widgets.py (55.9K, 1,452 lines)
│   │   │   ├── static/
│   │   │   │   └── __init__.py (41B, 1 lines)
│   │   │   ├── templates/
│   │   │   │   └── __init__.py (44B, 1 lines)
│   │   │   ├── __init__.py (43B, 3 lines)
│   │   │   ├── config.py (4.1K, 124 lines)
│   │   │   └── hitl_widgets.py (539B, 26 lines)
│   │   ├── logs/
│   │   │   └── __init__.py (28B, 1 lines)
│   │   ├── outputs/
│   │   │   ├── BE-07/
│   │   │   │   └── prompt_backend.md (194B, 10 lines)
│   │   │   └── __init__.py (31B, 1 lines)
│   │   ├── reports/
│   │   │   └── day84_eod_report_2025-06-23.md (1.0K, 52 lines)
│   │   ├── visualization/
│   │   │   ├── __init__.py (34B, 1 lines)
│   │   │   └── build_json.py (30.5K, 823 lines)
│   │   ├── webhooks/
│   │   │   └── __init__.py (28B, 1 lines)
│   │   └── __init__.py (43B, 3 lines)
│   ├── __init__.py (38B, 1 lines)
│   └── README.md (2.2K, 66 lines)
├── storage/
│   ├── feedback/
│   ├── hitl_tasks/
│   │   └── QA-02.json (634B, 25 lines)
│   └── storage_metadata.json (369B, 15 lines)
├── tasks/
├── templates/
│   └── email/
│       ├── eod_report.html (2.1K, 61 lines)
│       └── morning_briefing.html (2.3K, 64 lines)
├── test_outputs/
├── tests/
│   ├── components/
│   │   ├── __init__.py (125B, 5 lines)
│   │   └── test_generator.py (1.1K, 36 lines)
│   ├── e2e/
│   │   ├── performance/
│   │   │   ├── __init__.py (28B, 1 lines)
│   │   │   ├── integration_enhanced_eod_reporting.py (5.2K, 133 lines)
│   │   │   └── performance_enhanced_eod_reporting.py (9.8K, 243 lines)
│   │   ├── system/
│   │   │   ├── __init__.py (28B, 1 lines)
│   │   │   ├── test_enhanced_qa_agent.py (14.3K, 316 lines)
│   │   │   ├── test_escalation_system.py (23.8K, 642 lines)
│   │   │   └── test_prompt_generation.py (323B, 19 lines)
│   │   ├── user_journeys/
│   │   │   └── __init__.py (28B, 1 lines)
│   │   ├── workflows/
│   │   │   ├── __init__.py (28B, 1 lines)
│   │   │   ├── test_phase4_final_validation.py (10.5K, 228 lines)
│   │   │   ├── test_phase6_automation.py (40.3K, 1,013 lines)
│   │   │   └── test_phase7_hitl.py (25.3K, 656 lines)
│   │   └── __init__.py (31B, 1 lines)
│   ├── fixtures/
│   │   ├── data/
│   │   │   ├── __init__.py (28B, 1 lines)
│   │   │   └── sample_data.py (1.2K, 41 lines)
│   │   ├── factories/
│   │   │   ├── __init__.py (28B, 1 lines)
│   │   │   ├── agent_factory.py (811B, 32 lines)
│   │   │   └── task_factory.py (982B, 34 lines)
│   │   ├── mocks/
│   │   │   ├── __init__.py (309B, 19 lines)
│   │   │   ├── mock_agents.py (1.6K, 71 lines)
│   │   │   ├── mock_api.py (1.3K, 61 lines)
│   │   │   ├── mock_dotenv.py (4.0K, 148 lines)
│   │   │   ├── mock_external_deps.py (2.2K, 92 lines)
│   │   │   ├── mock_memory.py (1.8K, 62 lines)
│   │   │   └── mock_schedule.py (3.1K, 149 lines)
│   │   ├── test_data/
│   │   │   └── __init__.py (28B, 1 lines)
│   │   ├── __init__.py (52B, 3 lines)
│   │   ├── test_environment.py (1.2K, 42 lines)
│   │   └── test_qa.py (3.0K, 99 lines)
│   ├── integration/
│   │   ├── api/
│   │   │   ├── __init__.py (28B, 1 lines)
│   │   │   └── test_api_integration_webhooks.py (9.7K, 266 lines)
│   │   ├── dashboard/
│   │   │   ├── __init__.py (28B, 1 lines)
│   │   │   ├── test_dashboard_integration.py (18.4K, 471 lines)
│   │   │   ├── test_dashboard_routes.py (3.9K, 106 lines)
│   │   │   └── test_dashboard_stability.py (10.6K, 265 lines)
│   │   ├── memory/
│   │   │   └── __init__.py (28B, 1 lines)
│   │   ├── workflows/
│   │   │   ├── __init__.py (28B, 1 lines)
│   │   │   └── test_workflow_integration.py (15.1K, 395 lines)
│   │   ├── test_agent_factory_integration.py (11.3K, 315 lines)
│   │   ├── test_analytics.py (23.5K, 559 lines)
│   │   ├── test_business_endpoints.py (4.8K, 131 lines)
│   │   ├── test_configuration_integration.py (3.1K, 99 lines)
│   │   ├── test_dashboard_integration.py (1.4K, 50 lines)
│   │   ├── test_data_flow_integration.py (22.3K, 651 lines)
│   │   ├── test_escalation_integration.py (20.5K, 538 lines)
│   │   ├── test_execution_monitor.py (1.3K, 44 lines)
│   │   ├── test_external_api_integration.py (8.6K, 245 lines)
│   │   ├── test_feedback_system.py (8.6K, 228 lines)
│   │   ├── test_hitl_engine_integration.py (19.6K, 484 lines)
│   │   ├── test_hitl_integration.py (19.0K, 525 lines)
│   │   ├── test_integration_validation.py (5.9K, 187 lines)
│   │   ├── test_memory_system_integration.py (8.9K, 258 lines)
│   │   ├── test_phase2_optimizations.py (14.0K, 327 lines)
│   │   ├── test_phase6_step_6_5_visual_progress_charts.py (17.5K, 421 lines)
│   │   ├── test_progress_trend_integration.py (7.1K, 167 lines)
│   │   ├── test_step_4_8_integration.py (2.5K, 64 lines)
│   │   ├── test_step_5_4_qa_registration.py (12.5K, 286 lines)
│   │   └── test_system_health_integration.py (8.9K, 245 lines)
│   ├── unit/
│   │   ├── core/
│   │   │   ├── agents/
│   │   │   │   ├── __init__.py (28B, 1 lines)
│   │   │   │   ├── test_agent_orchestration.py (11.9K, 321 lines)
│   │   │   │   ├── test_agent_orchestration_new.py (792B, 32 lines)
│   │   │   │   ├── test_agents.py (775B, 32 lines)
│   │   │   │   ├── test_documentation_agent.py (11.3K, 303 lines)
│   │   │   │   ├── test_enhanced_qa.py (28.8K, 723 lines)
│   │   │   │   ├── test_enhanced_qa_agent.py (786B, 32 lines)
│   │   │   │   ├── test_enhanced_test_generator.py (20.5K, 561 lines)
│   │   │   │   ├── test_human_agents.py (16.2K, 456 lines)
│   │   │   │   ├── test_qa_agent_decisions.py (3.3K, 98 lines)
│   │   │   │   ├── test_qa_execution.py (1.3K, 50 lines)
│   │   │   │   └── test_qa_validation.py (2.0K, 64 lines)
│   │   │   ├── states/
│   │   │   │   └── __init__.py (28B, 1 lines)
│   │   │   ├── tasks/
│   │   │   │   ├── __init__.py (28B, 1 lines)
│   │   │   │   ├── test_summarise_task.py (783B, 32 lines)
│   │   │   │   ├── test_task_declaration.py (19.1K, 555 lines)
│   │   │   │   └── test_update_task_status.py (1.2K, 41 lines)
│   │   │   ├── workflows/
│   │   │   │   ├── __init__.py (28B, 1 lines)
│   │   │   │   ├── test_daily_cycle.py (39.1K, 907 lines)
│   │   │   │   ├── test_end_of_day_reporting.py (11.5K, 252 lines)
│   │   │   │   ├── test_enhanced_eod_reporting.py (14.7K, 346 lines)
│   │   │   │   ├── test_enhanced_workflow.py (12.5K, 346 lines)
│   │   │   │   ├── test_execute_graph_comprehensive.py (796B, 32 lines)
│   │   │   │   ├── test_extract_code.py (17.7K, 310 lines)
│   │   │   │   ├── test_generate_briefing_comprehensive.py (22.4K, 516 lines)
│   │   │   │   ├── test_langgraph_workflow.py (4.4K, 126 lines)
│   │   │   │   ├── test_orchestrator.py (1.2K, 39 lines)
│   │   │   │   ├── test_progress_trend_integration.py (6.8K, 157 lines)
│   │   │   │   ├── test_register_output.py (784B, 32 lines)
│   │   │   │   ├── test_summarise_task.py (21.7K, 608 lines)
│   │   │   │   ├── test_task_declaration.py (785B, 32 lines)
│   │   │   │   ├── test_task_lifecycle.py (783B, 32 lines)
│   │   │   │   ├── test_timeline_method.py (968B, 33 lines)
│   │   │   │   ├── test_update_task_status.py (978B, 38 lines)
│   │   │   │   ├── test_workflow_helpers.py (2.3K, 71 lines)
│   │   │   │   ├── test_workflow_recursion_patch.py (973B, 32 lines)
│   │   │   │   └── test_workflow_states.py (784B, 32 lines)
│   │   │   ├── __init__.py (31B, 1 lines)
│   │   │   ├── test_agents.py (312B, 19 lines)
│   │   │   ├── test_chromadb_patch.py (1.1K, 43 lines)
│   │   │   ├── test_chromadb_patch_optimized.py (4.0K, 135 lines)
│   │   │   ├── test_cleanup_verification.py (3.9K, 117 lines)
│   │   │   ├── test_config_loading.py (701B, 27 lines)
│   │   │   ├── test_coverage.py (673B, 33 lines)
│   │   │   ├── test_enhanced_test_generator.py (329B, 19 lines)
│   │   │   ├── test_environment.py (4.6K, 138 lines)
│   │   │   ├── test_execute_graph_comprehensive.py (333B, 19 lines)
│   │   │   ├── test_generator.py (29.7K, 653 lines)
│   │   │   ├── test_input_validation.py (322B, 19 lines)
│   │   │   ├── test_orchestrator.py (918B, 31 lines)
│   │   │   ├── test_patches.py (13.6K, 356 lines)
│   │   │   ├── test_prompt_generation.py (323B, 19 lines)
│   │   │   ├── test_register_output.py (321B, 19 lines)
│   │   │   ├── test_timeline_method.py (1.2K, 41 lines)
│   │   │   ├── test_updated_retrieval_qa.py (3.8K, 98 lines)
│   │   │   └── test_utils.py (8.3K, 240 lines)
│   │   ├── infrastructure/
│   │   │   └── tools/
│   │   │       └── validation/
│   │   │           ├── test_incremental_analyzer.py (33.7K, 959 lines)
│   │   │           ├── test_management_dashboard.py (44.2K, 1,305 lines)
│   │   │           ├── test_nfr_validator.py (34.5K, 1,143 lines)
│   │   │           ├── test_quality_gates.py (18.4K, 595 lines)
│   │   │           ├── test_unified_validator.py (27.5K, 869 lines)
│   │   │           └── test_vv_validator.py (23.6K, 710 lines)
│   │   ├── integrations/
│   │   │   ├── analytics/
│   │   │   │   └── __init__.py (28B, 1 lines)
│   │   │   ├── external/
│   │   │   │   └── __init__.py (28B, 1 lines)
│   │   │   └── __init__.py (31B, 1 lines)
│   │   ├── interfaces/
│   │   │   ├── api/
│   │   │   │   ├── __init__.py (28B, 1 lines)
│   │   │   │   └── test_hitl_api_routes.py (17.5K, 426 lines)
│   │   │   ├── cli/
│   │   │   │   ├── __init__.py (28B, 1 lines)
│   │   │   │   └── test_gemini_cli.py (10.8K, 312 lines)
│   │   │   ├── dashboard/
│   │   │   │   ├── __init__.py (28B, 1 lines)
│   │   │   │   ├── test_hitl_cli.py (21.1K, 498 lines)
│   │   │   │   ├── test_hitl_cli_comprehensive.py (37.9K, 973 lines)
│   │   │   │   ├── test_hitl_dashboard_widgets.py (18.2K, 435 lines)
│   │   │   │   └── test_hitl_engine_integration.py (15.9K, 372 lines)
│   │   │   └── __init__.py (31B, 1 lines)
│   │   ├── platform/
│   │   │   ├── memory/
│   │   │   │   ├── __init__.py (28B, 1 lines)
│   │   │   │   ├── test_memory_config.py (1.9K, 61 lines)
│   │   │   │   ├── test_memory_engine.py (7.6K, 212 lines)
│   │   │   │   └── test_memory_functionality.py (10.6K, 277 lines)
│   │   │   ├── security/
│   │   │   │   └── __init__.py (28B, 1 lines)
│   │   │   ├── storage/
│   │   │   │   └── __init__.py (28B, 1 lines)
│   │   │   ├── tools/
│   │   │   │   ├── __init__.py (28B, 1 lines)
│   │   │   │   └── test_tool_loader.py (780B, 32 lines)
│   │   │   └── __init__.py (31B, 1 lines)
│   │   └── __init__.py (31B, 1 lines)
│   ├── utils/
│   │   ├── __init__.py (1.1K, 40 lines)
│   │   ├── test_utils.py (15.9K, 498 lines)
│   │   └── workflow_helpers.py (12.4K, 319 lines)
│   ├── validation/
│   │   └── __init__.py (36B, 1 lines)
│   ├── __init__.py (43B, 3 lines)
│   ├── benchmark_parallel.py (3.9K, 130 lines)
│   ├── conftest.py (6.7K, 245 lines)
│   ├── helpers.py (3.2K, 91 lines)
│   ├── mock_environment.py (1.8K, 72 lines)
│   ├── mock_openai_embeddings.py (1.8K, 54 lines)
│   ├── monkey_patch.py (313B, 19 lines)
│   ├── pytest_config.py (5.1K, 159 lines)
│   ├── test_smoke.py (2.9K, 80 lines)
│   ├── test_utils.py (1.5K, 66 lines)
│   └── test_utils_compat.py (676B, 24 lines)
├── .env.example (1.6K)
├── __init__.py (21B, 1 lines)
├── bandit-report.json (308.1K, 8,902 lines)
├── CLAUDE.md (7.4K, 221 lines)
├── code-quality.ps1 (27.6K, 706 lines)
├── CONTRIBUTING.md (8.1K, 268 lines)
├── copilot-instructions.md (5.4K, 139 lines)
├── core_ruff_report.json (0B, 0 lines)
├── coverage.xml (1.5M, 33,782 lines)
├── dependency_analyzer.py (4.7K, 122 lines)
├── docker-compose.dev.yml (5.9K, 251 lines)
├── Dockerfile.dev (150B)
├── Dockerfile.docs (131B)
├── Dockerfile.jupyter (210B)
├── infrastructure_ruff_report.json (530.8K, 22,925 lines)
├── LICENSE (1.1K)
├── main.py (19.3K, 558 lines)
├── Makefile (9.1K)
├── mypy.ini (235B)
├── parallel_dependency_analysis.json (686B, 25 lines)
├── PARALLEL_INVESTIGATION_ACTION_PLAN.md (7.5K, 238 lines)
├── parallel_investigation_infrastructure_batch2.md (11.5K, 336 lines)
├── PARALLEL_INVESTIGATION_REPORT.md (8.6K, 260 lines)
├── parallel_safe_fix_files.txt (157B, 5 lines)
├── PARALLEL_VALIDATION_COMPLETION_REPORT.md (8.2K, 178 lines)
├── pyproject.toml (2.9K)
├── pytest (1.3K)
├── pytest.ini (2.6K)
├── QUALITY_IMPROVEMENT_MASTER_CHECKLIST.md (14.7K, 393 lines)
├── README.md (9.7K, 248 lines)
├── requirements.lock (13.1K)
├── requirements.txt (11.1K, 234 lines)
├── setup-code-quality.ps1 (10.4K, 373 lines)
├── setup.cfg (281B)
├── sonar-project.properties (1.8K)
└── sonarqube_integration_config.json (513B, 24 lines)
```

## Summary

- **Total files**: 1,129
- **Total directories**: 304
- **Total items**: 1,433
- **Total lines of code**: 246,122
- **Generation method**: Depth-First Search (DFS) traversal
- **Tree algorithm**: Recursive directory iteration with size and line count information
- **Excluded patterns**: .coverage, .git, .log, .mypy_cache, .pytest_cache, .tox, .venv, __pycache__, build/archives, dist, htmlcov, lib64, logs/, node_modules, runtime/cache, runtime/logs, runtime/temp, test_logs/, venv

## Tree Traversal Algorithm

This tree structure was generated using a **Depth-First Search (DFS)** algorithm:

1. **Recursive Traversal**: Starting from root, recursively visit each directory
2. **Sorting Strategy**: Directories first, then files (alphabetically)
3. **Size Calculation**: File sizes shown in appropriate units (B/K/M)
4. **Line Counting**: Text files show line counts for code analysis
5. **Exclusion Filtering**: Skip temporary, cache, and build directories
6. **Depth Limiting**: Maximum depth of 8 levels to prevent excessive output

## Architecture Insights

Based on this tree structure with **1,129 files** and **246,122 lines of code**:

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
- **Python code**: Estimated 172,285 lines (70% of total)
- **Documentation**: Estimated 36,918 lines (15% of total)  
- **Configuration**: Estimated 24,612 lines (10% of total)
- **Other files**: Estimated 12,306 lines (5% of total)

This represents a **substantial codebase** with comprehensive documentation and configuration.
