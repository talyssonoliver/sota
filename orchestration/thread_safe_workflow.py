"""
Thread-Safe Workflow Orchestration
Provides thread-safe mechanisms for parallel agent execution and workflow management.
"""
from concurrent.futures import ThreadPoolExecutor, as_completed, Future
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Set, Union
from .error_handling import ErrorPropagationManager, handle_task_error
import threading
import queue
import time
from .states import TaskStatus
import logging

logger = logging.getLogger(__name__)

class WorkflowPriority(str, Enum):
    """Workflow execution priority levels"""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class TaskExecution:
    """Thread-safe task execution context"""
    task_id: str
    agent_type: str
    execution_function: Callable
    priority: WorkflowPriority = WorkflowPriority.NORMAL
    dependencies: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    # Execution state
    status: TaskStatus = TaskStatus.CREATED
    thread_id: Optional[int] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    result: Any = None
    error: Optional[Exception] = None
    retry_count: int = 0
    
    # Thread synchronization
    completion_event: threading.Event = field(default_factory=threading.Event)
    lock: threading.RLock = field(default_factory=threading.RLock)

class ThreadSafeWorkflowOrchestrator:
    """
    Thread-safe workflow orchestrator for parallel agent execution.
    Manages dependencies, priorities, and error propagation across concurrent tasks.
    """
    
    def __init__(self, max_workers: int = None, enable_error_propagation: bool = True):
        """
        Initialize thread-safe workflow orchestrator.
        
        Args:
            max_workers: Maximum number of worker threads (None for auto)
            enable_error_propagation: Whether to enable error propagation system
        """
        self.max_workers = max_workers or min(32, (threading.active_count() or 1) + 4)
        self.enable_error_propagation = enable_error_propagation
        
        # Thread synchronization
        self._orchestrator_lock = threading.RLock()
        self._task_lock = threading.RLock()
        self._stats_lock = threading.RLock()
        self._dependency_lock = threading.RLock()
        
        # Task management
        self._tasks: Dict[str, TaskExecution] = {}
        self._dependency_graph: Dict[str, Set[str]] = {}
        self._reverse_dependencies: Dict[str, Set[str]] = {}
        self._ready_queue = queue.PriorityQueue()
        
        # Execution state
        self._executor: Optional[ThreadPoolExecutor] = None
        self._active_futures: Dict[str, Future] = {}
        self._workflow_active = False
        
        # Error handling
        if self.enable_error_propagation:
            self.error_manager = ErrorPropagationManager()
        
        # Statistics
        self._stats = {
            'total_tasks': 0,
            'completed_tasks': 0,
            'failed_tasks': 0,
            'active_tasks': 0,
            'max_concurrent': 0,
            'workflow_executions': 0
        }
        
        logger.info(f"ThreadSafeWorkflowOrchestrator initialized with {self.max_workers} workers")
    
    def add_task(self, task_id: str, agent_type: str, execution_function: Callable,
                 dependencies: Optional[List[str]] = None, 
                 priority: WorkflowPriority = WorkflowPriority.NORMAL,
                 metadata: Optional[Dict[str, Any]] = None) -> bool:
        """
        Add a task to the workflow (thread-safe).
        
        Args:
            task_id: Unique task identifier
            agent_type: Type of agent to execute the task
            execution_function: Function to execute for this task
            dependencies: List of task IDs this task depends on
            priority: Task execution priority
            metadata: Additional task metadata
            
        Returns:
            True if task was added successfully, False otherwise
        """
        with self._task_lock:
            if task_id in self._tasks:
                logger.warning(f"Task {task_id} already exists in workflow")
                return False
            
            # Create task execution context
            task = TaskExecution(
                task_id=task_id,
                agent_type=agent_type,
                execution_function=execution_function,
                dependencies=dependencies or [],
                priority=priority,
                metadata=metadata or {}
            )
            
            self._tasks[task_id] = task
            
            # Update dependency graph
            with self._dependency_lock:
                self._dependency_graph[task_id] = set(dependencies or [])
                
                # Update reverse dependencies
                for dep in dependencies or []:
                    if dep not in self._reverse_dependencies:
                        self._reverse_dependencies[dep] = set()
                    self._reverse_dependencies[dep].add(task_id)
            
            # Update statistics
            with self._stats_lock:
                self._stats['total_tasks'] += 1
            
            logger.debug(f"Task added to workflow: {task_id} (deps: {dependencies})")
            return True
    
    def execute_workflow(self, timeout: Optional[float] = None) -> Dict[str, Any]:
        """
        Execute the workflow with all added tasks (thread-safe).
        
        Args:
            timeout: Maximum time to wait for workflow completion
            
        Returns:
            Dictionary with execution results and statistics
        """
        with self._orchestrator_lock:
            if self._workflow_active:
                raise RuntimeError("Workflow is already executing")
            
            self._workflow_active = True
            start_time = datetime.now()
            
            try:
                # Update statistics
                with self._stats_lock:
                    self._stats['workflow_executions'] += 1
                
                # Initialize executor
                self._executor = ThreadPoolExecutor(max_workers=self.max_workers)
                
                # Validate dependencies
                if not self._validate_dependencies():
                    raise ValueError("Circular dependencies detected in workflow")
                
                # Queue ready tasks
                self._queue_ready_tasks()
                
                # Execute tasks
                self._execute_tasks_parallel()
                
                # Wait for completion
                self._wait_for_completion(timeout)
                
                # Collect results
                results = self._collect_results()
                
                execution_time = (datetime.now() - start_time).total_seconds()
                logger.info(f"Workflow completed in {execution_time:.2f}s")
                
                return {
                    'success': True,
                    'execution_time_seconds': execution_time,
                    'task_results': results,
                    'statistics': self.get_statistics()
                }
                
            except Exception as e:
                logger.error(f"Workflow execution failed: {e}")
                return {
                    'success': False,
                    'error': str(e),
                    'execution_time_seconds': (datetime.now() - start_time).total_seconds(),
                    'statistics': self.get_statistics()
                }
                
            finally:
                self._cleanup_execution()
                self._workflow_active = False
    
    def _validate_dependencies(self) -> bool:
        """Validate workflow for circular dependencies."""
        visited = set()
        rec_stack = set()
        
        def has_cycle(task_id: str) -> bool:
            if task_id in rec_stack:
                return True
            if task_id in visited:
                return False
            
            visited.add(task_id)
            rec_stack.add(task_id)
            
            for dependency in self._dependency_graph.get(task_id, []):
                if has_cycle(dependency):
                    return True
            
            rec_stack.remove(task_id)
            return False
        
        for task_id in self._tasks:
            if task_id not in visited:
                if has_cycle(task_id):
                    logger.error(f"Circular dependency detected involving task: {task_id}")
                    return False
        
        return True
    
    def _queue_ready_tasks(self):
        """Queue tasks that have no pending dependencies."""
        with self._dependency_lock:
            for task_id, task in self._tasks.items():
                if self._is_task_ready(task_id):
                    priority_value = self._get_priority_value(task.priority)
                    self._ready_queue.put((priority_value, task_id))
                    
                    with task.lock:
                        task.status = TaskStatus.PLANNED
    
    def _is_task_ready(self, task_id: str) -> bool:
        """Check if a task is ready for execution."""
        task = self._tasks[task_id]
        
        with task.lock:
            if task.status != TaskStatus.CREATED:
                return False
        
        # Check if all dependencies are completed
        for dep_id in self._dependency_graph.get(task_id, []):
            if dep_id not in self._tasks:
                logger.warning(f"Task {task_id} depends on non-existent task {dep_id}")
                return False
            
            dep_task = self._tasks[dep_id]
            with dep_task.lock:
                if dep_task.status not in [TaskStatus.COMPLETED, TaskStatus.DONE]:
                    return False
        
        return True
    
    def _get_priority_value(self, priority: WorkflowPriority) -> int:
        """Convert priority enum to numeric value (lower = higher priority)."""
        priority_map = {
            WorkflowPriority.CRITICAL: 0,
            WorkflowPriority.HIGH: 1,
            WorkflowPriority.NORMAL: 2,
            WorkflowPriority.LOW: 3
        }
        return priority_map.get(priority, 2)
    
    def _execute_tasks_parallel(self):
        """Execute tasks in parallel using thread pool."""
        while not self._ready_queue.empty() or self._active_futures:
            # Submit ready tasks
            while not self._ready_queue.empty():
                try:
                    priority, task_id = self._ready_queue.get_nowait()
                    if task_id not in self._active_futures:
                        future = self._executor.submit(self._execute_task, task_id)
                        self._active_futures[task_id] = future
                        
                        # Update statistics
                        with self._stats_lock:
                            self._stats['active_tasks'] += 1
                            self._stats['max_concurrent'] = max(
                                self._stats['max_concurrent'],
                                self._stats['active_tasks']
                            )
                        
                except queue.Empty:
                    break
            
            # Check for completed tasks
            completed_tasks = []
            for task_id, future in list(self._active_futures.items()):
                if future.done():
                    completed_tasks.append(task_id)
                    del self._active_futures[task_id]
                    
                    # Update statistics
                    with self._stats_lock:
                        self._stats['active_tasks'] -= 1
                        
                        if future.exception() is None:
                            self._stats['completed_tasks'] += 1
                        else:
                            self._stats['failed_tasks'] += 1
                    
                    # Queue newly ready tasks
                    self._queue_dependent_tasks(task_id)
            
            # Small delay to prevent busy waiting
            if not completed_tasks and self._active_futures:
                time.sleep(0.01)
    
    def _execute_task(self, task_id: str) -> Any:
        """Execute a single task in thread-safe manner."""
        task = self._tasks[task_id]
        
        with task.lock:
            task.status = TaskStatus.IN_PROGRESS
            task.thread_id = threading.get_ident()
            task.start_time = datetime.now()
        
        logger.debug(f"Executing task {task_id} in thread {task.thread_id}")
        
        try:
            # Execute the task function
            result = task.execution_function()
            
            with task.lock:
                task.result = result
                task.status = TaskStatus.COMPLETED
                task.end_time = datetime.now()
                task.completion_event.set()
            
            logger.debug(f"Task {task_id} completed successfully")
            return result
            
        except Exception as e:
            with task.lock:
                task.error = e
                task.status = TaskStatus.FAILED
                task.end_time = datetime.now()
                task.completion_event.set()
            
            # Handle error propagation
            if self.enable_error_propagation:
                error_context = handle_task_error(
                    e, task_id, task.agent_type, task.metadata
                )
                logger.error(f"Task {task_id} failed with error context: {error_context.error_id}")
            else:
                logger.error(f"Task {task_id} failed: {e}")
            
            raise
    
    def _queue_dependent_tasks(self, completed_task_id: str):
        """Queue tasks that were waiting for the completed task."""
        if completed_task_id not in self._reverse_dependencies:
            return
        
        for dependent_id in self._reverse_dependencies[completed_task_id]:
            if self._is_task_ready(dependent_id):
                task = self._tasks[dependent_id]
                priority_value = self._get_priority_value(task.priority)
                self._ready_queue.put((priority_value, dependent_id))
                
                with task.lock:
                    task.status = TaskStatus.PLANNED
    
    def _wait_for_completion(self, timeout: Optional[float] = None):
        """Wait for all tasks to complete."""
        start_time = time.time()
        
        while self._active_futures:
            if timeout and (time.time() - start_time) > timeout:
                logger.error(f"Workflow timeout after {timeout}s with {len(self._active_futures)} tasks still running")
                break
            
            time.sleep(0.1)
        
        # Wait for any remaining completion events
        for task in self._tasks.values():
            if not task.completion_event.wait(timeout=1.0):
                logger.warning(f"Task {task.task_id} completion event not set")
    
    def _collect_results(self) -> Dict[str, Any]:
        """Collect results from all executed tasks."""
        results = {}
        
        for task_id, task in self._tasks.items():
            with task.lock:
                execution_time = None
                if task.start_time and task.end_time:
                    execution_time = (task.end_time - task.start_time).total_seconds()
                
                results[task_id] = {
                    'status': task.status.value,
                    'agent_type': task.agent_type,
                    'thread_id': task.thread_id,
                    'execution_time_seconds': execution_time,
                    'result': task.result,
                    'error': str(task.error) if task.error else None,
                    'retry_count': task.retry_count,
                    'metadata': task.metadata
                }
        
        return results
    
    def _cleanup_execution(self):
        """Clean up execution resources."""
        if self._executor:
            self._executor.shutdown(wait=True)
            self._executor = None
        
        self._active_futures.clear()
        
        # Clear the ready queue
        while not self._ready_queue.empty():
            try:
                self._ready_queue.get_nowait()
            except queue.Empty:
                break
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get workflow execution statistics (thread-safe)."""
        with self._stats_lock:
            return {
                'total_tasks': self._stats['total_tasks'],
                'completed_tasks': self._stats['completed_tasks'],
                'failed_tasks': self._stats['failed_tasks'],
                'active_tasks': self._stats['active_tasks'],
                'success_rate': (
                    self._stats['completed_tasks'] / max(1, self._stats['total_tasks']) * 100
                ),
                'max_concurrent_tasks': self._stats['max_concurrent'],
                'workflow_executions': self._stats['workflow_executions'],
                'thread_safety_enabled': True,
                'max_workers': self.max_workers
            }
    
    def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get status of a specific task (thread-safe)."""
        if task_id not in self._tasks:
            return None
        
        task = self._tasks[task_id]
        with task.lock:
            return {
                'task_id': task_id,
                'status': task.status.value,
                'agent_type': task.agent_type,
                'thread_id': task.thread_id,
                'start_time': task.start_time.isoformat() if task.start_time else None,
                'end_time': task.end_time.isoformat() if task.end_time else None,
                'dependencies': list(self._dependency_graph.get(task_id, [])),
                'priority': task.priority.value,
                'retry_count': task.retry_count,
                'has_error': task.error is not None
            }
    
    def cancel_workflow(self):
        """Cancel workflow execution (thread-safe)."""
        with self._orchestrator_lock:
            if not self._workflow_active:
                return
            
            logger.info("Cancelling workflow execution")
            
            # Cancel all active futures
            for future in self._active_futures.values():
                future.cancel()
            
            # Set all pending tasks to cancelled
            for task in self._tasks.values():
                with task.lock:
                    if task.status in [TaskStatus.CREATED, TaskStatus.PLANNED, TaskStatus.IN_PROGRESS]:
                        task.status = TaskStatus.FAILED
                        task.error = Exception("Workflow cancelled")
                        task.completion_event.set()
            
            self._cleanup_execution()
            self._workflow_active = False
    
    def reset(self):
        """Reset orchestrator state (thread-safe)."""
        with self._orchestrator_lock:
            if self._workflow_active:
                self.cancel_workflow()
            
            with self._task_lock:
                self._tasks.clear()
            
            with self._dependency_lock:
                self._dependency_graph.clear()
                self._reverse_dependencies.clear()
            
            with self._stats_lock:
                self._stats = {
                    'total_tasks': 0,
                    'completed_tasks': 0,
                    'failed_tasks': 0,
                    'active_tasks': 0,
                    'max_concurrent': 0,
                    'workflow_executions': 0
                }
            
            logger.info("Workflow orchestrator reset")

