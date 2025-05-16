"""
Task Graph Visualization
Generates visual representation of tasks and their dependencies.
"""

import os
import sys
import argparse
import yaml
import json
from pathlib import Path
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
import numpy as np
from collections import defaultdict

# Add parent directory to path to allow imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from orchestration.states import TaskStatus

def load_all_tasks(tasks_dir):
    """
    Load all task YAML files from the tasks directory.
    
    Args:
        tasks_dir: Directory containing task YAML files
        
    Returns:
        Dictionary of task data by task ID
    """
    tasks = {}
    
    # Ensure tasks_dir is a Path object
    tasks_dir = Path(tasks_dir)
    
    # Find all YAML files in the tasks directory
    for yaml_file in tasks_dir.glob("*.yaml"):
        try:
            with open(yaml_file, 'r') as f:
                task_data = yaml.safe_load(f)
                
                # Ensure this is a task with an ID
                if task_data and "id" in task_data:
                    tasks[task_data["id"]] = task_data
        except Exception as e:
            print(f"Error loading task file {yaml_file}: {str(e)}")
    
    return tasks

def build_dependency_graph(tasks):
    """
    Build a NetworkX graph from task dependencies.
    
    Args:
        tasks: Dictionary of task data by task ID
        
    Returns:
        NetworkX directed graph
    """
    # Create a directed graph
    G = nx.DiGraph()
    
    # Add nodes for all tasks
    for task_id, task_data in tasks.items():
        G.add_node(task_id, **task_data)
    
    # Add edges for dependencies
    for task_id, task_data in tasks.items():
        if "depends_on" in task_data and task_data["depends_on"]:
            for dependency in task_data["depends_on"]:
                # Only add edge if the dependency exists
                if dependency in tasks:
                    G.add_edge(dependency, task_id)
    
    return G

def get_task_status_color(status):
    """
    Get color for a task status.
    
    Args:
        status: Task status
        
    Returns:
        Color string
    """
    status_colors = {
        TaskStatus.CREATED: "lightskyblue",
        TaskStatus.PLANNED: "lightblue",
        TaskStatus.IN_PROGRESS: "orange",
        TaskStatus.QA_PENDING: "yellow",
        TaskStatus.DOCUMENTATION: "lightgreen",
        TaskStatus.HUMAN_REVIEW: "purple",
        TaskStatus.DONE: "green",
        TaskStatus.BLOCKED: "red"
    }
    
    return status_colors.get(status, "gray")

def get_owner_color(owner):
    """
    Get color for a task owner.
    
    Args:
        owner: Task owner
        
    Returns:
        Color string
    """
    owner_colors = {
        "backend": "lightcoral",
        "frontend": "lightskyblue",
        "qa": "lightgreen",
        "ux": "mediumpurple",
        "technical": "orange",
        "product": "pink",
        "documentation": "lightgray",
        "coordinator": "yellow"
    }
    
    return owner_colors.get(owner, "lightgray")

