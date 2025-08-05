# HITL Kanban Dashboard - Human-in-the-Loop Review Board

## Overview

The HITL (Human-in-the-Loop) Kanban Dashboard implements the bonus feature from the system implementation plan, providing a comprehensive Kanban-style board for tracking Human-in-the-Loop reviews across the AI agent system.

```
Task ID    Status           Pending Reviewer    Deadline    Action
BE-07      Awaiting QA      QA Agent           4 PM        Review
UX-02      Awaiting Human   UX Lead            6 PM        Approve
PM-05      Approved         —                  —           Completed
```

**Live-updated from `pending_reviews/` and `feedback_logs/`**

## 🚀 Quick Start

### Option 1: PowerShell Launcher (Recommended)
```powershell
# Start the dashboard with automatic dependency checking
.\start-hitl-dashboard.ps1

# Start on specific host/port
.\start-hitl-dashboard.ps1 -Host "0.0.0.0" -Port 8080

# Start in background
.\start-hitl-dashboard.ps1 -Background

# Demo mode only
.\start-hitl-dashboard.ps1 -Demo
```

### Option 2: Quick Status Check
```bash
# Simple status check (no server needed)
python cli/quick_hitl_status.py

# JSON output
python cli/quick_hitl_status.py --json

# Help
python cli/quick_hitl_status.py --help
```

### Option 3: Command Line Interface
```bash
# Rich table display
python dashboard\hitl_kanban_demo.py

# Export to JSON
python dashboard\hitl_kanban_demo.py --export board_data.json

# Simple text format
python dashboard\hitl_kanban_demo.py --simple
```

### Option 4: Web Dashboard Server
```bash
# Start full dashboard server
python dashboard\unified_api_server.py

# Custom host/port
python dashboard\unified_api_server.py --host 0.0.0.0 --port 8080

# Production mode
python dashboard\unified_api_server.py --no-debug
```

## 📊 Features

### Core Functionality
- **Kanban-style Board**: Visual representation matching the system specification
- **Real-time Updates**: Live data from `pending_reviews/` and `feedback_logs/`
- **Priority Sorting**: Automatic prioritization based on risk, deadlines, and age
- **Status Tracking**: Complete workflow status from creation to completion
- **Action Buttons**: One-click approval, rejection, and escalation

### Display Modes
- **Web Dashboard**: Full interactive HTML interface
- **CLI Rich Tables**: Terminal-based rich formatting
- **Simple Text**: Plain text for logging/scripting
- **JSON Export**: Machine-readable data export

### Filtering & Search
- **Task ID Filter**: View specific tasks
- **Status Filter**: Filter by review status
- **Reviewer Filter**: View items by assigned reviewer
- **Priority Filter**: Show high priority or overdue items only
- **Risk Level Filter**: Filter by risk assessment

### Status Categories
- **Awaiting QA**: Technical review required
- **Awaiting Human**: Human approval needed
- **In Review**: Currently being reviewed
- **Escalated**: Requires team lead intervention
- **Approved**: Successfully approved
- **Rejected**: Rejected with feedback
- **Completed**: Fully processed

## 🛠️ Installation

### Prerequisites
```bash
# Required Python packages
pip install flask flask-cors rich

# Optional: For full dashboard integration
pip install -r requirements.txt
```

### File Structure
```
dashboard/
├── hitl_kanban_board.py      # Main Kanban board implementation
├── hitl_kanban_demo.py       # Standalone demo version
├── hitl_widgets.py           # Web dashboard widgets
├── unified_api_server.py     # Flask API server
├── hitl_kanban_board.html    # Web interface
└── hitl_data.json           # Sample data

cli/
├── hitl_kanban_cli.py        # Command line interface
└── quick_hitl_status.py      # Quick status checker

tests/
└── validate_hitl_dashboard.py # Validation script

start-hitl-dashboard.ps1      # PowerShell launcher
```

## 🌐 Web Interface

### Endpoints

| Endpoint | Method | Description |
|----------|---------|-------------|
| `/` | GET | Main Kanban board interface |
| `/demo` | GET | Demo page with mock data |
| `/api/hitl/kanban-data` | GET | Get board data (JSON) |
| `/api/hitl/action` | POST | Process approval actions |
| `/api/hitl/status` | GET | API health check |
| `/api/hitl/export` | GET | Export board data |

### API Usage

#### Get Board Data
```bash
curl http://localhost:8080/api/hitl/kanban-data
```

#### Process Action
```bash
curl -X POST http://localhost:8080/api/hitl/action \
  -H "Content-Type: application/json" \
  -d '{
    "checkpoint_id": "hitl_BE-07_agent_prompt_123",
    "action": "approve",
    "reviewer": "alice",
    "comments": "Looks good to me"
  }'
```

## 📱 Usage Examples

