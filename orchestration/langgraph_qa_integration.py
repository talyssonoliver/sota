#!/usr/bin/env python3
"""
LangGraph Integration for QA Agent Execution

This module integrates the QA execution system with LangGraph workflow states.
When a task reaches QA_PENDING state, it automatically triggers the QA Agent
for automated validation.
"""

import json
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

from orchestration.qa_execution import QAExecutionEngine

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))


class LangGraphQAIntegration:
    """Integration layer between LangGraph and QA execution system"""

    def __init__(self, outputs_dir: str = "outputs"):
        self.qa_engine = QAExecutionEngine(outputs_dir)
        self.logger = logging.getLogger(__name__)

    def handle_qa_pending_state(
            self, task_id: str, task_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Handle QA_PENDING state transition in LangGraph.

        This function is called when a task reaches QA_PENDING state.
        It triggers the QA Agent for automated validation.

        Args:
            task_id: Task identifier
            task_context: Additional context from LangGraph workflow

        Returns:
            QA validation result and next state information
        """
        print(f"🔄 LangGraph QA_PENDING state triggered for {task_id}")

        # Log the state transition
        self._log_state_transition(task_id, "QA_PENDING", task_context)

        try:
            # Execute QA validation
            qa_result = self.qa_engine.execute_qa_for_task(task_id)

            # Determine next state based on QA result
            next_state = self._determine_next_state(qa_result)

            # Create LangGraph response
            response = {
                "task_id": task_id,
                "current_state": "QA_PENDING",
                "next_state": next_state,
                "qa_result": qa_result,
                "timestamp": datetime.now().isoformat(),
                "transition_reason": self._get_transition_reason(qa_result)
            }

            # Log the result
            self._log_qa_result(task_id, qa_result, next_state)

            return response

        except Exception as e:
            self.logger.error(f"QA execution failed for {task_id}: {e}")

            # Create error response
            error_response = {
                "task_id": task_id,
                "current_state": "QA_PENDING",
                "next_state": "ERROR",
                "qa_result": {
                    "tests_passed": 0,
                    "tests_failed": 0,
                    "coverage": 0.0,
                    "issues": [{"severity": "error", "message": str(e)}],
                    "status": "ERROR"
                },
                "timestamp": datetime.now().isoformat(),
                "transition_reason": f"QA execution error: {str(e)}"
            }

            return error_response

    def _determine_next_state(self, qa_result: Dict[str, Any]) -> str:
        """Determine next LangGraph state based on QA result"""
        status = qa_result.get("status", "ERROR")

        if status == "PASSED":
            return "DOCUMENTATION"  # Move to documentation phase
        elif status == "WARNING":
            return "REVIEW_REQUIRED"  # Needs human review
        elif status == "FAILED":
            return "FIXES_REQUIRED"  # Needs fixes before proceeding
        elif status == "ERROR":
            return "ERROR"  # Error state
        else:
            return "REVIEW_REQUIRED"  # Default to review

    def _get_transition_reason(self, qa_result: Dict[str, Any]) -> str:
        """Get human-readable reason for state transition"""
        status = qa_result.get("status", "ERROR")
        tests_passed = qa_result.get("tests_passed", 0)
        tests_failed = qa_result.get("tests_failed", 0)
        coverage = qa_result.get("coverage", 0.0)
        issues_count = len(qa_result.get("issues", []))

        if status == "PASSED":
            return f"QA validation passed: {tests_passed} tests passed, {coverage}% coverage, no critical issues"
        elif status == "WARNING":
            return f"QA validation passed with warnings: {tests_passed} tests passed, {coverage}% coverage, {issues_count} issues"
        elif status == "FAILED":
            if tests_failed > 0:
                return f"QA validation failed: {tests_failed} tests failed"
            elif issues_count > 0:
                return f"QA validation failed: {issues_count} critical issues found"
            elif coverage < 75.0:
                return f"QA validation failed: insufficient coverage ({coverage}%)"
            else:
                return "QA validation failed: unspecified issues"
        elif status == "ERROR":
            return "QA validation error occurred"
        else:
            return f"QA validation completed with status: {status}"

    def _log_state_transition(self,
                              task_id: str,
                              state: str,
                              context: Dict[str,
                                            Any] = None) -> None:
        """Log LangGraph state transition"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "task_id": task_id,
            "event": "state_transition",
            "state": state,
            "context": context or {}
        }

        # Save to logs directory
        logs_dir = Path("logs/langgraph")
        logs_dir.mkdir(parents=True, exist_ok=True)

        log_file = logs_dir / f"{task_id}_transitions.jsonl"
        with open(log_file, 'a') as f:
            f.write(json.dumps(log_entry) + '\n')

    def _log_qa_result(self,
                       task_id: str,
                       qa_result: Dict[str,
                                       Any],
                       next_state: str) -> None:
        """Log QA result and state transition"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "task_id": task_id,
            "event": "qa_completion",
            "qa_status": qa_result.get("status"),
            "tests_passed": qa_result.get("tests_passed"),
            "tests_failed": qa_result.get("tests_failed"),
            "coverage": qa_result.get("coverage"),
            "issues_count": len(qa_result.get("issues", [])),
            "next_state": next_state
        }

        # Save to logs directory
        logs_dir = Path("logs/langgraph")
        logs_dir.mkdir(parents=True, exist_ok=True)

        log_file = logs_dir / f"{task_id}_qa_results.jsonl"
        with open(log_file, 'a') as f:
            f.write(json.dumps(log_entry) + '\n')

        print(
            f"  📝 QA result logged: {qa_result.get('status')} -> {next_state}")


def create_qa_node_handler() -> callable:
    """
    Create a LangGraph node handler for QA validation.

    This can be used directly in LangGraph workflow definitions.

    Returns:
        Callable that can be used as a LangGraph node
    """
    qa_integration = LangGraphQAIntegration()

    def qa_node_handler(state: Dict[str, Any]) -> Dict[str, Any]:
        """LangGraph node handler for QA validation"""
        task_id = state.get("task_id")
        if not task_id:
            raise ValueError("task_id not found in LangGraph state")

        # Execute QA validation
        result = qa_integration.handle_qa_pending_state(task_id, state)

        # Update state with QA results
        updated_state = {
            **state,
            "qa_result": result["qa_result"],
            "next_state": result["next_state"],
            "qa_timestamp": result["timestamp"]
        }

        return updated_state

    return qa_node_handler


def create_qa_conditional_edge() -> callable:
    """
    Create a conditional edge function for LangGraph that routes based on QA results.

    Returns:
        Callable that can be used as a LangGraph conditional edge
    """
    def qa_conditional_router(state: Dict[str, Any]) -> str:
        """Route to next state based on QA result"""
        qa_result = state.get("qa_result", {})
        status = qa_result.get("status", "ERROR")

        if status == "PASSED":
            return "documentation"
        elif status == "WARNING":
            return "review_required"
        elif status == "FAILED":
            return "fixes_required"
        else:
            return "error"

    return qa_conditional_router


if __name__ == "__main__":
    # Example usage and testing
    import argparse

    parser = argparse.ArgumentParser(
        description="Test LangGraph QA integration")
    parser.add_argument("task_id", help="Task ID to test (e.g., BE-07)")

    args = parser.parse_args()

    # Setup logging
    logging.basicConfig(level=logging.INFO)

    # Test QA integration
    qa_integration = LangGraphQAIntegration()

    # Simulate LangGraph state
    test_state = {
        "task_id": args.task_id,
        "agent": "backend",
        "workflow_stage": "qa_validation"
    }

    # Execute QA pending state handler
    result = qa_integration.handle_qa_pending_state(args.task_id, test_state)

    print("\n" + "=" * 60)
    print("LANGGRAPH QA INTEGRATION TEST RESULT")
    print("=" * 60)
    print(json.dumps(result, indent=2))
    print("=" * 60)