def visualize_task_graph(graph, output_file, color_by="status", layout="spring"):
    """
    Visualize the task dependency graph.
    
    Args:
        graph: NetworkX directed graph
        output_file: File to save the visualization
        color_by: Property to color nodes by (status or owner)
        layout: Graph layout algorithm
    """
    plt.figure(figsize=(20, 16))
    
    # Choose layout
    if layout == "spring":
        pos = nx.spring_layout(graph, k=0.5, iterations=50)
    elif layout == "spectral":
        pos = nx.spectral_layout(graph)
    elif layout == "kamada_kawai":
        pos = nx.kamada_kawai_layout(graph)
    elif layout == "planar":
        try:
            pos = nx.planar_layout(graph)
        except nx.exception.NetworkXException:
            print("Warning: Graph is not planar, falling back to spring layout")
            pos = nx.spring_layout(graph, k=0.5, iterations=50)
    elif layout == "circular":
        pos = nx.circular_layout(graph)
    else:
        pos = nx.spring_layout(graph, k=0.5, iterations=50)
    
    # Organize nodes by owner
    nodes_by_owner = defaultdict(list)
    for node, data in graph.nodes(data=True):
        owner = data.get("owner", "unknown")
        nodes_by_owner[owner].append(node)
    
    # Draw nodes with colors based on status or owner
    for node, data in graph.nodes(data=True):
        if color_by == "status":
            status = data.get("state", "UNKNOWN")
            node_color = get_task_status_color(status)
        else:  # color_by == "owner"
            owner = data.get("owner", "unknown")
            node_color = get_owner_color(owner)
        
        # Calculate node size based on priority
        priority = data.get("priority", "MEDIUM")
        if priority == "HIGH":
            size = 1200
        elif priority == "MEDIUM":
            size = 800
        else:  # LOW
            size = 500
        
        nx.draw_networkx_nodes(
            graph, pos, nodelist=[node], 
            node_color=node_color, 
            node_size=size,
            alpha=0.8
        )
    
    # Draw edges
    nx.draw_networkx_edges(
        graph, pos, 
        arrows=True, 
        edge_color="gray", 
        width=1.0, 
        alpha=0.5
    )
    
    # Draw node labels
    nx.draw_networkx_labels(
        graph, pos, 
        font_size=10, 
        font_family="sans-serif"
    )
    
    # Create legend for status or owner
    if color_by == "status":
        status_handles = []
        for status, color in {
            TaskStatus.CREATED: "lightskyblue",
            TaskStatus.PLANNED: "lightblue",
            TaskStatus.IN_PROGRESS: "orange",
            TaskStatus.QA_PENDING: "yellow",
            TaskStatus.DOCUMENTATION: "lightgreen",
            TaskStatus.HUMAN_REVIEW: "purple",
            TaskStatus.DONE: "green",
            TaskStatus.BLOCKED: "red"
        }.items():
            status_handles.append(plt.Line2D([0], [0], marker='o', color='w', 
                                         markerfacecolor=color, markersize=15, 
                                         label=status))
        plt.legend(handles=status_handles, title="Task Status", loc="upper right")
    else:  # color_by == "owner"
        owner_handles = []
        for owner, color in {
            "backend": "lightcoral",
            "frontend": "lightskyblue",
            "qa": "lightgreen",
            "ux": "mediumpurple",
            "technical": "orange",
            "product": "pink",
            "documentation": "lightgray",
            "coordinator": "yellow"
        }.items():
            owner_handles.append(plt.Line2D([0], [0], marker='o', color='w', 
                                         markerfacecolor=color, markersize=15, 
                                         label=owner))
        plt.legend(handles=owner_handles, title="Task Owner", loc="upper right")
    
    # Add priority legend
    priority_handles = [
        plt.Line2D([0], [0], marker='o', color='w', 
                  markerfacecolor='gray', markersize=15, 
                  label="HIGH"),
        plt.Line2D([0], [0], marker='o', color='w', 
                  markerfacecolor='gray', markersize=12, 
                  label="MEDIUM"),
        plt.Line2D([0], [0], marker='o', color='w', 
                  markerfacecolor='gray', markersize=10, 
                  label="LOW")
    ]
    plt.legend(handles=priority_handles, title="Priority", loc="upper left")
    
    plt.title(f"Task Dependency Graph (colored by {color_by})")
    plt.axis('off')
    
    # Save the figure
    plt.tight_layout()
    plt.savefig(output_file)
    plt.close()
    
    print(f"Task graph saved to {output_file}")

