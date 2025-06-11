#!/usr/bin/env python3
"""
HITL Dashboard API Server

Flask API server for the HITL Kanban dashboard providing real-time data
and action endpoints for the web interface.
"""

import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any
from flask import Flask, jsonify, request, render_template_string, send_from_directory
from flask_cors import CORS

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

try:
    from dashboard.hitl_widgets import HITLDashboardManager, get_hitl_kanban_data, process_hitl_action
    from dashboard.hitl_kanban_board import HITLKanbanBoard
    DASHBOARD_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Dashboard components not available: {e}")
    DASHBOARD_AVAILABLE = False

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Initialize dashboard components
if DASHBOARD_AVAILABLE:
    dashboard_manager = HITLDashboardManager()
    kanban_board = HITLKanbanBoard()
else:
    dashboard_manager = None
    kanban_board = None


@app.route('/')
def index():
    """Serve the HITL Kanban board HTML page."""
    try:
        html_file = Path(__file__).parent / 'hitl_kanban_board.html'
        with open(html_file, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return jsonify({"error": "HITL Kanban board HTML not found"}), 404


@app.route('/api/hitl/kanban-data')
def get_kanban_data():
    """Get HITL Kanban board data."""
    try:
        if not DASHBOARD_AVAILABLE:
            # Return mock data if dashboard components not available
            return jsonify({
                "pending_reviews": [
                    {
                        "task_id": "BE-07",
                        "status": "Awaiting QA",
                        "pending_reviewer": "QA Agent",
                        "deadline": "4 PM",
                        "action": "Review",
                        "priority": 8,
                        "checkpoint_type": "agent_prompt",
                        "risk_level": "high",
                        "overdue": False,
                        "time_remaining": "4h"
                    },
                    {
                        "task_id": "UX-02",
                        "status": "Awaiting Human",
                        "pending_reviewer": "UX Lead",
                        "deadline": "6 PM",
                        "action": "Approve",
                        "priority": 6,
                        "checkpoint_type": "task_transitions",
                        "risk_level": "medium",
                        "overdue": False,
                        "time_remaining": "2h"
                    },
                    {
                        "task_id": "PM-05",
                        "status": "Approved",
                        "pending_reviewer": "—",
                        "deadline": "—",
                        "action": "Completed",
                        "priority": 0,
                        "checkpoint_type": "documentation",
                        "risk_level": "low",
                        "overdue": False,
                        "time_remaining": "—"
                    },
                    {
                        "task_id": "FE-12",
                        "status": "Escalated",
                        "pending_reviewer": "Team Lead",
                        "deadline": "Overdue by 2h",
                        "action": "Resolve",
                        "priority": 12,
                        "checkpoint_type": "output_evaluation",
                        "risk_level": "critical",
                        "overdue": True,
                        "time_remaining": "Overdue by 2h"
                    }
                ],
                "summary": {
                    "total_pending": 4,
                    "overdue_count": 1,
                    "high_priority_count": 2,
                    "last_updated": datetime.now().isoformat()
                },
                "filters": {
                    "risk_levels": ["low", "medium", "high", "critical"],
                    "task_types": ["BE", "UX", "PM", "FE"],
                    "checkpoint_types": ["agent_prompt", "task_transitions", "documentation", "output_evaluation"]
                }
            })
        
        # Get real data from dashboard
        data = get_hitl_kanban_data()
        return jsonify(data)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/hitl/dashboard-data')
def get_dashboard_data():
    """Get complete dashboard data."""
    try:
        if not DASHBOARD_AVAILABLE:
            return jsonify({"error": "Dashboard components not available"}), 503
        
        data = dashboard_manager.get_dashboard_data()
        return jsonify(data)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/hitl/action', methods=['POST'])
def process_action():
    """Process a HITL approval action."""
    try:
        if not DASHBOARD_AVAILABLE:
            return jsonify({"error": "Dashboard components not available"}), 503
        
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400
        
        checkpoint_id = data.get('checkpoint_id')
        action = data.get('action')
        reviewer = data.get('reviewer', 'unknown')
        comments = data.get('comments', '')
        
        if not checkpoint_id or not action:
            return jsonify({"error": "checkpoint_id and action are required"}), 400
        
        success = process_hitl_action(checkpoint_id, action, reviewer, comments)
        
        return jsonify({
            "success": success,
            "message": f"Action '{action}' {'processed successfully' if success else 'failed'}"
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/hitl/widget/<widget_name>')
def get_widget_data(widget_name):
    """Get data for a specific widget."""
    try:
        if not DASHBOARD_AVAILABLE:
            return jsonify({"error": "Dashboard components not available"}), 503
        
        data = dashboard_manager.get_widget_data(widget_name)
        return jsonify(data)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/hitl/export')
def export_board_data():
    """Export current board data."""
    try:
        if not DASHBOARD_AVAILABLE:
            return jsonify({"error": "Dashboard components not available"}), 503
        
        # Export board data
        export_filename = f"hitl_board_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        kanban_board.export_board_data(export_filename)
        
        return jsonify({
            "success": True,
            "filename": export_filename,
            "message": "Board data exported successfully"
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/hitl/status')
def get_api_status():
    """Get API status and health check."""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "dashboard_available": DASHBOARD_AVAILABLE,
        "endpoints": [
            "/api/hitl/kanban-data",
            "/api/hitl/dashboard-data",
            "/api/hitl/action",
            "/api/hitl/widget/<widget_name>",
            "/api/hitl/export",
            "/api/hitl/status"
        ]
    })


@app.route('/demo')
def demo_page():
    """Serve a demo page with mock data."""
    return render_template_string("""
<!DOCTYPE html>
<html>
<head>
    <title>HITL Kanban Demo</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .board { background: #f5f5f5; padding: 20px; border-radius: 8px; }
        .item { background: white; margin: 10px 0; padding: 15px; border-radius: 4px; border-left: 4px solid #007bff; }
        .overdue { border-left-color: #dc3545; }
        .high-priority { border-left-color: #ffc107; }
        .approved { border-left-color: #28a745; }
        .button { background: #007bff; color: white; padding: 8px 16px; border: none; border-radius: 4px; cursor: pointer; margin: 5px; }
        .button:hover { background: #0056b3; }
    </style>
</head>
<body>
    <h1>🔄 HITL Kanban Board Demo</h1>
    <p>This demo shows the Kanban-style board for Human-in-the-Loop reviews.</p>
    
    <div class="board">
        <h2>Current Review Queue</h2>
        
        <div class="item high-priority">
            <strong>BE-07</strong> - Awaiting QA<br>
            <em>Reviewer:</em> QA Agent<br>
            <em>Deadline:</em> 4 PM<br>
            <button class="button">Review</button>
        </div>
        
        <div class="item">
            <strong>UX-02</strong> - Awaiting Human<br>
            <em>Reviewer:</em> UX Lead<br>
            <em>Deadline:</em> 6 PM<br>
            <button class="button">Approve</button>
        </div>
        
        <div class="item approved">
            <strong>PM-05</strong> - Approved<br>
            <em>Reviewer:</em> —<br>
            <em>Status:</em> Completed<br>
        </div>
        
        <div class="item overdue">
            <strong>FE-12</strong> - Escalated<br>
            <em>Reviewer:</em> Team Lead<br>
            <em>Deadline:</em> Overdue by 2h<br>
            <button class="button">Resolve</button>
        </div>
    </div>
    
    <p><strong>Features:</strong></p>
    <ul>
        <li>Real-time status updates</li>
        <li>Priority-based sorting</li>
        <li>Deadline tracking with overdue alerts</li>
        <li>One-click approval actions</li>
        <li>Live updates from pending_reviews/ and feedback_logs/</li>
    </ul>
    
    <p><a href="/">← Back to Full Dashboard</a></p>
    
    <script>
        // Demo functionality
        document.querySelectorAll('.button').forEach(btn => {
            btn.addEventListener('click', function() {
                alert('In production, this would process the action: ' + this.textContent);
            });
        });
    </script>
</body>
</html>
    """)


def run_server(host='0.0.0.0', port=8080, debug=True):
    """Run the Flask server."""
    print(f"🚀 Starting HITL Dashboard API Server")
    print(f"📊 Dashboard available: {DASHBOARD_AVAILABLE}")
    print(f"🌐 Server URL: http://{host}:{port}")
    print(f"🔄 Kanban Board: http://{host}:{port}/")
    print(f"🎮 Demo Page: http://{host}:{port}/demo")
    print(f"📡 API Status: http://{host}:{port}/api/hitl/status")
    
    app.run(host=host, port=port, debug=debug)


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='HITL Dashboard API Server')
    parser.add_argument('--host', default='0.0.0.0', help='Host to bind to')
    parser.add_argument('--port', type=int, default=8080, help='Port to bind to')
    parser.add_argument('--no-debug', action='store_true', help='Disable debug mode')
    
    args = parser.parse_args()
    
    run_server(
        host=args.host,
        port=args.port,
        debug=not args.no_debug
    )