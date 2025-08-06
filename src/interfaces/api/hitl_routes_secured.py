#!/usr/bin/env python3

from src.infrastructure.utils.common_imports import datetime, logging
"""
HITL API Endpoints - Phase 7 Integration with Security

Flask routes for Human-in-the-Loop dashboard integration,
checkpoint management, and approval workflows with proper authentication.
"""

# import logging  # Consolidated to common_imports
# from datetime import datetime  # Consolidated to common_imports

from flask import Blueprint, request, jsonify, g
from src.core.workflows.hitl_engine import HITLPolicyEngine
from src.infrastructure.utils.feedback_system import get_feedback_system
from src.infrastructure.security.auth_middleware import requires_auth, public_endpoint

try:
    from src.interfaces.dashboard.hitl_widgets import HITLDashboardManager
    
except ImportError:    # Fallback if dashboard module is not available
    class HITLDashboardManager:
        def __init__(self):
            self.widgets = {}
        
        def get_all_widget_data(self):
            return {"widgets": {}, "status": "dashboard_unavailable"}
        
        def get_dashboard_data(self):
            return {
                "pending_reviews": [],
                "metrics": {"total_pending": 0, "high_risk_count": 0},
                "workflow_status": {"active_tasks": 0, "blocked_tasks": 0}
            }
          
        def get_task_dashboard_data(self, task_id, task_type=None):
            return {
                "task_id": task_id,
                "workflow_status": {"current_phase": "agent_prompt", "blocked_on_review": True},
                "pending_checkpoints": []
            }
        
        def get_widget_data(self, widget_id):
            return {"widget_id": widget_id, "status": "unavailable"}
        
        def process_widget_action(self, widget_id, action, action_data):
            return {"status": "dashboard_unavailable"}


# Create HITL blueprint
hitl_bp = Blueprint('hitl', __name__, url_prefix='/api/hitl')
logger = logging.getLogger("hitl.api")

# Initialize HITL components
policy_engine = HITLPolicyEngine()
dashboard_manager = HITLDashboardManager()
feedback_system = get_feedback_system()

# Health Check (public endpoint)
@hitl_bp.route('/health', methods=['GET'])
@public_endpoint
def health_check():
    """Health check endpoint - no authentication required."""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "hitl-api"
    })

# Dashboard Endpoints - All require authentication
@hitl_bp.route('/dashboard', methods=['GET'])
@requires_auth
def get_dashboard():
    """Get dashboard overview data."""
    logger.info(f"Dashboard accessed by user: {g.current_user}")
    return jsonify({
        "status": "success",
        "user": g.current_user,
        "data": dashboard_manager.get_dashboard_data(),
        "generated_at": datetime.utcnow().isoformat()
    })

@hitl_bp.route('/dashboard/task/<task_id>', methods=['GET'])
@requires_auth
def get_task_dashboard(task_id):
    """Get task-specific dashboard data."""
    logger.info(f"Task dashboard accessed by user {g.current_user} for task: {task_id}")
    task_type = request.args.get('type', 'general')
    return jsonify({
        "status": "success",
        "user": g.current_user,
        "data": dashboard_manager.get_task_dashboard_data(task_id, task_type),
        "generated_at": datetime.utcnow().isoformat()
    })

