"""
Step 4.1 - Task Declaration & Preparation
Transform task plans into live executions using defined agents, prompts, and memory context.

This module provides the complete task declaration and preparation system that:
1. Fully describes and registers tasks with all metadata
2. Generates enriched prompts with task metadata and memory context
3. Determines appropriate context and routing for LangGraph execution
4. Validates task readiness and dependencies
"""

import os
import sys
import yaml
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass, asdict
from enum import Enum

# Add parent directory to path to allow imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.task_loader import load_task_metadata, save_task_metadata, get_all_tasks
from tools.memory_engine import MemoryEngine
from orchestration.states import TaskStatus
from tools.context_tracker import track_context_usage

# Configure logging
logger = logging.getLogger(__name__)


class TaskPreparationStatus(str, Enum):
    """Status of task preparation process"""
    PENDING = "PENDING"
    CONTEXT_LOADED = "CONTEXT_LOADED"
    PROMPT_GENERATED = "PROMPT_GENERATED"
    READY_FOR_EXECUTION = "READY_FOR_EXECUTION"
    FAILED = "FAILED"


@dataclass
class TaskDeclaration:
    """
    Complete task declaration with all metadata and preparation status.
    This represents the fully prepared task ready for LangGraph execution.
    """
    # Core task metadata
    id: str
    title: str
    description: str
    owner: str
    state: str
    priority: str
    estimation_hours: float
    
    # Dependencies and artifacts
    depends_on: List[str]
    artefacts: List[str]
    context_topics: List[str]
    
    # Preparation metadata
    preparation_status: TaskPreparationStatus
    context_loaded: bool = False
    prompt_generated: bool = False
    dependencies_satisfied: bool = False
    
    # Runtime data
    context_content: Optional[str] = None
    generated_prompt: Optional[str] = None
    agent_assignment: Optional[str] = None
    execution_plan: Optional[Dict[str, Any]] = None
    
    # Tracking information
    declared_at: Optional[str] = None
    prepared_by: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation"""
        return asdict(self)
    
    @classmethod
    def from_metadata(cls, task_metadata: Dict[str, Any]) -> 'TaskDeclaration':
        """Create TaskDeclaration from task metadata"""
        return cls(
            id=task_metadata.get('id', ''),
            title=task_metadata.get('title', ''),
            description=task_metadata.get('description', ''),
            owner=task_metadata.get('owner', ''),
            state=task_metadata.get('state', 'CREATED'),
            priority=task_metadata.get('priority', 'MEDIUM'),
            estimation_hours=task_metadata.get('estimation_hours', 0),
            depends_on=task_metadata.get('depends_on', []),
            artefacts=task_metadata.get('artefacts', []),
            context_topics=task_metadata.get('context_topics', []),
            preparation_status=TaskPreparationStatus.PENDING,
            declared_at=datetime.now().isoformat()
        )
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TaskDeclaration':
        """Create TaskDeclaration from a dictionary (e.g., loaded from JSON)"""
        return cls(
            id=data.get('id', ''),
            title=data.get('title', ''),
            description=data.get('description', ''),
            owner=data.get('owner', ''),
            state=data.get('state', 'CREATED'),
            priority=data.get('priority', 'MEDIUM'),
            estimation_hours=data.get('estimation_hours', 0),
            depends_on=data.get('depends_on', []),
            artefacts=data.get('artefacts', []),
            context_topics=data.get('context_topics', []),
            preparation_status=TaskPreparationStatus(data.get('preparation_status', TaskPreparationStatus.PENDING)),
            context_loaded=data.get('context_loaded', False),
            prompt_generated=data.get('prompt_generated', False),
            dependencies_satisfied=data.get('dependencies_satisfied', False),
            context_content=data.get('context_content'),
            generated_prompt=data.get('generated_prompt'),
            agent_assignment=data.get('agent_assignment'),
            execution_plan=data.get('execution_plan'),
            declared_at=data.get('declared_at'),
            prepared_by=data.get('prepared_by')
        )


class TaskDeclarationManager:
    """
    Manages the complete task declaration and preparation workflow.
    Orchestrates the transformation from task plans to live executions.
    """
    def __init__(self, memory_engine: Optional[MemoryEngine] = None):
        """
        Initialize the task declaration manager.
        
        Args:
            memory_engine: Optional memory engine instance for context loading
        """
        self.memory_engine = memory_engine or MemoryEngine()
        self.declared_tasks: Dict[str, TaskDeclaration] = {}
        
        # Create outputs directory for task preparation
        self.outputs_dir = Path("outputs")
        self.outputs_dir.mkdir(exist_ok=True)
        
        # Load existing task declarations from previous runs
        self._load_existing_declarations()
        
        logger.info(f"Task Declaration Manager initialized with {len(self.declared_tasks)} existing declarations")
    
    def declare_task(self, task_id: str, force_reload: bool = False) -> TaskDeclaration:
        """
        Declare a task with full metadata registration.
        
        Args:
            task_id: The task identifier (e.g., BE-07)
            force_reload: Whether to force reload even if already declared
            
        Returns:
            TaskDeclaration: Fully declared task with metadata
            
        Raises:
            FileNotFoundError: If task metadata file doesn't exist
            ValueError: If task metadata is invalid
        """
        logger.info(f"Declaring task: {task_id}")
        
        # Check if already declared
        if task_id in self.declared_tasks and not force_reload:
            logger.info(f"Task {task_id} already declared, returning existing declaration")
            return self.declared_tasks[task_id]
        
        # Load task metadata from YAML
        try:
            task_metadata = load_task_metadata(task_id)
        except FileNotFoundError:
            logger.error(f"Task metadata file not found for {task_id}")
            raise
        except Exception as e:
            logger.error(f"Error loading task metadata for {task_id}: {e}")
            raise ValueError(f"Invalid task metadata for {task_id}: {e}")
        
        # Validate required metadata fields
        self._validate_task_metadata(task_metadata)
        
        # Create task declaration
        declaration = TaskDeclaration.from_metadata(task_metadata)
        declaration.prepared_by = "TaskDeclarationManager"
        
        # Store the declaration
        self.declared_tasks[task_id] = declaration
        
        # Save declaration metadata
        self._save_declaration_metadata(declaration)
        
        logger.info(f"Task {task_id} successfully declared")
        return declaration
    
    def prepare_task_for_execution(self, task_id: str) -> TaskDeclaration:
        """
        Complete preparation of a task for LangGraph execution.
        
        This method:
        1. Declares the task if not already done
        2. Loads context based on context_topics
        3. Generates enriched prompts
        4. Validates dependencies
        5. Creates execution plan
        
        Args:
            task_id: The task identifier
            
        Returns:
            TaskDeclaration: Fully prepared task ready for execution
        """
        logger.info(f"Preparing task for execution: {task_id}")
        
        # Step 1: Declare task
        declaration = self.declare_task(task_id)
        
        # Step 2: Load context
        self._load_task_context(declaration)
        
        # Step 3: Generate prompt
        self._generate_task_prompt(declaration)
        
        # Step 4: Validate dependencies
        self._validate_dependencies(declaration)
        
        # Step 5: Create execution plan
        self._create_execution_plan(declaration)
        
        # Update preparation status
        if all([
            declaration.context_loaded,
            declaration.prompt_generated,
            declaration.dependencies_satisfied
        ]):
            declaration.preparation_status = TaskPreparationStatus.READY_FOR_EXECUTION
            logger.info(f"Task {task_id} is ready for execution")
        else:
            declaration.preparation_status = TaskPreparationStatus.FAILED
            logger.error(f"Task {task_id} preparation failed")
        
        # Save updated declaration
        self._save_declaration_metadata(declaration)
        
        return declaration
    
    def _validate_task_metadata(self, metadata: Dict[str, Any]) -> None:
        """Validate that task metadata contains required fields"""
        required_fields = ['id', 'title', 'owner', 'state']
        
        for field in required_fields:
            if field not in metadata:
                raise ValueError(f"Missing required field: {field}")
        
        # Validate owner is a valid agent role
        valid_owners = ['backend', 'frontend', 'technical', 'qa', 'doc', 'coordinator', 'product', 'ux']
        if metadata['owner'] not in valid_owners:
            raise ValueError(f"Invalid owner '{metadata['owner']}'. Must be one of: {valid_owners}")
        
        # Validate state
        valid_states = ['CREATED', 'PLANNED', 'IN_PROGRESS', 'QA_PENDING', 'DOCUMENTATION', 'HUMAN_REVIEW', 'DONE', 'BLOCKED']
        if metadata['state'] not in valid_states:
            raise ValueError(f"Invalid state '{metadata['state']}'. Must be one of: {valid_states}")
    
    def _load_task_context(self, declaration: TaskDeclaration) -> None:
        """Load context for the task based on context_topics"""
        logger.info(f"Loading context for task {declaration.id}")
        
        try:
            if declaration.context_topics:
                # Use focused context builder from memory engine
                context_content = self.memory_engine.build_focused_context(
                    context_topics=declaration.context_topics,
                    max_tokens=2000,
                    max_per_topic=3,
                    user="task_preparation",
                    task_id=declaration.id,
                    agent_role=declaration.owner
                )
                
                # Get document details for tracking
                documents = self.memory_engine.get_documents(
                    declaration.context_topics,
                    max_per_topic=3,
                    user="task_preparation"
                )
                
                # Track context usage
                track_context_usage(
                    task_id=declaration.id,
                    context_topics=declaration.context_topics,
                    documents_used=documents,
                    agent_role="task_preparation",
                    context_length=len(context_content),
                    additional_metadata={
                        "phase": "task_declaration",
                        "preparation_step": "context_loading"
                    }
                )
                
                declaration.context_content = context_content
                declaration.context_loaded = True
                
                logger.info(f"Context loaded for task {declaration.id}: {len(declaration.context_topics)} topics, {len(context_content)} characters")
            else:
                # No context topics specified, provide basic context
                declaration.context_content = f"# Task Context\nNo specific context topics defined for task {declaration.id}"
                declaration.context_loaded = True
                logger.warning(f"No context topics specified for task {declaration.id}")
                
        except Exception as e:
            logger.error(f"Error loading context for task {declaration.id}: {e}")
            declaration.context_loaded = False
            declaration.preparation_status = TaskPreparationStatus.FAILED
    
    def _generate_task_prompt(self, declaration: TaskDeclaration) -> None:
        """Generate enriched prompt for the task"""
        logger.info(f"Generating prompt for task {declaration.id}")
        
        try:
            # Create enriched prompt with task metadata and context
            prompt_template = self._get_prompt_template(declaration.owner)
            
            # Replace placeholders with actual content
            enriched_prompt = prompt_template.format(
                task_id=declaration.id,
                task_title=declaration.title,
                task_description=declaration.description,
                task_priority=declaration.priority,
                estimation_hours=declaration.estimation_hours,
                dependencies=", ".join(declaration.depends_on) if declaration.depends_on else "None",
                artefacts="\n".join(f"- {artifact}" for artifact in declaration.artefacts),
                context_topics=", ".join(declaration.context_topics) if declaration.context_topics else "None",
                context_content=declaration.context_content or "No context available",
                current_state=declaration.state
            )
            
            declaration.generated_prompt = enriched_prompt
            declaration.prompt_generated = True
            
            # Save prompt to file
            task_dir = self.outputs_dir / declaration.id
            task_dir.mkdir(exist_ok=True)
            
            prompt_file = task_dir / f"prompt_{declaration.owner}.md"
            with open(prompt_file, 'w', encoding='utf-8') as f:
                f.write(enriched_prompt)
            
            logger.info(f"Prompt generated and saved for task {declaration.id}")
            
        except Exception as e:
            logger.error(f"Error generating prompt for task {declaration.id}: {e}")
            declaration.prompt_generated = False
            declaration.preparation_status = TaskPreparationStatus.FAILED
    
    def _get_prompt_template(self, agent_role: str) -> str:
        """Get prompt template for the specified agent role"""
        # Basic prompt template - in practice, this would load from prompts/ directory
        template = """# Task Execution Prompt for {agent_role}

