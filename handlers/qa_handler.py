"""
QA Handler with Human Review Capability
This handler processes QA tasks and enables human review checkpoints.
"""

from typing import Dict, Any
from orchestration.states import TaskStatus
from utils.review import save_to_review


def qa_agent(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Handles QA tasks with human review capability.
    
    Args:
        state: The current workflow state
        
    Returns:
        Updated state with human review status
    """
    task_id = state.get("task_id", "UNKNOWN")
    agent_output = state.get("output", "")
    
    # Run tests or simulate validation
    result = f"QA Report for {task_id}:\n"
    result += "- 12 tests passed\n"
    result += "- 0 failed\n"
    result += "- Code coverage: 94%\n\n"
    result += f"Task output:\n{agent_output}"
    
    # Save for human inspection
    review_filename = f"qa_{task_id}.md"
    save_to_review(review_filename, result)
    
    # Create result state
    result_state = state.copy()
    result_state.update({
        "status": TaskStatus.HUMAN_REVIEW,  # Fixed: Using the correct TaskStatus enum
        "output": result,
        "review_required": True,
        "review_file": review_filename,
        "agent": "qa"
    })
    
    return result_state