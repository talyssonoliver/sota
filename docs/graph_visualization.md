# Graph Visualization

This document describes the graph visualization components of the AI Agent System, which enable visual representation of agent-to-agent task flows.

## Overview

The graph visualization system provides tools and formats to visually represent the relationships and task flows between agents in the system. These visualizations help understand dependency chains, critical paths, and orchestrated execution sequences.

## Visualization Formats

### Mermaid Diagram Format

The system uses Mermaid, a Markdown-based diagramming and charting tool, to create visual representations of agent workflows. Mermaid diagrams are:

- Markdown-compatible
- Human-readable in source form
- Renderable in GitHub, documentation platforms, and browsers
- Easy to modify and maintain

### Implementation Files

The graph visualization implementation consists of several key files:

1. **`graph/critical_path.mmd`**: Mermaid source for the agent workflow diagram
2. **`graph/critical_path.html`**: HTML page for browser-based rendering
3. **`graph/visualize.py`**: Python utility for programmatic graph visualization
4. **`graph/critical_path.json`**: Data representation of the workflow (used by LangGraph)
5. **`graph/critical_path.yaml`**: YAML configuration for the workflow

## Mermaid Diagram (`graph/critical_path.mmd`)

The primary visualization is defined in a Mermaid diagram file:

```mermaid
graph TD;
    %% Define main agent nodes
    CO[Coordinator Agent]
    TA[Technical Architect Agent]
    BA[Backend Agent]
    QA[QA Agent]
    DOC[Documentation Agent]
    FE[Frontend Agent]
    
    %% Define the critical path flow
    CO --> TA
    TA --> BA
    BA --> QA
    QA -->|passed| DOC
    QA -->|failed| CO
    CO --> FE
    
    %% Node styling
    classDef coordinator fill:#f96,stroke:#333,stroke-width:2px;
    classDef agent fill:#bbf,stroke:#333,stroke-width:1px;
    classDef conditional stroke:#f66,stroke-width:1.5px,stroke-dasharray: 5 5;
    
    %% Apply styling
    class CO coordinator;
    class TA,BA,QA,DOC,FE agent;
    class QA-->CO conditional;
```

The diagram shows the critical path of task flow between agents, including:
- Agent nodes with their roles
- Directional edges showing task flow
- Conditional edges (like QA passing or failing)
- Visual styling to distinguish different agent types and edge conditions

## HTML Rendering (`graph/critical_path.html`)

For browser-based rendering, an HTML file is provided that includes the Mermaid diagram with proper rendering support:

```html
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>Task Flow Diagram</title>
  <script type="module">
    import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.esm.min.mjs';
    mermaid.initialize({ startOnLoad: true });
  </script>
</head>
<body>
  <h2>Critical Path Workflow</h2>
  <div class="mermaid">
    graph TD
      CO[Coordinator Agent] --> TA[Technical Architect Agent]
      TA --> BA[Backend Agent]
      BA --> QA[QA Agent]
      QA -->|passed| DOC[Documentation Agent]
      QA -->|failed| CO
      CO --> FE[Frontend Agent]
      
      %% Node styling
      classDef coordinator fill:#f96,stroke:#333,stroke-width:2px;
      classDef agent fill:#bbf,stroke:#333,stroke-width:1px;
      classDef conditional stroke:#f66,stroke-width:1.5px,stroke-dasharray: 5 5;
      
      %% Apply styling
      class CO coordinator;
      class TA,BA,QA,DOC,FE agent;
      class QA-->CO conditional;
  </div>
</body>
</html>
```

This file can be opened in any modern browser to visualize the workflow diagram.

## Visualization Utility (`graph/visualize.py`)

For programmatic visualization of LangGraph workflows, a Python utility is provided:

```python
def visualize_workflow(output_path: str = "graph/critical_path_output.html", workflow_type: str = "basic"):
    """
    Generate an HTML visualization of the specified workflow type.
    
    Args:
        output_path: Path where the visualization should be saved
        workflow_type: Type of workflow to visualize ('basic', 'state', 'advanced', or 'dynamic')
    
    Returns:
        Path to the generated visualization file
    """
    # Create directory if it doesn't exist
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # Build the requested workflow type
    if workflow_type == "basic":
        workflow = build_workflow_graph()
    elif workflow_type == "state":
        workflow = build_state_workflow_graph()
    elif workflow_type == "advanced":
        workflow = build_advanced_workflow_graph()
    elif workflow_type == "dynamic":
        workflow = build_dynamic_workflow_graph()
    else:
        raise ValueError(f"Unknown workflow type: {workflow_type}")
    
    # Generate visualization
    workflow.visualize(output_path)
    return output_path
```

