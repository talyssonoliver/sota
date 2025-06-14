#!/usr/bin/env python3
"""
Sample Test Data
"""

SAMPLE_TASKS = [
    {
        "task_id": "BE-01",
        "title": "Setup database schema",
        "description": "Create initial database schema for user management",
        "status": "completed",
        "agent_type": "backend"
    },
    {
        "task_id": "FE-01", 
        "title": "Create login page",
        "description": "Design and implement user login interface",
        "status": "in_progress",
        "agent_type": "frontend"
    },
    {
        "task_id": "QA-01",
        "title": "Test user registration",
        "description": "Comprehensive testing of user registration flow",
        "status": "pending",
        "agent_type": "qa"
    }
]

SAMPLE_MEMORY_DATA = [
    {
        "content": "The system uses a microservices architecture",
        "metadata": {"type": "architecture", "priority": "high"}
    },
    {
        "content": "User authentication is handled by JWT tokens", 
        "metadata": {"type": "security", "priority": "medium"}
    }
]

SAMPLE_API_RESPONSES = {
    "/api/health": {"status": "ok", "timestamp": "2025-06-13T10:00:00Z"},
    "/api/tasks": {"tasks": SAMPLE_TASKS, "total": len(SAMPLE_TASKS)}
}
