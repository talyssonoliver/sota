"""
Human Agent Role Integration System

This module treats human reviewers as agents in the system with:
- Role-based assignment logic
- Workload tracking and balancing  
- Integration with notification system
- Performance monitoring and SLA tracking
"""

import json
import logging
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum
from pathlib import Path

# Configure logging
logger = logging.getLogger(__name__)


class ReviewerRole(Enum):
    """Human reviewer roles with specialized expertise areas"""
    TECHNICAL_LEAD = "Technical Lead"
    UX_LEAD = "UX Lead"  
    BACKEND_ENGINEER = "Backend Engineer"
    FRONTEND_ENGINEER = "Frontend Engineer"
    QA_ANALYST = "QA Analyst"
    PRODUCT_MANAGER = "Product Manager"
    SECURITY_SPECIALIST = "Security Specialist"
    REVIEWER_AGENT = "Reviewer Agent"
    APPROVER_AGENT = "Approver Agent"
    CURATOR_AGENT = "Curator Agent"


class ReviewPriority(Enum):
    """Review priority levels"""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"
    CRITICAL = "critical"


class ReviewStatus(Enum):
    """Review assignment status"""
    ASSIGNED = "assigned"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    EXPIRED = "expired"
    CANCELLED = "cancelled"


@dataclass
class ReviewAssignment:
    """Represents a review assignment to a human agent"""
    task_id: str
    reviewer: str
    assigned_at: datetime
    urgency: str = "normal"
    estimated_duration: int = 30  # minutes
    deadline: Optional[datetime] = None
    status: str = "assigned"
    context: Optional[Dict] = None
    
    def __post_init__(self):
        """Set deadline based on urgency if not provided"""
        if self.deadline is None:
            urgency_hours = {
                "low": 24,
                "normal": 8,
                "high": 4,
                "urgent": 2,
                "critical": 1
            }
            hours = urgency_hours.get(self.urgency, 8)
            self.deadline = self.assigned_at + timedelta(hours=hours)
    
    def is_expired(self) -> bool:
        """Check if assignment has expired"""
        return datetime.now() > self.deadline
    
    def time_remaining(self) -> timedelta:
        """Get remaining time for assignment"""
        return self.deadline - datetime.now()
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization"""
        result = asdict(self)
        result['assigned_at'] = self.assigned_at.isoformat()
        if self.deadline:
            result['deadline'] = self.deadline.isoformat()
        return result


@dataclass
class AssignmentResult:
    """Result of assignment attempt"""
    success: bool
    reason: str
    assignment: Optional[ReviewAssignment] = None
    
    
class WorkloadTracker:
    """Tracks workload and capacity for human reviewers"""
    
    def __init__(self, max_concurrent: int = 5, max_daily: int = 20):
        self.max_concurrent = max_concurrent
        self.max_daily = max_daily
        self.active_assignments: List[ReviewAssignment] = []
        self.completed_today: List[ReviewAssignment] = []
        
    def has_capacity(self) -> bool:
        """Check if reviewer has capacity for new assignments"""
        active_count = len([a for a in self.active_assignments if not a.is_expired()])
        today = datetime.now().date()
        daily_count = len([a for a in self.completed_today 
                          if a.assigned_at.date() == today])
        
        return active_count < self.max_concurrent and daily_count < self.max_daily
    
    def add_assignment(self, assignment: ReviewAssignment) -> AssignmentResult:
        """Add new assignment if capacity allows"""
        if not self.has_capacity():
            return AssignmentResult(
                success=False,
                reason="Reviewer at capacity limit"
            )
        
        self.active_assignments.append(assignment)
        logger.info(f"Assignment added for {assignment.reviewer}: {assignment.task_id}")
        
        return AssignmentResult(
            success=True,
            reason="Assignment created successfully",
            assignment=assignment
        )
    
    def complete_assignment(self, task_id: str) -> bool:
        """Mark assignment as completed"""
        for assignment in self.active_assignments:
            if assignment.task_id == task_id:
                assignment.status = "completed"
                self.completed_today.append(assignment)
                self.active_assignments.remove(assignment)
                logger.info(f"Assignment completed: {task_id}")
                return True
        return False
    
    def get_workload_summary(self) -> Dict:
        """Get current workload summary"""
        active_count = len([a for a in self.active_assignments if not a.is_expired()])
        today = datetime.now().date()
        daily_count = len([a for a in self.completed_today 
                          if a.assigned_at.date() == today])
        
        return {
            "active_assignments": active_count,
            "max_concurrent": self.max_concurrent,
            "completed_today": daily_count,
            "max_daily": self.max_daily,
            "has_capacity": self.has_capacity(),
            "expired_assignments": len([a for a in self.active_assignments if a.is_expired()])
        }


class HumanReviewerAgent:
    """Human reviewer agent with role-based capabilities"""
    
    def __init__(self, role: str, expertise: List[str], availability: Dict,
                 max_concurrent: int = 5, max_daily: int = 20):
        self.role = role
        self.expertise = expertise
        self.availability = availability
        self.workload = WorkloadTracker(max_concurrent, max_daily)
        self.performance_metrics = {
            "total_reviews": 0,
            "avg_response_time": 0,
            "approval_rate": 0.0,
            "quality_score": 0.0
        }
        
    def can_review(self, task: Dict) -> bool:
        """Check if this reviewer can handle the task"""
        # Check expertise match
        required_expertise = task.get('required_expertise', [])
        has_expertise = any(exp in self.expertise for exp in required_expertise)
        
        # Check availability and capacity  
        return (
            has_expertise and
            self.workload.has_capacity() and
            self.is_available()
        )
    
    def is_available(self) -> bool:
        """Check if reviewer is currently available"""
        # Simplified availability check - could be enhanced with calendar integration
        current_hour = datetime.now().hour
        working_hours = self.availability.get("working_hours", "9-17")
        start_hour, end_hour = map(int, working_hours.split("-"))
        
        return start_hour <= current_hour <= end_hour
    
    def assign_review(self, task_id: str, urgency: str = "normal", 
                     context: Optional[Dict] = None) -> AssignmentResult:
        """Assign review task to this human agent"""
        task = context or {}
        
        if not self.can_review(task):
            return AssignmentResult(
                success=False, 
                reason="Capacity or expertise mismatch"
            )
            
        assignment = ReviewAssignment(
            task_id=task_id,
            reviewer=self.role,
            assigned_at=datetime.now(),
            urgency=urgency,
            estimated_duration=self.estimate_review_duration(task),
            context=context
        )
        
        return self.workload.add_assignment(assignment)
    
    def estimate_review_duration(self, task: Dict) -> int:
        """Estimate review duration in minutes based on task complexity"""
        complexity = task.get('complexity', 'medium')
        task_type = task.get('type', 'general')
        
        base_times = {
            'low': 15,
            'medium': 30, 
            'high': 60,
            'critical': 90
        }
        
        type_multipliers = {
            'security': 1.5,
            'infrastructure': 1.3,
            'backend': 1.2,
            'frontend': 1.0,
            'design': 0.8
        }
        
        base_time = base_times.get(complexity, 30)
        multiplier = type_multipliers.get(task_type, 1.0)
        
        return int(base_time * multiplier)
    
    def get_active_assignments(self) -> List[ReviewAssignment]:
        """Get current active assignments"""
        return [a for a in self.workload.active_assignments if not a.is_expired()]
    
    def get_performance_summary(self) -> Dict:
        """Get performance metrics summary"""
        workload_summary = self.workload.get_workload_summary()
        return {
            **self.performance_metrics,
            **workload_summary,
            "role": self.role,
            "expertise": self.expertise,
            "availability": self.availability
        }


class HumanAgentRegistry:
    """Registry and management system for human agents"""
    
    def __init__(self):
        self.agents: Dict[str, HumanReviewerAgent] = {}
        self.assignment_history: List[ReviewAssignment] = []
        self._initialize_default_agents()
        
    def _initialize_default_agents(self):
        """Initialize default human agents based on requirements"""
        default_agents = {
            "technical_lead": HumanReviewerAgent(
                role="Technical Lead",
                expertise=["architecture", "security", "performance", "code_review"],
                availability={"timezone": "PST", "working_hours": "9-17"}
            ),
            "ux_lead": HumanReviewerAgent(
                role="UX Lead", 
                expertise=["design", "accessibility", "user_experience", "usability"],
                availability={"timezone": "EST", "working_hours": "8-16"}
            ),
            "backend_engineer": HumanReviewerAgent(
                role="Backend Engineer",
                expertise=["api_design", "database", "backend_logic", "microservices"],
                availability={"timezone": "GMT", "working_hours": "9-17"}
            ),
            "frontend_engineer": HumanReviewerAgent(
                role="Frontend Engineer",
                expertise=["ui_components", "react", "javascript", "css"],
                availability={"timezone": "PST", "working_hours": "10-18"}
            ),
            "qa_analyst": HumanReviewerAgent(
                role="QA Analyst",
                expertise=["testing", "automation", "quality_assurance", "bug_detection"],
                availability={"timezone": "EST", "working_hours": "9-17"}
            ),
            "product_manager": HumanReviewerAgent(
                role="Product Manager",
                expertise=["product_strategy", "user_stories", "requirements", "roadmap"],
                availability={"timezone": "PST", "working_hours": "8-17"}
            ),
            "security_specialist": HumanReviewerAgent(
                role="Security Specialist",
                expertise=["security", "vulnerability_assessment", "compliance", "encryption"],
                availability={"timezone": "GMT", "working_hours": "9-17"}
            )
        }
        
        self.agents.update(default_agents)
        logger.info(f"Initialized {len(default_agents)} default human agents")
    
    def register_agent(self, agent_id: str, agent: HumanReviewerAgent):
        """Register a new human agent"""
        self.agents[agent_id] = agent
        logger.info(f"Registered human agent: {agent_id} ({agent.role})")
    
    def find_best_reviewer(self, task: Dict, exclude: List[str] = None) -> Optional[Tuple[str, HumanReviewerAgent]]:
        """Find the best available reviewer for a task"""
        exclude = exclude or []
        candidates = []
        
        for agent_id, agent in self.agents.items():
            if agent_id in exclude:
                continue
                
            if agent.can_review(task):
                # Score based on expertise match and availability
                expertise_score = len(set(agent.expertise) & set(task.get('required_expertise', [])))
                workload_score = 1.0 / max(1, len(agent.get_active_assignments()))
                total_score = expertise_score + workload_score
                
                candidates.append((total_score, agent_id, agent))
        
        if candidates:
            # Return highest scoring candidate
            candidates.sort(key=lambda x: x[0], reverse=True)
            _, agent_id, agent = candidates[0]
            return agent_id, agent
        
        return None
    
    def assign_review(self, task_id: str, task_context: Dict, 
                     urgency: str = "normal", preferred_reviewer: str = None) -> AssignmentResult:
        """Assign a review task to the best available human agent"""
        
        # Try preferred reviewer first
        if preferred_reviewer and preferred_reviewer in self.agents:
            agent = self.agents[preferred_reviewer]
            if agent.can_review(task_context):
                result = agent.assign_review(task_id, urgency, task_context)
                if result.success:
                    self.assignment_history.append(result.assignment)
                    logger.info(f"Assigned {task_id} to preferred reviewer {preferred_reviewer}")
                    return result
        
        # Find best available reviewer
        best_match = self.find_best_reviewer(task_context)
        if not best_match:
            return AssignmentResult(
                success=False,
                reason="No available reviewers found for this task"
            )
        
        agent_id, agent = best_match
        result = agent.assign_review(task_id, urgency, task_context)
        
        if result.success:
            self.assignment_history.append(result.assignment)
            logger.info(f"Assigned {task_id} to {agent_id} ({agent.role})")
        
        return result
    
    def complete_assignment(self, task_id: str, reviewer_id: str) -> bool:
        """Mark an assignment as completed"""
        if reviewer_id in self.agents:
            success = self.agents[reviewer_id].workload.complete_assignment(task_id)
            if success:
                logger.info(f"Completed assignment {task_id} for {reviewer_id}")
            return success
        return False
    
    def get_registry_status(self) -> Dict:
        """Get overall registry status and metrics"""
        total_capacity = sum(agent.workload.max_concurrent for agent in self.agents.values())
        current_load = sum(len(agent.get_active_assignments()) for agent in self.agents.values())
        
        agent_statuses = {}
        for agent_id, agent in self.agents.items():
            agent_statuses[agent_id] = agent.get_performance_summary()
        
        return {
            "total_agents": len(self.agents),
            "total_capacity": total_capacity,
            "current_load": current_load,
            "utilization": current_load / max(1, total_capacity),
            "agents": agent_statuses,
            "assignment_history_count": len(self.assignment_history)
        }
    
    def save_registry_state(self, filepath: str):
        """Save registry state to file"""
        try:
            state = {
                "timestamp": datetime.now().isoformat(),
                "agents": {
                    agent_id: {
                        "role": agent.role,
                        "expertise": agent.expertise,
                        "availability": agent.availability,
                        "performance_metrics": agent.performance_metrics,
                        "workload_summary": agent.workload.get_workload_summary()
                    }
                    for agent_id, agent in self.agents.items()
                },
                "assignment_history": [
                    assignment.to_dict() for assignment in self.assignment_history[-100:]  # Last 100
                ]
            }
            
            Path(filepath).parent.mkdir(parents=True, exist_ok=True)
            with open(filepath, 'w') as f:
                json.dump(state, f, indent=2)
                
            logger.info(f"Registry state saved to {filepath}")
            
        except Exception as e:
            logger.error(f"Failed to save registry state: {e}")


# Global registry instance
HUMAN_AGENT_REGISTRY = HumanAgentRegistry()

# Convenience access to pre-configured agents
HUMAN_AGENTS = HUMAN_AGENT_REGISTRY.agents


def get_human_agent_registry() -> HumanAgentRegistry:
    """Get the global human agent registry"""
    return HUMAN_AGENT_REGISTRY


def assign_human_review(task_id: str, task_context: Dict, 
                       urgency: str = "normal", preferred_reviewer: str = None) -> AssignmentResult:
    """Convenience function to assign human review"""
    return HUMAN_AGENT_REGISTRY.assign_review(task_id, task_context, urgency, preferred_reviewer)


def complete_human_review(task_id: str, reviewer_id: str) -> bool:
    """Convenience function to complete human review"""
    return HUMAN_AGENT_REGISTRY.complete_assignment(task_id, reviewer_id)


def get_available_reviewers(task_context: Dict = None) -> List[Tuple[str, str]]:
    """Get list of available reviewers for a task"""
    task_context = task_context or {}
    available = []
    
    for agent_id, agent in HUMAN_AGENTS.items():
        if agent.can_review(task_context):
            available.append((agent_id, agent.role))
    
    return available


if __name__ == "__main__":
    # Example usage and testing
    registry = get_human_agent_registry()
    
    # Test assignment
    test_task = {
        "type": "backend",
        "required_expertise": ["api_design", "database"],
        "complexity": "medium"
    }
    
    result = assign_human_review("BE-123", test_task, urgency="high")
    print(f"Assignment result: {result.success} - {result.reason}")
    
    # Print registry status
    status = registry.get_registry_status()
    print(f"Registry status: {status['total_agents']} agents, {status['utilization']:.2%} utilization")
