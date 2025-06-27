"""Graph builder utilities."""

class GraphBuilder:
    """Build graphs for workflows."""
    
    def __init__(self):
        """Initialize graph builder."""
        self.graph = {"nodes": [], "edges": []}
    
    def add_node(self, node_id, label, **kwargs):
        """Add a node to the graph."""
        node = {"id": node_id, "label": label, **kwargs}
        self.graph["nodes"].append(node)
        return node
    
    def add_edge(self, from_node, to_node, **kwargs):
        """Add an edge to the graph."""
        edge = {"from": from_node, "to": to_node, **kwargs}
        self.graph["edges"].append(edge)
        return edge
    
    def build(self):
        """Build and return the graph."""
        return self.graph

def build_advanced_workflow_graph(tasks, dependencies=None, config=None):
    """Build an advanced workflow graph with sophisticated dependency resolution.
    
    Args:
        tasks: List of tasks to include in the workflow
        dependencies: Dict of task dependencies
        config: Optional configuration for graph building
        
    Returns:
        Dict: Built workflow graph
    """
    builder = GraphBuilder()
    dependencies = dependencies or {}
    config = config or {}
    
    # Add nodes for each task
    for task in tasks:
        task_id = task.get('id', str(task))
        task_label = task.get('title', task_id)
        
        # Add task node with metadata
        builder.add_node(
            task_id, 
            task_label,
            type='task',
            status=task.get('status', 'pending'),
            priority=task.get('priority', 'medium'),
            estimated_duration=task.get('estimated_duration'),
            agent=task.get('agent'),
            metadata=task.get('metadata', {})
        )
    
    # Add dependency edges
    for task_id, deps in dependencies.items():
        if isinstance(deps, list):
            for dep_id in deps:
                builder.add_edge(dep_id, task_id, type='dependency')
        elif isinstance(deps, str):
            builder.add_edge(deps, task_id, type='dependency')
    
    # Add conditional edges based on task status
    for task in tasks:
        task_id = task.get('id', str(task))
        
        # Add error handling edges
        if config.get('add_error_handling', True):
            builder.add_edge(task_id, f"{task_id}_error_handler", type='error')
        
        # Add success edges
        if config.get('add_success_paths', True):
            builder.add_edge(task_id, f"{task_id}_success", type='success')
    
    return builder.build()

def build_dynamic_workflow_graph(tasks, config=None):
    """Build a dynamic workflow graph that can adapt at runtime.
    
    Args:
        tasks: List of tasks
        config: Optional configuration
        
    Returns:
        Dict: Built dynamic workflow graph
    """
    builder = GraphBuilder()
    config = config or {}
    
    for task in tasks:
        task_id = task.get('id', str(task))
        builder.add_node(
            task_id,
            task.get('title', task_id),
            type='dynamic_task',
            adaptable=True,
            runtime_config=task.get('runtime_config', {})
        )
    
    return builder.build()

def build_state_workflow_graph(tasks, states=None, config=None):
    """Build a state-based workflow graph.
    
    Args:
        tasks: List of tasks
        states: Dict of state definitions
        config: Optional configuration
        
    Returns:
        Dict: Built state workflow graph
    """
    builder = GraphBuilder()
    states = states or {}
    config = config or {}
    
    # Add state nodes
    for state_name, state_config in states.items():
        builder.add_node(
            state_name,
            state_config.get('label', state_name),
            type='state',
            transitions=state_config.get('transitions', []),
            actions=state_config.get('actions', [])
        )
    
    # Add task nodes
    for task in tasks:
        task_id = task.get('id', str(task))
        builder.add_node(
            task_id,
            task.get('title', task_id),
            type='task',
            initial_state=task.get('initial_state', 'pending'),
            valid_states=task.get('valid_states', ['pending', 'running', 'completed', 'failed'])
        )
    
    return builder.build()

def build_workflow_graph(tasks, config=None):
    """Build a basic workflow graph.
    
    Args:
        tasks: List of tasks
        config: Optional configuration
        
    Returns:
        Dict: Built workflow graph
    """
    builder = GraphBuilder()
    config = config or {}
    
    for task in tasks:
        task_id = task.get('id', str(task))
        builder.add_node(
            task_id,
            task.get('title', task_id),
            type='basic_task'
        )
    
    return builder.build()

__all__ = [
    "GraphBuilder", 
    "build_advanced_workflow_graph", 
    "build_dynamic_workflow_graph", 
    "build_state_workflow_graph", 
    "build_workflow_graph"
]
