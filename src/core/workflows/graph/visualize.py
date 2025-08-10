
from src.infrastructure.utils.common_imports import os, sys
"""
Workflow Visualization Utility
Generates visual representations of the LangGraph workflow.
"""

import argparse
# import os  # Consolidated to common_imports
# import sys  # Consolidated to common_imports

# Add parent directory to path to allow imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import workflow building functions
try:
    from .graph_builder import (build_dynamic_workflow_graph,
                                build_workflow_graph)
except ImportError:
    # Create placeholder functions if imports fail
    def build_workflow_graph():
        print("build_workflow_graph not available")
        return None

    def build_dynamic_workflow_graph():
        print("build_dynamic_workflow_graph not available")
        return None


try:
    from .flow import build_workflow_graph as build_state_workflow_graph
except ImportError:

    def build_state_workflow_graph():
        print("build_state_workflow_graph not available")
        return None


# Create placeholder for missing function
def build_advanced_workflow_graph():
    print("build_advanced_workflow_graph not implemented yet")
    return None


def visualize_workflow(
    output_path: str = "src/core/workflows/graph/config/critical_path_output.html",
    workflow_type: str = "basic",
):
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
        print("Building basic workflow graph...")
        workflow = build_workflow_graph()
    elif workflow_type == "state":
        print("Building stateful workflow graph...")
        workflow = build_state_workflow_graph()
    elif workflow_type == "advanced":
        print("Building advanced workflow graph...")
        workflow = build_advanced_workflow_graph()
    elif workflow_type == "dynamic":
        print("Building dynamic workflow graph...")
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
    parser = argparse.ArgumentParser(description="Generate workflow visualizations")

    parser.add_argument(
        "--output",
        "-o",
        default="src/core/workflows/graph/config/critical_path_output.html",
        help="Output path for the visualization",
    )
    parser.add_argument(
        "--type",
        "-t",
        default="basic",
        choices=["basic", "state", "advanced", "dynamic"],
        help="Type of workflow to visualize",
    )

    args = parser.parse_args()

    try:
        visualize_workflow(args.output, args.type)
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
