#!/usr/bin/env python3
"""
Demo: Step 4.6 — Agent Summarisation

Demonstrates the automated task completion summary generation system.
This example shows how to use the TaskSummarizer to analyze agent outputs,
extract artifacts, and generate completion reports.

Usage:
    python examples/demo_step_4_6_summarization.py
"""

import json
import os
import sys
import tempfile
from datetime import datetime
from pathlib import Path

from orchestration.summarise_task import (AgentOutput, QAResults, TaskArtifact,
                                          TaskSummarizer)

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def create_demo_structure(temp_dir: Path, task_id: str):
    """Create a demo file structure for testing."""
    print(f"📁 Creating demo file structure for task {task_id}...")

    # Create directory structure
    outputs_dir = temp_dir / "outputs" / task_id
    outputs_dir.mkdir(parents=True)

    context_store_dir = temp_dir / "context-store"
    context_store_dir.mkdir(parents=True)

    code_dir = outputs_dir / "code"
    code_dir.mkdir()

    # Create status.json (Step 4.4 output)
    status_data = {
        'agent_outputs': [
            {
                'agent_id': 'backend_agent',
                'timestamp': '2024-01-15T10:30:00',
                'status': 'completed',
                'files_generated': [
                    'src/api/routes.py',
                    'src/models/user.py',
                    'tests/test_api.py'],
                'files_modified': [
                    'src/main.py',
                    'requirements.txt'],
                'metadata': {
                    'lines_added': 245,
                    'endpoints_created': 5,
                    'models_implemented': 2}},
            {
                'agent_id': 'frontend_agent',
                'timestamp': '2024-01-15T11:15:00',
                            'status': 'completed',
                            'files_generated': [
                                'src/components/UserProfile.tsx',
                                'src/pages/Dashboard.tsx'],
                'files_modified': [
                                'src/App.tsx',
                                'package.json'],
                'metadata': {
                                'components_created': 2,
                                'pages_updated': 1,
                                'dependencies_added': 3}},
            {
                'agent_id': 'documentation_agent',
                'timestamp': '2024-01-15T12:00:00',
                'status': 'completed',
                'files_generated': [
                    'docs/api.md',
                    'docs/frontend-guide.md',
                    'README.md'],
                'files_modified': [],
                'metadata': {
                    'pages_generated': 3,
                    'endpoints_documented': 5}}]}

    with open(outputs_dir / "status.json", 'w') as f:
        json.dump(status_data, f, indent=2)

    # Create QA report
    qa_data = {'test_coverage': 87.5,
               'tests_passed': 24,
               'tests_failed': 2,
               'critical_issues': 1,
               'warnings': 5,
               'overall_status': 'passed_with_warnings',
               'detailed_findings': [{'severity': 'critical',
                                      'message': 'SQL injection vulnerability in user search endpoint',
                                      'file': 'src/api/routes.py',
                                      'line': 45},
                                     {'severity': 'warning',
                                      'message': 'Missing error handling in UserProfile component',
                                      'file': 'src/components/UserProfile.tsx',
                                      'line': 23},
                                     {'severity': 'warning',
                                      'message': 'Deprecated API usage in dashboard',
                                      'file': 'src/pages/Dashboard.tsx',
                                      'line': 67},
                                     {'severity': 'info',
                                      'message': 'Consider adding loading states for better UX',
                                      'file': 'src/components/UserProfile.tsx',
                                      'line': 15}]}

    with open(outputs_dir / "qa_report.json", 'w') as f:
        json.dump(qa_data, f, indent=2)

    # Create task metadata
    task_metadata = {
        'tasks': [
            {
                'id': task_id,
                'title': 'User Profile Management System',
                'description': 'Implement user profile management with backend API and frontend interface',
                'start_date': '2024-01-15T09:00:00',
                'dependencies': [
                    'AUTH-01',
                    'DB-02'],
                'priority': 'high',
                'estimated_hours': 16,
                'assigned_agents': [
                    'backend_agent',
                    'frontend_agent',
                    'documentation_agent']}]}

    with open(context_store_dir / "agent_task_assignments.json", 'w') as f:
        json.dump(task_metadata, f, indent=2)

    # Create some actual code files (Step 4.5 extraction)
    (code_dir / "src" / "api").mkdir(parents=True)
    (code_dir / "src" / "models").mkdir(parents=True)
    (code_dir / "src" / "components").mkdir(parents=True)
    (code_dir / "src" / "pages").mkdir(parents=True)
    (code_dir / "tests").mkdir(parents=True)
    (code_dir / "docs").mkdir(parents=True)

    # Backend code
    with open(code_dir / "src" / "api" / "routes.py", 'w') as f:
        f.write("""# API Routes for User Management
from flask import Flask, request, jsonify
from models.user import User

app = Flask(__name__)

@app.route('/api/users', methods=['GET'])
def get_users():
    \"\"\"Get all users\"\"\"
    users = User.query.all()
    return jsonify([user.to_dict() for user in users])

@app.route('/api/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    \"\"\"Get user by ID\"\"\"
    user = User.query.get_or_404(user_id)
    return jsonify(user.to_dict())

@app.route('/api/users/search', methods=['GET'])
def search_users():
    \"\"\"Search users by name\"\"\"
    query = request.args.get('q')
    # SECURITY ISSUE: Direct SQL query - vulnerable to injection
    users = User.query.filter(f"name LIKE '%{query}%'").all()
    return jsonify([user.to_dict() for user in users])
""")

    with open(code_dir / "src" / "models" / "user.py", 'w') as f:
        f.write("""# User Model
from sqlalchemy import Column, Integer, String, DateTime
from database import Base

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    username = Column(String(80), unique=True, nullable=False)
    email = Column(String(120), unique=True, nullable=False)
    created_at = Column(DateTime, nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'created_at': self.created_at.isoformat()
        }
""")

    # Frontend code
    with open(code_dir / "src" / "components" / "UserProfile.tsx", 'w') as f:
        f.write("""// User Profile Component
import React, { useState, useEffect } from 'react';

interface User {
  id: number;
  username: string;
  email: string;
  created_at: string;
}

export const UserProfile: React.FC<{ userId: number }> = ({ userId }) => {
  const [user, setUser] = useState<User | null>(null);

  useEffect(() => {
    // TODO: Add loading state
    fetch(`/api/users/${userId}`)
      .then(response => response.json())
      .then(setUser);
      // Missing error handling
  }, [userId]);

  if (!user) return <div>Loading...</div>;

  return (
    <div className="user-profile">
      <h2>{user.username}</h2>
      <p>Email: {user.email}</p>
      <p>Member since: {new Date(user.created_at).toLocaleDateString()}</p>
    </div>
  );
};
""")

    with open(code_dir / "src" / "pages" / "Dashboard.tsx", 'w') as f:
        f.write("""// Dashboard Page
import React, { useState, useEffect } from 'react';
import { UserProfile } from '../components/UserProfile';

export const Dashboard: React.FC = () => {
  const [users, setUsers] = useState([]);
  const [selectedUser, setSelectedUser] = useState(null);

  useEffect(() => {
    // Using deprecated API method
    fetchUsers().then(setUsers);
  }, []);

  const fetchUsers = async () => {
    const response = await fetch('/api/users');
    return response.json();
  };

  return (
    <div className="dashboard">
      <h1>User Dashboard</h1>
      <div className="users-list">
        {users.map(user => (
          <div key={user.id} onClick={() => setSelectedUser(user.id)}>
            {user.username}
          </div>
        ))}
      </div>
      {selectedUser && <UserProfile userId={selectedUser} />}
    </div>
  );
};
""")

    # Test files
    with open(code_dir / "tests" / "test_api.py", 'w') as f:
        f.write("""# API Tests
import pytest
from app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_get_users(client):
    \"\"\"Test getting all users\"\"\"
    response = client.get('/api/users')
    assert response.status_code == 200
    assert isinstance(response.json, list)

def test_get_user_by_id(client):
    \"\"\"Test getting user by ID\"\"\"
    response = client.get('/api/users/1')
    assert response.status_code in [200, 404]

def test_search_users(client):
    \"\"\"Test user search functionality\"\"\"
    response = client.get('/api/users/search?q=john')
    assert response.status_code == 200
""")

    # Documentation
    with open(code_dir / "docs" / "api.md", 'w') as f:
        f.write("""# User Management API

## Endpoints

### GET /api/users
Returns a list of all users.

**Response:**
```json
[
  {
    "id": 1,
    "username": "john_doe",
    "email": "john@example.com",
    "created_at": "2024-01-15T10:00:00"
  }
]
```

### GET /api/users/{id}
Returns a specific user by ID.

### GET /api/users/search?q={query}
Search users by name.

**Note:** This endpoint is currently vulnerable to SQL injection.
""")

    # Config file
    with open(code_dir / "package.json", 'w') as f:
        f.write("""{
  "name": "user-profile-system",
  "version": "1.0.0",
  "dependencies": {
    "react": "^18.2.0",
    "typescript": "^5.0.0"
  }
}
""")

    print(f"✅ Demo structure created successfully!")
    return temp_dir


