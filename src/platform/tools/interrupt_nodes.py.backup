#!/usr/bin/env python3
"""
LangGraph Interrupt Nodes - Phase 7 Step 7.3 Implementation

Enhanced interrupt node implementation for workflow pausing, human checkpoints,
and approval-based workflow continuation in the AI Agent System.
"""

import os
import json
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List, Callable
from pathlib import Path
from dataclasses import dataclass, asdict

logger = logging.getLogger(__name__)

# Ensure required directories exist
PENDING_REVIEWS_DIR = Path("pending_reviews")
APPROVED_DIR = Path(".approved")

for directory in [PENDING_REVIEWS_DIR, APPROVED_DIR]:
    directory.mkdir(exist_ok=True)


@dataclass
class InterruptCheckpoint:
    """Represents a workflow interruption point."""
    task_id: str
    node_name: str
    interrupt_reason: str
    agent_output: Dict[str, Any]
    created_at: datetime
    timeout_minutes: int = 60
    reviewer_required: Optional[str] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}
    
    @property
    def is_expired(self) -> bool:
        """Check if the checkpoint has expired."""
        if self.timeout_minutes <= 0:
            return False
        expiry_time = self.created_at + timedelta(minutes=self.timeout_minutes)
        return datetime.now() > expiry_time
    
    @property
    def approval_file_path(self) -> Path:
        """Get the path to the approval flag file."""
        return APPROVED_DIR / f"{self.task_id}.flag"
    
    @property
    def pending_file_path(self) -> Path:
        """Get the path to the pending review file."""
        return PENDING_REVIEWS_DIR / f"{self.task_id}.json"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert checkpoint to dictionary for serialization."""
        data = asdict(self)
        data["created_at"] = self.created_at.isoformat()
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'InterruptCheckpoint':
        """Create checkpoint from dictionary."""
        data["created_at"] = datetime.fromisoformat(data["created_at"])
        return cls(**data)


class InterruptNodeManager:
    """Manages LangGraph interrupt nodes and human checkpoints."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.active_checkpoints: Dict[str, InterruptCheckpoint] = {}
        self._load_existing_checkpoints()
    
    def _load_existing_checkpoints(self):
        """Load existing checkpoints from disk."""
        try:
            for pending_file in PENDING_REVIEWS_DIR.glob("*.json"):
                task_id = pending_file.stem
                with open(pending_file, 'r') as f:
                    data = json.load(f)
                    checkpoint = InterruptCheckpoint.from_dict(data)
                    self.active_checkpoints[task_id] = checkpoint
                    
            self.logger.info(f"Loaded {len(self.active_checkpoints)} existing checkpoints")
        except Exception as e:
            self.logger.error(f"Error loading checkpoints: {e}")
    
    def create_checkpoint(self, 
                         task_id: str,
                         node_name: str,
                         interrupt_reason: str,
                         agent_output: Dict[str, Any],
                         timeout_minutes: int = 60,
                         reviewer_required: Optional[str] = None,
                         metadata: Optional[Dict[str, Any]] = None) -> InterruptCheckpoint:
        """Create a new interrupt checkpoint."""
        checkpoint = InterruptCheckpoint(
            task_id=task_id,
            node_name=node_name,
            interrupt_reason=interrupt_reason,
            agent_output=agent_output,
            created_at=datetime.now(),
            timeout_minutes=timeout_minutes,
            reviewer_required=reviewer_required,
            metadata=metadata or {}
        )
        
        # Store checkpoint
        self.active_checkpoints[task_id] = checkpoint
        self._save_checkpoint(checkpoint)
        
        self.logger.info(f"Created checkpoint for task {task_id} at node {node_name}")
        return checkpoint
    
    def _save_checkpoint(self, checkpoint: InterruptCheckpoint):
        """Save checkpoint to disk."""
        try:
            with open(checkpoint.pending_file_path, 'w') as f:
                json.dump(checkpoint.to_dict(), f, indent=2)
        except Exception as e:
            self.logger.error(f"Error saving checkpoint {checkpoint.task_id}: {e}")
    
    def check_approval_status(self, task_id: str) -> str:
        """Check the approval status of a task."""
        checkpoint = self.active_checkpoints.get(task_id)
        if not checkpoint:
            return "NO_CHECKPOINT"
        
        # Check if approved
        if checkpoint.approval_file_path.exists():
            return "APPROVED"
        
        # Check if expired
        if checkpoint.is_expired:
            return "EXPIRED"
        
        return "WAITING"
    
    def approve_task(self, task_id: str, approver: str, comments: str = "") -> bool:
        """Approve a task and create approval flag."""
        try:
            checkpoint = self.active_checkpoints.get(task_id)
            if not checkpoint:
                self.logger.error(f"No checkpoint found for task {task_id}")
                return False
            
            approval_data = {
                "task_id": task_id,
                "approver": approver,
                "approved_at": datetime.now().isoformat(),
                "comments": comments,
                "checkpoint_data": checkpoint.to_dict()
            }
            
            with open(checkpoint.approval_file_path, 'w') as f:
                json.dump(approval_data, f, indent=2)
            
            self.logger.info(f"Task {task_id} approved by {approver}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error approving task {task_id}: {e}")
            return False
    
    def reject_task(self, task_id: str, reviewer: str, reason: str) -> bool:
        """Reject a task and set it to BLOCKED state."""
        try:
            checkpoint = self.active_checkpoints.get(task_id)
            if not checkpoint:
                self.logger.error(f"No checkpoint found for task {task_id}")
                return False
            
            rejection_data = {
                "task_id": task_id,
                "reviewer": reviewer,
                "rejected_at": datetime.now().isoformat(),
                "reason": reason,
                "status": "BLOCKED",
                "checkpoint_data": checkpoint.to_dict()
            }
            
            # Save rejection data
            rejection_file = PENDING_REVIEWS_DIR / f"{task_id}_rejected.json"
            with open(rejection_file, 'w') as f:
                json.dump(rejection_data, f, indent=2)
            
            # Remove from active checkpoints
            self._cleanup_checkpoint(task_id)
            
            self.logger.info(f"Task {task_id} rejected by {reviewer}: {reason}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error rejecting task {task_id}: {e}")
            return False
    
    def _cleanup_checkpoint(self, task_id: str):
        """Clean up checkpoint files and data."""
        try:
            checkpoint = self.active_checkpoints.pop(task_id, None)
            if checkpoint:
                # Remove pending review file
                if checkpoint.pending_file_path.exists():
                    checkpoint.pending_file_path.unlink()
                
                # Remove approval file if exists
                if checkpoint.approval_file_path.exists():
                    checkpoint.approval_file_path.unlink()
                    
        except Exception as e:
            self.logger.error(f"Error cleaning up checkpoint {task_id}: {e}")
    
    def get_pending_reviews(self) -> List[InterruptCheckpoint]:
        """Get all pending review checkpoints."""
        return [cp for cp in self.active_checkpoints.values() 
                if not cp.approval_file_path.exists() and not cp.is_expired]
    
    def get_expired_checkpoints(self) -> List[InterruptCheckpoint]:
        """Get all expired checkpoints."""
        return [cp for cp in self.active_checkpoints.values() if cp.is_expired]
    
    def cleanup_expired_checkpoints(self) -> int:
        """Clean up expired checkpoints and return count."""
        expired = self.get_expired_checkpoints()
        for checkpoint in expired:
            self._cleanup_checkpoint(checkpoint.task_id)
        
        self.logger.info(f"Cleaned up {len(expired)} expired checkpoints")
        return len(expired)


