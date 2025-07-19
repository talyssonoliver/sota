"""
Checkpoint Business Service

Centralizes all checkpoint-related business logic and operations.
Extracted from API routes to follow clean architecture principles.
"""

import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional

from ..workflows.hitl.models import HITLCheckpoint
from ..workflows.hitl.policy_engine import HITLPolicyEngine

logger = logging.getLogger(__name__)


@dataclass
class CheckpointApprovalRequest:
    """Request data for checkpoint approval"""

    reviewer_id: str
    comments: str = ""
    metadata: Dict[str, Any] = None


@dataclass
class CheckpointRejectionRequest:
    """Request data for checkpoint rejection"""

    reviewer_id: str
    reason: str
    comments: str = ""
    metadata: Dict[str, Any] = None


@dataclass
class CheckpointServiceResult:
    """Result from checkpoint service operations"""

    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None
    error_code: Optional[str] = None


class CheckpointService:
    """
    Business service for checkpoint operations.

    Centralizes checkpoint business logic that was previously
    scattered across API routes and infrastructure layers.
    """

    def __init__(self, hitl_engine: Optional[HITLPolicyEngine] = None):
        """Initialize checkpoint service

        Args:
            hitl_engine: HITL policy engine for checkpoint operations
        """
        self.hitl_engine = hitl_engine or HITLPolicyEngine()

    def approve_checkpoint(
        self, checkpoint_id: str, approval_request: CheckpointApprovalRequest
    ) -> CheckpointServiceResult:
        """
        Approve a checkpoint with business rule validation

        Args:
            checkpoint_id: ID of checkpoint to approve
            approval_request: Approval request data

        Returns:
            CheckpointServiceResult with operation result
        """
        try:
            # Validate business rules
            validation_result = self._validate_approval_request(
                checkpoint_id, approval_request
            )
            if not validation_result.success:
                return validation_result

            # Get checkpoint
            checkpoint = self.hitl_engine.get_checkpoint(checkpoint_id)
            if not checkpoint:
                return CheckpointServiceResult(
                    success=False,
                    message=f"Checkpoint {checkpoint_id} not found",
                    error_code="CHECKPOINT_NOT_FOUND",
                )

            # Business rule: Check if checkpoint can be approved
            if not self._can_approve_checkpoint(checkpoint, approval_request):
                return CheckpointServiceResult(
                    success=False,
                    message="Checkpoint cannot be approved due to business rules",
                    error_code="APPROVAL_NOT_ALLOWED",
                )

            # Perform approval (note: hitl_engine methods may be async)
            try:
                import asyncio

                success = asyncio.run(
                    self.hitl_engine.approve_checkpoint(
                        checkpoint_id=checkpoint_id,
                        reviewer=approval_request.reviewer_id,
                        comments=approval_request.comments,
                    )
                )
            except Exception:
                # Fallback to sync call if async fails
                success = self.hitl_engine.approve_checkpoint(
                    checkpoint_id=checkpoint_id,
                    reviewer=approval_request.reviewer_id,
                    comments=approval_request.comments,
                )

            if success:
                # Business logic: Update dependent workflows
                self._handle_checkpoint_approved(checkpoint, approval_request)

                return CheckpointServiceResult(
                    success=True,
                    message="Checkpoint approved successfully",
                    data={
                        "checkpoint_id": checkpoint_id,
                        "approved_by": approval_request.reviewer_id,
                        "approved_at": datetime.now().isoformat(),
                    },
                )
            else:
                return CheckpointServiceResult(
                    success=False,
                    message="Failed to approve checkpoint",
                    error_code="APPROVAL_FAILED",
                )

        except Exception as e:
            logger.error(f"Error approving checkpoint {checkpoint_id}: {e}")
            return CheckpointServiceResult(
                success=False,
                message=f"Internal error: {str(e)}",
                error_code="INTERNAL_ERROR",
            )

    def reject_checkpoint(
        self, checkpoint_id: str, rejection_request: CheckpointRejectionRequest
    ) -> CheckpointServiceResult:
        """
        Reject a checkpoint with business rule validation

        Args:
            checkpoint_id: ID of checkpoint to reject
            rejection_request: Rejection request data

        Returns:
            CheckpointServiceResult with operation result
        """
        try:
            # Validate business rules
            validation_result = self._validate_rejection_request(
                checkpoint_id, rejection_request
            )
            if not validation_result.success:
                return validation_result

            # Get checkpoint
            checkpoint = self.hitl_engine.get_checkpoint(checkpoint_id)
            if not checkpoint:
                return CheckpointServiceResult(
                    success=False,
                    message=f"Checkpoint {checkpoint_id} not found",
                    error_code="CHECKPOINT_NOT_FOUND",
                )

            # Perform rejection (note: hitl_engine methods may be async)
            try:
                import asyncio

                success = asyncio.run(
                    self.hitl_engine.reject_checkpoint(
                        checkpoint_id=checkpoint_id,
                        reviewer=rejection_request.reviewer_id,
                        reason=rejection_request.reason,
                        comments=rejection_request.comments,
                    )
                )
            except Exception:
                # Fallback to sync call if async fails
                success = self.hitl_engine.reject_checkpoint(
                    checkpoint_id=checkpoint_id,
                    reviewer=rejection_request.reviewer_id,
                    reason=rejection_request.reason,
                    comments=rejection_request.comments,
                )

            if success:
                # Business logic: Handle rejection consequences
                self._handle_checkpoint_rejected(checkpoint, rejection_request)

                return CheckpointServiceResult(
                    success=True,
                    message="Checkpoint rejected successfully",
                    data={
                        "checkpoint_id": checkpoint_id,
                        "rejected_by": rejection_request.reviewer_id,
                        "rejection_reason": rejection_request.reason,
                        "rejected_at": datetime.now().isoformat(),
                    },
                )
            else:
                return CheckpointServiceResult(
                    success=False,
                    message="Failed to reject checkpoint",
                    error_code="REJECTION_FAILED",
                )

        except Exception as e:
            logger.error(f"Error rejecting checkpoint {checkpoint_id}: {e}")
            return CheckpointServiceResult(
                success=False,
                message=f"Internal error: {str(e)}",
                error_code="INTERNAL_ERROR",
            )

    def get_checkpoint_details(self, checkpoint_id: str) -> CheckpointServiceResult:
        """
        Get detailed checkpoint information with business context

        Args:
            checkpoint_id: ID of checkpoint to retrieve

        Returns:
            CheckpointServiceResult with checkpoint details
        """
        try:
            checkpoint = self.hitl_engine.get_checkpoint(checkpoint_id)
            if not checkpoint:
                return CheckpointServiceResult(
                    success=False,
                    message=f"Checkpoint {checkpoint_id} not found",
                    error_code="CHECKPOINT_NOT_FOUND",
                )

            # Add business context
            checkpoint_data = checkpoint.to_dict()
            checkpoint_data.update(
                {
                    "business_context": self._get_business_context(checkpoint),
                    "available_actions": self._get_available_actions(checkpoint),
                    "risk_analysis": self._get_risk_analysis(checkpoint),
                }
            )

            return CheckpointServiceResult(
                success=True,
                message="Checkpoint retrieved successfully",
                data=checkpoint_data,
            )

        except Exception as e:
            logger.error(f"Error retrieving checkpoint {checkpoint_id}: {e}")
            return CheckpointServiceResult(
                success=False,
                message=f"Internal error: {str(e)}",
                error_code="INTERNAL_ERROR",
            )

    def list_pending_checkpoints(
        self, task_id: Optional[str] = None, reviewer_id: Optional[str] = None
    ) -> CheckpointServiceResult:
        """
        List pending checkpoints with business filtering

        Args:
            task_id: Optional task ID filter
            reviewer_id: Optional reviewer filter

        Returns:
            CheckpointServiceResult with checkpoint list
        """
        try:
            # Get pending checkpoints from engine
            pending_checkpoints = self.hitl_engine.get_pending_checkpoints(task_id)

            # Apply business filtering
            filtered_checkpoints = []
            for checkpoint in pending_checkpoints:
                if reviewer_id and reviewer_id not in checkpoint.assigned_reviewers:
                    continue

                # Add business context to each checkpoint
                checkpoint_data = checkpoint.to_dict()
                checkpoint_data.update(
                    {
                        "priority": self._calculate_checkpoint_priority(checkpoint),
                        "urgency": self._calculate_checkpoint_urgency(checkpoint),
                        "business_impact": self._assess_business_impact(checkpoint),
                    }
                )

                filtered_checkpoints.append(checkpoint_data)

            # Sort by business priority
            filtered_checkpoints.sort(
                key=lambda x: (x["priority"], x["urgency"]), reverse=True
            )

            return CheckpointServiceResult(
                success=True,
                message=f"Found {len(filtered_checkpoints)} pending checkpoints",
                data={
                    "checkpoints": filtered_checkpoints,
                    "total_count": len(filtered_checkpoints),
                    "filters_applied": {"task_id": task_id, "reviewer_id": reviewer_id},
                },
            )

        except Exception as e:
            logger.error(f"Error listing pending checkpoints: {e}")
            return CheckpointServiceResult(
                success=False,
                message=f"Internal error: {str(e)}",
                error_code="INTERNAL_ERROR",
            )

    # Private business logic methods

    def _validate_approval_request(
        self, checkpoint_id: str, request: CheckpointApprovalRequest
    ) -> CheckpointServiceResult:
        """Validate approval request against business rules"""
        if not request.reviewer_id:
            return CheckpointServiceResult(
                success=False,
                message="Missing required field: reviewer_id",
                error_code="VALIDATION_ERROR",
            )

        # Add more business validation rules here
        return CheckpointServiceResult(success=True, message="Validation passed")

    def _validate_rejection_request(
        self, checkpoint_id: str, request: CheckpointRejectionRequest
    ) -> CheckpointServiceResult:
        """Validate rejection request against business rules"""
        if not request.reviewer_id:
            return CheckpointServiceResult(
                success=False,
                message="Missing required field: reviewer_id",
                error_code="VALIDATION_ERROR",
            )

        if not request.reason:
            return CheckpointServiceResult(
                success=False,
                message="Missing required field: reason",
                error_code="VALIDATION_ERROR",
            )

        # Add more business validation rules here
        return CheckpointServiceResult(success=True, message="Validation passed")

    def _can_approve_checkpoint(
        self, checkpoint: HITLCheckpoint, request: CheckpointApprovalRequest
    ) -> bool:
        """Business rules for checkpoint approval eligibility"""
        # Example business rules
        if checkpoint.status.value != "pending":
            return False

        if request.reviewer_id not in checkpoint.assigned_reviewers:
            logger.warning(f"Reviewer {request.reviewer_id} not assigned to checkpoint")
            # Still allow approval but log warning

        return True

    def _handle_checkpoint_approved(
        self, checkpoint: HITLCheckpoint, request: CheckpointApprovalRequest
    ):
        """Business logic to execute after checkpoint approval"""
        # Implement post-approval business logic
        logger.info(f"Checkpoint {checkpoint.id} approved by {request.reviewer_id}")

        # Example: Trigger dependent workflows
        # Example: Send notifications
        # Example: Update metrics

    def _handle_checkpoint_rejected(
        self, checkpoint: HITLCheckpoint, request: CheckpointRejectionRequest
    ):
        """Business logic to execute after checkpoint rejection"""
        # Implement post-rejection business logic
        logger.info(f"Checkpoint {checkpoint.id} rejected by {request.reviewer_id}")

        # Example: Trigger remediation workflows
        # Example: Escalate to higher authority
        # Example: Update risk assessments

    def _get_business_context(self, checkpoint: HITLCheckpoint) -> Dict[str, Any]:
        """Get business context for a checkpoint"""
        return {
            "related_tasks": [],  # Implement task relationship logic
            "dependencies": [],  # Implement dependency logic
            "impact_analysis": {},  # Implement impact analysis
        }

    def _get_available_actions(self, checkpoint: HITLCheckpoint) -> List[str]:
        """Get available actions based on business rules"""
        actions = []
        if checkpoint.status.value == "pending":
            actions.extend(["approve", "reject", "escalate"])
        return actions

    def _get_risk_analysis(self, checkpoint: HITLCheckpoint) -> Dict[str, Any]:
        """Get risk analysis for business decision making"""
        return {
            "risk_level": checkpoint.risk_level.value,
            "risk_factors": checkpoint.risk_factors,
            "mitigation_suggestions": checkpoint.mitigation_suggestions,
        }

    def _calculate_checkpoint_priority(self, checkpoint: HITLCheckpoint) -> int:
        """Calculate business priority (1-10, higher is more priority)"""
        priority_map = {"critical": 10, "high": 7, "medium": 4, "low": 1}
        return priority_map.get(checkpoint.risk_level.value, 1)

    def _calculate_checkpoint_urgency(self, checkpoint: HITLCheckpoint) -> int:
        """Calculate urgency based on deadlines (1-10, higher is more urgent)"""
        if checkpoint.is_overdue:
            return 10

        # Calculate based on time remaining
        if checkpoint.timeout_at:
            time_remaining = (checkpoint.timeout_at - datetime.now()).total_seconds()
            hours_remaining = time_remaining / 3600

            if hours_remaining < 2:
                return 9
            elif hours_remaining < 6:
                return 7
            elif hours_remaining < 24:
                return 5
            else:
                return 3

        return 1

    def _assess_business_impact(self, checkpoint: HITLCheckpoint) -> str:
        """Assess business impact of the checkpoint"""
        if checkpoint.risk_level.value == "critical":
            return "high"
        elif checkpoint.risk_level.value == "high":
            return "medium"
        else:
            return "low"