def analyze_graph_metrics(graph):
    """
    Analyze graph metrics.
    
    Args:
        graph: NetworkX directed graph
        
    Returns:
        Dictionary of graph metrics
    """
    metrics = {}
    
    # Basic metrics
    metrics["num_tasks"] = graph.number_of_nodes()
    metrics["num_dependencies"] = graph.number_of_edges()
    
    # Calculate in-degree and out-degree for each node
    in_degrees = dict(graph.in_degree())
    out_degrees = dict(graph.out_degree())
    
    # Find tasks with most dependencies and dependents
    max_in_degree = max(in_degrees.items(), key=lambda x: x[1]) if in_degrees else ("None", 0)
    max_out_degree = max(out_degrees.items(), key=lambda x: x[1]) if out_degrees else ("None", 0)
    
    metrics["most_dependent_task"] = max_in_degree[0]
    metrics["most_dependent_count"] = max_in_degree[1]
    metrics["most_dependents_task"] = max_out_degree[0]
    metrics["most_dependents_count"] = max_out_degree[1]
    
    # Calculate average number of dependencies
    metrics["avg_dependencies"] = sum(in_degrees.values()) / len(in_degrees) if in_degrees else 0
    
    # Check if the graph is acyclic
    metrics["is_acyclic"] = nx.is_directed_acyclic_graph(graph)
    
    # Find nodes without dependencies (root tasks)
    metrics["root_tasks"] = [node for node, in_degree in in_degrees.items() if in_degree == 0]
    
    # Find nodes without dependents (leaf tasks)
    metrics["leaf_tasks"] = [node for node, out_degree in out_degrees.items() if out_degree == 0]
    
    # Calculate longest path
    if metrics["is_acyclic"]:
        try:
            metrics["critical_path"] = nx.dag_longest_path(graph)
            metrics["critical_path_length"] = len(metrics["critical_path"]) - 1
        except:
            metrics["critical_path"] = []
            metrics["critical_path_length"] = 0
    else:
        metrics["critical_path"] = []
        metrics["critical_path_length"] = 0
    
    # Calculate connected components
    metrics["connected_components"] = list(nx.weakly_connected_components(graph))
    metrics["num_connected_components"] = len(metrics["connected_components"])
    
    return metrics

def print_metrics(metrics):
    """
    Print graph metrics in a readable format.
    
    Args:
        metrics: Dictionary of graph metrics
    """
    print("\n===== Task Graph Analysis =====")
    print(f"Number of tasks: {metrics['num_tasks']}")
    print(f"Number of dependencies: {metrics['num_dependencies']}")
    print(f"Average dependencies per task: {metrics['avg_dependencies']:.2f}")
    print(f"Is acyclic: {metrics['is_acyclic']}")
    print(f"Number of connected components: {metrics['num_connected_components']}")
    
    print(f"\nTask with most dependencies: {metrics['most_dependent_task']} ({metrics['most_dependent_count']} dependencies)")
    print(f"Task with most dependents: {metrics['most_dependents_task']} ({metrics['most_dependents_count']} dependents)")
    
    print(f"\nRoot tasks (no dependencies): {', '.join(metrics['root_tasks'])}")
    print(f"\nLeaf tasks (no dependents): {', '.join(metrics['leaf_tasks'])}")
    
    print("\nCritical Path:")
    if metrics["critical_path"]:
        print(" -> ".join(metrics["critical_path"]))
        print(f"Length: {metrics['critical_path_length']}")
    else:
        print("No critical path found (graph may contain cycles)")

def main():
    """
    Main function to visualize task dependencies.
    """
    parser = argparse.ArgumentParser(description="Visualize task dependencies")
    parser.add_argument("--tasks-dir", default="tasks", help="Directory containing task YAML files")
    parser.add_argument("--output", default="reports/task_graph.png", help="Output file path")
    parser.add_argument("--color-by", choices=["status", "owner"], default="status", help="Property to color nodes by")
    parser.add_argument("--layout", choices=["spring", "spectral", "kamada_kawai", "planar", "circular"], 
                       default="spring", help="Graph layout algorithm")
    parser.add_argument("--metrics", action="store_true", help="Print graph metrics")
    
    args = parser.parse_args()
    
    # Get the absolute path of the tasks directory
    if not os.path.isabs(args.tasks_dir):
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        tasks_dir = os.path.join(base_dir, args.tasks_dir)
    else:
        tasks_dir = args.tasks_dir
    
    # Get the absolute path of the output file
    if not os.path.isabs(args.output):
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        output_file = os.path.join(base_dir, args.output)
    else:
        output_file = args.output
    
    # Ensure output directory exists
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    # Load tasks
    print(f"Loading tasks from {tasks_dir}...")
    tasks = load_all_tasks(tasks_dir)
    print(f"Loaded {len(tasks)} tasks")
    
    # Build dependency graph
    print("Building dependency graph...")
    graph = build_dependency_graph(tasks)
    print(f"Built graph with {graph.number_of_nodes()} nodes and {graph.number_of_edges()} edges")
    
    # Analyze graph metrics
    if args.metrics:
        metrics = analyze_graph_metrics(graph)
        print_metrics(metrics)
    
    # Visualize graph
    print(f"Visualizing graph (colored by {args.color_by}, layout: {args.layout})...")
    visualize_task_graph(graph, output_file, args.color_by, args.layout)

if __name__ == "__main__":
    main()