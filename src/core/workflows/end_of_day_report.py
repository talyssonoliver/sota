#!/usr/bin/env python3

"""
End-of-Day Report Generator - Phase 6 Step 6.3

Enhanced reporting system for comprehensive end-of-day analysis,
building upon existing Phase 5 infrastructure with automation-specific insights.

Provides detailed daily summaries including task analysis, sprint progress,
quality metrics, and preparation insights for the following day.
"""

from src.infrastructure.utils.common_imports import (
    Any,
    Dict,
    List,
    Optional,
    Path,
    datetime,
    json,
    logging,
    sys
)
from datetime import date
sys.path.append(str(Path(__file__).parent.parent))

from src.infrastructure.scripts.generation.generate_progress_report import \
    ProgressReportGenerator
from src.infrastructure.utils.completion_metrics import \
    CompletionMetricsCalculator
from src.infrastructure.utils.execution_monitor import ExecutionMonitor


class EndOfDayReportGenerator:
    """
    Enhanced end-of-day reporting with automation insights and daily summaries.
    """
    
    # Constants for commonly used strings
    TIMEZONE_SUFFIX = '+00:00'
    COMPLETED_IN_PHRASE = "completed in"
    THIRD_PARTY_KEYWORD = "third party"

    def __init__(self):
        """Initialize the end-of-day report generator.
        
        Sets up necessary components for report generation including metrics
        calculation, execution monitoring, and output directory structure.
        """
        self.logger = logging.getLogger(__name__)
        
        # Initialize core components
        self.metrics_calculator = self._initialize_metrics_calculator()
        self.execution_monitor = self._initialize_execution_monitor()
        self.progress_generator = self._initialize_progress_generator()
        
        # Setup output directory
        self.reports_dir = self._setup_reports_directory()

    def _initialize_metrics_calculator(self) -> Optional[CompletionMetricsCalculator]:
        """Initialize metrics calculator with error handling.
        
        Returns:
            CompletionMetricsCalculator instance or None if initialization fails
        """
        try:
            return CompletionMetricsCalculator()
        except Exception as e:
            self.logger.warning(f"Failed to initialize metrics calculator: {e}")
            return None
    
    def _initialize_execution_monitor(self) -> Optional[ExecutionMonitor]:
        """Initialize execution monitor with error handling.
        
        Returns:
            ExecutionMonitor instance or None if initialization fails
        """
        try:
            return ExecutionMonitor()
        except Exception as e:
            self.logger.warning(f"Failed to initialize execution monitor: {e}")
            return None
    
    def _initialize_progress_generator(self) -> Optional[ProgressReportGenerator]:
        """Initialize progress generator with error handling.
        
        Returns:
            ProgressReportGenerator instance or None if initialization fails
        """
        try:
            return ProgressReportGenerator()
        except Exception as e:
            self.logger.warning(f"Failed to initialize progress generator: {e}")
            return None
    
    def _setup_reports_directory(self) -> Path:
        """Setup reports directory with error handling.
        
        Returns:
            Path to reports directory, falls back to current directory if setup fails
        """
        try:
            reports_dir = Path("docs/sprint/daily_reports")
            reports_dir.mkdir(parents=True, exist_ok=True)
            return reports_dir
        except Exception as e:
            self.logger.error(f"Failed to create reports directory: {e}")
            return Path(".")

    def generate_eod_report(
        self,
        report_date: Optional[str] = None,
        include_automation_stats: bool = True,
        include_detailed_metrics: bool = True,
        output_format: str = "markdown",
    ) -> Dict[str, Any]:
        """
        Generate comprehensive end-of-day report.

        Args:
            report_date: Date for report (YYYY-MM-DD), defaults to today
            include_automation_stats: Include daily automation statistics
            include_detailed_metrics: Include detailed task metrics
            output_format: Output format (markdown, html, console)

        Returns:
            Dict containing report data and metadata
        """
        report_date = self._normalize_report_date(report_date)
        report_data = self._initialize_report_structure(report_date, output_format)
        
        # Gather core report sections
        self._populate_core_sections(report_data, report_date)
        
        # Add optional sections based on configuration
        self._add_optional_sections(
            report_data, report_date, include_automation_stats, include_detailed_metrics
        )
        
        # Generate and save formatted output
        return self._finalize_report_output(report_data, report_date, output_format)

    def _normalize_report_date(self, report_date: Optional[str]) -> str:
        """Normalize report date to standard format.
        
        Args:
            report_date: Input date string or None
            
        Returns:
            Normalized date string in YYYY-MM-DD format
        """
        return report_date or datetime.now().strftime("%Y-%m-%d")
    
    def _initialize_report_structure(self, report_date: str, output_format: str) -> Dict[str, Any]:
        """Initialize basic report data structure.
        
        Args:
            report_date: Report date in YYYY-MM-DD format
            output_format: Desired output format
            
        Returns:
            Initialized report data dictionary
        """
        return {
            "date": report_date,
            "timestamp": datetime.now().isoformat(),
            "type": "end_of_day",
            "format": output_format,
        }
    
    def _populate_core_sections(self, report_data: Dict[str, Any], report_date: str) -> None:
        """Populate core report sections that are always included.
        
        Args:
            report_data: Report data dictionary to populate
            report_date: Report date for analysis
        """
        # Core daily metrics
        report_data["daily_summary"] = self._generate_daily_summary(report_date)
        
        # Sprint progress analysis
        report_data["sprint_progress"] = self._analyze_sprint_progress()
        
        # Task completion analysis
        report_data["task_analysis"] = self._analyze_daily_tasks(report_date)
        
        # Quality and blockers analysis
        report_data["quality_analysis"] = self._analyze_quality_metrics()
        report_data["blockers_analysis"] = self._analyze_blockers()
        
        # Tomorrow's preparation
        report_data["tomorrow_prep"] = self._prepare_tomorrow_insights()
    
    def _add_optional_sections(
        self, 
        report_data: Dict[str, Any], 
        report_date: str, 
        include_automation_stats: bool, 
        include_detailed_metrics: bool
    ) -> None:
        """Add optional report sections based on configuration.
        
        Args:
            report_data: Report data dictionary to populate
            report_date: Report date for analysis
            include_automation_stats: Whether to include automation statistics
            include_detailed_metrics: Whether to include detailed metrics
        """
        if include_automation_stats:
            report_data["automation_stats"] = self._gather_automation_statistics(report_date)
            
        if include_detailed_metrics:
            report_data["detailed_metrics"] = self._gather_detailed_metrics()
    
    def _finalize_report_output(
        self, 
        report_data: Dict[str, Any], 
        report_date: str, 
        output_format: str
    ) -> Dict[str, Any]:
        """Generate formatted output and save report to file.
        
        Args:
            report_data: Complete report data
            report_date: Report date for filename
            output_format: Format for output generation
            
        Returns:
            Complete report data with output information
        """
        # Generate formatted output
        formatted_report = self._format_report(report_data, output_format)
        
        # Save report
        report_filename = self._save_report(formatted_report, report_date, output_format)
        
        # Add output metadata
        report_data["output_file"] = report_filename
        report_data["formatted_content"] = formatted_report
        
        return report_data

    def _generate_daily_summary(self, report_date: str) -> Dict[str, Any]:
        """Generate daily summary using existing infrastructure."""
        try:
            # Use existing progress report generator for base summary
            if self.progress_generator is not None:
                # Create proper day_data dictionary instead of passing string
                day_data = {"date": report_date, "tasks": self._get_all_tasks()}
                daily_report = self.progress_generator.generate_daily_report(day_data)
            else:
                daily_report = {"error": "Progress generator not available"}

            # Extract key metrics
            if self.metrics_calculator is not None:
                team_metrics = self.metrics_calculator.calculate_team_metrics()
            else:
                team_metrics = {}

            return {
                "daily_report": daily_report,
                "completed_tasks": team_metrics.get("completed_tasks", 0),
                "total_tasks": team_metrics.get("total_tasks", 0),
                "completion_rate": team_metrics.get("completion_rate", 0),
                "daily_velocity": self._calculate_daily_velocity(report_date),
                "key_accomplishments": self._extract_accomplishments(report_date),
                "challenges_faced": self._identify_daily_challenges(report_date),
            }
        except Exception as e:
            self.logger.error(f"Error generating daily summary: {e}")
            return {"error": str(e)}

    def _analyze_sprint_progress(self) -> Dict[str, Any]:
        """Analyze overall sprint progress trends."""
        try:
            if self.metrics_calculator is not None:
                sprint_metrics = self.metrics_calculator.calculate_sprint_metrics()
                team_metrics = self.metrics_calculator.calculate_team_metrics()
            else:
                sprint_metrics = {}
                team_metrics = {}

            # Calculate trend analysis
            trend_data = self._calculate_progress_trend()

            return {
                "sprint_metrics": sprint_metrics,
                "current_completion": team_metrics.get("completion_rate", 0),
                "sprint_health": self._assess_sprint_health_detailed(),
                "velocity_trend": trend_data.get("velocity", "stable"),
                "projected_completion": self._project_sprint_completion(),
                "risk_assessment": self._assess_sprint_risks(),
                "recommendations": self._generate_sprint_recommendations(),
            }
        except Exception as e:
            self.logger.error(f"Error analyzing sprint progress: {e}")
            return {"error": str(e)}

    def _analyze_daily_tasks(self, report_date: str) -> Dict[str, Any]:
        """Analyze tasks completed and worked on during the day."""
        try:
            all_tasks = self._get_all_tasks()

            # Filter tasks worked on today
            today_tasks = []
            completed_today = []
            started_today = []
            blocked_today = []

            for task in all_tasks:
                # Check if task was modified today (simplified heuristic)
                if self._was_task_active_today(task, report_date):
                    today_tasks.append(task)

                    if task.get("status") == "COMPLETED":
                        completed_today.append(task)
                    elif task.get("status") == "IN_PROGRESS":
                        if self._was_task_started_today(task, report_date):
                            started_today.append(task)
                    elif task.get("status") == "BLOCKED":
                        blocked_today.append(task)

            return {
                "total_active": len(today_tasks),
                "completed_count": len(completed_today),
                "started_count": len(started_today),
                "blocked_count": len(blocked_today),
                "completed_tasks": [
                    self._format_task_summary(task) for task in completed_today
                ],
                "active_tasks": [
                    self._format_task_summary(task) for task in started_today
                ],
                "blocked_tasks": [
                    self._format_task_summary(task) for task in blocked_today
                ],
                "productivity_score": self._calculate_productivity_score(today_tasks),
            }
        except Exception as e:
            self.logger.error(f"Error analyzing daily tasks: {e}")
            return {"error": str(e)}

    def _gather_automation_statistics(self, report_date: str) -> Dict[str, Any]:
        """Gather statistics about daily automation performance."""
        try:
            # Check execution monitor logs for automation runs
            execution_stats = self._analyze_execution_logs(report_date)

            return {
                "briefings_generated": execution_stats.get("briefings", 0),
                "reports_generated": execution_stats.get("reports", 0),
                "dashboard_updates": execution_stats.get("dashboard_updates", 0),
                "automation_uptime": execution_stats.get("uptime_percentage", 100.0),
                "error_count": execution_stats.get("errors", 0),
                "performance_metrics": {
                    "avg_briefing_time": execution_stats.get("avg_briefing_time", 0),
                    "avg_report_time": execution_stats.get("avg_report_time", 0),
                },
            }
        except Exception as e:
            self.logger.error(f"Error gathering automation statistics: {e}")
            return {"error": str(e)}

    def _gather_detailed_metrics(self) -> Dict[str, Any]:
        """Gather detailed metrics for comprehensive analysis."""
        try:
            if self.metrics_calculator is not None:
                team_metrics = self.metrics_calculator.calculate_team_metrics()
                sprint_metrics = self.metrics_calculator.calculate_sprint_metrics()
            else:
                team_metrics = {}
                sprint_metrics = {}

            return {
                "team_metrics": team_metrics,
                "sprint_metrics": sprint_metrics,
                "task_distribution": self._analyze_task_distribution(),
                "complexity_analysis": self._analyze_task_complexity(),
                "time_tracking": self._analyze_time_metrics(),
                "qa_metrics": self._analyze_qa_metrics(),
            }
        except Exception as e:
            self.logger.error(f"Error gathering detailed metrics: {e}")
            return {"error": str(e)}

    def _analyze_quality_metrics(self) -> Dict[str, Any]:
        """Analyze quality metrics and QA coverage."""
        try:
            # Use existing QA analysis capabilities
            qa_stats = self._gather_qa_statistics()

            return {
                "test_coverage": qa_stats.get("coverage_percentage", 0),
                "code_quality_score": qa_stats.get("quality_score", 0),
                "review_completion": qa_stats.get("review_completion", 0),
                "defect_rate": qa_stats.get("defect_rate", 0),
                "quality_trend": self._calculate_quality_trend(),
            }
        except Exception as e:
            self.logger.error(f"Error analyzing quality metrics: {e}")
            return {"error": str(e)}

    def _analyze_blockers(self) -> Dict[str, Any]:
        """Analyze current blockers and their impact."""
        try:
            all_tasks = self._get_all_tasks()
            blocked_tasks = [
                task for task in all_tasks if task.get("status") == "BLOCKED"
            ]

            blocker_analysis = {
                "total_blocked": len(blocked_tasks),
                "blocker_categories": self._categorize_blockers(blocked_tasks),
                "impact_assessment": self._assess_blocker_impact(blocked_tasks),
                "resolution_timeline": self._estimate_blocker_resolution(blocked_tasks),
                "recommendations": self._generate_blocker_recommendations(
                    blocked_tasks
                ),
            }

            return blocker_analysis
        except Exception as e:
            self.logger.error(f"Error analyzing blockers: {e}")
            return {"error": str(e)}

    def _prepare_tomorrow_insights(self) -> Dict[str, Any]:
        """Prepare insights and recommendations for tomorrow."""
        try:
            # Analyze tomorrow's planned tasks
            planned_tasks = self._get_planned_tasks_for_tomorrow()

            return {
                "planned_tasks": len(planned_tasks),
                "priority_tasks": self._identify_priority_tasks(planned_tasks),
                "potential_blockers": self._identify_potential_blockers(planned_tasks),
                "resource_requirements": self._analyze_resource_needs(planned_tasks),
                "success_factors": self._identify_success_factors(),
                "preparation_checklist": self._generate_preparation_checklist(),
            }
        except Exception as e:
            self.logger.error(f"Error preparing tomorrow insights: {e}")
            return {"error": str(e)}

    def _format_report(self, report_data: Dict[str, Any], output_format: str) -> str:
        """Format the report in the specified format."""
        if output_format == "markdown":
            return self._format_markdown_report(report_data)
        elif output_format == "html":
            return self._format_html_report(report_data)
        elif output_format == "console":
            return self._format_console_report(report_data)
        else:
            raise ValueError(f"Unsupported output format: {output_format}")

    def _format_markdown_report(self, data: Dict[str, Any]) -> str:
        """Format report as markdown.
        
        Args:
            data: Complete report data dictionary
            
        Returns:
            Formatted markdown report string
        """
        report_date = self._format_report_date(data["date"])
        
        sections = [
            self._format_markdown_header(report_date),
            self._format_daily_summary_section(data['daily_summary']),
            self._format_sprint_progress_section(data['sprint_progress']),
            self._format_task_analysis_section(data['task_analysis']),
            self._format_quality_blockers_section(data['quality_analysis'], data['blockers_analysis']),
            self._format_tomorrow_prep_section(data['tomorrow_prep']),
            self._format_automation_section(data.get('automation_stats', {})),
            self._format_markdown_footer(data['timestamp'])
        ]
        
        return "\n\n".join(sections)
    
    def _format_report_date(self, date_str: str) -> str:
        """Format report date for display.
        
        Args:
            date_str: Date string in YYYY-MM-DD format
            
        Returns:
            Formatted date string for display
        """
        return datetime.strptime(date_str, "%Y-%m-%d").strftime("%A, %B %d, %Y")
    
    def _format_markdown_header(self, report_date: str) -> str:
        """Format markdown report header.
        
        Args:
            report_date: Formatted report date string
            
        Returns:
            Markdown header section
        """
        return f"# End-of-Day Report - {report_date}"
    
    def _format_daily_summary_section(self, daily_summary: Dict[str, Any]) -> str:
        """Format daily summary section.
        
        Args:
            daily_summary: Daily summary data
            
        Returns:
            Formatted daily summary markdown section
        """
        accomplishments = self._format_accomplishments_list(
            daily_summary.get('key_accomplishments', [])
        )
        
        return f"""## Daily Summary
**Tasks Completed:** {daily_summary.get('completed_tasks', 0)}
**Total Tasks:** {daily_summary.get('total_tasks', 0)}
**Completion Rate:** {daily_summary.get('completion_rate', 0):.1f}%
**Daily Velocity:** {daily_summary.get('daily_velocity', 0)} tasks

### Key Accomplishments
{accomplishments}"""
    
    def _format_sprint_progress_section(self, sprint_progress: Dict[str, Any]) -> str:
        """Format sprint progress section.
        
        Args:
            sprint_progress: Sprint progress data
            
        Returns:
            Formatted sprint progress markdown section
        """
        risk_assessment = self._format_risk_assessment(
            sprint_progress.get('risk_assessment', {})
        )
        
        return f"""## Sprint Progress Analysis
**Current Completion:** {sprint_progress.get('current_completion', 0):.1f}%
**Sprint Health:** {sprint_progress.get('sprint_health', {}).get('status', 'Unknown')}
**Velocity Trend:** {sprint_progress.get('velocity_trend', 'stable')}
**Projected Completion:** {sprint_progress.get('projected_completion', 0):.1f}%

### Risk Assessment
{risk_assessment}"""
    
    def _format_task_analysis_section(self, task_analysis: Dict[str, Any]) -> str:
        """Format task analysis section.
        
        Args:
            task_analysis: Task analysis data
            
        Returns:
            Formatted task analysis markdown section
        """
        completed_tasks = self._format_task_list(
            task_analysis.get('completed_tasks', [])
        )
        
        return f"""## Task Analysis
- **Active Today:** {task_analysis.get('total_active', 0)} tasks
- **Completed:** {task_analysis.get('completed_count', 0)} tasks
- **Started:** {task_analysis.get('started_count', 0)} tasks
- **Blocked:** {task_analysis.get('blocked_count', 0)} tasks
- **Productivity Score:** {task_analysis.get('productivity_score', 0):.1f}/10

### Completed Tasks Today
{completed_tasks}"""
    
    def _format_quality_blockers_section(
        self, 
        quality_analysis: Dict[str, Any], 
        blockers_analysis: Dict[str, Any]
    ) -> str:
        """Format quality and blockers section.
        
        Args:
            quality_analysis: Quality analysis data
            blockers_analysis: Blockers analysis data
            
        Returns:
            Formatted quality and blockers markdown section
        """
        blocker_impact = self._format_blocker_analysis(blockers_analysis)
        
        return f"""## Quality & Blockers
**Test Coverage:** {quality_analysis.get('test_coverage', 0):.1f}%
**Code Quality Score:** {quality_analysis.get('code_quality_score', 0):.1f}/10
**Active Blockers:** {blockers_analysis.get('total_blocked', 0)}

### Blocker Impact
{blocker_impact}"""
    
    def _format_tomorrow_prep_section(self, tomorrow_prep: Dict[str, Any]) -> str:
        """Format tomorrow's preparation section.
        
        Args:
            tomorrow_prep: Tomorrow preparation data
            
        Returns:
            Formatted tomorrow preparation markdown section
        """
        success_factors = self._format_success_factors(
            tomorrow_prep.get('success_factors', [])
        )
        checklist = self._format_checklist(
            tomorrow_prep.get('preparation_checklist', [])
        )
        
        return f"""## Tomorrow's Preparation
**Planned Tasks:** {tomorrow_prep.get('planned_tasks', 0)}
**Priority Tasks:** {len(tomorrow_prep.get('priority_tasks', []))}

### Success Factors
{success_factors}

### Preparation Checklist
{checklist}"""
    
    def _format_automation_section(self, automation_stats: Dict[str, Any]) -> str:
        """Format automation performance section.
        
        Args:
            automation_stats: Automation statistics data
            
        Returns:
            Formatted automation performance markdown section
        """
        stats_content = self._format_automation_stats(automation_stats)
        return f"## Automation Performance\n{stats_content}"
    
    def _format_markdown_footer(self, timestamp: str) -> str:
        """Format markdown report footer.
        
        Args:
            timestamp: Generation timestamp
            
        Returns:
            Markdown footer section
        """
        return f"---\n*Generated at {timestamp} by Enhanced Daily Automation System*"

    def _save_report(self, content: str, report_date: str, output_format: str) -> str:
        """Save the formatted report to file with proper error handling and resource cleanup."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"eod_report_{report_date}_{timestamp}.{output_format}"
        filepath = self.reports_dir / filename

        try:
            # Ensure directory exists
            filepath.parent.mkdir(parents=True, exist_ok=True)
            
            # Write file with proper encoding and buffering
            with open(filepath, "w", encoding="utf-8", buffering=8192) as f:
                f.write(content)
                f.flush()  # Ensure data is written to disk
                
            # Verify file was written successfully
            if not filepath.exists() or filepath.stat().st_size == 0:
                raise IOError(f"Failed to write report file: {filepath}")
                
            self.logger.info(f"Report saved successfully: {filepath}")
            return str(filepath)
            
        except Exception as e:
            self.logger.error(f"Failed to save report to {filepath}: {e}")
            # Try fallback location
            fallback_path = Path(".") / filename
            try:
                with open(fallback_path, "w", encoding="utf-8") as f:
                    f.write(content)
                self.logger.info(f"Report saved to fallback location: {fallback_path}")
                return str(fallback_path)
            except Exception as fallback_error:
                self.logger.error(f"Fallback save also failed: {fallback_error}")
                raise IOError(f"Could not save report: {e}") from e

    # Helper methods for formatting and analysis
    def _get_all_tasks(self) -> List[Dict[str, Any]]:
        """Get all tasks from the system.
        
        Implementation scans outputs directory for task data files
        and aggregates task information from various sources.
        """
        try:
            # Get configuration and collect all tasks
            task_sources = self._get_task_source_directories()
            task_patterns = self._get_task_file_patterns()
            all_tasks = self._process_task_files_from_sources(task_sources, task_patterns)
            
            # Remove duplicates and return final list
            final_tasks = self._remove_duplicate_tasks(all_tasks)
            self.logger.info(f"Loaded {len(final_tasks)} tasks from {len(task_sources)} sources")
            
            return final_tasks
            
        except Exception as e:
            self.logger.error(f"Error loading tasks: {e}")
            return []

    def _get_task_source_directories(self) -> List[Path]:
        """Get list of potential task data source directories."""
        return [
            Path("outputs"),
            Path("data"),
            Path("tasks"),
            Path("runtime"),
            Path("storage"),
            Path("reports")
        ]

    def _get_task_file_patterns(self) -> List[str]:
        """Get list of file patterns to search for task data."""
        return [
            "*.json",
            "*task*.json",
            "*briefing*.json",
            "*report*.json",
            "*status*.json"
        ]

    def _process_task_files_from_sources(self, task_sources: List[Path], task_patterns: List[str]) -> List[Dict[str, Any]]:
        """Process task files from all source directories."""
        all_tasks = []
        
        for source_dir in task_sources:
            if not source_dir.exists():
                continue
                
            for pattern in task_patterns:
                for task_file in source_dir.rglob(pattern):
                    tasks_from_file = self._extract_tasks_from_file(task_file)
                    all_tasks.extend(tasks_from_file)
        
        return all_tasks

    def _extract_tasks_from_file(self, task_file: Path) -> List[Dict[str, Any]]:
        """Extract tasks from a single file with error handling."""
        try:
            with open(task_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return self._extract_tasks_from_data(data, task_file.name)
        except (json.JSONDecodeError, FileNotFoundError, PermissionError) as e:
            self.logger.debug(f"Could not read {task_file}: {e}")
            return []
        except Exception as e:
            self.logger.warning(f"Error processing {task_file}: {e}")
            return []

    def _remove_duplicate_tasks(self, all_tasks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicate tasks based on task ID, keeping most recent version."""
        unique_tasks = {}
        
        for task in all_tasks:
            task_id = task.get("id", task.get("task_id", f"unnamed_{len(unique_tasks)}"))
            
            if task_id not in unique_tasks:
                unique_tasks[task_id] = task
            else:
                # Keep the most recent version if multiple exist
                if self._is_task_more_recent(task, unique_tasks[task_id]):
                    unique_tasks[task_id] = task
        
        return list(unique_tasks.values())

    def _is_task_more_recent(self, task: Dict[str, Any], existing_task: Dict[str, Any]) -> bool:
        """Check if task is more recent than existing task."""
        current_modified = task.get("last_modified", task.get("updated_date", ""))
        existing_modified = existing_task.get("last_modified", existing_task.get("updated_date", ""))
        return current_modified > existing_modified

    def _extract_tasks_from_data(self, data: Any, filename: str) -> List[Dict[str, Any]]:
        """Extract task data from various JSON structures.
        
        Args:
            data: JSON data that might contain task information
            filename: Name of the source file for context
            
        Returns:
            List of task dictionaries extracted from the data
        """
        tasks = []
        
        try:
            # Handle different data structures
            if isinstance(data, list):
                # Direct list of tasks
                tasks.extend(self._extract_tasks_from_list(data, filename))
            
            elif isinstance(data, dict):
                # Check for tasks in various nested structures
                tasks.extend(self._extract_tasks_from_dict_keys(data, filename))
                
                # Check if the root object itself is a task
                if self._is_task_like(data):
                    tasks.append(self._normalize_task_data(data, filename))
                
                # Look for tasks in nested objects
                tasks.extend(self._extract_tasks_from_nested_objects(data, filename))
        
        except Exception as e:
            self.logger.debug(f"Error extracting tasks from {filename}: {e}")
        
        return tasks
    
    def _is_task_like(self, item: Dict[str, Any]) -> bool:
        """Check if a dictionary represents a task.
        
        Args:
            item: Dictionary to check
            
        Returns:
            True if the item appears to be a task
        """
        # Look for task-like characteristics
        task_indicators = [
            "id", "task_id", "title", "name", "description",
            "status", "priority", "assignee", "created_date"
        ]
        
        indicator_count = sum(1 for indicator in task_indicators if indicator in item)
        
        # Also check for status values that indicate a task
        status = item.get("status", "").upper()
        if status in ["TODO", "IN_PROGRESS", "COMPLETED", "BLOCKED", "FAILED", "DONE"]:
            indicator_count += 2
        
        return indicator_count >= 3
    
    def _normalize_task_data(self, task: Dict[str, Any], source: str) -> Dict[str, Any]:
        """Normalize task data to a consistent format.
        
        Args:
            task: Raw task data
            source: Source filename for tracking
            
        Returns:
            Normalized task dictionary
        """
        normalized = {
            "id": task.get("id", task.get("task_id", f"task_from_{source}")),
            "title": task.get("title", task.get("name", "Unnamed Task")),
            "description": task.get("description", task.get("desc", "")),
            "status": task.get("status", "UNKNOWN").upper(),
            "priority": task.get("priority", "MEDIUM").upper(),
            "assignee": task.get("assignee", task.get("assigned_to", "")),
            "created_date": task.get("created_date", task.get("created", "")),
            "updated_date": task.get("updated_date", task.get("last_modified", "")),
            "completed_date": task.get("completed_date", task.get("completed", "")),
            "due_date": task.get("due_date", task.get("deadline", "")),
            "story_points": task.get("story_points", task.get("points", 1)),
            "complexity": task.get("complexity", 1),
            "blocker_reason": task.get("blocker_reason", task.get("blocked_reason", "")),
            "blocker_type": task.get("blocker_type", ""),
            "source_file": source
        }
        
        # Copy any additional fields that might be useful
        for key, value in task.items():
            if key not in normalized and not key.startswith("_"):
                normalized[key] = value
        
        return normalized

    def _calculate_daily_velocity(self, report_date: str) -> float:
        """Calculate velocity for the specific day.
        
        Args:
            report_date: Date for velocity calculation
        """
        try:
            all_tasks = self._get_all_tasks()
            target_date = datetime.strptime(report_date, "%Y-%m-%d").date()
            
            # Get tasks completed on the target date
            completed_today = self._get_tasks_completed_on_date(all_tasks, target_date)
            
            # Calculate velocity based on task complexity/points
            return self._calculate_velocity_points(completed_today)
            
        except Exception as e:
            self.logger.warning(f"Error calculating daily velocity: {e}")
            return 0.0

    def _extract_accomplishments(self, report_date: str) -> List[str]:
        """Extract key accomplishments for the day.
        
        Args:
            report_date: Date to extract accomplishments for
        """
        try:
            all_tasks = self._get_all_tasks()
            accomplishments = []
            target_date = datetime.strptime(report_date, "%Y-%m-%d").date()
            
            # Get tasks completed on target date
            completed_today = self._get_tasks_completed_on_date(all_tasks, target_date)
            
            # Process significant accomplishments first
            for task in completed_today:
                if self._is_significant_accomplishment(task):
                    accomplishments.append(self._format_accomplishment_description(task))
            
            # Add regular accomplishments if we have room
            for task in completed_today:
                if len(accomplishments) >= 5:
                    break
                if not self._is_significant_accomplishment(task):
                    accomplishments.append(self._format_accomplishment_description(task))
            
            # If no specific accomplishments, provide a summary
            if not accomplishments:
                accomplishments = self._generate_fallback_accomplishments(all_tasks)
            
            return accomplishments[:5]  # Limit to top 5 accomplishments
            
        except Exception as e:
            self.logger.warning(f"Error extracting accomplishments: {e}")
            return ["Daily development activities completed"]

    def _identify_daily_challenges(self, report_date: str) -> List[str]:
        """Identify challenges faced during the day.
        
        Args:
            report_date: Date to identify challenges for
        """
        try:
            all_tasks = self._get_all_tasks()
            challenges = []
            
            # Parse the report date for comparison
            target_date = datetime.strptime(report_date, "%Y-%m-%d").date()
            
            blocked_count = failed_count = overdue_count = 0
            
            for task in all_tasks:
                # Check if task had issues on the target date
                if self._was_task_modified_on_date(task, target_date):
                    b_count, f_count, o_count = self._check_task_status_for_challenges(
                        task, target_date, challenges
                    )
                    blocked_count += b_count
                    failed_count += f_count
                    overdue_count += o_count
            
            # Add summary challenges if counts are significant
            self._add_summary_challenges(challenges, blocked_count, failed_count, overdue_count)
            
            # If no specific challenges found, check for general patterns
            self._add_default_challenges(challenges, all_tasks)
            
            return challenges[:5]  # Limit to top 5 challenges
            
        except Exception as e:
            self.logger.warning(f"Error identifying daily challenges: {e}")
            return ["Unable to analyze daily challenges due to data processing issues"]

    def _calculate_progress_trend(self) -> Dict[str, str]:
        """Calculate progress trends."""
        # Implementation would analyze historical data
        return {"velocity": "stable"}

    def _assess_sprint_health_detailed(self) -> Dict[str, Any]:
        """Detailed sprint health assessment."""
        # Use the existing sprint health logic from briefing generator
        return {"status": "needs_attention"}

    def _project_sprint_completion(self) -> float:
        """Project final sprint completion percentage."""
        # Implementation would use velocity and remaining time
        return 0.0

    def _assess_sprint_risks(self) -> Dict[str, Any]:
        """Assess sprint risks."""
        # Implementation would analyze blockers, velocity, etc.
        return {}

    def _generate_sprint_recommendations(self) -> List[str]:
        """Generate sprint recommendations."""
        # Implementation would provide actionable recommendations
        return []

    def _was_task_active_today(self, task: Dict[str, Any], report_date: str) -> bool:
        """Check if task was active on the given date.
        
        Args:
            task: Task data to check
            report_date: Date to check activity for
        """
        try:
            target_date = datetime.strptime(report_date, "%Y-%m-%d").date()
            
            # Check various date fields that indicate activity
            if self._check_task_date_fields_for_activity(task, target_date):
                return True
            
            # Also check if task has any activity logs for the date
            if self._check_activity_logs_for_date(task, target_date):
                return True
            
            return False
            
        except Exception as e:
            self.logger.warning(f"Error checking task activity: {e}")
            return False

    def _was_task_started_today(self, task: Dict[str, Any], report_date: str) -> bool:
        """Check if task was started on the given date.
        
        Args:
            task: Task data to check
            report_date: Date to check start time for
        """
        try:
            target_date = datetime.strptime(report_date, "%Y-%m-%d").date()
            
            # Check started_date field
            if self._check_task_started_date(task, target_date):
                return True
            
            # Check activity logs for start events
            if self._check_activity_logs_for_start(task, target_date):
                return True
            
            # Fallback: check if status changed to IN_PROGRESS today
            if self._check_status_change_to_in_progress(task, report_date):
                return True
            
            return False
            
        except Exception as e:
            self.logger.warning(f"Error checking if task was started today: {e}")
            return False

    def _format_task_summary(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Format task data for summary display."""
        return {
            "id": task.get("id", "Unknown"),
            "title": task.get("title", "Unknown"),
            "status": task.get("status", "Unknown"),
        }

    def _calculate_productivity_score(self, tasks: List[Dict[str, Any]]) -> float:
        """Calculate productivity score for the day.
        
        Args:
            tasks: List of tasks to analyze for productivity calculation
        """
        try:
            if not tasks:
                return 0.0
            
            # Categorize tasks by status
            task_categories = self._categorize_tasks_by_status(tasks)
            
            # Calculate base completion score
            base_score = self._calculate_base_completion_score(task_categories, len(tasks))
            
            # Calculate complexity-weighted score
            complexity_score = self._calculate_complexity_weighted_score(tasks)
            
            # Combine base and complexity scores
            combined_score = (base_score + complexity_score) / 2 if complexity_score > 0 else base_score
            
            # Apply productivity modifiers
            final_score = self._apply_productivity_modifiers(combined_score, task_categories, tasks)
            
            # Ensure score is within 0-10 range
            return round(max(0.0, min(10.0, final_score)), 1)
            
        except Exception as e:
            self.logger.warning(f"Error calculating productivity score: {e}")
            return 5.0  # Default middle score

    def _categorize_tasks_by_status(self, tasks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Categorize tasks by their status for productivity analysis."""
        completed_tasks = [t for t in tasks if t.get("status") == "COMPLETED"]
        blocked_tasks = [t for t in tasks if t.get("status") == "BLOCKED"]
        in_progress_tasks = [t for t in tasks if t.get("status") == "IN_PROGRESS"]
        
        return {
            "completed": completed_tasks,
            "blocked": blocked_tasks,
            "in_progress": in_progress_tasks,
            "completed_count": len(completed_tasks),
            "blocked_count": len(blocked_tasks),
            "in_progress_count": len(in_progress_tasks)
        }

    def _calculate_base_completion_score(self, task_categories: Dict[str, Any], total_tasks: int) -> float:
        """Calculate base productivity score from completion rate."""
        completed_count = task_categories["completed_count"]
        completion_rate = completed_count / total_tasks if total_tasks > 0 else 0
        return completion_rate * 10

    def _calculate_complexity_weighted_score(self, tasks: List[Dict[str, Any]]) -> float:
        """Calculate productivity score weighted by task complexity/story points."""
        total_points_attempted = 0
        completed_points = 0
        
        for task in tasks:
            points = task.get("story_points", task.get("complexity", 1))
            if isinstance(points, (int, float)):
                total_points_attempted += points
                if task.get("status") == "COMPLETED":
                    completed_points += points
            else:
                total_points_attempted += 1
                if task.get("status") == "COMPLETED":
                    completed_points += 1
        
        if total_points_attempted > 0:
            return (completed_points / total_points_attempted) * 10
        return 0

    def _apply_productivity_modifiers(self, base_score: float, task_categories: Dict[str, Any], tasks: List[Dict[str, Any]]) -> float:
        """Apply bonus and penalty modifiers to the base productivity score."""
        productivity_score = base_score
        total_tasks = len(tasks)
        
        # Apply penalty for blocked tasks
        productivity_score -= self._calculate_blocked_task_penalty(task_categories, total_tasks)
        
        # Apply bonus for high completion with good progress distribution
        productivity_score += self._calculate_progress_distribution_bonus(task_categories, total_tasks)
        
        # Apply bonus for completing high-priority tasks
        productivity_score += self._calculate_high_priority_bonus(task_categories["completed"])
        
        return productivity_score

    def _calculate_blocked_task_penalty(self, task_categories: Dict[str, Any], total_tasks: int) -> float:
        """Calculate penalty for blocked tasks."""
        blocked_count = task_categories["blocked_count"]
        if blocked_count > 0:
            return min(blocked_count / total_tasks * 2, 2.0)  # Max 2 point penalty
        return 0.0

    def _calculate_progress_distribution_bonus(self, task_categories: Dict[str, Any], total_tasks: int) -> float:
        """Calculate bonus for good progress distribution."""
        completed_count = task_categories["completed_count"]
        in_progress_count = task_categories["in_progress_count"]
        completion_rate = completed_count / total_tasks if total_tasks > 0 else 0
        
        if completion_rate > 0.7 and in_progress_count > 0:
            return 0.5
        return 0.0

    def _calculate_high_priority_bonus(self, completed_tasks: List[Dict[str, Any]]) -> float:
        """Calculate bonus for completing high-priority tasks."""
        high_priority_completed = len([
            t for t in completed_tasks 
            if t.get("priority", "").upper() in ["HIGH", "CRITICAL"]
        ])
        if high_priority_completed > 0:
            return min(high_priority_completed * 0.5, 1.5)
        return 0.0

    def _analyze_execution_logs(self, report_date: str) -> Dict[str, Any]:
        """Analyze execution monitor logs for automation statistics.
        
        Args:
            report_date: Date to analyze execution logs for
        """
        try:
            execution_stats = self._initialize_execution_stats()
            
            # Check if execution monitor is available
            if self.execution_monitor is None:
                return execution_stats
            
            # Get log paths and process files
            log_paths = self._get_execution_log_paths()
            briefing_times = []
            report_times = []
            
            self._process_execution_log_files(
                log_paths, report_date, execution_stats, briefing_times, report_times
            )
            
            # Calculate final statistics
            self._calculate_execution_statistics(execution_stats, briefing_times, report_times)
            
            return execution_stats
            
        except Exception as e:
            self.logger.warning(f"Error analyzing execution logs: {e}")
            return self._initialize_execution_stats()

    def _analyze_task_distribution(self) -> Dict[str, Any]:
        """Analyze task distribution by status, priority, etc."""
        # Implementation would analyze task characteristics
        return {}

    def _analyze_task_complexity(self) -> Dict[str, Any]:
        """Analyze task complexity metrics."""
        # Implementation would analyze task complexity
        return {}

    def _analyze_time_metrics(self) -> Dict[str, Any]:
        """Analyze time tracking metrics."""
        # Implementation would analyze time spent on tasks
        return {}

    def _analyze_qa_metrics(self) -> Dict[str, Any]:
        """Analyze QA and testing metrics."""
        # Implementation would analyze QA coverage and quality
        return {}

    def _gather_qa_statistics(self) -> Dict[str, Any]:
        """Gather QA statistics."""
        # Implementation would gather QA data
        return {}

    def _calculate_quality_trend(self) -> str:
        """Calculate quality trend."""
        # Implementation would analyze quality over time
        return "stable"

    def _categorize_blockers(
        self, blocked_tasks: List[Dict[str, Any]]
    ) -> Dict[str, int]:
        """Categorize blockers by type.
        
        Args:
            blocked_tasks: List of blocked tasks to categorize
        """
        try:
            categories = {
                "dependency": 0,
                "resource": 0,
                "technical": 0,
                "external": 0,
                "approval": 0,
                "information": 0,
                "other": 0
            }
            
            for task in blocked_tasks:
                blocker_reason = task.get("blocker_reason", "").lower()
                blocker_type = task.get("blocker_type", "").lower()
                
                # Categorize based on keywords in blocker reason or type
                if any(keyword in blocker_reason for keyword in [
                    "dependency", "depends on", "waiting for", "requires"
                ]):
                    categories["dependency"] += 1
                elif any(keyword in blocker_reason for keyword in [
                    "resource", "capacity", "availability", "team member"
                ]):
                    categories["resource"] += 1
                elif any(keyword in blocker_reason for keyword in [
                    "technical", "bug", "infrastructure", "environment", "deployment"
                ]):
                    categories["technical"] += 1
                elif any(keyword in blocker_reason for keyword in [
                    "external", self.THIRD_PARTY_KEYWORD, "vendor", "client", "customer"
                ]):
                    categories["external"] += 1
                elif any(keyword in blocker_reason for keyword in [
                    "approval", "review", "sign-off", "authorization", "permission"
                ]):
                    categories["approval"] += 1
                elif any(keyword in blocker_reason for keyword in [
                    "information", "requirements", "specification", "clarification", "details"
                ]):
                    categories["information"] += 1
                elif blocker_type in categories:
                    categories[blocker_type] += 1
                else:
                    categories["other"] += 1
            
            return categories
            
        except Exception as e:
            self.logger.warning(f"Error categorizing blockers: {e}")
            return {"other": len(blocked_tasks)}

    def _assess_blocker_impact(
        self, blocked_tasks: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Assess impact of blockers.
        
        Args:
            blocked_tasks: List of blocked tasks to assess impact for
        """
        try:
            impact_assessment = {
                "high_impact": 0,
                "medium_impact": 0,
                "low_impact": 0,
                "critical_path_affected": False,
                "total_story_points_blocked": 0,
                "avg_days_blocked": 0,
                "most_critical_blocker": None
            }
            
            total_days_blocked = 0
            most_critical_task = None
            highest_impact_score = 0
            
            for task in blocked_tasks:
                # Calculate impact score based on multiple factors
                impact_score = 0
                
                # Priority impact
                impact_score += self._calculate_priority_impact(task)
                
                # Story points/complexity impact
                impact_score += self._calculate_story_points_impact(task, impact_assessment)
                
                # Duration blocked impact
                duration_impact, days_blocked = self._calculate_duration_impact(task)
                impact_score += duration_impact
                total_days_blocked += days_blocked
                
                # Critical path check
                if self._is_critical_path_task(task):
                    impact_score += 3
                    impact_assessment["critical_path_affected"] = True
                
                # Categorize impact level
                self._categorize_impact_level(impact_score, impact_assessment)
                
                # Track most critical blocker
                if impact_score > highest_impact_score:
                    highest_impact_score = impact_score
                    most_critical_task = {
                        "id": task.get("id", "Unknown"),
                        "title": task.get("title", "Unknown"),
                        "reason": task.get("blocker_reason", "Unknown"),
                        "impact_score": impact_score
                    }
            
            # Calculate average days blocked
            if blocked_tasks:
                impact_assessment["avg_days_blocked"] = total_days_blocked / len(blocked_tasks)
            
            impact_assessment["most_critical_blocker"] = most_critical_task
            
            return impact_assessment
            
        except Exception as e:
            self.logger.warning(f"Error assessing blocker impact: {e}")
            return {
                "high_impact": 0,
                "medium_impact": 0,
                "low_impact": len(blocked_tasks),
                "critical_path_affected": False,
                "total_story_points_blocked": 0,
                "avg_days_blocked": 0,
                "most_critical_blocker": None
            }

    def _estimate_blocker_resolution(
        self, blocked_tasks: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Estimate blocker resolution timeline.
        
        Args:
            blocked_tasks: List of blocked tasks to estimate resolution for
        """
        try:
            resolution_estimates = {
                "immediate": 0,  # < 1 day
                "short_term": 0,  # 1-3 days
                "medium_term": 0,  # 4-7 days
                "long_term": 0,  # > 7 days
                "unknown": 0,
                "estimated_resolution_days": {}
            }
            
            for task in blocked_tasks:
                task_id = task.get("id", f"task_{len(resolution_estimates['estimated_resolution_days'])}")
                blocker_reason = task.get("blocker_reason", "")
                priority = task.get("priority", "").upper()
                
                # Estimate based on blocker type and characteristics
                estimated_days = self._estimate_base_resolution_days(blocker_reason)
                
                # Adjust for priority
                estimated_days = self._adjust_estimate_for_priority(estimated_days, priority)
                
                # Adjust for existing blocker duration
                estimated_days = self._adjust_for_existing_blocker_duration(estimated_days, task)
                
                # Categorize resolution timeline
                self._categorize_resolution_timeline(estimated_days, resolution_estimates)
                
                resolution_estimates["estimated_resolution_days"][task_id] = estimated_days
            
            return resolution_estimates
            
        except Exception as e:
            self.logger.warning(f"Error estimating blocker resolution: {e}")
            return {
                "immediate": 0,
                "short_term": 0,
                "medium_term": 0,
                "long_term": len(blocked_tasks),
                "unknown": 0,
                "estimated_resolution_days": {}
            }

    def _generate_blocker_recommendations(
        self, blocked_tasks: List[Dict[str, Any]]
    ) -> List[str]:
        """Generate recommendations for resolving blockers.
        
        Args:
            blocked_tasks: List of blocked tasks to generate recommendations for
        """
        try:
            if not blocked_tasks:
                return ["No active blockers - maintain current momentum"]
            
            recommendations = []
            
            # Analyze blocker patterns
            blocker_categories = self._categorize_blockers(blocked_tasks)
            high_priority_blocked = self._get_high_priority_blocked_tasks(blocked_tasks)
            long_blocked = self._get_long_blocked_tasks(blocked_tasks)
            
            # Generate category-specific recommendations
            recommendations.extend(self._generate_category_specific_recommendations(blocker_categories))
            
            # Add priority and duration-based recommendations
            self._add_priority_and_duration_recommendations(
                recommendations, high_priority_blocked, long_blocked, len(blocked_tasks)
            )
            
            # Limit to most actionable recommendations
            return recommendations[:5]
            
        except Exception as e:
            self.logger.warning(f"Error generating blocker recommendations: {e}")
            return [f"Review and address {len(blocked_tasks)} active blockers systematically"]

    def _get_planned_tasks_for_tomorrow(self) -> List[Dict[str, Any]]:
        """Get tasks planned for tomorrow."""
        # Implementation would identify tomorrow's planned tasks
        return []

    def _identify_priority_tasks(
        self, tasks: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Identify priority tasks.
        
        Args:
            tasks: List of tasks to analyze for priority identification
        """
        try:
            high_priority_tasks = []
            
            for task in tasks:
                priority = task.get("priority", "").upper()
                due_date_str = task.get("due_date")
                
                # High priority based on priority field
                if priority in ["HIGH", "CRITICAL"]:
                    high_priority_tasks.append(task)
                    continue
                
                # High priority based on due date (due soon)
                if due_date_str:
                    try:
                        due_date = datetime.strptime(due_date_str, "%Y-%m-%d").date()
                        days_until_due = (due_date - datetime.now().date()).days
                        
                        if days_until_due <= 2:  # Due within 2 days
                            high_priority_tasks.append(task)
                            continue
                    except ValueError:
                        pass
                
                # High priority based on keywords in title
                title = task.get("title", "").lower()
                if any(keyword in title for keyword in [
                    "urgent", "critical", "blocker", "milestone", "release"
                ]):
                    high_priority_tasks.append(task)
            
            return high_priority_tasks
            
        except Exception as e:
            self.logger.warning(f"Error identifying priority tasks: {e}")
            return []

    def _identify_potential_blockers(
        self, tasks: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Identify potential blockers for tomorrow.
        
        Args:
            tasks: List of tasks to analyze for potential blocking issues
        """
        try:
            potential_blockers = []
            
            for task in tasks:
                # Check for dependency indicators
                description = task.get("description", "").lower()
                title = task.get("title", "").lower()
                
                # Tasks with external dependencies
                if any(keyword in description or keyword in title for keyword in [
                    "depends on", "waiting for", "requires", "blocked by",
                    "external", self.THIRD_PARTY_KEYWORD, "approval needed"
                ]):
                    potential_blockers.append(task)
                    continue
                
                # Tasks with resource constraints
                if any(keyword in description or keyword in title for keyword in [
                    "needs review", "pending", "clarification required",
                    "environment", "deployment", "access"
                ]):
                    potential_blockers.append(task)
                    continue
                
                # Complex tasks without clear definition
                complexity = task.get("complexity", 1)
                if complexity >= 5 and not task.get("description"):
                    potential_blockers.append(task)
            
            return potential_blockers
            
        except Exception as e:
            self.logger.warning(f"Error identifying potential blockers: {e}")
            return []

    def _analyze_resource_needs(self, tasks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze resource requirements for tomorrow.
        
        Args:
            tasks: List of tasks to analyze for resource requirements
        """
        try:
            resource_analysis = {
                "total_estimated_hours": 0,
                "skills_required": [],
                "team_members_needed": 0,
                "external_dependencies": 0,
                "tools_required": [],
                "capacity_assessment": "normal"
            }
            
            skills_set = set()
            tools_set = set()
            
            for task in tasks:
                # Estimate hours
                resource_analysis["total_estimated_hours"] += self._estimate_task_hours(task)
                
                # Extract skills and tools
                skills_set.update(self._extract_skills_from_task(task))
                tools_set.update(self._extract_tools_from_task(task))
                
                # Count external dependencies
                resource_analysis["external_dependencies"] += self._count_external_dependencies(task)
            
            resource_analysis["skills_required"] = list(skills_set)
            resource_analysis["tools_required"] = list(tools_set)
            
            # Estimate team members needed (assuming 8-hour work day)
            if resource_analysis["total_estimated_hours"] > 0:
                resource_analysis["team_members_needed"] = max(
                    1, int(resource_analysis["total_estimated_hours"] / 8)
                )
            
            # Capacity assessment
            resource_analysis["capacity_assessment"] = self._assess_capacity_level(
                resource_analysis["total_estimated_hours"]
            )
            
            return resource_analysis
            
        except Exception as e:
            self.logger.warning(f"Error analyzing resource needs: {e}")
            return {
                "total_estimated_hours": 0,
                "skills_required": [],
                "team_members_needed": 1,
                "external_dependencies": 0,
                "tools_required": [],
                "capacity_assessment": "normal"
            }

    def _identify_success_factors(self) -> List[str]:
        """Identify factors for tomorrow's success."""
        # Implementation would identify success factors
        return []

    def _generate_preparation_checklist(self) -> List[str]:
        """Generate preparation checklist for tomorrow."""
        # Implementation would generate checklist
        return []

    def _format_console_report(self, data: Dict[str, Any]) -> str:
        """Format report for console output.
        
        Args:
            data: Report data to format for console display
        """
        # Basic console formatting for the report
        report_lines = [
            "=" * 60,
            f"END-OF-DAY REPORT - {data.get('date', 'Unknown')}",
            "=" * 60,
            "",
            "DAILY SUMMARY:",
            f"  Tasks Completed: {data.get('daily_summary', {}).get('completed_tasks', 0)}",
            f"  Total Tasks: {data.get('daily_summary', {}).get('total_tasks', 0)}",
            f"  Completion Rate: {data.get('daily_summary', {}).get('completion_rate', 0):.1f}%",
            "",
            "TASK ANALYSIS:",
            f"  Active Today: {data.get('task_analysis', {}).get('total_active', 0)}",
            f"  Productivity Score: {data.get('task_analysis', {}).get('productivity_score', 0):.1f}/10",
            "",
            "BLOCKERS:",
            f"  Total Blocked: {data.get('blockers_analysis', {}).get('total_blocked', 0)}",
            "",
            "=" * 60,
            f"Generated: {data.get('timestamp', 'Unknown')}",
            "=" * 60
        ]
        
        return "\n".join(report_lines)

    def _format_html_report(self, data: Dict[str, Any]) -> str:
        """Format report as HTML.
        
        Args:
            data: Report data to format as HTML
        """
        # Basic HTML structure for the report
        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>End-of-Day Report - {data.get('date', 'Unknown')}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .header {{ background-color: #f4f4f4; padding: 10px; border-radius: 5px; }}
        .section {{ margin: 20px 0; }}
        .metric {{ display: inline-block; margin: 10px; padding: 10px; background-color: #e9e9e9; border-radius: 3px; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>End-of-Day Report</h1>
        <p>Date: {data.get('date', 'Unknown')}</p>
        <p>Generated: {data.get('timestamp', 'Unknown')}</p>
    </div>
    
    <div class="section">
        <h2>Daily Summary</h2>
        <div class="metric">Completed Tasks: {data.get('daily_summary', {}).get('completed_tasks', 0)}</div>
        <div class="metric">Total Tasks: {data.get('daily_summary', {}).get('total_tasks', 0)}</div>
        <div class="metric">Completion Rate: {data.get('daily_summary', {}).get('completion_rate', 0):.1f}%</div>
    </div>
    
    <div class="section">
        <h2>Task Analysis</h2>
        <p>Active Today: {data.get('task_analysis', {}).get('total_active', 0)}</p>
        <p>Productivity Score: {data.get('task_analysis', {}).get('productivity_score', 0):.1f}/10</p>
    </div>
    
    <div class="section">
        <h2>Blockers</h2>
        <p>Total Blocked: {data.get('blockers_analysis', {}).get('total_blocked', 0)}</p>
    </div>
</body>
</html>
        """
        return html_content

    # Additional formatting helper methods
    def _format_accomplishments_list(self, accomplishments: List[str]) -> str:
        """Format accomplishments as markdown list."""
        if not accomplishments:
            return "- No major accomplishments recorded"
        return "\n".join([f"- {acc}" for acc in accomplishments])

    def _format_risk_assessment(self, risk_data: Dict[str, Any]) -> str:
        """Format risk assessment data."""
        if not risk_data:
            return "- No significant risks identified"
        # Implementation would format risk data
        return "- Risk assessment data not available"

    def _format_task_list(self, tasks: List[Dict[str, Any]]) -> str:
        """Format task list for markdown."""
        if not tasks:
            return "- No tasks completed today"
        return "\n".join([f"- **{task['id']}**: {task['title']}" for task in tasks])

    def _format_blocker_analysis(self, blocker_data: Dict[str, Any]) -> str:
        """Format blocker analysis."""
        if blocker_data.get("total_blocked", 0) == 0:
            return "- No active blockers ✅"
        # Implementation would format blocker data
        return f"- {blocker_data.get('total_blocked', 0)} active blockers requiring attention"

    def _format_success_factors(self, factors: List[str]) -> str:
        """Format success factors list."""
        if not factors:
            return "- No specific success factors identified"
        return "\n".join([f"- {factor}" for factor in factors])

    def _format_checklist(self, checklist: List[str]) -> str:
        """Format preparation checklist."""
        if not checklist:
            return "- [ ] No preparation items identified"
        return "\n".join([f"- [ ] {item}" for item in checklist])

    def _format_automation_stats(self, stats: Dict[str, Any]) -> str:
        """Format automation statistics."""
        if not stats or "error" in stats:
            return "- Automation statistics not available"

        return f"""**Briefings Generated:** {stats.get('briefings_generated', 0)}
**Reports Generated:** {stats.get('reports_generated', 0)}
**Dashboard Updates:** {stats.get('dashboard_updates', 0)}
**System Uptime:** {stats.get('automation_uptime', 100.0):.1f}%
**Error Count:** {stats.get('error_count', 0)}"""

    def _initialize_execution_stats(self) -> Dict[str, Any]:
        """Initialize default execution statistics."""
        return {
            "briefings": 0,
            "reports": 0,
            "dashboard_updates": 0,
            "errors": 0,
            "uptime_percentage": 100.0,
            "avg_briefing_time": 0,
            "avg_report_time": 0
        }

    def _get_execution_log_paths(self) -> List[Path]:
        """Get list of potential log directories to search."""
        return [
            Path("logs"),
            Path("execution_logs"),
            Path("runtime/logs"),
            Path("outputs/logs")
        ]

    def _process_execution_log_files(self, log_paths: List[Path], report_date: str, 
                                    execution_stats: Dict[str, Any], 
                                    briefing_times: List[float], 
                                    report_times: List[float]) -> None:
        """Process all execution log files for the given date."""
        for log_dir in log_paths:
            if log_dir.exists():
                log_patterns = [
                    f"execution-*-{report_date}.log",
                    f"*{report_date}*.log",
                    "execution-*.log"
                ]
                
                for pattern in log_patterns:
                    for log_file in log_dir.glob(pattern):
                        self._process_single_execution_log_file(
                            log_file, report_date, execution_stats, 
                            briefing_times, report_times
                        )

    def _process_single_execution_log_file(self, log_file: Path, report_date: str,
                                          execution_stats: Dict[str, Any],
                                          briefing_times: List[float],
                                          report_times: List[float]) -> None:
        """Process a single execution log file."""
        try:
            with open(log_file, 'r', encoding='utf-8') as f:
                for line in f:
                    if report_date in line:
                        self._parse_execution_log_line(
                            line, execution_stats, briefing_times, report_times
                        )
        except Exception as e:
            self.logger.warning(f"Error reading log file {log_file}: {e}")

    def _parse_execution_log_line(self, line: str, execution_stats: Dict[str, Any],
                                 briefing_times: List[float], 
                                 report_times: List[float]) -> None:
        """Parse a single log line for execution statistics."""
        line_lower = line.lower()
        
        if "briefing" in line_lower:
            execution_stats["briefings"] += 1
            self._extract_timing_from_line(line, briefing_times)
        
        elif "report" in line_lower:
            execution_stats["reports"] += 1
            self._extract_timing_from_line(line, report_times)
        
        elif "dashboard" in line_lower:
            execution_stats["dashboard_updates"] += 1
        
        elif any(error_word in line_lower for error_word in ["error", "failed", "exception"]):
            execution_stats["errors"] += 1

    def _extract_timing_from_line(self, line: str, times_list: List[float]) -> None:
        """Extract timing information from a log line."""
        if self.COMPLETED_IN_PHRASE in line.lower():
            time_match = line.split(self.COMPLETED_IN_PHRASE)[-1].strip()
            if "sec" in time_match:
                try:
                    time_val = float(time_match.split("sec")[0].strip())
                    times_list.append(time_val)
                except ValueError:
                    pass

    def _calculate_execution_statistics(self, execution_stats: Dict[str, Any],
                                       briefing_times: List[float],
                                       report_times: List[float]) -> None:
        """Calculate final execution statistics."""
        # Calculate averages
        if briefing_times:
            execution_stats["avg_briefing_time"] = sum(briefing_times) / len(briefing_times)
        
        if report_times:
            execution_stats["avg_report_time"] = sum(report_times) / len(report_times)
        
        # Calculate uptime percentage
        total_operations = (execution_stats["briefings"] + 
                          execution_stats["reports"] + 
                          execution_stats["dashboard_updates"])
        
        if total_operations > 0:
            error_rate = execution_stats["errors"] / total_operations
            execution_stats["uptime_percentage"] = max(0, (1 - error_rate) * 100)

    def _extract_tasks_from_list(self, data_list: List[Any], filename: str) -> List[Dict[str, Any]]:
        """Extract tasks from a list data structure."""
        tasks = []
        for item in data_list:
            if isinstance(item, dict) and self._is_task_like(item):
                tasks.append(self._normalize_task_data(item, filename))
        return tasks

    def _extract_tasks_from_dict_keys(self, data: Dict[str, Any], filename: str) -> List[Dict[str, Any]]:
        """Extract tasks from known dictionary keys."""
        tasks = []
        task_keys = [
            "tasks", "task_list", "items", "entries", 
            "active_tasks", "completed_tasks", "all_tasks"
        ]
        
        for key in task_keys:
            if key in data and isinstance(data[key], list):
                tasks.extend(self._extract_tasks_from_list(data[key], filename))
        
        return tasks

    def _extract_tasks_from_nested_objects(self, data: Dict[str, Any], filename: str) -> List[Dict[str, Any]]:
        """Extract tasks from nested objects in the data."""
        tasks = []
        for key, value in data.items():
            if isinstance(value, dict) and "tasks" in value:
                if isinstance(value["tasks"], list):
                    tasks.extend(self._extract_tasks_from_list(value["tasks"], filename))
        return tasks

    def _check_task_status_for_challenges(self, task: Dict[str, Any], target_date: date, 
                                         challenges: List[str]) -> tuple[int, int, int]:
        """Check a single task for challenges and return counts."""
        blocked_count = failed_count = overdue_count = 0
        status = task.get("status", "").upper()
        
        if status == "BLOCKED":
            blocked_count = 1
            blocker_reason = task.get("blocker_reason", "Unknown blocker")
            challenges.append(f"Task blocked: {task.get('title', 'Unknown')} - {blocker_reason}")
        
        elif status == "FAILED":
            failed_count = 1
            challenges.append(f"Task failed: {task.get('title', 'Unknown')}")
        
        elif status in ["IN_PROGRESS", "TODO"]:
            # Check if task is overdue
            due_date_str = task.get("due_date")
            if due_date_str:
                try:
                    due_date = datetime.strptime(due_date_str, "%Y-%m-%d").date()
                    if due_date < target_date:
                        overdue_count = 1
                        challenges.append(f"Overdue task: {task.get('title', 'Unknown')}")
                except ValueError:
                    pass
        
        return blocked_count, failed_count, overdue_count

    def _was_task_modified_on_date(self, task: Dict[str, Any], target_date: date) -> bool:
        """Check if task was modified on the target date."""
        last_modified_str = task.get("last_modified", task.get("updated_date"))
        if not last_modified_str:
            return False
            
        try:
            # Parse last modified date
            if 'T' in last_modified_str:  # ISO format
                last_modified = datetime.fromisoformat(last_modified_str.replace('Z', self.TIMEZONE_SUFFIX)).date()
            else:  # Simple date format
                last_modified = datetime.strptime(last_modified_str, "%Y-%m-%d").date()
            
            return last_modified == target_date
        except (ValueError, AttributeError):
            return False

    def _add_summary_challenges(self, challenges: List[str], blocked_count: int, 
                               failed_count: int, overdue_count: int) -> None:
        """Add summary challenges based on counts."""
        if blocked_count > 2:
            challenges.append(f"Multiple tasks blocked ({blocked_count} total) - resource dependencies")
        if failed_count > 1:
            challenges.append(f"Several task failures ({failed_count} total) - quality/complexity issues")
        if overdue_count > 2:
            challenges.append(f"Multiple overdue items ({overdue_count} total) - capacity planning needed")

    def _add_default_challenges(self, challenges: List[str], all_tasks: List[Dict[str, Any]]) -> None:
        """Add default challenges when no specific ones are found."""
        if not challenges:
            total_tasks = len(all_tasks)
            in_progress = len([t for t in all_tasks if t.get("status") == "IN_PROGRESS"])
            
            if in_progress > total_tasks * 0.6:  # More than 60% in progress
                challenges.append("High number of concurrent tasks - focus and prioritization needed")
            else:
                challenges.append("No significant challenges identified - steady progress maintained")

    def _parse_date_from_string(self, date_str: str) -> date:
        """Parse date from string handling multiple formats."""
        if 'T' in date_str:
            return datetime.fromisoformat(date_str.replace('Z', self.TIMEZONE_SUFFIX)).date()
        else:
            return datetime.strptime(date_str, "%Y-%m-%d").date()

    def _check_task_started_date(self, task: Dict[str, Any], target_date: date) -> bool:
        """Check if task has started_date matching target date."""
        started_date_str = task.get("started_date")
        if not started_date_str:
            return False
            
        try:
            started_date = self._parse_date_from_string(started_date_str)
            return started_date == target_date
        except (ValueError, AttributeError):
            return False

    def _check_activity_logs_for_start(self, task: Dict[str, Any], target_date: date) -> bool:
        """Check activity logs for task start on target date."""
        activity_logs = task.get("activity_log", [])
        for log_entry in activity_logs:
            if not isinstance(log_entry, dict):
                continue
                
            log_date_str = log_entry.get("date", log_entry.get("timestamp"))
            action = log_entry.get("action", "")
            new_status = log_entry.get("new_status", "")
            
            if (log_date_str and 
                ("started" in action.lower() or new_status == "IN_PROGRESS")):
                try:
                    log_date = self._parse_date_from_string(log_date_str)
                    if log_date == target_date:
                        return True
                except (ValueError, AttributeError):
                    continue
        return False

    def _check_status_change_to_in_progress(self, task: Dict[str, Any], report_date: str) -> bool:
        """Check if task changed to IN_PROGRESS status today."""
        if (task.get("status") == "IN_PROGRESS" and 
            self._was_task_active_today(task, report_date)):
            # Additional check to see if it wasn't already in progress
            previous_status = task.get("previous_status")
            return bool(previous_status and previous_status != "IN_PROGRESS")
        return False

    def _calculate_priority_impact(self, task: Dict[str, Any]) -> int:
        """Calculate impact score based on task priority."""
        priority = task.get("priority", "").upper()
        if priority == "CRITICAL":
            return 5
        elif priority == "HIGH":
            return 3
        elif priority == "MEDIUM":
            return 2
        else:
            return 1

    def _calculate_story_points_impact(self, task: Dict[str, Any], impact_assessment: Dict[str, Any]) -> int:
        """Calculate impact score based on story points/complexity."""
        story_points = task.get("story_points", task.get("complexity", 1))
        if isinstance(story_points, (int, float)):
            impact_assessment["total_story_points_blocked"] += story_points
            return min(int(story_points), 5)  # Cap at 5 points
        else:
            impact_assessment["total_story_points_blocked"] += 1
            return 1

    def _calculate_duration_impact(self, task: Dict[str, Any]) -> tuple[int, int]:
        """Calculate impact score and days blocked based on duration."""
        blocked_date_str = task.get("blocked_date", task.get("last_modified"))
        if not blocked_date_str:
            return 0, 1
            
        try:
            blocked_date = self._parse_date_from_string(blocked_date_str)
            days_blocked = (datetime.now().date() - blocked_date).days
            
            if days_blocked > 5:
                return 3, days_blocked
            elif days_blocked > 2:
                return 2, days_blocked
            elif days_blocked > 0:
                return 1, days_blocked
            else:
                return 0, days_blocked
                
        except (ValueError, AttributeError):
            return 0, 1

    def _is_critical_path_task(self, task: Dict[str, Any]) -> bool:
        """Check if task is on critical path."""
        return (task.get("is_critical_path") or 
                "milestone" in task.get("title", "").lower() or
                "release" in task.get("title", "").lower())

    def _categorize_impact_level(self, impact_score: int, impact_assessment: Dict[str, Any]) -> None:
        """Categorize impact level based on score."""
        if impact_score >= 10:
            impact_assessment["high_impact"] += 1
        elif impact_score >= 6:
            impact_assessment["medium_impact"] += 1
        else:
            impact_assessment["low_impact"] += 1

    def _check_task_date_fields_for_activity(self, task: Dict[str, Any], target_date: date) -> bool:
        """Check various date fields for activity on target date."""
        date_fields = [
            "last_modified", "updated_date", "started_date", 
            "completed_date", "status_changed_date"
        ]
        
        for field in date_fields:
            date_str = task.get(field)
            if date_str:
                try:
                    task_date = self._parse_date_from_string(date_str)
                    if task_date == target_date:
                        return True
                except (ValueError, AttributeError):
                    continue
        return False

    def _check_activity_logs_for_date(self, task: Dict[str, Any], target_date: date) -> bool:
        """Check activity logs for any activity on target date."""
        activity_logs = task.get("activity_log", [])
        for log_entry in activity_logs:
            if not isinstance(log_entry, dict):
                continue
                
            log_date_str = log_entry.get("date", log_entry.get("timestamp"))
            if log_date_str:
                try:
                    log_date = self._parse_date_from_string(log_date_str)
                    if log_date == target_date:
                        return True
                except (ValueError, AttributeError):
                    continue
        return False

    def _get_tasks_completed_on_date(self, all_tasks: List[Dict[str, Any]], target_date: date) -> List[Dict[str, Any]]:
        """Get all tasks completed on the target date."""
        completed_today = []
        
        for task in all_tasks:
            if task.get("status") == "COMPLETED":
                if self._was_task_completed_on_date(task, target_date):
                    completed_today.append(task)
        
        return completed_today

    def _was_task_completed_on_date(self, task: Dict[str, Any], target_date: date) -> bool:
        """Check if task was completed on the specific date."""
        completed_date_str = task.get("completed_date")
        if not completed_date_str:
            return False
            
        try:
            completed_date = self._parse_date_from_string(completed_date_str)
            return completed_date == target_date
        except (ValueError, AttributeError):
            return False

    def _calculate_velocity_points(self, completed_tasks: List[Dict[str, Any]]) -> float:
        """Calculate total velocity points from completed tasks."""
        total_points = 0
        for task in completed_tasks:
            task_points = task.get("story_points", task.get("complexity", 1))
            if isinstance(task_points, (int, float)):
                total_points += task_points
            else:
                total_points += 1
        
        return float(total_points)

    def _estimate_task_hours(self, task: Dict[str, Any]) -> int:
        """Estimate hours for a task based on story points/complexity."""
        story_points = task.get("story_points", task.get("complexity", 1))
        if isinstance(story_points, (int, float)):
            # Rough conversion: 1 story point = 4-6 hours
            return int(story_points * 5)
        return 5  # Default 5 hours

    def _extract_skills_from_task(self, task: Dict[str, Any]) -> set:
        """Extract required skills from task description and title."""
        skills_set = set()
        description = task.get("description", "").lower()
        title = task.get("title", "").lower()
        
        # Technical skills mapping
        if any(skill in description or skill in title for skill in [
            "python", "javascript", "react", "database", "sql"
        ]):
            skills_set.add("Backend Development")
        
        if any(skill in description or skill in title for skill in [
            "ui", "frontend", "css", "html", "design"
        ]):
            skills_set.add("Frontend Development")
        
        if any(skill in description or skill in title for skill in [
            "test", "qa", "automation", "selenium"
        ]):
            skills_set.add("Quality Assurance")
        
        if any(skill in description or skill in title for skill in [
            "deploy", "devops", "infrastructure", "aws", "docker"
        ]):
            skills_set.add("DevOps")
        
        return skills_set

    def _extract_tools_from_task(self, task: Dict[str, Any]) -> set:
        """Extract required tools from task description and title."""
        tools_set = set()
        description = task.get("description", "").lower()
        title = task.get("title", "").lower()
        
        if any(tool in description or tool in title for tool in [
            "docker", "kubernetes", "jenkins", "git"
        ]):
            tools_set.add("Development Tools")
        
        if any(tool in description or tool in title for tool in [
            "database", "mysql", "postgresql", "mongodb"
        ]):
            tools_set.add("Database Systems")
        
        return tools_set

    def _count_external_dependencies(self, task: Dict[str, Any]) -> int:
        """Count external dependencies for a task."""
        description = task.get("description", "").lower()
        title = task.get("title", "").lower()
        
        if any(keyword in description or keyword in title for keyword in [
            "external", self.THIRD_PARTY_KEYWORD, "vendor", "client"
        ]):
            return 1
        return 0

    def _assess_capacity_level(self, total_hours: int) -> str:
        """Assess capacity level based on total estimated hours."""
        if total_hours > 40:
            return "high"
        elif total_hours > 16:
            return "normal"
        else:
            return "low"

    def _is_significant_accomplishment(self, task: Dict[str, Any]) -> bool:
        """Check if a task represents a significant accomplishment."""
        title = task.get("title", "").strip().lower()
        priority = task.get("priority", "").upper()
        complexity = task.get("complexity", 1)
        
        # High-priority or complex tasks are significant
        if priority in ["HIGH", "CRITICAL"] or complexity >= 3:
            return True
        
        # Milestone or release tasks are significant
        if "milestone" in title or "release" in title:
            return True
        
        return False

    def _format_accomplishment_description(self, task: Dict[str, Any]) -> str:
        """Format accomplishment description based on task properties."""
        title = task.get("title", "").strip()
        priority = task.get("priority", "").upper()
        complexity = task.get("complexity", 1)
        task_title_lower = title.lower()
        
        if priority in ["HIGH", "CRITICAL"] or complexity >= 3:
            return f"Completed {priority.lower()} priority task: {title}"
        elif "milestone" in task_title_lower or "release" in task_title_lower:
            return f"Achieved milestone: {title}"
        else:
            return f"Completed: {title}"

    def _generate_fallback_accomplishments(self, all_tasks: List[Dict[str, Any]]) -> List[str]:
        """Generate fallback accomplishments when no specific ones are found."""
        completed_count = len([t for t in all_tasks if t.get("status") == "COMPLETED"])
        if completed_count > 0:
            return [f"Successfully completed {completed_count} tasks"]
        else:
            return ["Focused on ongoing development and planning activities"]

    def _estimate_base_resolution_days(self, blocker_reason: str) -> int:
        """Estimate base resolution days based on blocker type."""
        blocker_reason_lower = blocker_reason.lower()
        
        if any(keyword in blocker_reason_lower for keyword in [
            "quick fix", "simple", "minor", "configuration"
        ]):
            return 1
        elif any(keyword in blocker_reason_lower for keyword in [
            "approval", "review", "sign-off"
        ]):
            return 2
        elif any(keyword in blocker_reason_lower for keyword in [
            "external", self.THIRD_PARTY_KEYWORD, "vendor"
        ]):
            return 7
        elif any(keyword in blocker_reason_lower for keyword in [
            "complex", "architecture", "design", "major"
        ]):
            return 10
        elif any(keyword in blocker_reason_lower for keyword in [
            "budget", "resource allocation", "hiring"
        ]):
            return 14
        else:
            return 3  # Default estimate

    def _adjust_estimate_for_priority(self, estimated_days: int, priority: str) -> int:
        """Adjust estimation based on task priority."""
        if priority == "CRITICAL":
            return max(1, estimated_days // 2)
        elif priority == "HIGH":
            return max(1, int(estimated_days * 0.75))
        elif priority == "LOW":
            return int(estimated_days * 1.5)
        else:
            return estimated_days

    def _adjust_for_existing_blocker_duration(self, estimated_days: int, task: Dict[str, Any]) -> int:
        """Adjust estimate based on how long task has been blocked."""
        blocked_date_str = task.get("blocked_date", task.get("last_modified"))
        if not blocked_date_str:
            return estimated_days
            
        try:
            blocked_date = self._parse_date_from_string(blocked_date_str)
            days_already_blocked = (datetime.now().date() - blocked_date).days
            # If already blocked for a while, it might take longer
            if days_already_blocked > 5:
                return max(estimated_days, days_already_blocked + 2)
        except (ValueError, AttributeError):
            pass
        
        return estimated_days

    def _categorize_resolution_timeline(self, estimated_days: int, resolution_estimates: Dict[str, Any]) -> None:
        """Categorize resolution timeline based on estimated days."""
        if estimated_days < 1:
            resolution_estimates["immediate"] += 1
        elif estimated_days <= 3:
            resolution_estimates["short_term"] += 1
        elif estimated_days <= 7:
            resolution_estimates["medium_term"] += 1
        else:
            resolution_estimates["long_term"] += 1

    def _generate_category_specific_recommendations(self, blocker_categories: Dict[str, int]) -> List[str]:
        """Generate recommendations based on blocker categories."""
        recommendations = []
        
        category_recommendations = {
            "dependency": "coordinating with relevant teams and establishing clear handoff timelines",
            "approval": "scheduling focused review sessions and providing complete context",
            "technical": "allocating dedicated technical resources and creating spike solutions",
            "resource": "reassigning priorities or bringing in additional capacity",
            "external": "establishing regular check-ins and backup plans",
            "information": "scheduling stakeholder sessions and documenting requirements"
        }
        
        for category, action in category_recommendations.items():
            count = blocker_categories.get(category, 0)
            if count > 0:
                recommendations.append(
                    f"Address {count} {category} blockers by {action}"
                )
        
        return recommendations

    def _get_high_priority_blocked_tasks(self, blocked_tasks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Get high priority blocked tasks."""
        return [
            t for t in blocked_tasks 
            if t.get("priority", "").upper() in ["CRITICAL", "HIGH"]
        ]

    def _get_long_blocked_tasks(self, blocked_tasks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Get tasks that have been blocked for more than 5 days."""
        long_blocked = []
        for task in blocked_tasks:
            blocked_date_str = task.get("blocked_date", task.get("last_modified"))
            if blocked_date_str:
                try:
                    blocked_date = self._parse_date_from_string(blocked_date_str)
                    if (datetime.now().date() - blocked_date).days > 5:
                        long_blocked.append(task)
                except (ValueError, AttributeError):
                    continue
        return long_blocked

    def _add_priority_and_duration_recommendations(self, recommendations: List[str], 
                                                  high_priority_blocked: List[Dict[str, Any]], 
                                                  long_blocked: List[Dict[str, Any]], 
                                                  total_blocked: int) -> None:
        """Add priority and duration-based recommendations."""
        if high_priority_blocked:
            recommendations.insert(0, 
                f"URGENT: {len(high_priority_blocked)} high-priority tasks blocked - "
                "escalate to leadership and allocate immediate resources"
            )
        
        if long_blocked:
            recommendations.append(
                f"Review {len(long_blocked)} long-standing blockers (>5 days) - "
                "consider alternative approaches or scope adjustments"
            )
        
        if total_blocked > 5:
            recommendations.append(
                "High blocker count indicates potential process issues - "
                "review workflow and implement preventive measures"
            )


def main():
    """Main entry point for end-of-day report generation."""
    generator = EndOfDayReportGenerator()

    try:
        # Generate today's end-of-day report
        report_data = generator.generate_eod_report()

        print(f"✅ End-of-day report generated: {report_data['output_file']}")
        print("📊 Report includes comprehensive daily analysis")
        print("🔄 Integrated with Phase 5 infrastructure")

        return True

    except Exception as e:
        print(f"❌ End-of-day report generation failed: {e}")
        return False


if __name__ == "__main__":
    main()