def create_thread_safe_workflow(max_workers: int = None, 
                               enable_error_propagation: bool = True) -> ThreadSafeWorkflowOrchestrator:
    """
    Create a new thread-safe workflow orchestrator.
    
    Args:
        max_workers: Maximum number of worker threads
        enable_error_propagation: Whether to enable error propagation system
        
    Returns:
        Configured thread-safe workflow orchestrator
    """
    return ThreadSafeWorkflowOrchestrator(max_workers, enable_error_propagation)

def execute_tasks_parallel(tasks: List[Dict[str, Any]], 
                          max_workers: int = None,
                          timeout: Optional[float] = None) -> Dict[str, Any]:
    """
    Convenience function to execute multiple tasks in parallel.
    
    Args:
        tasks: List of task dictionaries with 'id', 'agent_type', 'function', etc.
        max_workers: Maximum number of worker threads
        timeout: Maximum execution time
        
    Returns:
        Execution results dictionary
    """
    orchestrator = create_thread_safe_workflow(max_workers)
    
    # Add all tasks
    for task_info in tasks:
        orchestrator.add_task(
            task_id=task_info['id'],
            agent_type=task_info['agent_type'],
            execution_function=task_info['function'],
            dependencies=task_info.get('dependencies', []),
            priority=WorkflowPriority(task_info.get('priority', 'normal')),
            metadata=task_info.get('metadata', {})
        )
    
    # Execute workflow
    return orchestrator.execute_workflow(timeout)