### Daily Standup
```bash
# Quick status for team standup
python cli/quick_hitl_status.py

# Get pending count
python cli/quick_hitl_status.py --json | jq '.summary.pending_count'
```

### CI/CD Integration
```bash
# Check for overdue items in pipeline
OVERDUE=$(python cli/quick_hitl_status.py --json | jq '.summary.overdue_count')
if [ $OVERDUE -gt 0 ]; then
  echo "Warning: $OVERDUE overdue reviews"
  exit 1
fi
```

### Monitoring
```bash
# Export data for monitoring system
python dashboard\hitl_kanban_demo.py --export /monitoring/hitl_status.json

# Watch mode for live monitoring
python dashboard\hitl_kanban_board.py --watch --refresh-interval 30
```

### Team Dashboards
```bash
# Filter by reviewer for individual workload
python cli\hitl_kanban_cli.py --reviewer "QA Agent"

# Show only high priority items
python cli\hitl_kanban_cli.py --high-priority-only

# Overdue items only
python cli\hitl_kanban_cli.py --overdue-only
```

## 🔧 Configuration

### Environment Variables
```bash
# API server configuration
HITL_API_HOST=0.0.0.0
HITL_API_PORT=8080
HITL_API_DEBUG=false

# Dashboard settings
HITL_REFRESH_INTERVAL=30
HITL_MAX_COMPLETED_ITEMS=10
```

### Data Sources

The dashboard automatically detects and aggregates data from:

1. **HITL Engine**: Real-time checkpoint data (if available)
2. **Pending Reviews Directory**: `pending_reviews/*.md` files
3. **Feedback Logs**: `outputs/*/review*.json` files
4. **Task Metadata**: `tasks/*.yaml` files with HITL configuration

### Mock Data Fallback

When real data sources are unavailable, the dashboard automatically falls back to demonstration data:

```json
{
  "task_id": "BE-07",
  "status": "Awaiting QA",
  "pending_reviewer": "QA Agent",
  "deadline": "4 PM",
  "action": "Review",
  "priority": 8,
  "risk_level": "high"
}
```

## 🎨 Customization

### Status Colors
- 🔥 **High Priority**: Red (priority >= 10)
- ⚠️ **Medium Priority**: Yellow (priority 6-9)
- • **Low Priority**: Green (priority < 6)
- 🚨 **Overdue**: Red with alert icon

### Risk Levels
- **Critical**: Immediate attention required
- **High**: Important review needed
- **Medium**: Standard review process
- **Low**: Routine approval

## 🔄 Integration with Phase 7 HITL

This Kanban dashboard is the bonus feature from **Phase 7 Step 7.9** of the system implementation:

> **Bonus: HITL Dashboard View**
> 
> Show team a Kanban-style HITL board:
> 
> | Task ID | Status | Pending Reviewer | Deadline | Action |
> |---------|--------|------------------|----------|---------|
> | BE-07 | Awaiting QA | QA Agent | 4 PM | Review |
> | UX-02 | Awaiting Human | UX Lead | 6 PM | Approve |
> | PM-05 | Approved | — | — | Completed |
> 
> Live-updated from pending_reviews/ and feedback_logs/

### Integration Points

- **HITL Engine**: Direct integration with checkpoint system
- **Review Portal**: Links to `orchestration/review_task.py` 
- **Approval Actions**: Integrates with approval workflow
- **Feedback System**: Reads from `utils/feedback_system.py`
- **Task Metadata**: Uses `orchestration/hitl_task_metadata.py`

## 🚀 Deployment

### Development
```bash
# Start development server
python dashboard\unified_api_server.py --host localhost --port 8080
```

### Production
```bash
# Start production server
python dashboard\unified_api_server.py --host 0.0.0.0 --port 80 --no-debug
```

### Docker (Optional)
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8080
CMD ["python", "dashboard/unified_api_server.py", "--host", "0.0.0.0", "--port", "8080"]
```

## 📊 Monitoring & Metrics

### Health Check
```bash
curl http://localhost:8080/api/hitl/status
```

### Metrics Available
- Total pending reviews
- Overdue item count  
- High priority item count
- Average review time
- Approval/rejection rates
- Reviewer workload distribution

## 🤝 Contributing

The HITL Kanban dashboard is part of the Phase 7 Human-in-the-Loop implementation. For contributions:

1. Follow the existing code structure
2. Maintain compatibility with the HITL engine
3. Test with both real and mock data
4. Update documentation for new features

## 📝 License

Part of the AI Agent System implementation - see main project license.

---

**🎯 Success Criteria Met:**
- ✅ Kanban-style HITL board implemented
- ✅ Real-time status updates
- ✅ Integration with pending_reviews/ and feedback_logs/
- ✅ Priority-based sorting and filtering
- ✅ Web and CLI interfaces
- ✅ Action processing capabilities
- ✅ Export and monitoring features
