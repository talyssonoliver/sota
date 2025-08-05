import React from 'react';
import ComponentCreator from '@docusaurus/ComponentCreator';

export default [
  {
    path: '/markdown-page',
    component: ComponentCreator('/markdown-page', '3d7'),
    exact: true
  },
  {
    path: '/docs',
    component: ComponentCreator('/docs', '98f'),
    routes: [
      {
        path: '/docs',
        component: ComponentCreator('/docs', 'd6e'),
        routes: [
          {
            path: '/docs',
            component: ComponentCreator('/docs', '385'),
            routes: [
              {
                path: '/docs/',
                component: ComponentCreator('/docs/', 'ee3'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/admin/CODE_QUALITY_IMPROVEMENTS_SUMMARY',
                component: ComponentCreator('/docs/admin/CODE_QUALITY_IMPROVEMENTS_SUMMARY', 'e11'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/admin/MEMORY_ENGINE_REFACTORING_SUMMARY',
                component: ComponentCreator('/docs/admin/MEMORY_ENGINE_REFACTORING_SUMMARY', 'fe4'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/adr/generated_artefact_strategy',
                component: ComponentCreator('/docs/adr/generated_artefact_strategy', 'cbc'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/adr/generated_artefact_strategy_fixed',
                component: ComponentCreator('/docs/adr/generated_artefact_strategy_fixed', '579'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/api/',
                component: ComponentCreator('/docs/api/', '788'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/api/api_reference',
                component: ComponentCreator('/docs/api/api_reference', '224'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/api/class_dictionary',
                component: ComponentCreator('/docs/api/class_dictionary', 'b36'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/api/external_integrations',
                component: ComponentCreator('/docs/api/external_integrations', 'db8'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/api/function_dictionary',
                component: ComponentCreator('/docs/api/function_dictionary', '521'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/api/hitl_routes',
                component: ComponentCreator('/docs/api/hitl_routes', '795'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/api/module_dictionary',
                component: ComponentCreator('/docs/api/module_dictionary', 'aa3'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/api/symbol_index',
                component: ComponentCreator('/docs/api/symbol_index', 'ff7'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/api/unified_api_server',
                component: ComponentCreator('/docs/api/unified_api_server', 'e01'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/api/webhook_manager',
                component: ComponentCreator('/docs/api/webhook_manager', 'ce3'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/architecture/',
                component: ComponentCreator('/docs/architecture/', 'ecf'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/architecture/agent_architecture',
                component: ComponentCreator('/docs/architecture/agent_architecture', '4bc'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/architecture/agent_system_overview',
                component: ComponentCreator('/docs/architecture/agent_system_overview', 'c6a'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/architecture/agents/agent_builder',
                component: ComponentCreator('/docs/architecture/agents/agent_builder', '52e'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/architecture/agents/agent_factory_refactoring_summary',
                component: ComponentCreator('/docs/architecture/agents/agent_factory_refactoring_summary', 'da1'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/architecture/agents/backend',
                component: ComponentCreator('/docs/architecture/agents/backend', '4b5'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/architecture/agents/backend_agent',
                component: ComponentCreator('/docs/architecture/agents/backend_agent', '303'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/architecture/agents/coordinator',
                component: ComponentCreator('/docs/architecture/agents/coordinator', '680'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/architecture/agents/coordinator_agent',
                component: ComponentCreator('/docs/architecture/agents/coordinator_agent', '6ff'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/architecture/agents/doc',
                component: ComponentCreator('/docs/architecture/agents/doc', '157'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/architecture/agents/documentation_agent',
                component: ComponentCreator('/docs/architecture/agents/documentation_agent', '1b9'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/architecture/agents/factory',
                component: ComponentCreator('/docs/architecture/agents/factory', '3e1'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/architecture/agents/frontend',
                component: ComponentCreator('/docs/architecture/agents/frontend', 'a89'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/architecture/agents/frontend_agent',
                component: ComponentCreator('/docs/architecture/agents/frontend_agent', 'd50'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/architecture/agents/human_agents',
                component: ComponentCreator('/docs/architecture/agents/human_agents', 'd10'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/architecture/agents/qa',
                component: ComponentCreator('/docs/architecture/agents/qa', '492'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/architecture/agents/qa_agent',
                component: ComponentCreator('/docs/architecture/agents/qa_agent', 'f65'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/architecture/agents/technical',
                component: ComponentCreator('/docs/architecture/agents/technical', '50f'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/architecture/agents/technical_lead_agent',
                component: ComponentCreator('/docs/architecture/agents/technical_lead_agent', '262'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/architecture/context_tracking_functionality',
                component: ComponentCreator('/docs/architecture/context_tracking_functionality', 'abe'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/architecture/COORDINATOR_IMPROVEMENTS',
                component: ComponentCreator('/docs/architecture/COORDINATOR_IMPROVEMENTS', '651'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/architecture/dependency_map',
                component: ComponentCreator('/docs/architecture/dependency_map', '501'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/architecture/error_handling',
                component: ComponentCreator('/docs/architecture/error_handling', '7fe'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/architecture/ERROR_HANDLING_IMPROVEMENTS',
                component: ComponentCreator('/docs/architecture/ERROR_HANDLING_IMPROVEMENTS', 'f6c'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/architecture/error_propagation_strategy',
                component: ComponentCreator('/docs/architecture/error_propagation_strategy', '485'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/architecture/FILE_ORGANIZATION_IMPROVEMENTS',
                component: ComponentCreator('/docs/architecture/FILE_ORGANIZATION_IMPROVEMENTS', 'ca2'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/architecture/flow',
                component: ComponentCreator('/docs/architecture/flow', '2e6'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/architecture/graph_builder',
                component: ComponentCreator('/docs/architecture/graph_builder', 'a8d'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/architecture/handlers',
                component: ComponentCreator('/docs/architecture/handlers', '66d'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/architecture/hitl_engine',
                component: ComponentCreator('/docs/architecture/hitl_engine', 'b4c'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/architecture/hitl_task_metadata',
                component: ComponentCreator('/docs/architecture/hitl_task_metadata', 'ac0'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/architecture/improvements/',
                component: ComponentCreator('/docs/architecture/improvements/', 'b6c'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/architecture/inject_context',
                component: ComponentCreator('/docs/architecture/inject_context', '227'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/architecture/interrupt_nodes',
                component: ComponentCreator('/docs/architecture/interrupt_nodes', '472'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/architecture/langgraph_qa_integration',
                component: ComponentCreator('/docs/architecture/langgraph_qa_integration', '96f'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/architecture/memory_engine',
                component: ComponentCreator('/docs/architecture/memory_engine', 'e9c'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/architecture/modernization-plan',
                component: ComponentCreator('/docs/architecture/modernization-plan', '47e'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/architecture/notification_handlers',
                component: ComponentCreator('/docs/architecture/notification_handlers', '2b5'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/architecture/notifications',
                component: ComponentCreator('/docs/architecture/notifications', 'ed3'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/architecture/qa_handler',
                component: ComponentCreator('/docs/architecture/qa_handler', '2c5'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/architecture/registry',
                component: ComponentCreator('/docs/architecture/registry', '840'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/architecture/scalable_storage',
                component: ComponentCreator('/docs/architecture/scalable_storage', '4ae'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/architecture/states',
                component: ComponentCreator('/docs/architecture/states', 'e7a'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/architecture/system_architecture',
                component: ComponentCreator('/docs/architecture/system_architecture', 'd43'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/architecture/system-architecture-overview',
                component: ComponentCreator('/docs/architecture/system-architecture-overview', '83d'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/architecture/system-overview',
                component: ComponentCreator('/docs/architecture/system-overview', '5f1'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/architecture/task_lifecycle',
                component: ComponentCreator('/docs/architecture/task_lifecycle', 'adb'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/architecture/thread_safe_workflow',
                component: ComponentCreator('/docs/architecture/thread_safe_workflow', 'd15'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/architecture/thread_safety_implementation_summary',
                component: ComponentCreator('/docs/architecture/thread_safety_implementation_summary', 'd3b'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/architecture/tools_system',
                component: ComponentCreator('/docs/architecture/tools_system', '7dd'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/architecture/workflow_task_system',
                component: ComponentCreator('/docs/architecture/workflow_task_system', 'ab1'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/cicd/slack-integration-guide',
                component: ComponentCreator('/docs/cicd/slack-integration-guide', '972'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/development/',
                component: ComponentCreator('/docs/development/', '930'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/development/annotate_context_tags_tasks',
                component: ComponentCreator('/docs/development/annotate_context_tags_tasks', '66a'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/development/automation',
                component: ComponentCreator('/docs/development/automation', '8a2'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/development/build_paths',
                component: ComponentCreator('/docs/development/build_paths', 'd92'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/development/chromadb_telemetry_patch',
                component: ComponentCreator('/docs/development/chromadb_telemetry_patch', 'ecf'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/development/CLAUDE_CODE_TEAM_ONBOARDING',
                component: ComponentCreator('/docs/development/CLAUDE_CODE_TEAM_ONBOARDING', '651'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/development/configuration_deep_dive',
                component: ComponentCreator('/docs/development/configuration_deep_dive', '54a'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/development/configuration_reference',
                component: ComponentCreator('/docs/development/configuration_reference', 'ee8'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/development/consolidate_dashboard',
                component: ComponentCreator('/docs/development/consolidate_dashboard', '36b'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/development/debugging/analyze_remaining_failures',
                component: ComponentCreator('/docs/development/debugging/analyze_remaining_failures', '0bf'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/development/debugging/fix_unicode_escapes',
                component: ComponentCreator('/docs/development/debugging/fix_unicode_escapes', 'e4d'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/development/debugging/verify_dashboard_fix',
                component: ComponentCreator('/docs/development/debugging/verify_dashboard_fix', '20e'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/development/ENHANCED_WORKFLOW_GUIDE',
                component: ComponentCreator('/docs/development/ENHANCED_WORKFLOW_GUIDE', '109'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/development/generation/automated_doc_generator',
                component: ComponentCreator('/docs/development/generation/automated_doc_generator', '267'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/development/generation/automated_symbol_extraction',
                component: ComponentCreator('/docs/development/generation/automated_symbol_extraction', '85b'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/development/generation/batch_qa_generation',
                component: ComponentCreator('/docs/development/generation/batch_qa_generation', 'e51'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/development/generation/generate_agent',
                component: ComponentCreator('/docs/development/generation/generate_agent', '804'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/development/generation/generate_briefing',
                component: ComponentCreator('/docs/development/generation/generate_briefing', 'a6e'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/development/generation/generate_progress_report',
                component: ComponentCreator('/docs/development/generation/generate_progress_report', '823'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/development/generation/generate_prompt',
                component: ComponentCreator('/docs/development/generation/generate_prompt', 'f15'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/development/generation/generate_task_report',
                component: ComponentCreator('/docs/development/generation/generate_task_report', '1c3'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/development/get-pip',
                component: ComponentCreator('/docs/development/get-pip', '346'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/development/helpers',
                component: ComponentCreator('/docs/development/helpers', '38c'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/development/INPUT_VALIDATION_IMPLEMENTATION_SUMMARY',
                component: ComponentCreator('/docs/development/INPUT_VALIDATION_IMPLEMENTATION_SUMMARY', 'ceb'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/development/main',
                component: ComponentCreator('/docs/development/main', '34d'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/development/main_entry_point',
                component: ComponentCreator('/docs/development/main_entry_point', '66b'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/development/migrate_source_code',
                component: ComponentCreator('/docs/development/migrate_source_code', '527'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/development/mock_memory_engine',
                component: ComponentCreator('/docs/development/mock_memory_engine', 'c0c'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/development/mocking/mock_dependencies',
                component: ComponentCreator('/docs/development/mocking/mock_dependencies', 'bd3'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/development/mocking/mock_environment',
                component: ComponentCreator('/docs/development/mocking/mock_environment', 'e17'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/development/mocking/mock_langchain',
                component: ComponentCreator('/docs/development/mocking/mock_langchain', '47d'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/development/mocking/mock_openai_embeddings',
                component: ComponentCreator('/docs/development/mocking/mock_openai_embeddings', 'cf1'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/development/monkey_patch',
                component: ComponentCreator('/docs/development/monkey_patch', 'e2a'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/development/patch_dotenv',
                component: ComponentCreator('/docs/development/patch_dotenv', 'ff2'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/development/security',
                component: ComponentCreator('/docs/development/security', '17e'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/development/setup',
                component: ComponentCreator('/docs/development/setup', '375'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/development/testing/analyse_feedback',
                component: ComponentCreator('/docs/development/testing/analyse_feedback', '6dd'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/development/testing/complete_validation',
                component: ComponentCreator('/docs/development/testing/complete_validation', 'f19'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/development/testing/conftest',
                component: ComponentCreator('/docs/development/testing/conftest', '0ed'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/development/testing/end_to_end_test',
                component: ComponentCreator('/docs/development/testing/end_to_end_test', '3cb'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/development/testing/final_validation_complete',
                component: ComponentCreator('/docs/development/testing/final_validation_complete', '66b'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/development/testing/optimize_tests',
                component: ComponentCreator('/docs/development/testing/optimize_tests', '476'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/development/testing/OPTIMIZED_TESTING',
                component: ComponentCreator('/docs/development/testing/OPTIMIZED_TESTING', '078'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/development/testing/pytest_simulator',
                component: ComponentCreator('/docs/development/testing/pytest_simulator', 'caf'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/development/testing/run_optimized_tests',
                component: ComponentCreator('/docs/development/testing/run_optimized_tests', '323'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/development/testing/run_optimized_tests_enhanced',
                component: ComponentCreator('/docs/development/testing/run_optimized_tests_enhanced', '24f'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/development/testing/run_tests',
                component: ComponentCreator('/docs/development/testing/run_tests', '4f2'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/development/testing/setup_context_for_testing',
                component: ComponentCreator('/docs/development/testing/setup_context_for_testing', '3f8'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/development/testing/simple_retrieval_test',
                component: ComponentCreator('/docs/development/testing/simple_retrieval_test', 'f6c'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/development/testing/test_collection_check',
                component: ComponentCreator('/docs/development/testing/test_collection_check', '258'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/development/testing/test_sprint_phases',
                component: ComponentCreator('/docs/development/testing/test_sprint_phases', '41d'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/development/testing/test_structure',
                component: ComponentCreator('/docs/development/testing/test_structure', '7d9'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/development/testing/testagent_agent',
                component: ComponentCreator('/docs/development/testing/testagent_agent', 'b94'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/development/testing/testing_best_practices',
                component: ComponentCreator('/docs/development/testing/testing_best_practices', '996'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/development/testing/testvalidation_agent',
                component: ComponentCreator('/docs/development/testing/testvalidation_agent', '7bb'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/development/testing/validate_imports',
                component: ComponentCreator('/docs/development/testing/validate_imports', '0dc'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/development/troubleshooting',
                component: ComponentCreator('/docs/development/troubleshooting', '1ef'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/development/visualization/auto_generate_graph',
                component: ComponentCreator('/docs/development/visualization/auto_generate_graph', 'bf4'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/development/visualization/build_json',
                component: ComponentCreator('/docs/development/visualization/build_json', 'fb6'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/development/visualization/gantt_analyzer',
                component: ComponentCreator('/docs/development/visualization/gantt_analyzer', 'ca7'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/development/visualization/graph_visualization',
                component: ComponentCreator('/docs/development/visualization/graph_visualization', 'f3e'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/development/visualization/sprint_visualizer',
                component: ComponentCreator('/docs/development/visualization/sprint_visualizer', '63c'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/development/visualization/visualize',
                component: ComponentCreator('/docs/development/visualization/visualize', '6f8'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/development/visualization/visualize_directory_tree',
                component: ComponentCreator('/docs/development/visualization/visualize_directory_tree', '9ff'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/development/visualization/visualize_task_graph',
                component: ComponentCreator('/docs/development/visualization/visualize_task_graph', '9c7'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/integrations/gemini-cli',
                component: ComponentCreator('/docs/integrations/gemini-cli', 'd0a'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/intro',
                component: ComponentCreator('/docs/intro', '61d'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/operations/',
                component: ComponentCreator('/docs/operations/', 'b23'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/operations/automation/automation_health_check',
                component: ComponentCreator('/docs/operations/automation/automation_health_check', 'b9c'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/operations/email_integration',
                component: ComponentCreator('/docs/operations/email_integration', '63c'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/operations/list_pending_reviews',
                component: ComponentCreator('/docs/operations/list_pending_reviews', 'cb6'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/operations/manage_knowledge_reviews',
                component: ComponentCreator('/docs/operations/manage_knowledge_reviews', '041'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/operations/mark_review_complete',
                component: ComponentCreator('/docs/operations/mark_review_complete', 'f73'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/operations/monitoring/monitor_workflow',
                component: ComponentCreator('/docs/operations/monitoring/monitor_workflow', 'e0b'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/operations/monitoring/workflow_monitoring',
                component: ComponentCreator('/docs/operations/monitoring/workflow_monitoring', 'e79'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/operations/update_dashboard',
                component: ComponentCreator('/docs/operations/update_dashboard', '976'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/operations/workflows/archive_task',
                component: ComponentCreator('/docs/operations/workflows/archive_task', 'b33'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/operations/workflows/complete_task',
                component: ComponentCreator('/docs/operations/workflows/complete_task', '4bc'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/operations/workflows/daily_cycle',
                component: ComponentCreator('/docs/operations/workflows/daily_cycle', 'fdb'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/operations/workflows/daily_cycle_orchestrator',
                component: ComponentCreator('/docs/operations/workflows/daily_cycle_orchestrator', '9ac'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/operations/workflows/delegation',
                component: ComponentCreator('/docs/operations/workflows/delegation', '7cb'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/operations/workflows/end_of_day_report',
                component: ComponentCreator('/docs/operations/workflows/end_of_day_report', '54d'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/operations/workflows/enhanced_workflow',
                component: ComponentCreator('/docs/operations/workflows/enhanced_workflow', 'e8b'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/operations/workflows/execute_graph',
                component: ComponentCreator('/docs/operations/workflows/execute_graph', '951'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/operations/workflows/execute_task',
                component: ComponentCreator('/docs/operations/workflows/execute_task', '7fa'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/operations/workflows/execute_workflow',
                component: ComponentCreator('/docs/operations/workflows/execute_workflow', 'f01'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/operations/workflows/extract_code',
                component: ComponentCreator('/docs/operations/workflows/extract_code', '7e2'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/operations/workflows/knowledge_curation_workflow',
                component: ComponentCreator('/docs/operations/workflows/knowledge_curation_workflow', '975'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/operations/workflows/langgraph_workflow',
                component: ComponentCreator('/docs/operations/workflows/langgraph_workflow', '6e2'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/operations/workflows/plan_execution_manager',
                component: ComponentCreator('/docs/operations/workflows/plan_execution_manager', '686'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/operations/workflows/qa_execution',
                component: ComponentCreator('/docs/operations/workflows/qa_execution', 'd05'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/operations/workflows/qa_validation',
                component: ComponentCreator('/docs/operations/workflows/qa_validation', '71e'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/operations/workflows/register_output',
                component: ComponentCreator('/docs/operations/workflows/register_output', '59d'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/operations/workflows/resilient_workflow',
                component: ComponentCreator('/docs/operations/workflows/resilient_workflow', '0c0'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/operations/workflows/review_context',
                component: ComponentCreator('/docs/operations/workflows/review_context', '0e9'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/operations/workflows/review_context_simple',
                component: ComponentCreator('/docs/operations/workflows/review_context_simple', 'eef'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/operations/workflows/review_task',
                component: ComponentCreator('/docs/operations/workflows/review_task', 'e0a'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/operations/workflows/run_workflow',
                component: ComponentCreator('/docs/operations/workflows/run_workflow', 'c0c'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/operations/workflows/summarise_task',
                component: ComponentCreator('/docs/operations/workflows/summarise_task', '878'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/operations/workflows/task_declaration',
                component: ComponentCreator('/docs/operations/workflows/task_declaration', '952'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/operations/workflows/task_orchestration',
                component: ComponentCreator('/docs/operations/workflows/task_orchestration', '5da'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/operations/workflows/workflow_executor',
                component: ComponentCreator('/docs/operations/workflows/workflow_executor', 'e50'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/optimizations/PHASE2_COMPLETE_DOCUMENTATION',
                component: ComponentCreator('/docs/optimizations/PHASE2_COMPLETE_DOCUMENTATION', '084'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/reports/',
                component: ComponentCreator('/docs/reports/', '3b9'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/reports/import_refactoring_completion_report',
                component: ComponentCreator('/docs/reports/import_refactoring_completion_report', '538'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/reports/memory-engine/consolidate_memory',
                component: ComponentCreator('/docs/reports/memory-engine/consolidate_memory', '2cb'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/reports/phase7-hitl/phase6_enhanced_eod_reporting_guide',
                component: ComponentCreator('/docs/reports/phase7-hitl/phase6_enhanced_eod_reporting_guide', 'fac'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/reports/phase7-hitl/PHASE6_STEP6.3_COMPLETION_SUMMARY',
                component: ComponentCreator('/docs/reports/phase7-hitl/PHASE6_STEP6.3_COMPLETION_SUMMARY', 'a96'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/reports/phase7-hitl/PHASE6_STEP6.5_COMPLETION_SUMMARY',
                component: ComponentCreator('/docs/reports/phase7-hitl/PHASE6_STEP6.5_COMPLETION_SUMMARY', 'da7'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/reports/phase7-hitl/PHASE6_STEP6.6_EMAIL_INTEGRATION_COMPLETION',
                component: ComponentCreator('/docs/reports/phase7-hitl/PHASE6_STEP6.6_EMAIL_INTEGRATION_COMPLETION', '057'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/reports/phase7-hitl/PHASE7_STEPS7.2-7.3_COMPLETION_SUMMARY',
                component: ComponentCreator('/docs/reports/phase7-hitl/PHASE7_STEPS7.2-7.3_COMPLETION_SUMMARY', '4f6'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/security/',
                component: ComponentCreator('/docs/security/', '4f0'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/security/security-overview',
                component: ComponentCreator('/docs/security/security-overview', '8d4'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/security/validation/',
                component: ComponentCreator('/docs/security/validation/', '835'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/security/validation/management_dashboard',
                component: ComponentCreator('/docs/security/validation/management_dashboard', 'f55'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/security/validation/quality_gates',
                component: ComponentCreator('/docs/security/validation/quality_gates', 'a2b'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/setup/',
                component: ComponentCreator('/docs/setup/', '38e'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/setup/complete-directory-structure',
                component: ComponentCreator('/docs/setup/complete-directory-structure', '2e4'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/setup/directory-structure',
                component: ComponentCreator('/docs/setup/directory-structure', 'c08'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/setup/requirements',
                component: ComponentCreator('/docs/setup/requirements', '85d'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/setup/requirements-compliance',
                component: ComponentCreator('/docs/setup/requirements-compliance', 'fb5'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/sprint/BRIEFING_GENERATOR_API',
                component: ComponentCreator('/docs/sprint/BRIEFING_GENERATOR_API', '320'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/sprint/briefings/briefing-2025-05-29',
                component: ComponentCreator('/docs/sprint/briefings/briefing-2025-05-29', 'bf8'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/sprint/briefings/briefing-2025-06-01',
                component: ComponentCreator('/docs/sprint/briefings/briefing-2025-06-01', '618'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/sprint/briefings/briefing-2025-06-02',
                component: ComponentCreator('/docs/sprint/briefings/briefing-2025-06-02', '90a'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/sprint/briefings/sprint-day1-briefing',
                component: ComponentCreator('/docs/sprint/briefings/sprint-day1-briefing', '266'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/sprint/briefings/sprint-day2-briefing',
                component: ComponentCreator('/docs/sprint/briefings/sprint-day2-briefing', '3d0'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/sprint/briefings/sprint-day3-briefing',
                component: ComponentCreator('/docs/sprint/briefings/sprint-day3-briefing', '980'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/sprint/PHASE6_COMPLETION_REPORT',
                component: ComponentCreator('/docs/sprint/PHASE6_COMPLETION_REPORT', '759'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/tools/__init__',
                component: ComponentCreator('/docs/tools/__init__', 'd72'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/tools/base_tool',
                component: ComponentCreator('/docs/tools/base_tool', '121'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/tools/context_tracker',
                component: ComponentCreator('/docs/tools/context_tracker', 'b2a'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/tools/context_visualizer',
                component: ComponentCreator('/docs/tools/context_visualizer', 'bb5'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/tools/coverage_tool',
                component: ComponentCreator('/docs/tools/coverage_tool', '61b'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/tools/cypress_tool',
                component: ComponentCreator('/docs/tools/cypress_tool', '562'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/tools/design_system_tool',
                component: ComponentCreator('/docs/tools/design_system_tool', '155'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/tools/echo_tool',
                component: ComponentCreator('/docs/tools/echo_tool', 'd09'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/tools/fixed_retrieval_qa',
                component: ComponentCreator('/docs/tools/fixed_retrieval_qa', '069'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/tools/github_finalise',
                component: ComponentCreator('/docs/tools/github_finalise', '992'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/tools/github_tool',
                component: ComponentCreator('/docs/tools/github_tool', '6d2'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/tools/jest_tool',
                component: ComponentCreator('/docs/tools/jest_tool', '6fb'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/tools/langChain_characterTextSplitter',
                component: ComponentCreator('/docs/tools/langChain_characterTextSplitter', '452'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/tools/markdown_tool',
                component: ComponentCreator('/docs/tools/markdown_tool', 'b05'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/tools/memory_engine',
                component: ComponentCreator('/docs/tools/memory_engine', '222'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/tools/memory_engine_examples',
                component: ComponentCreator('/docs/tools/memory_engine_examples', '1fd'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/tools/qa_cli',
                component: ComponentCreator('/docs/tools/qa_cli', 'c70'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/tools/rate_limiter',
                component: ComponentCreator('/docs/tools/rate_limiter', '4a3'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/tools/retrieval_qa',
                component: ComponentCreator('/docs/tools/retrieval_qa', '70f'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/tools/retrieval_qa_refactored',
                component: ComponentCreator('/docs/tools/retrieval_qa_refactored', '849'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/tools/retrieval_qa_usage',
                component: ComponentCreator('/docs/tools/retrieval_qa_usage', '962'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/tools/supabase_tool',
                component: ComponentCreator('/docs/tools/supabase_tool', 'e5c'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/tools/tailwind_tool',
                component: ComponentCreator('/docs/tools/tailwind_tool', '396'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/tools/task_loader',
                component: ComponentCreator('/docs/tools/task_loader', 'ab5'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/tools/tool_loader',
                component: ComponentCreator('/docs/tools/tool_loader', '520'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/tools/utilities_catalog',
                component: ComponentCreator('/docs/tools/utilities_catalog', 'fe2'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/tools/utils',
                component: ComponentCreator('/docs/tools/utils', '8eb'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/tools/validation/',
                component: ComponentCreator('/docs/tools/validation/', '09d'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/tools/vercel_tool',
                component: ComponentCreator('/docs/tools/vercel_tool', 'f1a'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/tools/vercel_tool_refactored',
                component: ComponentCreator('/docs/tools/vercel_tool_refactored', 'c31'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/user-guides/',
                component: ComponentCreator('/docs/user-guides/', '6b2'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/user-guides/demos/agent_output_demo',
                component: ComponentCreator('/docs/user-guides/demos/agent_output_demo', '19f'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/user-guides/demos/agent_summarization_demo',
                component: ComponentCreator('/docs/user-guides/demos/agent_summarization_demo', '963'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/user-guides/demos/code_extraction_demo',
                component: ComponentCreator('/docs/user-guides/demos/code_extraction_demo', 'da7'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/user-guides/demos/hitl_cli_demo',
                component: ComponentCreator('/docs/user-guides/demos/hitl_cli_demo', '92b'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/user-guides/demos/hitl_kanban_demo',
                component: ComponentCreator('/docs/user-guides/demos/hitl_kanban_demo', '1d9'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/user-guides/demos/human-in-the-Loop_context_review',
                component: ComponentCreator('/docs/user-guides/demos/human-in-the-Loop_context_review', '509'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/user-guides/demos/mcp_context_usage',
                component: ComponentCreator('/docs/user-guides/demos/mcp_context_usage', '495'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/user-guides/demos/qa_execution_demo',
                component: ComponentCreator('/docs/user-guides/demos/qa_execution_demo', 'dde'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/user-guides/demos/register_agent_output_demo',
                component: ComponentCreator('/docs/user-guides/demos/register_agent_output_demo', '19f'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/user-guides/demos/task_declaration_preparation',
                component: ComponentCreator('/docs/user-guides/demos/task_declaration_preparation', '8b4'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/user-guides/demos/visualise_context_coverage',
                component: ComponentCreator('/docs/user-guides/demos/visualise_context_coverage', '707'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/user-guides/documentation_completeness',
                component: ComponentCreator('/docs/user-guides/documentation_completeness', 'eda'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/user-guides/documentation_index',
                component: ComponentCreator('/docs/user-guides/documentation_index', '95f'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/user-guides/documentation_search_index',
                component: ComponentCreator('/docs/user-guides/documentation_search_index', '432'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/user-guides/escalation_cli',
                component: ComponentCreator('/docs/user-guides/escalation_cli', 'eb9'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/user-guides/feedback_cli',
                component: ComponentCreator('/docs/user-guides/feedback_cli', 'a49'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/user-guides/hitl_cli',
                component: ComponentCreator('/docs/user-guides/hitl_cli', '5b4'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/user-guides/hitl_kanban_board',
                component: ComponentCreator('/docs/user-guides/hitl_kanban_board', '600'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/user-guides/hitl_kanban_cli',
                component: ComponentCreator('/docs/user-guides/hitl_kanban_cli', '603'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/user-guides/hitl_kanban_dashboard',
                component: ComponentCreator('/docs/user-guides/hitl_kanban_dashboard', '5b7'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/user-guides/hitl_widgets',
                component: ComponentCreator('/docs/user-guides/hitl_widgets', 'c32'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/user-guides/MASTER_DOCUMENTATION_GUIDE',
                component: ComponentCreator('/docs/user-guides/MASTER_DOCUMENTATION_GUIDE', '203'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/user-guides/qa_execution_cli',
                component: ComponentCreator('/docs/user-guides/qa_execution_cli', '582'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/user-guides/quick_hitl_status',
                component: ComponentCreator('/docs/user-guides/quick_hitl_status', '671'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/user-guides/quick_reference_cards',
                component: ComponentCreator('/docs/user-guides/quick_reference_cards', '6ec'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/user-guides/visual_documentation',
                component: ComponentCreator('/docs/user-guides/visual_documentation', '841'),
                exact: true,
                sidebar: "tutorialSidebar"
              }
            ]
          }
        ]
      }
    ]
  },
  {
    path: '/',
    component: ComponentCreator('/', 'e5f'),
    exact: true
  },
  {
    path: '*',
    component: ComponentCreator('*'),
  },
];