This utility uses LangGraph's built-in visualization capabilities to generate HTML diagrams of any workflow type.

## Usage

### Viewing Mermaid Diagrams

1. **In GitHub**: The `.mmd` files are automatically rendered in GitHub markdown files and repositories.

2. **In Documentation**: Include the Mermaid code in markdown documentation with triple-backtick fencing:
   ```markdown
   ```mermaid
   graph TD;
       CO[Coordinator Agent] --> TA[Technical Architect Agent]
       // ...rest of diagram
   ```
   ```

3. **In Browser**: Open the `critical_path.html` file in any modern browser.

### Programmatic Visualization

Use the Python utility to generate visualizations programmatically:

```bash
# Generate a visualization of the basic workflow
python graph/visualize.py

# Generate a visualization of the advanced workflow
python graph/visualize.py --type advanced

# Specify a custom output path
python graph/visualize.py --output docs/workflow.html
```

### From Python Code

```python
from graph.visualize import visualize_workflow

# Generate visualization of the advanced workflow
visualize_workflow(
    output_path="docs/advanced_workflow.html", 
    workflow_type="advanced"
)
```

## Diagram Types

The visualization system supports different diagram types based on the workflow being visualized:

### Basic Workflow

Shows a simple linear flow between agents without conditions:

```
Coordinator → Technical → Backend → QA → Documentation
```

### Advanced Workflow

Shows the full agent flow with conditional paths based on task outcomes:

```
Coordinator → Technical → Backend → QA → Documentation
     ↑                              |
     └──────────────────────────────┘
               (if failed)
```

### State-Based Workflow

Visualizes transitions between task states rather than agents:

```
CREATED → PLANNED → IN_PROGRESS → QA_PENDING → DOCUMENTATION → DONE
                                       |
                                       v
                                    BLOCKED
```

### Dynamic Workflow

Represents a workflow with dynamic routing based on task characteristics:

```
Coordinator → [Dynamic Router] → Appropriate Agent
```

## Integration with LangGraph

The visualizations are designed to match the actual execution flow defined in the LangGraph workflow. This ensures that the diagrams accurately represent the system's behavior.

```python
# In LangGraph workflow definition
builder = StateGraphBuilder()
builder.add_node("coordinator", coordinator_handler)
builder.add_node("technical", technical_handler)
builder.add_node("backend", backend_handler)
builder.add_node("qa", qa_handler)
builder.add_node("documentation", documentation_handler)

# Add edges matching the visualization
builder.add_edge("coordinator", "technical")
builder.add_edge("technical", "backend")
builder.add_edge("backend", "qa")
builder.add_conditional_edges(
    "qa",
    lambda state: "documentation" if state["status"] == "QA_PENDING" else "coordinator"
)
builder.add_edge("documentation", END)
```

## Benefits

- **Visual Documentation**: Clear visualization of complex agent interactions
- **Debugging Aid**: Helps identify issues in workflow design
- **Communication Tool**: Simplifies explaining system structure to new team members
- **Planning Support**: Assists in planning modifications to the agent system
- **Execution Tracking**: Can be enhanced to show active nodes during execution
- **Human Review**: Helps identify critical checkpoints for human review

## Best Practices

1. **Keep Diagrams Updated**: Ensure diagrams match actual workflow implementation
2. **Use Conditional Edges**: Show different paths based on execution outcomes
3. **Consistent Styling**: Use consistent node and edge styles for better readability
4. **Add Comments**: Include comments in the Mermaid source for clarity
5. **Include in Documentation**: Embed diagrams in relevant documentation files
6. **Generate Programmatically**: When possible, generate diagrams from actual workflow code
7. **Use Multiple Views**: Create different diagrams to show different aspects of the system

## Future Enhancements

- **Live Visualization**: Show the active state during workflow execution
- **Interactive Diagrams**: Add interactive elements for exploring the workflow
- **Metrics Integration**: Visualize performance metrics and bottlenecks
- **Task Dependency View**: Create diagrams showing task-level dependencies
- **Timeline View**: Show expected execution sequence with timing information