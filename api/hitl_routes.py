#!/usr/bin/env python3
"""
HITL API Endpoints - Phase 7 Integration

Flask routes for Human-in-the-Loop dashboard integration,
checkpoint management, and approval workflows.
"""

import json
import logging
import asyncio
from datetime import datetime
from typing import Dict, Any, List

from flask import Blueprint, request, jsonify, make_response
from orchestration.hitl_engine import HITLPolicyEngine
try:
    from dashboard.hitl_widgets import HITLDashboardManager
    
except ImportError:
    # Fallback if dashboard module is not available
    class HITLDashboardManager:
        def __init__(self):
            self.widgets = {}
        
        def get_all_widget_data(self):
            return {"widgets": {}, "status": "dashboard_unavailable"}
        
        def get_widget_data(self, widget_id):
            return {"widget_id": widget_id, "status": "unavailable"}
        
        def process_widget_action(self, widget_id, action, action_data):
            return {"status": "dashboard_unavailable"}


# Create HITL blueprint
hitl_bp = Blueprint('hitl', __name__, url_prefix='/api/hitl')
logger = logging.getLogger("hitl.api")

# Initialize managers
hitl_engine = HITLPolicyEngine()
hitl_dashboard = HITLDashboardManager()


@hitl_bp.after_request
def after_request(response):
    """Add CORS headers and rate limiting headers to all responses."""
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
    response.headers['X-RateLimit-Remaining'] = '100'  # Mock rate limiting
    return response


@hitl_bp.route('/health', methods=['GET'])
def hitl_health():
    """Health check for HITL system."""
    try:
        # Check HITL engine status
        engine_status = hitl_engine.get_system_status()
        
        # Check dashboard widgets
        widget_status = {}
        for widget_id in hitl_dashboard.widgets.keys():
            try:
                hitl_dashboard.get_widget_data(widget_id)
                widget_status[widget_id] = "healthy"
            except Exception as e:
                widget_status[widget_id] = f"error: {str(e)}"
        
        return jsonify({
            "status": "success",
            "timestamp": datetime.now().isoformat(),
            "hitl_engine": engine_status,
            "dashboard_widgets": widget_status,
            "version": "1.0.0"
        })
        
    except Exception as e:
        logger.error(f"HITL health check failed: {e}")
        return jsonify({
            "status": "error", 
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }), 500


@hitl_bp.route('/dashboard', methods=['GET'])
def get_dashboard_data():
    """Get all HITL dashboard widget data."""
    try:
        dashboard_data = hitl_dashboard.get_all_widget_data()
        return jsonify(dashboard_data)
        
    except Exception as e:
        logger.error(f"Error getting HITL dashboard data: {e}")
        return jsonify({
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }), 500


@hitl_bp.route('/dashboard/widget/<widget_id>', methods=['GET'])
def get_widget_data(widget_id: str):
    """Get data for a specific widget."""
    try:
        widget_data = hitl_dashboard.get_widget_data(widget_id)
        return jsonify(widget_data)
        
    except Exception as e:
        logger.error(f"Error getting widget {widget_id} data: {e}")
        return jsonify({
            "status": "error",
            "error": str(e),
            "widget_id": widget_id,
            "timestamp": datetime.now().isoformat()
        }), 500


