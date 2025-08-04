#!/usr/bin/env python3

from src.infrastructure.utils.common_imports import (
    Path,
    dataclass,
    datetime,
    json,
    sys
)
"""
HITL Dashboard Widgets - Web Components for Kanban Board

Implements web-based widgets for the HITL Kanban dashboard that can be
integrated into the unified dashboard system.
"""

# import json  # Consolidated to common_imports
# import sys  # Consolidated to common_imports
# from datetime import datetime  # Consolidated to common_imports
# from pathlib import Path  # Consolidated to common_imports
from typing import Dict, List, Any, Optional
from abc import ABC, abstractmethod

# Use centralized path management
sys.path.append(str(Path(__file__).parent.parent))

# Use centralized import utilities for optional dependencies
from src.infrastructure.utils.import_utils import conditional_import

HITLPolicyEngine = conditional_import('src.core.workflows.hitl_engine', 'HITLPolicyEngine')
CheckpointStatus = conditional_import('src.core.workflows.hitl.types', 'CheckpointStatus')
RiskLevel = conditional_import('src.core.workflows.hitl.types', 'RiskLevel')
HITLTaskMetadataManager = conditional_import('src.core.workflows.hitl_task_metadata', 'HITLTaskMetadataManager')
FeedbackSystem = conditional_import('src.infrastructure.utils.feedback_system', 'FeedbackSystem')


class HITLWidget(ABC):
    """Base class for HITL dashboard widgets."""
    
    def __init__(self):
        self.hitl_engine = HITLPolicyEngine()
        self.metadata_manager = HITLTaskMetadataManager()
        self.feedback_system = FeedbackSystem()
    
    @abstractmethod
    def get_data(self) -> Dict[str, Any]:
        """Get widget data."""
        pass
    
    @abstractmethod
    def get_widget_config(self) -> Dict[str, Any]:
        """Get widget configuration."""
        pass