## Task Information
- **Task ID**: {task_id}
- **Title**: {task_title}
- **Priority**: {task_priority}
- **Estimated Hours**: {estimation_hours}
- **Current State**: {current_state}

## Task Description
{task_description}

## Dependencies
{dependencies}

## Expected Artifacts
{artefacts}

## Context Topics
{context_topics}

## Relevant Context
{context_content}

## Instructions
Please execute this task according to your role as {agent_role}. Consider the provided context and ensure all artifacts are properly created or modified. Update the task state appropriately upon completion.

---
*Generated by Task Declaration Manager at {timestamp}*
""".replace('{agent_role}', agent_role).replace('{timestamp}', datetime.now().isoformat())
        
        return template
    
    def _validate_dependencies(self, declaration: TaskDeclaration) -> None:
        """Validate that all task dependencies are satisfied"""
        logger.info(f"Validating dependencies for task {declaration.id}")
        
        if not declaration.depends_on:
            declaration.dependencies_satisfied = True
            logger.info(f"No dependencies for task {declaration.id}")
            return
        
        unsatisfied_dependencies = []
        
        for dep_id in declaration.depends_on:
            try:
                dep_metadata = load_task_metadata(dep_id)
                dep_state = dep_metadata.get('state', 'CREATED')
                
                # Consider task satisfied if it's in an advanced state
                # For demonstration purposes, allow PLANNED and higher states
                satisfactory_states = {
                    'PLANNED', 'IN_PROGRESS', 'QA_PENDING', 
                    'DOCUMENTATION', 'DONE', 'COMPLETED'
                }
                
                if dep_state not in satisfactory_states:
                    unsatisfied_dependencies.append(f"{dep_id} (state: {dep_state})")
                    
            except FileNotFoundError:
                unsatisfied_dependencies.append(f"{dep_id} (not found)")
            except Exception as e:
                unsatisfied_dependencies.append(f"{dep_id} (error: {e})")
        
        if unsatisfied_dependencies:
            declaration.dependencies_satisfied = False
            logger.warning(f"Task {declaration.id} has unsatisfied dependencies: {unsatisfied_dependencies}")
        else:
            declaration.dependencies_satisfied = True
            logger.info(f"All dependencies satisfied for task {declaration.id}")
    
    def _create_execution_plan(self, declaration: TaskDeclaration) -> None:
        """Create execution plan for LangGraph routing"""
        logger.info(f"Creating execution plan for task {declaration.id}")
        
        try:
            # Determine agent assignment based on owner
            agent_mapping = {
                'backend': 'backend_handler',
                'frontend': 'frontend_handler',
                'technical': 'technical_handler',
                'qa': 'qa_handler',
                'doc': 'documentation_handler',
                'coordinator': 'coordinator_handler',
                'product': 'coordinator_handler',  # Product tasks go through coordinator
                'ux': 'coordinator_handler'  # UX tasks go through coordinator
            }
            
            declaration.agent_assignment = agent_mapping.get(declaration.owner, 'coordinator_handler')
            
            # Create execution plan
            execution_plan = {
                'entry_point': declaration.agent_assignment,
                'workflow_type': 'dynamic',
                'expected_transitions': self._get_expected_transitions(declaration),
                'timeout_minutes': declaration.estimation_hours * 60,
                'retry_count': 3,
                'artifacts_to_create': declaration.artefacts,
                'success_criteria': {
                    'artifacts_created': len(declaration.artefacts) > 0,
                    'state_advanced': True,
                    'no_errors': True
                }
            }
            
            declaration.execution_plan = execution_plan
            
            logger.info(f"Execution plan created for task {declaration.id}")
            
        except Exception as e:
            logger.error(f"Error creating execution plan for task {declaration.id}: {e}")
            declaration.preparation_status = TaskPreparationStatus.FAILED
    
    def _get_expected_transitions(self, declaration: TaskDeclaration) -> List[str]:
        """Get expected state transitions for the task"""
        current_state = declaration.state
        
        # Define typical transition paths
        transition_paths = {
            'CREATED': ['PLANNED'],
            'PLANNED': ['IN_PROGRESS'],
            'IN_PROGRESS': ['QA_PENDING'],
            'QA_PENDING': ['DOCUMENTATION', 'BLOCKED'],
            'DOCUMENTATION': ['DONE'],
            'BLOCKED': ['PLANNED', 'IN_PROGRESS']        }
        
        return transition_paths.get(current_state, ['DONE'])

    def _save_declaration_metadata(self, declaration: TaskDeclaration) -> None:
        """Save task declaration metadata to file"""
        try:
            task_dir = self.outputs_dir / declaration.id
            task_dir.mkdir(exist_ok=True)
            
            declaration_file = task_dir / "task_declaration.json"
            with open(declaration_file, 'w', encoding='utf-8') as f:
                json.dump(declaration.to_dict(), f, indent=2, ensure_ascii=False)
            
            logger.debug(f"Declaration metadata saved for task {declaration.id}")
            
        except Exception as e:
            logger.error(f"Error saving declaration metadata for task {declaration.id}: {e}")
    
    def _load_existing_declarations(self) -> None:
        """
        Load existing task declarations from the outputs directory.
        This allows persistence of declarations between runs.
        """
        try:
            for task_dir in self.outputs_dir.iterdir():
                if task_dir.is_dir():
                    declaration_file = task_dir / "task_declaration.json"
                    if declaration_file.exists():
                        try:
                            with open(declaration_file, 'r', encoding='utf-8') as f:
                                declaration_data = json.load(f)
                            
                            # Convert dict back to TaskDeclaration object
                            declaration = TaskDeclaration.from_dict(declaration_data)
                            self.declared_tasks[declaration.id] = declaration
                            
                            logger.debug(f"Loaded existing declaration for task {declaration.id}")
                            
                        except Exception as e:
                            logger.warning(f"Failed to load declaration from {declaration_file}: {e}")
                            
        except Exception as e:
            logger.error(f"Error loading existing declarations: {e}")
    
    def get_tasks_ready_for_execution(self) -> List[TaskDeclaration]:
        """Get all tasks that are ready for execution"""
        ready_tasks = [
            declaration for declaration in self.declared_tasks.values()
            if declaration.preparation_status == TaskPreparationStatus.READY_FOR_EXECUTION
        ]
        
        logger.info(f"Found {len(ready_tasks)} tasks ready for execution")
        return ready_tasks
    
    def get_task_declaration(self, task_id: str) -> Optional[TaskDeclaration]:
        """Get task declaration by ID"""
        return self.declared_tasks.get(task_id)
    
    def declare_all_tasks(self) -> Dict[str, TaskDeclaration]:
        """Declare all available tasks"""
        logger.info("Declaring all available tasks")
        
        all_task_ids = get_all_tasks()
        declared_count = 0
        
        for task_id in all_task_ids:
            try:
                self.declare_task(task_id)
                declared_count += 1
            except Exception as e:
                logger.error(f"Failed to declare task {task_id}: {e}")
        
        logger.info(f"Declared {declared_count} out of {len(all_task_ids)} tasks")
        return self.declared_tasks

    def prepare_all_tasks(self) -> Dict[str, TaskDeclaration]:
        """Prepare all declared tasks for execution"""
        logger.info("Preparing all declared tasks for execution")
        
        if not self.declared_tasks:
            self.declare_all_tasks()
        
        prepared_count = 0
        
        for task_id in self.declared_tasks.keys():
            try:
                self.prepare_task_for_execution(task_id)
                if self.declared_tasks[task_id].preparation_status == TaskPreparationStatus.READY_FOR_EXECUTION:
                    prepared_count += 1
            except Exception as e:
                logger.error(f"Failed to prepare task {task_id}: {e}")
        
        logger.info(f"Prepared {prepared_count} out of {len(self.declared_tasks)} tasks")
        return self.declared_tasks

    def get_preparation_summary(self) -> Dict[str, Any]:
        """Get summary of task preparation status"""
        if not self.declared_tasks:
            return {
                "total_tasks": 0, 
                "summary": "No tasks declared",
                "status_breakdown": {},
                "ready_for_execution": 0,
                "failed_preparation": 0
            }
        
        status_counts = {}
        for declaration in self.declared_tasks.values():
            status = declaration.preparation_status
            status_counts[status] = status_counts.get(status, 0) + 1
        
        return {
            "total_tasks": len(self.declared_tasks),
            "status_breakdown": status_counts,
            "ready_for_execution": status_counts.get(TaskPreparationStatus.READY_FOR_EXECUTION, 0),
            "failed_preparation": status_counts.get(TaskPreparationStatus.FAILED, 0)
        }


def main():
    """Command-line interface for task declaration and preparation"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Step 4.1 - Task Declaration & Preparation")
    parser.add_argument("command", choices=["declare", "prepare", "summary", "all"], 
                       help="Command to execute")
    parser.add_argument("--task-id", "-t", help="Specific task ID to process")
    parser.add_argument("--output-dir", "-o", help="Output directory for task preparations")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    
    args = parser.parse_args()
    
    # Set up logging
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(level=log_level, format='%(asctime)s - %(levelname)s - %(message)s')
    
    # Initialize manager
    manager = TaskDeclarationManager()
    
    try:
        if args.command == "declare":
            if args.task_id:
                declaration = manager.declare_task(args.task_id)
                print(f"✅ Task {args.task_id} declared successfully")
                print(f"   Title: {declaration.title}")
                print(f"   Owner: {declaration.owner}")
                print(f"   State: {declaration.state}")
            else:
                declarations = manager.declare_all_tasks()
                print(f"✅ Declared {len(declarations)} tasks")
        
        elif args.command == "prepare":
            if args.task_id:
                declaration = manager.prepare_task_for_execution(args.task_id)
                print(f"✅ Task {args.task_id} prepared with status: {declaration.preparation_status}")
                if declaration.preparation_status == TaskPreparationStatus.READY_FOR_EXECUTION:
                    print("   Task is ready for LangGraph execution")
                else:
                    print("   Task preparation failed or incomplete")
            else:
                declarations = manager.prepare_all_tasks()
                ready_count = sum(1 for d in declarations.values() 
                                if d.preparation_status == TaskPreparationStatus.READY_FOR_EXECUTION)
                print(f"✅ Prepared {len(declarations)} tasks, {ready_count} ready for execution")
        
        elif args.command == "summary":
            summary = manager.get_preparation_summary()
            print("📊 Task Preparation Summary:")
            print(f"   Total tasks: {summary['total_tasks']}")
            print(f"   Ready for execution: {summary['ready_for_execution']}")
            print(f"   Failed preparation: {summary['failed_preparation']}")
            
            if "status_breakdown" in summary:
                print("   Status breakdown:")
                for status, count in summary["status_breakdown"].items():
                    print(f"     {status}: {count}")
        
        elif args.command == "all":
            print("🚀 Running complete task declaration and preparation workflow...")
            
            # Declare all tasks
            declarations = manager.declare_all_tasks()
            print(f"📝 Declared {len(declarations)} tasks")
            
            # Prepare all tasks
            prepared = manager.prepare_all_tasks()
            ready_count = sum(1 for d in prepared.values() 
                            if d.preparation_status == TaskPreparationStatus.READY_FOR_EXECUTION)
            print(f"⚙️  Prepared {len(prepared)} tasks")
            print(f"✅ {ready_count} tasks ready for LangGraph execution")
            
            # Show summary
            summary = manager.get_preparation_summary()
            print("\n📊 Final Summary:")
            for status, count in summary["status_breakdown"].items():
                print(f"   {status}: {count}")
    
    except Exception as e:
        logger.error(f"Error in task declaration workflow: {e}")
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