def run_demo():
    """Run the Step 4.6 summarization demo."""
    print("🚀 Step 4.6 — Agent Summarisation Demo")
    print("=" * 50)

    task_id = "DEMO-46"

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)

        # Create demo structure
        demo_dir = create_demo_structure(temp_path, task_id)

        # Initialize TaskSummarizer
        print(f"\n🔍 Initializing TaskSummarizer for {task_id}...")
        summarizer = TaskSummarizer(task_id, str(demo_dir))

        # Run full analysis
        print(f"\n📊 Running comprehensive task analysis...")
        summary = summarizer.analyze_task_completion()

        # Display results
        print(f"\n📋 Task Summary Results:")
        print(f"   Task ID: {summary.task_id}")
        print(f"   Title: {summary.task_title}")
        print(f"   Status: {summary.completion_status}")
        print(f"   Completion Date: {summary.completion_date}")

        print(f"\n📂 Agent Outputs:")
        for output in summary.agent_outputs:
            print(f"   • {output.agent_id}: {output.status}")
            print(f"     Generated: {len(output.files_generated)} files")
            print(f"     Modified: {len(output.files_modified)} files")

        print(f"\n🔧 Artifacts Generated:")
        artifact_types = {}
        for artifact in summary.artifacts:
            artifact_types[artifact.type] = artifact_types.get(
                artifact.type, 0) + 1

        for artifact_type, count in artifact_types.items():
            print(f"   • {artifact_type.title()}: {count} files")

        print(f"\n🧪 Quality Assurance:")
        if summary.qa_results:
            qa = summary.qa_results
            print(f"   • Test Coverage: {qa.test_coverage}%")
            print(f"   • Tests Passed: {qa.tests_passed}")
            print(f"   • Tests Failed: {qa.tests_failed}")
            print(f"   • Critical Issues: {qa.critical_issues}")
            print(f"   • Warnings: {qa.warnings}")
            print(f"   • Overall Status: {qa.overall_status}")

        print(f"\n📈 Summary Statistics:")
        print(f"   • Total Files Created: {summary.total_files_created}")
        print(f"   • Total Files Modified: {summary.total_files_modified}")
        print(f"   • Total Code Lines: {summary.total_code_lines:,}")

        print(f"\n🎯 Next Steps:")
        for i, step in enumerate(summary.next_steps, 1):
            print(f"   {i}. {step}")

        # Generate and save report
        print(f"\n📄 Generating markdown report...")
        report_path = summarizer.save_completion_report(summary)

        print(f"\n✅ Demo completed successfully!")
        print(f"📄 Report would be saved to: {report_path}")

        # Show a snippet of the generated report
        markdown_content = summarizer.generate_markdown_report(summary)
        print(f"\n📝 Report Preview (first 1000 chars):")
        print("=" * 50)
        print(markdown_content[:1000] +
              "..." if len(markdown_content) > 1000 else markdown_content)


if __name__ == "__main__":
    run_demo()