class HITLPendingReviewsWidget(HITLWidget):
    """Widget showing pending reviews in Kanban format."""
    
    def get_data(self) -> Dict[str, Any]:
        """Get pending reviews data for Kanban board."""
        try:
            pending_checkpoints = self.hitl_engine.get_pending_checkpoints()
            
            # Convert checkpoints to board items
            pending_reviews = []
            for checkpoint in pending_checkpoints:
                # Calculate time remaining
                time_remaining, overdue = self._calculate_time_remaining(checkpoint.timeout_at)
                
                # Determine reviewer and action
                if checkpoint.checkpoint_type in ["agent_prompt", "output_evaluation"]:
                    reviewer = "QA Agent"
                    action = "Review"
                    status = "Awaiting QA"
                else:
                    reviewer = self._get_assigned_reviewer(checkpoint.task_id, checkpoint.checkpoint_type)
                    action = "Approve"
                    status = "Awaiting Human"
                
                if checkpoint.status == CheckpointStatus.ESCALATED:
                    status = "Escalated"
                    reviewer = "Team Lead"
                    action = "Resolve"
                elif checkpoint.status == CheckpointStatus.PENDING:
                    status = "In Review"
                    action = "Complete Review"
                
                pending_reviews.append({
                    "checkpoint_id": checkpoint.checkpoint_id,
                    "task_id": checkpoint.task_id,
                    "task_type": checkpoint.task_type,  # Add task_type to data
                    "status": status,
                    "pending_reviewer": reviewer,
                    "deadline": checkpoint.timeout_at.isoformat() if checkpoint.timeout_at else None,
                    "action": action,
                    "checkpoint_type": checkpoint.checkpoint_type,
                    "risk_level": checkpoint.risk_level.value if checkpoint.risk_level else "low",
                    "created_at": checkpoint.created_at.isoformat() if checkpoint.created_at else None,
                    "time_remaining": time_remaining,
                    "overdue": overdue,
                    "priority": self._calculate_priority(checkpoint.risk_level, overdue, checkpoint.created_at)
                })
            
            # Sort by priority
            pending_reviews.sort(key=lambda x: (-x["priority"], x["overdue"], x["task_id"]))
            
            # Summary statistics
            total_pending = len(pending_reviews)
            overdue_count = len([r for r in pending_reviews if r["overdue"]])
            high_priority = len([r for r in pending_reviews if r["priority"] >= 6])
            high_risk_count = len([r for r in pending_reviews if r["risk_level"] == "high"])
            escalated_count = len([r for r in pending_reviews if r["status"] == "Escalated"])
            
            # Filter options
            risk_levels = list(set(r["risk_level"] for r in pending_reviews))
            task_types = list(set(r["task_type"] for r in pending_reviews))
            checkpoint_types = list(set(r["checkpoint_type"] for r in pending_reviews))
            
            return {
                "pending_reviews": pending_reviews,
                "summary": {
                    "total_pending": total_pending,
                    "overdue_count": overdue_count,
                    "high_priority_count": high_priority,
                    "high_risk_count": high_risk_count,
                    "escalated_count": escalated_count,
                    "last_updated": datetime.now().isoformat()
                },
                "filters": {
                    "risk_levels": risk_levels,
                    "task_types": task_types,
                    "checkpoint_types": checkpoint_types
                }
            }
            
        except Exception as e:
            return {
                "error": str(e),
                "pending_reviews": [],
                "summary": {"total_pending": 0, "overdue_count": 0, "high_priority_count": 0, "high_risk_count": 0, "escalated_count": 0},
                "filters": {"risk_levels": [], "task_types": [], "checkpoint_types": []}
            }
    
    def get_widget_config(self) -> Dict[str, Any]:
        """Get widget configuration."""
        return {
            "title": "HITL Kanban Board",
            "type": "kanban",
            "refresh_interval": 30,
            "height": "large",
            "columns": [
                {"key": "task_id", "title": "Task ID", "width": "10%"},
                {"key": "status", "title": "Status", "width": "20%"},
                {"key": "pending_reviewer", "title": "Pending Reviewer", "width": "25%"},
                {"key": "time_remaining", "title": "Deadline", "width": "15%"},
                {"key": "action", "title": "Action", "width": "15%"},
                {"key": "priority", "title": "Priority", "width": "15%"}
            ],
            "actions": [
                {"key": "approve", "label": "Approve", "style": "success"},
                {"key": "reject", "label": "Reject", "style": "danger"},
                {"key": "escalate", "label": "Escalate", "style": "warning"}
            ]
        }
    
    def _calculate_time_remaining(self, deadline: Optional[datetime]) -> tuple[str, bool]:
        """Calculate time remaining until deadline."""
        if not deadline:
            return "—", False
        
        now = datetime.now()
        if deadline.tzinfo:
            from datetime import timezone
            now = now.replace(tzinfo=timezone.utc)
        
        time_diff = deadline - now
        
        if time_diff.total_seconds() < 0:
            overdue_time = abs(time_diff)
            if overdue_time.days > 0:
                return f"Overdue by {overdue_time.days} days", True
            else:
                hours = int(overdue_time.total_seconds() // 3600)
                return f"Overdue by {hours}h", True
        else:
            if time_diff.days > 0:
                return f"{time_diff.days} days", False
            else:
                hours = int(time_diff.total_seconds() // 3600)
                return f"{hours}h", False
    
    def _calculate_priority(self, risk_level: Optional[RiskLevel], overdue: bool, created_at: Optional[datetime]) -> int:
        """Calculate priority score."""
        priority = 0
        
        if overdue:
            priority += 10
        
        if risk_level == RiskLevel.CRITICAL:
            priority += 8
        elif risk_level == RiskLevel.HIGH:
            priority += 6
        elif risk_level == RiskLevel.MEDIUM:
            priority += 4
        elif risk_level == RiskLevel.LOW:
            priority += 2
        
        if created_at:
            age_hours = (datetime.now() - created_at).total_seconds() / 3600
            priority += min(int(age_hours / 24), 5)
        
        return priority
    
    def _get_assigned_reviewer(self, task_id: str, checkpoint_type: str) -> str:
        """Get assigned reviewer for a task."""
        try:
            metadata = self.metadata_manager.load_task_metadata(task_id)
            if metadata and metadata.hitl_checkpoints:
                for checkpoint in metadata.hitl_checkpoints:
                    if checkpoint.checkpoint_type == checkpoint_type:
                        return checkpoint.assigned_reviewers[0] if checkpoint.assigned_reviewers else "Unknown"
        except Exception:
            pass
        
        defaults = {
            "agent_prompt": "QA Agent",
            "output_evaluation": "Tech Lead",
            "qa": "QA Agent",
            "documentation": "PM",
            "task_transitions": "Team Lead"
        }
        return defaults.get(checkpoint_type, "Unknown")


class HITLApprovalActionsWidget(HITLWidget):
    """Widget for performing approval actions."""
    
    def get_data(self) -> Dict[str, Any]:
        """Get available actions data."""
        return {
            "available_actions": [
                {"action": "approve", "label": "Approve", "icon": "✅", "style": "success"},
                {"action": "reject", "label": "Reject", "icon": "❌", "style": "danger"},
                {"action": "escalate", "label": "Escalate", "icon": "⚠️", "style": "warning"},
                {"action": "request_changes", "label": "Request Changes", "icon": "📝", "style": "info"}
            ]
        }
    
    def get_widget_config(self) -> Dict[str, Any]:
        """Get widget configuration."""
        return {
            "title": "Quick Actions",
            "type": "actions",
            "height": "small",
            "position": "sidebar"
        }
    
    def process_action(self, checkpoint_id: str, action: str, reviewer: str, comments: str = "") -> Dict[str, Any]:
        """Process an approval action."""
        try:
#             from dataclasses import dataclass  # Consolidated to common_imports
            
            @dataclass
            class DecisionRequest:
                checkpoint_id: str
                decision: str
                reviewer_id: str
                comments: str
            
            request = DecisionRequest(
                checkpoint_id=checkpoint_id,
                decision=action,
                reviewer_id=reviewer,
                comments=comments
            )
            
            if action == "approve":
                success = self.hitl_engine.process_decision(request)
                return {"success": success}
            elif action == "reject":
                success = self.hitl_engine.process_decision(request)
                return {"success": success}
            elif action == "escalate":
                success = self.hitl_engine.escalate_checkpoint(checkpoint_id, reviewer)
                return {"success": success}
            else:
                return {"success": False, "error": f"Invalid action: {action}"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def process_batch_action(self, checkpoint_ids: List[str], action: str, reviewer: str, comments: str = "") -> Dict[str, Any]:
        """Process a batch approval action."""
        try:
            processed_count = 0
            for checkpoint_id in checkpoint_ids:
                result = self.process_action(checkpoint_id, action, reviewer, comments)
                if result.get("success", False):
                    processed_count += 1
            
            return {
                "success": processed_count == len(checkpoint_ids),
                "processed_count": processed_count,
                "total_requested": len(checkpoint_ids)
            }
        except Exception as e:
            return {"success": False, "error": str(e), "processed_count": 0}


class HITLMetricsWidget(HITLWidget):
    """Widget showing HITL metrics and statistics."""
    
    def get_data(self) -> Dict[str, Any]:
        """Get HITL metrics data."""
        try:
            # Get metrics from HITL engine
            metrics = self.hitl_engine.get_metrics()
            
            # Add calculated metrics
            total_checkpoints = metrics.get('total_checkpoints', 0)
            pending_count = metrics.get('pending_count', 0)
            approved_count = metrics.get('approved_count', 0)
            rejected_count = metrics.get('rejected_count', 0)
            
            # Calculate percentages (use from metrics if available, otherwise calculate)
            approval_rate = metrics.get('approval_rate', 0)
            if approval_rate == 0 and total_checkpoints > 0:
                approval_rate = (approved_count / total_checkpoints) * 100
            
            pending_rate = pending_count / total_checkpoints * 100 if total_checkpoints > 0 else 0
            
            return {
                "metrics": {
                    "total_checkpoints": total_checkpoints,
                    "pending_count": pending_count,
                    "approved_count": approved_count,
                    "rejected_count": rejected_count,
                    "approval_rate": round(approval_rate, 1),
                    "pending_rate": round(pending_rate, 1),
                    "average_review_time_hours": metrics.get('average_review_time_hours', 0),
                    "escalation_rate": metrics.get('escalation_rate', 0)
                },
                "charts": {
                    "status_distribution": {
                        "labels": ["Approved", "Rejected", "Pending"],
                        "data": [approved_count, rejected_count, pending_count]
                    },
                    "task_type_breakdown": self._generate_task_type_chart(metrics),
                    "risk_level_distribution": self._generate_risk_level_chart(metrics),
                    "daily_trends": {
                        "labels": self._get_daily_trend_labels(),
                        "data": [
                            self._get_daily_trend("created"),
                            self._get_daily_trend("processed")
                        ]
                    }
                }
            }
            
        except Exception as e:
            return {
                "error": str(e),
                "metrics": {},
                "trends": {}
            }
    
    def get_widget_config(self) -> Dict[str, Any]:
        """Get widget configuration."""
        return {
            "title": "HITL Metrics",
            "type": "metrics",
            "height": "medium",
            "charts": [
                {"type": "donut", "key": "approval_rate", "title": "Approval Rate"},
                {"type": "line", "key": "daily_approvals", "title": "Daily Trends"},
                {"type": "gauge", "key": "average_review_time", "title": "Avg Review Time"}
            ]
        }
    
    def _get_daily_trend(self, metric_type: str) -> List[Dict[str, Any]]:
        """Get daily trend data."""
        # Placeholder - would integrate with actual metrics collection
        return [
            {"date": "2025-06-09", "value": 12},
            {"date": "2025-06-10", "value": 8},
            {"date": "2025-06-11", "value": 15}
        ]
    
    def _get_review_time_trend(self) -> List[Dict[str, Any]]:
        """Get review time trend data."""
        # Placeholder - would integrate with actual metrics collection
        return [
            {"date": "2025-06-09", "avg_time": 2.5},
            {"date": "2025-06-10", "avg_time": 1.8},
            {"date": "2025-06-11", "avg_time": 2.1}
        ]
    
    def _generate_task_type_chart(self, metrics: Dict[str, Any]) -> Dict[str, List]:
        """Generate task type breakdown chart."""
        task_types = metrics.get('by_task_type', {})
        labels = list(task_types.keys())
        data = [task_types[t]['total'] for t in labels]
        return {"labels": labels, "data": data}
    
    def _generate_risk_level_chart(self, metrics: Dict[str, Any]) -> Dict[str, List]:
        """Generate risk level distribution chart."""
        risk_levels = metrics.get('by_risk_level', {})
        labels = list(risk_levels.keys())
        data = [risk_levels[r]['total'] for r in labels]
        return {"labels": labels, "data": data}
    
    def _get_daily_trend_labels(self) -> List[str]:
        """Get daily trend labels."""
        return ["2024-01-15", "2024-01-16", "2024-01-17"]


class HITLWorkflowStatusWidget(HITLWidget):
    """Widget showing workflow status with HITL integration."""
    
    def get_data(self, task_id: Optional[str] = None, task_type: Optional[str] = None) -> Dict[str, Any]:
        """Get workflow status data."""
        try:
            if task_id:
                # Get specific task workflow status
                workflow_status = self.get_workflow_status(task_id)
                pending_checkpoints = self.hitl_engine.get_pending_checkpoints_for_task(task_id)
                
                return {
                    "workflow_status": {
                        "blocked_on_review": len(pending_checkpoints) > 0,
                        "pending_checkpoints": [
                            {
                                "checkpoint_id": cp.checkpoint_id,
                                "checkpoint_type": cp.checkpoint_type,
                                "risk_level": cp.risk_level.value
                            } for cp in pending_checkpoints
                        ],
                        "current_phase": workflow_status.get("current_phase", "unknown"),
                        "task_status": workflow_status.get("task_status", "unknown"),
                        "progress_percentage": workflow_status.get("progress_percentage", 0),
                        "next_checkpoint": self._predict_next_checkpoint(workflow_status.get("current_phase", ""), task_type)
                    }
                }
            else:
                # Get all workflow statuses
                workflows = self._get_active_workflows()
                
                # Add HITL checkpoint information
                for workflow in workflows:
                    hitl_checkpoints = self._get_workflow_hitl_status(workflow["task_id"])
                    workflow["hitl_status"] = hitl_checkpoints
                
                return {
                    "workflows": workflows,
                    "summary": {
                        "total_workflows": len(workflows),
                        "blocked_by_hitl": len([w for w in workflows if w["hitl_status"]["blocked"]]),
                        "pending_review": len([w for w in workflows if w["hitl_status"]["pending_count"] > 0])
                    }
                }
            
        except Exception as e:
            return {
                "error": str(e),
                "workflows": [],
                "summary": {}
            }
    
    def get_widget_config(self) -> Dict[str, Any]:
        """Get widget configuration."""
        return {
            "title": "Workflow Status",
            "type": "workflow",
            "height": "medium",
            "show_hitl_indicators": True
        }
    
    def _get_active_workflows(self) -> List[Dict[str, Any]]:
        """Get active workflows."""
        # Placeholder - would integrate with actual workflow system
        return [
            {"task_id": "BE-07", "status": "in_progress", "stage": "qa"},
            {"task_id": "FE-05", "status": "pending", "stage": "review"},
            {"task_id": "UX-02", "status": "blocked", "stage": "approval"}
        ]
    
    def _get_workflow_hitl_status(self, task_id: str) -> Dict[str, Any]:
        """Get HITL status for a workflow."""
        try:
            pending_checkpoints = [
                cp for cp in self.hitl_engine.get_pending_checkpoints()
                if cp.task_id == task_id
            ]
            
            return {
                "pending_count": len(pending_checkpoints),
                "blocked": any(cp.status == CheckpointStatus.ESCALATED for cp in pending_checkpoints),
                "overdue_count": len([
                    cp for cp in pending_checkpoints
                    if cp.timeout_at and cp.timeout_at < datetime.now()
                ])
            }
            
        except Exception:
            return {"pending_count": 0, "blocked": False, "overdue_count": 0}
    
    def get_workflow_status(self, task_id: str) -> Dict[str, Any]:
        """Get workflow status for a specific task."""
        # Placeholder - would integrate with actual workflow system
        return {
            "current_phase": "agent_prompt",
            "task_status": "in_progress", 
            "progress_percentage": 25
        }
    
    def _predict_next_checkpoint(self, current_phase: str, task_type: Optional[str] = None) -> str:
        """Predict the next checkpoint based on current phase."""
        phase_transitions = {
            "agent_prompt": "output_evaluation",
            "output_evaluation": "qa_validation",
            "qa_validation": "documentation",
            "documentation": "task_transitions"
        }
        return phase_transitions.get(current_phase, "unknown")


class HITLDashboardManager:
    """Manager for coordinating HITL dashboard widgets."""
    
    hitl_engine = None  # Class attribute for test mocking
    
    def __init__(self):
        if self.hitl_engine is None:
            self.hitl_engine = HITLPolicyEngine()  # Instance fallback
        self.widgets = {
            "pending_reviews": HITLPendingReviewsWidget(),
            "approval_actions": HITLApprovalActionsWidget(),
            "metrics": HITLMetricsWidget(),
            "workflow_status": HITLWorkflowStatusWidget()
        }
    
    def get_dashboard_data(self) -> Dict[str, Any]:
        """Get complete dashboard data."""
        dashboard_data = {
            "last_updated": datetime.now().isoformat()
        }
        
        for widget_name, widget in self.widgets.items():
            try:
                widget_data = widget.get_data()
                dashboard_data[widget_name] = widget_data
            except Exception as e:
                dashboard_data[widget_name] = {
                    "error": str(e)
                }
        
        return dashboard_data
    
    def get_widget_data(self, widget_name: str) -> Dict[str, Any]:
        """Get data for a specific widget."""
        if widget_name in self.widgets:
            return self.widgets[widget_name].get_data()
        else:
            return {"error": f"Widget '{widget_name}' not found"}
    
    def process_widget_action(self, widget_name: str, action: str, **kwargs) -> Dict[str, Any]:
        """Process an action for a specific widget."""
        if widget_name == "approval_actions":
            widget = self.widgets[widget_name]
            success = widget.process_action(
                kwargs.get("checkpoint_id"),
                action,
                kwargs.get("reviewer", "unknown"),
                kwargs.get("comments", "")
            )
            return {"success": success}
        else:
            return {"error": f"Action '{action}' not supported for widget '{widget_name}'"}
    
    def get_task_dashboard_data(self, task_id: str, task_type: str) -> Dict[str, Any]:
        """Get task-specific dashboard data."""
        try:
            # Get workflow status for the specific task
            workflow_widget = self.widgets["workflow_status"]
            workflow_data = workflow_widget.get_data(task_id, task_type)
            
            return {
                "task_id": task_id,
                "task_type": task_type,
                "workflow_status": workflow_data.get("workflow_status", {}),
                "last_updated": datetime.now().isoformat()
            }
        except Exception as e:
            return {
                "error": str(e),
                "task_id": task_id,
                "task_type": task_type
            }
    
    def export_dashboard_state(self, output_file: str = "hitl_dashboard_state.json") -> None:
        """Export current dashboard state to file."""
        dashboard_data = self.get_dashboard_data()
        
        with open(output_file, 'w') as f:
            json.dump(dashboard_data, f, indent=2)


# Convenience functions for external integration
def get_hitl_kanban_data() -> Dict[str, Any]:
    """Get HITL Kanban board data."""
    widget = HITLPendingReviewsWidget()
    return widget.get_data()


def get_hitl_dashboard_data() -> Dict[str, Any]:
    """Get complete HITL dashboard data."""
    manager = HITLDashboardManager()
    return manager.get_dashboard_data()


def process_hitl_action(checkpoint_id: str, action: str, reviewer: str, comments: str = "") -> bool:
    """Process a HITL approval action."""
    widget = HITLApprovalActionsWidget()
    return widget.process_action(checkpoint_id, action, reviewer, comments)


if __name__ == "__main__":
    # Demo usage
    manager = HITLDashboardManager()
    dashboard_data = manager.get_dashboard_data()
    
    print("HITL Dashboard Data:")
    print(json.dumps(dashboard_data, indent=2))