# Global interrupt node manager instance
_interrupt_manager = None

def get_interrupt_manager() -> InterruptNodeManager:
    """Get the global interrupt node manager instance."""
    global _interrupt_manager
    if _interrupt_manager is None:
        _interrupt_manager = InterruptNodeManager()
    return _interrupt_manager


# LangGraph interrupt node functions
def human_checkpoint_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    LangGraph node that creates a human checkpoint and waits for approval.
    
    This is the main interrupt node that pauses workflow execution.
    """
    task_id = state.get("task_id", "unknown_task")
    node_name = state.get("current_node", "human_checkpoint")
    
    manager = get_interrupt_manager()
    
    # Check if already approved
    approval_status = manager.check_approval_status(task_id)
    
    if approval_status == "APPROVED":
        # Resume workflow
        manager._cleanup_checkpoint(task_id)
        return {
            **state,
            "status": "APPROVED", 
            "next_action": "resume",
            "human_checkpoint_result": "approved"
        }
    
    elif approval_status == "EXPIRED":
        # Handle timeout
        manager._cleanup_checkpoint(task_id)
        return {
            **state,
            "status": "TIMEOUT",
            "next_action": "escalate",
            "human_checkpoint_result": "timeout"
        }
    
    elif approval_status == "WAITING":
        # Continue waiting
        return {
            **state,
            "status": "WAITING",
            "next_action": "wait",
            "human_checkpoint_result": "pending"
        }
    
    else:
        # Create new checkpoint
        interrupt_reason = state.get("interrupt_reason", "Human review required")
        timeout_minutes = state.get("timeout_minutes", 60)
        reviewer_required = state.get("reviewer_required")
        
        agent_output = {
            key: value for key, value in state.items()
            if key not in ["task_id", "current_node", "interrupt_reason"]
        }
        
        checkpoint = manager.create_checkpoint(
            task_id=task_id,
            node_name=node_name,
            interrupt_reason=interrupt_reason,
            agent_output=agent_output,
            timeout_minutes=timeout_minutes,
            reviewer_required=reviewer_required,
            metadata=state.get("metadata", {})
        )
        
        return {
            **state,
            "status": "CHECKPOINT_CREATED",
            "next_action": "wait",
            "checkpoint_id": checkpoint.task_id,
            "human_checkpoint_result": "created"
        }


def conditional_human_checkpoint(state: Dict[str, Any]) -> str:
    """
    Conditional edge function that determines if human review is needed.
    
    Returns:
        "needs_human": If human review is required
        "continue": If workflow can continue without human review
    """
    # Check various conditions that might require human review
    conditions = [
        state.get("requires_human_review", False),
        state.get("qa_coverage", 100) < state.get("qa_threshold", 80),
        state.get("risk_level", "low") in ["high", "critical"],
        state.get("complexity_score", 0) > state.get("complexity_threshold", 7),
        "sensitive" in state.get("task_tags", []),
        state.get("force_human_review", False)
    ]
    
    if any(conditions):
        return "needs_human"
    else:
        return "continue"


# Utility functions for LangGraph integration
def create_qa_checkpoint_node(qa_threshold: int = 80) -> Callable:
    """Create a QA checkpoint node with specific threshold."""
    def qa_checkpoint(state: Dict[str, Any]) -> Dict[str, Any]:
        qa_coverage = state.get("qa_coverage", 0)
        
        if qa_coverage < qa_threshold:
            return human_checkpoint_node({
                **state,
                "interrupt_reason": f"QA coverage {qa_coverage}% below threshold {qa_threshold}%",
                "reviewer_required": "QA Analyst",
                "timeout_minutes": 120
            })
        else:
            return {**state, "status": "QA_PASSED", "next_action": "continue"}
    
    return qa_checkpoint


def create_code_review_checkpoint_node() -> Callable:
    """Create a code review checkpoint node."""
    def code_review_checkpoint(state: Dict[str, Any]) -> Dict[str, Any]:
        return human_checkpoint_node({
            **state,
            "interrupt_reason": "Critical code changes require human review",
            "reviewer_required": "Technical Lead",
            "timeout_minutes": 240
        })
    
    return code_review_checkpoint


def create_documentation_checkpoint_node() -> Callable:
    """Create a documentation review checkpoint node."""
    def doc_checkpoint(state: Dict[str, Any]) -> Dict[str, Any]:
        return human_checkpoint_node({
            **state,
            "interrupt_reason": "Documentation requires human verification",
            "reviewer_required": "Product Manager",
            "timeout_minutes": 180
        })
    
    return doc_checkpoint


# CLI interface functions
def list_pending_reviews() -> List[Dict[str, Any]]:
    """List all pending reviews for CLI interface."""
    manager = get_interrupt_manager()
    pending = manager.get_pending_reviews()
    
    return [
        {
            "task_id": cp.task_id,
            "node_name": cp.node_name,
            "interrupt_reason": cp.interrupt_reason,
            "created_at": cp.created_at.isoformat(),
            "reviewer_required": cp.reviewer_required,
            "time_remaining": max(0, cp.timeout_minutes - 
                                 int((datetime.now() - cp.created_at).total_seconds() / 60))
        }
        for cp in pending
    ]


def approve_task_cli(task_id: str, approver: str, comments: str = "") -> bool:
    """Approve a task via CLI."""
    manager = get_interrupt_manager()
    return manager.approve_task(task_id, approver, comments)


def reject_task_cli(task_id: str, reviewer: str, reason: str) -> bool:
    """Reject a task via CLI."""
    manager = get_interrupt_manager()
    return manager.reject_task(task_id, reviewer, reason)


if __name__ == "__main__":
    # Example usage and testing
    import sys
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "list":
            pending = list_pending_reviews()
            print(f"\nPending Reviews ({len(pending)}):")
            for review in pending:
                print(f"  {review['task_id']}: {review['interrupt_reason']}")
                print(f"    Reviewer: {review['reviewer_required']}")
                print(f"    Time remaining: {review['time_remaining']} minutes")
                print()
        
        elif command == "approve" and len(sys.argv) >= 4:
            task_id, approver = sys.argv[2], sys.argv[3]
            comments = sys.argv[4] if len(sys.argv) > 4 else ""
            success = approve_task_cli(task_id, approver, comments)
            print(f"Approval {'successful' if success else 'failed'} for {task_id}")
        
        elif command == "reject" and len(sys.argv) >= 5:
            task_id, reviewer, reason = sys.argv[2], sys.argv[3], sys.argv[4]
            success = reject_task_cli(task_id, reviewer, reason)
            print(f"Rejection {'successful' if success else 'failed'} for {task_id}")
        
        else:
            print("Usage:")
            print("  python interrupt_nodes.py list")
            print("  python interrupt_nodes.py approve <task_id> <approver> [comments]")
            print("  python interrupt_nodes.py reject <task_id> <reviewer> <reason>")
    
    else:
        # Create test checkpoint
        manager = get_interrupt_manager()
        test_checkpoint = manager.create_checkpoint(
            task_id="TEST-001",
            node_name="qa",
            interrupt_reason="Test checkpoint for validation",
            agent_output={"test": "data"},
            timeout_minutes=1
        )
        print(f"Created test checkpoint: {test_checkpoint.task_id}")
        print(f"Approval status: {manager.check_approval_status('TEST-001')}")
