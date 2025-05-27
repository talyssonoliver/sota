"""
Workflow Visualization Utility
Generates visual representations of the LangGraph workflow.
"""

import os
import sys
from pathlib import Path

from graph.graph_builder import (build_advanced_workflow_graph,
                                 build_dynamic_workflow_graph,
                                 build_state_workflow_graph,
                                 build_workflow_graph)

# Add parent directory to path to allow imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def visualize_workflow(
        output_path: str = "graph/critical_path_output.html",
        workflow_type: str = "basic"):
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
        print(f"Building basic workflow graph...")
        workflow = build_workflow_graph()
    elif workflow_type == "state":
        print(f"Building stateful workflow graph...")
        workflow = build_state_workflow_graph()
    elif workflow_type == "advanced":
        print(f"Building advanced workflow graph...")
        workflow = build_advanced_workflow_graph()
    elif workflow_type == "dynamic":
        print(f"Building dynamic workflow graph...")
        workflow = build_dynamic_workflow_graph()
    else:
        raise ValueError(f"Unknown workflow type: {workflow_type}")

    # Generate visualization
    print(f"Generating visualization at {output_path}...")
    try:
        workflow.visualize(output_path)
        print(f"Visualization saved to {output_path}")
        return output_path
    except Exception as e:
        print(f"Error generating visualization: {str(e)}")
        raise


def main():
    """Command-line interface for generating workflow visualizations."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Generate workflow visualizations")

    parser.add_argument(
        "--output",
        "-o",
        default="graph/critical_path_output.html",
        help="Output path for the visualization")
    parser.add_argument("--type", "-t", default="basic",
                        choices=["basic", "state", "advanced", "dynamic"],
                        help="Type of workflow to visualize")

    args = parser.parse_args()

    try:
        visualize_workflow(args.output, args.type)
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
