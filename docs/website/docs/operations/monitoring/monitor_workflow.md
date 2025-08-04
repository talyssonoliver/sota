# scripts/monitor_workflow.py

## Classes
- **NodeStatus** (line 48)
- **WorkflowMonitor** (line 57)
  - Methods: __init__, add_log_message, scan_output_directory, display_dashboard_data, run_simple_monitor
- **OutputDirectoryEventHandler** (line 356)
  - Methods: __init__, on_modified, on_created

## Functions
- **clear_screen()** (line 40)
- **draw_ui(stdscr, monitor, curses_module)** (line 391)
- **run_ui_wrapper_fn(stdscr, monitor, curses_module)** (line 528)
- **main()** (line 590)