# Checkpoint Management - All require authentication
@hitl_bp.route('/checkpoints', methods=['POST'])
@requires_auth
def create_checkpoint():
    """Create a new checkpoint for review."""
    logger.info(f"Checkpoint creation requested by user: {g.current_user}")
    
    checkpoint_data = request.json
    checkpoint_data['created_by'] = g.current_user  # Track who created the checkpoint
    
    try:
        # Validate required fields
        required = ['task_id', 'checkpoint_type', 'data', 'risk_score']
        missing = [f for f in required if f not in checkpoint_data]
        if missing:
            return jsonify({
                "status": "error",
                "error": f"Missing required fields: {missing}"
            }), 400
        
        # Store checkpoint and check policies
        checkpoint_id = f"chk_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
        requires_review = policy_engine.check_policies(checkpoint_data)
        
        logger.info(f"Checkpoint {checkpoint_id} created by {g.current_user}, requires_review: {requires_review}")
        
        return jsonify({
            "status": "success",
            "checkpoint_id": checkpoint_id,
            "requires_review": requires_review,
            "created_by": g.current_user,
            "created_at": datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error creating checkpoint: {str(e)}")
        return jsonify({
            "status": "error",
            "error": "Failed to create checkpoint"
        }), 500

@hitl_bp.route('/checkpoints', methods=['GET'])
@requires_auth
def list_checkpoints():
    """List checkpoints with filtering."""
    logger.info(f"Checkpoint list requested by user: {g.current_user}")
    
    # Filter parameters
    status = request.args.get('status', 'all')
    limit = int(request.args.get('limit', 10))
    offset = int(request.args.get('offset', 0))
    
    # Mock checkpoint list with user tracking
    checkpoints = [
        {
            "checkpoint_id": f"chk_20250101_{i:04d}",
            "task_id": f"task_{i}",
            "status": "pending" if i % 2 == 0 else "approved",
            "risk_score": 0.3 + (i * 0.1),
            "created_at": datetime.utcnow().isoformat(),
            "created_by": g.current_user if i % 3 == 0 else "other_user",
            "reviewed_by": None if i % 2 == 0 else g.current_user
        }
        for i in range(5)
    ]
    
    return jsonify({
        "status": "success",
        "checkpoints": checkpoints[offset:offset+limit],
        "total": len(checkpoints),
        "limit": limit,
        "offset": offset,
        "user": g.current_user
    })

@hitl_bp.route('/checkpoints/<checkpoint_id>/approve', methods=['POST'])
@requires_auth
def approve_checkpoint(checkpoint_id):
    """Approve a checkpoint."""
    logger.info(f"Checkpoint {checkpoint_id} approval by user: {g.current_user}")
    
    approval_data = request.json or {}
    approval_data['approved_by'] = g.current_user
    approval_data['approved_at'] = datetime.utcnow().isoformat()
    
    return jsonify({
        "status": "success",
        "checkpoint_id": checkpoint_id,
        "action": "approved",
        "approved_by": g.current_user,
        "timestamp": approval_data['approved_at']
    })

@hitl_bp.route('/checkpoints/<checkpoint_id>/reject', methods=['POST'])
@requires_auth
def reject_checkpoint(checkpoint_id):
    """Reject a checkpoint."""
    logger.info(f"Checkpoint {checkpoint_id} rejection by user: {g.current_user}")
    
    rejection_data = request.json or {}
    reason = rejection_data.get('reason', 'No reason provided')
    
    return jsonify({
        "status": "success",
        "checkpoint_id": checkpoint_id,
        "action": "rejected",
        "rejected_by": g.current_user,
        "reason": reason,
        "timestamp": datetime.utcnow().isoformat()
    })

@hitl_bp.route('/checkpoints/<checkpoint_id>/escalate', methods=['POST'])
@requires_auth
def escalate_checkpoint(checkpoint_id):
    """Escalate a checkpoint for higher-level review."""
    logger.info(f"Checkpoint {checkpoint_id} escalation by user: {g.current_user}")
    
    escalation_data = request.json or {}
    escalation_data['escalated_by'] = g.current_user
    escalation_data['escalated_at'] = datetime.utcnow().isoformat()
    
    return jsonify({
        "status": "success",
        "checkpoint_id": checkpoint_id,
        "action": "escalated",
        "escalated_by": g.current_user,
        "escalation_reason": escalation_data.get('reason', 'Requires higher-level review'),
        "timestamp": escalation_data['escalated_at']
    })

# Batch Operations - Require authentication
@hitl_bp.route('/checkpoints/batch/approve', methods=['POST'])
@requires_auth
def batch_approve():
    """Batch approve multiple checkpoints."""
    logger.info(f"Batch approval requested by user: {g.current_user}")
    
    checkpoint_ids = request.json.get('checkpoint_ids', [])
    
    if not checkpoint_ids:
        return jsonify({
            "status": "error",
            "error": "No checkpoint IDs provided"
        }), 400
    
    results = []
    for cp_id in checkpoint_ids:
        results.append({
            "checkpoint_id": cp_id,
            "status": "approved",
            "approved_by": g.current_user
        })
    
    return jsonify({
        "status": "success",
        "action": "batch_approve",
        "approved_by": g.current_user,
        "results": results,
        "total": len(results),
        "timestamp": datetime.utcnow().isoformat()
    })

@hitl_bp.route('/checkpoints/batch/reject', methods=['POST'])
@requires_auth
def batch_reject():
    """Batch reject multiple checkpoints."""
    logger.info(f"Batch rejection requested by user: {g.current_user}")
    
    data = request.json
    checkpoint_ids = data.get('checkpoint_ids', [])
    reason = data.get('reason', 'Batch rejection')
    
    if not checkpoint_ids:
        return jsonify({
            "status": "error",
            "error": "No checkpoint IDs provided"
        }), 400
    
    results = []
    for cp_id in checkpoint_ids:
        results.append({
            "checkpoint_id": cp_id,
            "status": "rejected",
            "rejected_by": g.current_user,
            "reason": reason
        })
    
    return jsonify({
        "status": "success",
        "action": "batch_reject",
        "rejected_by": g.current_user,
        "results": results,
        "total": len(results),
        "timestamp": datetime.utcnow().isoformat()
    })

# Feedback Management - Require authentication
@hitl_bp.route('/feedback', methods=['POST'])
@requires_auth
def submit_feedback():
    """Submit feedback for a task or decision."""
    logger.info(f"Feedback submission by user: {g.current_user}")
    
    feedback_data = request.json
    feedback_data['submitted_by'] = g.current_user
    
    if not feedback_data:
        return jsonify({
            "status": "error",
            "error": "No feedback data provided"
        }), 400
    
    try:
        # Store feedback with user tracking
        feedback_id = feedback_system.submit_feedback({
            **feedback_data,
            'submitted_by': g.current_user,
            'submitted_at': datetime.utcnow().isoformat()
        })
        
        return jsonify({
            "status": "success",
            "feedback_id": feedback_id,
            "submitted_by": g.current_user,
            "timestamp": datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error submitting feedback: {str(e)}")
        return jsonify({
            "status": "error",
            "error": "Failed to submit feedback"
        }), 500

@hitl_bp.route('/feedback/<task_id>', methods=['GET'])
@requires_auth
def get_feedback(task_id):
    """Get feedback for a specific task."""
    logger.info(f"Feedback retrieval for task {task_id} by user: {g.current_user}")
    
    try:
        feedback = feedback_system.get_feedback(task_id)
        
        return jsonify({
            "status": "success",
            "task_id": task_id,
            "feedback": feedback,
            "retrieved_by": g.current_user,
            "timestamp": datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error retrieving feedback: {str(e)}")
        return jsonify({
            "status": "error",
            "error": "Failed to retrieve feedback"
        }), 500

# Metrics and Analytics - Require authentication
@hitl_bp.route('/metrics', methods=['GET'])
@requires_auth
def get_metrics():
    """Get HITL metrics and statistics."""
    logger.info(f"Metrics requested by user: {g.current_user}")
    
    time_range = request.args.get('range', '24h')
    
    # Mock metrics with user context
    metrics = {
        "total_checkpoints": 150,
        "pending_reviews": 23,
        "approval_rate": 0.85,
        "average_review_time": "2.5 hours",
        "high_risk_items": 5,
        "reviewer_stats": {
            g.current_user: {
                "reviewed": 45,
                "approved": 38,
                "rejected": 7
            }
        },
        "time_range": time_range,
        "generated_at": datetime.utcnow().isoformat()
    }
    
    return jsonify({
        "status": "success",
        "metrics": metrics,
        "requested_by": g.current_user
    })

# Widget Management - Require authentication
@hitl_bp.route('/widgets', methods=['GET'])
@requires_auth
def get_all_widgets():
    """Get all dashboard widgets data."""
    logger.info(f"All widgets data requested by user: {g.current_user}")
    
    widget_data = dashboard_manager.get_all_widget_data()
    
    return jsonify({
        "status": "success",
        "data": widget_data,
        "user": g.current_user,
        "timestamp": datetime.utcnow().isoformat()
    })

@hitl_bp.route('/widgets/<widget_id>', methods=['GET'])
@requires_auth
def get_widget(widget_id):
    """Get specific widget data."""
    logger.info(f"Widget {widget_id} data requested by user: {g.current_user}")
    
    widget_data = dashboard_manager.get_widget_data(widget_id)
    
    return jsonify({
        "status": "success",
        "widget_id": widget_id,
        "data": widget_data,
        "user": g.current_user,
        "timestamp": datetime.utcnow().isoformat()
    })

@hitl_bp.route('/widgets/<widget_id>/action', methods=['POST'])
@requires_auth
def widget_action(widget_id):
    """Perform action on a widget."""
    logger.info(f"Widget {widget_id} action by user: {g.current_user}")
    
    action_data = request.json
    action = action_data.get('action')
    
    if not action:
        return jsonify({
            "status": "error",
            "error": "No action specified"
        }), 400
    
    # Add user context to action
    action_data['performed_by'] = g.current_user
    
    result = dashboard_manager.process_widget_action(widget_id, action, action_data)
    
    return jsonify({
        "status": "success",
        "widget_id": widget_id,
        "action": action,
        "result": result,
        "performed_by": g.current_user,
        "timestamp": datetime.utcnow().isoformat()
    })

# Workflow Management - Require authentication
@hitl_bp.route('/workflows', methods=['GET'])
@requires_auth
def list_workflows():
    """List active workflows requiring HITL."""
    logger.info(f"Workflow list requested by user: {g.current_user}")
    
    # Mock workflow data
    workflows = [
        {
            "workflow_id": "wf_001",
            "task_id": "task_123",
            "status": "blocked_on_review",
            "checkpoint_count": 3,
            "created_at": datetime.utcnow().isoformat(),
            "assigned_to": g.current_user
        },
        {
            "workflow_id": "wf_002",
            "task_id": "task_456",
            "status": "in_progress",
            "checkpoint_count": 1,
            "created_at": datetime.utcnow().isoformat(),
            "assigned_to": "other_reviewer"
        }
    ]
    
    return jsonify({
        "status": "success",
        "workflows": workflows,
        "total": len(workflows),
        "user": g.current_user
    })

# Policy Management - Require authentication with elevated privileges
@hitl_bp.route('/policies', methods=['GET'])
@requires_auth
def get_policies():
    """Get current HITL policies."""
    logger.info(f"Policy list requested by user: {g.current_user}")
    
    # TODO: Add role-based access control check here
    # For now, just log who is accessing policies
    
    policies = policy_engine.get_all_policies()
    
    return jsonify({
        "status": "success",
        "policies": policies,
        "accessed_by": g.current_user,
        "timestamp": datetime.utcnow().isoformat()
    })

@hitl_bp.route('/policies', methods=['POST'])
@requires_auth
def update_policies():
    """Update HITL policies (admin only)."""
    logger.info(f"Policy update requested by user: {g.current_user}")
    
    # TODO: Implement proper role-based access control
    # For now, log who is trying to update policies
    logger.warning(f"Policy update attempted by user: {g.current_user}")
    
    policy_data = request.json
    
    if not policy_data:
        return jsonify({
            "status": "error",
            "error": "No policy data provided"
        }), 400
    
    try:
        # Update policies with audit trail
        policy_engine.update_policies(policy_data)
        
        logger.info(f"Policies updated by user: {g.current_user}")
        
        return jsonify({
            "status": "success",
            "message": "Policies updated",
            "updated_by": g.current_user,
            "timestamp": datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error updating policies: {str(e)}")
        return jsonify({
            "status": "error",
            "error": "Failed to update policies"
        }), 500

# Error handlers
@hitl_bp.errorhandler(404)
def not_found(error):
    return jsonify({
        "status": "error",
        "error": "Endpoint not found"
    }), 404

@hitl_bp.errorhandler(500)
def internal_error(error):
    logger.error(f"Internal server error: {str(error)}")
    return jsonify({
        "status": "error",
        "error": "Internal server error"
    }), 500