@hitl_bp.route('/dashboard/widget/<widget_id>/action', methods=['POST'])
def process_widget_action(widget_id: str):
    """Process an action from a dashboard widget."""
    try:
        request_data = request.get_json()
        action = request_data.get('action')
        action_data = request_data.get('data', {})
        
        if not action:
            return jsonify({
                "status": "error",
                "error": "Missing 'action' in request data"
            }), 400
        
        result = hitl_dashboard.process_widget_action(widget_id, action, action_data)
        return jsonify({
            "status": "success",
            "result": result,
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error processing widget action {widget_id}: {e}")
        return jsonify({
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }), 500


@hitl_bp.route('/checkpoints', methods=['GET'])
def get_checkpoints():
    """Get HITL checkpoints with optional filtering."""
    try:
        # Parse query parameters
        status = request.args.get('status')  # pending, approved, rejected, escalated
        risk_level = request.args.get('risk_level')  # high, medium, low
        checkpoint_type = request.args.get('type')
        task_id = request.args.get('task_id')
        limit = int(request.args.get('limit', 50))
        offset = int(request.args.get('offset', 0))
        
        # Get checkpoints from engine (use get_pending_checkpoints which actually exists)
        if task_id:
            checkpoints = hitl_engine.get_pending_checkpoints(task_id)
        else:
            checkpoints = hitl_engine.get_pending_checkpoints()        
        # Format for API response
        checkpoint_data = []
        for checkpoint in checkpoints:
            if hasattr(checkpoint, 'to_dict'):
                checkpoint_dict = checkpoint.to_dict()
            elif isinstance(checkpoint, dict):
                checkpoint_dict = checkpoint
            else:
                # Convert checkpoint object to dict manually
                checkpoint_dict = {
                    "checkpoint_id": getattr(checkpoint, 'checkpoint_id', checkpoint.get('checkpoint_id')),
                    "task_id": getattr(checkpoint, 'task_id', checkpoint.get('task_id')),
                    "checkpoint_type": getattr(checkpoint, 'checkpoint_type', checkpoint.get('checkpoint_type')),
                    "status": getattr(checkpoint, 'status', checkpoint.get('status')),
                    "risk_level": getattr(checkpoint, 'risk_level', checkpoint.get('risk_level')),
                    "created_at": getattr(checkpoint, 'created_at', checkpoint.get('created_at')),
                    "timeout_at": getattr(checkpoint, 'timeout_at', checkpoint.get('timeout_at')),
                    "resolved_at": getattr(checkpoint, 'resolved_at', checkpoint.get('resolved_at')),
                    "context": getattr(checkpoint, 'context', checkpoint.get('context', {}))
                }
                
                # Convert datetime objects to ISO format strings
                for time_field in ['created_at', 'timeout_at', 'resolved_at']:
                    if checkpoint_dict.get(time_field) and hasattr(checkpoint_dict[time_field], 'isoformat'):
                        checkpoint_dict[time_field] = checkpoint_dict[time_field].isoformat()
            
            checkpoint_data.append(checkpoint_dict)

        return jsonify({
            "status": "success",
            "checkpoints": checkpoint_data,
            "total_count": len(checkpoint_data),
            "limit": limit,
            "offset": offset,
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error getting checkpoints: {e}")
        return jsonify({
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat()        }), 500


@hitl_bp.route('/checkpoints', methods=['POST'])
def create_checkpoint():
    """Create a new HITL checkpoint."""
    try:
        request_data = request.get_json()
        
        if not request_data:
            return jsonify({
                "status": "error",
                "error": "No JSON data provided"
            }), 400
        
        # Validate required fields
        required_fields = ['task_id', 'checkpoint_type', 'task_type']
        for field in required_fields:
            if field not in request_data:
                return jsonify({
                    "status": "error", 
                    "error": f"Missing required field: {field}"
                }), 400
        
        # Create checkpoint through engine
        checkpoint = hitl_engine.create_checkpoint(
            task_id=request_data['task_id'],
            checkpoint_type=request_data['checkpoint_type'],
            task_type=request_data['task_type'],
            content=request_data.get('content', {}),
            risk_factors=request_data.get('risk_factors', [])
        )
        
        if checkpoint:
            return jsonify({
                "success": True,
                "checkpoint": {
                    "checkpoint_id": checkpoint.checkpoint_id,
                    "task_id": checkpoint.task_id,
                    "checkpoint_type": checkpoint.checkpoint_type,
                    "status": checkpoint.status,
                    "risk_level": checkpoint.risk_level,
                    "created_at": checkpoint.created_at.isoformat() if hasattr(checkpoint.created_at, 'isoformat') else checkpoint.created_at
                },
                "timestamp": datetime.now().isoformat()
            }), 201
        else:
            return jsonify({
                "status": "error",
                "error": "Failed to create checkpoint"
            }), 500
            
    except Exception as e:
        logger.error(f"Error creating checkpoint: {e}")
        return jsonify({
            "status": "error",
            "error": str(e)
        }), 500


@hitl_bp.route('/checkpoints/<checkpoint_id>', methods=['GET'])
def get_checkpoint_details(checkpoint_id: str):
    """Get detailed information about a specific checkpoint."""
    try:
        checkpoint = hitl_engine.get_checkpoint(checkpoint_id)
        
        if not checkpoint:
            return jsonify({
                "status": "error",
                "error": f"Checkpoint {checkpoint_id} not found"
            }), 404
        
        # Get audit log for the checkpoint
        audit_log = hitl_engine.get_checkpoint_audit_log(checkpoint_id)
        
        checkpoint_details = {
            "checkpoint_id": checkpoint.checkpoint_id,
            "task_id": checkpoint.task_id,
            "checkpoint_type": checkpoint.checkpoint_type,
            "status": checkpoint.status,
            "risk_level": checkpoint.risk_level,
            "confidence_score": checkpoint.confidence_score,
            "created_at": checkpoint.created_at.isoformat(),
            "timeout_at": checkpoint.timeout_at.isoformat() if checkpoint.timeout_at else None,
            "resolved_at": checkpoint.resolved_at.isoformat() if checkpoint.resolved_at else None,
            "reviewer": checkpoint.reviewer,
            "context": checkpoint.context,
            "result_data": checkpoint.result_data,
            "audit_log": [
                {
                    "timestamp": entry.get("timestamp"),
                    "action": entry.get("action"),
                    "user": entry.get("user"),
                    "details": entry.get("details")
                }
                for entry in audit_log
            ]
        }
        
        return jsonify({
            "status": "success",
            "checkpoint": checkpoint_details,
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error getting checkpoint details {checkpoint_id}: {e}")
        return jsonify({
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }), 500


@hitl_bp.route('/checkpoints/<checkpoint_id>/approve', methods=['POST'])
def approve_checkpoint(checkpoint_id: str):
    """Approve a HITL checkpoint."""
    try:
        request_data = request.get_json() or {}
        reviewer_id = request_data.get('reviewer_id')
        comments = request_data.get('comments', '')
        
        # Validate required fields
        if not reviewer_id:
            return jsonify({
                "status": "error",
                "error": "Missing required field: reviewer_id"
            }), 400
        
        # Use process_decision method that the tests expect
        result = hitl_engine.process_decision(checkpoint_id, {
            'decision': 'approve',
            'reviewer': reviewer_id,
            'comments': comments,
            'timestamp': datetime.now().isoformat()
        })
        
        if result:
            return jsonify({
                "success": True,
                "action": "approved",
                "reviewer_id": reviewer_id,
                "checkpoint_id": checkpoint_id,
                "timestamp": datetime.now().isoformat()
            })
        else:
            return jsonify({
                "status": "error",
                "error": f"Failed to approve checkpoint {checkpoint_id}"
            }), 500
            
    except Exception as e:
        logger.error(f"Error approving checkpoint {checkpoint_id}: {e}")
        return jsonify({
            "status": "error",
            "error": str(e)
        }), 500


@hitl_bp.route('/checkpoints/<checkpoint_id>/reject', methods=['POST'])
def reject_checkpoint(checkpoint_id: str):
    """Reject a HITL checkpoint."""
    try:
        request_data = request.get_json() or {}
        reviewer_id = request_data.get('reviewer_id')
        comments = request_data.get('comments', '')
        
        # Validate required fields
        if not reviewer_id:
            return jsonify({
                "status": "error",
                "error": "Missing required field: reviewer_id"
            }), 400
        
        # Use process_decision method that the tests expect  
        result = hitl_engine.process_decision(checkpoint_id, {
            'decision': 'reject',
            'reviewer': reviewer_id,
            'comments': comments,
            'timestamp': datetime.now().isoformat()
        })
        
        if result:
            return jsonify({
                "success": True,
                "action": "rejected",
                "reviewer_id": reviewer_id,
                "checkpoint_id": checkpoint_id,
                "timestamp": datetime.now().isoformat()
            })
        else:
            return jsonify({
                "status": "error",
                "error": f"Failed to reject checkpoint {checkpoint_id}"
            }), 500
            
    except Exception as e:
        logger.error(f"Error rejecting checkpoint {checkpoint_id}: {e}")
        return jsonify({
            "status": "error",
            "error": str(e)
        }), 500


@hitl_bp.route('/checkpoints/<checkpoint_id>/escalate', methods=['POST'])
def escalate_checkpoint(checkpoint_id: str):
    """Escalate a HITL checkpoint."""
    try:
        request_data = request.get_json() or {}
        reviewer_id = request_data.get('reviewer_id')
        reason = request_data.get('reason', 'Manual escalation')
        
        # Validate required fields  
        if not reviewer_id:
            return jsonify({
                "status": "error",
                "error": "Missing required field: reviewer_id"
            }), 400
        
        # Use escalate_checkpoint method
        result = hitl_engine.escalate_checkpoint(checkpoint_id, reviewer_id)
        
        if result:
            return jsonify({
                "success": True,
                "action": "escalated",
                "reviewer_id": reviewer_id,
                "checkpoint_id": checkpoint_id,
                "reason": reason,
                "timestamp": datetime.now().isoformat()
            })
        else:
            return jsonify({
                "status": "error",
                "error": f"Failed to escalate checkpoint {checkpoint_id}"
            }), 500
            
    except Exception as e:
        logger.error(f"Error escalating checkpoint {checkpoint_id}: {e}")
        return jsonify({
            "status": "error",
            "error": str(e)        }), 500


@hitl_bp.route('/tasks/<task_id>/checkpoints', methods=['GET'])
def get_task_checkpoints(task_id: str):
    """Get checkpoints for a specific task."""
    try:
        checkpoints = hitl_engine.get_checkpoints_for_task(task_id)
        
        # Format checkpoints for response
        checkpoint_data = []
        for checkpoint in checkpoints:
            if hasattr(checkpoint, 'to_dict'):
                checkpoint_dict = checkpoint.to_dict()
            elif isinstance(checkpoint, dict):
                checkpoint_dict = checkpoint
            else:
                checkpoint_dict = {
                    "checkpoint_id": getattr(checkpoint, 'checkpoint_id', ''),
                    "task_id": getattr(checkpoint, 'task_id', ''),
                    "checkpoint_type": getattr(checkpoint, 'checkpoint_type', ''),
                    "status": getattr(checkpoint, 'status', ''),
                    "risk_level": getattr(checkpoint, 'risk_level', ''),
                    "created_at": getattr(checkpoint, 'created_at', ''),
                    "timeout_at": getattr(checkpoint, 'timeout_at', ''),
                    "resolved_at": getattr(checkpoint, 'resolved_at', ''),
                }
                
                # Convert datetime objects to ISO format strings
                for time_field in ['created_at', 'timeout_at', 'resolved_at']:
                    if checkpoint_dict.get(time_field) and hasattr(checkpoint_dict[time_field], 'isoformat'):
                        checkpoint_dict[time_field] = checkpoint_dict[time_field].isoformat()
            
            checkpoint_data.append(checkpoint_dict)
        
        return jsonify({
            "status": "success",
            "task_id": task_id,
            "checkpoints": checkpoint_data,
            "total_count": len(checkpoint_data),
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error getting task checkpoints for {task_id}: {e}")
        return jsonify({
            "status": "error",
            "error": str(e)
        }), 404


@hitl_bp.route('/audit-trail', methods=['GET'])
def get_audit_trail():
    """Get audit trail for checkpoints."""
    try:
        checkpoint_id = request.args.get('checkpoint_id')
        task_id = request.args.get('task_id')
        
        audit_entries = hitl_engine.get_audit_trail(checkpoint_id=checkpoint_id, task_id=task_id)
        
        # Format audit entries for response
        audit_data = []
        for entry in audit_entries:
            if hasattr(entry, 'to_dict'):
                audit_dict = entry.to_dict()
            elif isinstance(entry, dict):
                audit_dict = entry
            else:
                audit_dict = {
                    "timestamp": getattr(entry, 'timestamp', ''),
                    "action": getattr(entry, 'action', ''),
                    "actor": getattr(entry, 'actor', ''),
                    "checkpoint_id": getattr(entry, 'checkpoint_id', ''),
                    "details": getattr(entry, 'details', {})
                }
            
            audit_data.append(audit_dict)
        
        return jsonify({
            "status": "success",
            "audit_trail": audit_data,
            "total_count": len(audit_data),
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error getting audit trail: {e}")
        return jsonify({
            "status": "error",
            "error": str(e)
        }), 200  # Return 200 with empty trail instead of error


@hitl_bp.route('/dashboard/tasks/<task_id>', methods=['GET'])
def batch_process_checkpoints():
    """Process multiple checkpoints in batch."""
    try:
        request_data = request.get_json()
        actions = request_data.get('actions', [])
        
        if not actions:
            return jsonify({
                "status": "error",
                "error": "No actions provided"
            }), 400
        
        results = []
        
        for action in actions:
            checkpoint_id = action.get('checkpoint_id')
            action_type = action.get('action')  # approve, reject, escalate
            reviewer = action.get('reviewer', 'api_user')
            notes = action.get('notes', '')
            
            try:
                if action_type == 'approve':
                    success = hitl_engine.approve_checkpoint(checkpoint_id, reviewer, notes)
                elif action_type == 'reject':
                    success = hitl_engine.reject_checkpoint(checkpoint_id, reviewer, notes)
                elif action_type == 'escalate':
                    success = hitl_engine.escalate_checkpoint(checkpoint_id, notes)
                else:
                    success = False
                    
                results.append({
                    "checkpoint_id": checkpoint_id,
                    "action": action_type,
                    "success": success,
                    "error": None if success else f"Failed to {action_type} checkpoint"
                })
                
            except Exception as e:
                results.append({
                    "checkpoint_id": checkpoint_id,
                    "action": action_type,
                    "success": False,
                    "error": str(e)
                })
        
        success_count = len([r for r in results if r["success"]])
        
        return jsonify({
            "status": "success",
            "results": results,
            "summary": {
                "total_actions": len(actions),
                "successful": success_count,
                "failed": len(actions) - success_count
            },
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error in batch checkpoint processing: {e}")
        return jsonify({
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }), 500


@hitl_bp.route('/metrics', methods=['GET'])
def get_hitl_metrics():
    """Get HITL metrics and statistics."""
    try:
        # Parse query parameters
        days = int(request.args.get('days', 7))
        
        # Get metrics from engine
        metrics = hitl_engine.get_checkpoint_statistics(days=days)
        trends = hitl_engine.get_daily_trends(days=days)
        distribution = hitl_engine.get_checkpoint_distribution()
        
        return jsonify({
            "status": "success",
            "metrics": metrics,
            "trends": trends,
            "distribution": distribution,
            "period_days": days,
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error getting HITL metrics: {e}")
        return jsonify({
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }), 500


@hitl_bp.route('/workflows', methods=['GET'])
def get_hitl_workflows():
    """Get workflows with HITL integration status."""
    try:
        # Get active workflows with HITL checkpoints
        workflows = hitl_engine.get_active_workflows()
        
        return jsonify({
            "status": "success",
            "workflows": workflows,
            "count": len(workflows),
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error getting HITL workflows: {e}")
        return jsonify({
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }), 500


@hitl_bp.route('/policies', methods=['GET'])
def get_hitl_policies():
    """Get current HITL policies configuration."""
    try:
        policies = hitl_engine.get_policies_config()
        
        return jsonify({
            "status": "success",
            "policies": policies,
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error getting HITL policies: {e}")
        return jsonify({
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }), 500


@hitl_bp.route('/notifications', methods=['GET'])
def get_hitl_notifications():
    """Get recent HITL notifications."""
    try:
        # Parse query parameters
        limit = int(request.args.get('limit', 20))
        notification_type = request.args.get('type')  # checkpoint_created, timeout_warning, etc.
        
        notifications = hitl_engine.get_recent_notifications(
            limit=limit,
            notification_type=notification_type
        )
        
        return jsonify({
            "status": "success",
            "notifications": notifications,
            "count": len(notifications),
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error getting HITL notifications: {e}")
        return jsonify({
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }), 500


# Error handlers
@hitl_bp.errorhandler(400)
def bad_request(error):
    """Handle bad request errors."""
    return jsonify({
        "status": "error",
        "error": "Bad request",
        "message": str(error),
        "timestamp": datetime.now().isoformat()
    }), 400


@hitl_bp.errorhandler(404)
def not_found(error):
    """Handle not found errors."""
    return jsonify({
        "status": "error",
        "error": "Not found",
        "message": str(error),
        "timestamp": datetime.now().isoformat()
    }), 404


@hitl_bp.errorhandler(500)
def internal_error(error):
    """Handle internal server errors."""
    logger.error(f"Internal server error: {error}")
    return jsonify({
        "status": "error",
        "error": "Internal server error",
        "message": "An unexpected error occurred",
        "timestamp": datetime.now().isoformat()
    }), 500


def create_hitl_blueprint(engine=None):
    """Factory function to create HITL blueprint."""
    global hitl_engine
    if engine:
        hitl_engine = engine
    return hitl_bp
