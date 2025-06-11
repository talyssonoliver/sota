"""
Tests for Human Agent Role Integration System
Step 7.6 of Phase 7 Human-in-the-Loop Implementation
"""

import pytest
import json
from datetime import datetime, timedelta
from unittest.mock import patch, Mock

from agents.human_agents import (
    HumanReviewerAgent,
    WorkloadTracker,
    ReviewAssignment,
    AssignmentResult,
    HumanAgentRegistry,
    ReviewerRole,
    ReviewPriority,
    ReviewStatus,
    HUMAN_AGENT_REGISTRY,
    assign_human_review,
    complete_human_review,
    get_available_reviewers,
    get_human_agent_registry
)


class TestReviewAssignment:
    """Test ReviewAssignment functionality"""
    
    def test_review_assignment_creation(self):
        """Test basic review assignment creation"""
        assignment = ReviewAssignment(
            task_id="BE-123",
            reviewer="technical_lead",
            assigned_at=datetime.now(),
            urgency="high"
        )
        
        assert assignment.task_id == "BE-123"
        assert assignment.reviewer == "technical_lead"
        assert assignment.urgency == "high"
        assert assignment.status == "assigned"
        assert assignment.deadline is not None
        
    def test_deadline_calculation(self):
        """Test automatic deadline calculation based on urgency"""
        now = datetime.now()
        
        # Test different urgency levels
        urgency_hours = {
            "low": 24,
            "normal": 8,
            "high": 4,
            "urgent": 2,
            "critical": 1
        }
        
        for urgency, expected_hours in urgency_hours.items():
            assignment = ReviewAssignment(
                task_id=f"TEST-{urgency}",
                reviewer="test_reviewer",
                assigned_at=now,
                urgency=urgency
            )
            
            expected_deadline = now + timedelta(hours=expected_hours)
            # Allow 1 minute tolerance for processing time
            assert abs((assignment.deadline - expected_deadline).total_seconds()) < 60
    
    def test_expiration_checking(self):
        """Test assignment expiration logic"""
        past_time = datetime.now() - timedelta(hours=2)
        future_time = datetime.now() + timedelta(hours=2)
        
        # Expired assignment
        expired_assignment = ReviewAssignment(
            task_id="EXPIRED-01",
            reviewer="test_reviewer",
            assigned_at=past_time,
            deadline=past_time + timedelta(hours=1)
        )
        
        # Active assignment
        active_assignment = ReviewAssignment(
            task_id="ACTIVE-01",
            reviewer="test_reviewer",
            assigned_at=datetime.now(),
            deadline=future_time
        )
        
        assert expired_assignment.is_expired()
        assert not active_assignment.is_expired()
    
    def test_serialization(self):
        """Test assignment to_dict conversion"""
        assignment = ReviewAssignment(
            task_id="SERIAL-01",
            reviewer="test_reviewer",
            assigned_at=datetime.now(),
            urgency="normal"
        )
        
        assignment_dict = assignment.to_dict()
        
        assert assignment_dict["task_id"] == "SERIAL-01"
        assert assignment_dict["reviewer"] == "test_reviewer"
        assert assignment_dict["urgency"] == "normal"
        assert "assigned_at" in assignment_dict
        assert "deadline" in assignment_dict


class TestWorkloadTracker:
    """Test WorkloadTracker functionality"""
    
    def test_workload_tracker_initialization(self):
        """Test workload tracker initialization"""
        tracker = WorkloadTracker(max_concurrent=3, max_daily=10)
        
        assert tracker.max_concurrent == 3
        assert tracker.max_daily == 10
        assert len(tracker.active_assignments) == 0
        assert len(tracker.completed_today) == 0
        assert tracker.has_capacity()
    
    def test_capacity_checking(self):
        """Test capacity checking logic"""
        tracker = WorkloadTracker(max_concurrent=2, max_daily=5)
        
        # Add assignments up to concurrent limit
        assignment1 = ReviewAssignment("TASK-1", "reviewer", datetime.now())
        assignment2 = ReviewAssignment("TASK-2", "reviewer", datetime.now())
        
        result1 = tracker.add_assignment(assignment1)
        result2 = tracker.add_assignment(assignment2)
        
        assert result1.success
        assert result2.success
        assert not tracker.has_capacity()  # At concurrent limit
        
        # Try to add another - should fail
        assignment3 = ReviewAssignment("TASK-3", "reviewer", datetime.now())
        result3 = tracker.add_assignment(assignment3)
        
        assert not result3.success
        assert "capacity limit" in result3.reason
    
    def test_assignment_completion(self):
        """Test assignment completion workflow"""
        tracker = WorkloadTracker()
        
        assignment = ReviewAssignment("COMPLETE-01", "reviewer", datetime.now())
        tracker.add_assignment(assignment)
        
        assert len(tracker.active_assignments) == 1
        assert len(tracker.completed_today) == 0
        
        # Complete the assignment
        success = tracker.complete_assignment("COMPLETE-01")
        
        assert success
        assert len(tracker.active_assignments) == 0
        assert len(tracker.completed_today) == 1
        assert tracker.completed_today[0].status == "completed"
    
    def test_workload_summary(self):
        """Test workload summary generation"""
        tracker = WorkloadTracker(max_concurrent=5, max_daily=20)
        
        # Add some assignments
        for i in range(3):
            assignment = ReviewAssignment(f"SUMMARY-{i}", "reviewer", datetime.now())
            tracker.add_assignment(assignment)
        
        summary = tracker.get_workload_summary()
        
        assert summary["active_assignments"] == 3
        assert summary["max_concurrent"] == 5
        assert summary["completed_today"] == 0
        assert summary["max_daily"] == 20
        assert summary["has_capacity"] is True
        assert summary["expired_assignments"] == 0


class TestHumanReviewerAgent:
    """Test HumanReviewerAgent functionality"""
    
    def test_agent_initialization(self):
        """Test human reviewer agent initialization"""
        agent = HumanReviewerAgent(
            role="Technical Lead",
            expertise=["architecture", "security"],
            availability={"timezone": "PST", "working_hours": "9-17"}
        )
        
        assert agent.role == "Technical Lead"
        assert agent.expertise == ["architecture", "security"]
        assert agent.availability["timezone"] == "PST"
        assert isinstance(agent.workload, WorkloadTracker)
        assert "total_reviews" in agent.performance_metrics
    
    def test_expertise_matching(self):
        """Test task expertise matching"""
        agent = HumanReviewerAgent(
            role="Backend Engineer",
            expertise=["api_design", "database", "microservices"],
            availability={"working_hours": "9-17"}
        )
        
        # Task that matches expertise
        matching_task = {
            "required_expertise": ["api_design", "database"],
            "type": "backend"
        }
        
        # Task that doesn't match
        non_matching_task = {
            "required_expertise": ["ui_design", "frontend"],
            "type": "frontend"
        }
        
        with patch.object(agent, 'is_available', return_value=True):
            assert agent.can_review(matching_task)
            assert not agent.can_review(non_matching_task)
    
    @patch('agents.human_agents.datetime')
    def test_availability_checking(self, mock_datetime):
        """Test availability checking based on working hours"""
        # Mock current time to 10 AM (within working hours)
        mock_datetime.now.return_value.hour = 10
        
        agent = HumanReviewerAgent(
            role="Test Agent",
            expertise=["testing"],
            availability={"working_hours": "9-17"}
        )
        
        assert agent.is_available()
        
        # Mock current time to 8 PM (outside working hours)
        mock_datetime.now.return_value.hour = 20
        assert not agent.is_available()
    
    def test_review_assignment(self):
        """Test review assignment to agent"""
        agent = HumanReviewerAgent(
            role="QA Analyst",
            expertise=["testing", "quality_assurance"],
            availability={"working_hours": "9-17"}
        )
        
        task_context = {
            "required_expertise": ["testing"],
            "type": "qa",
            "complexity": "medium"
        }
        
        with patch.object(agent, 'can_review', return_value=True):
            result = agent.assign_review("QA-123", "high", task_context)
            
            assert result.success
            assert result.assignment is not None
            assert result.assignment.task_id == "QA-123"
            assert result.assignment.urgency == "high"
    
    def test_duration_estimation(self):
        """Test review duration estimation"""
        agent = HumanReviewerAgent(
            role="Test Agent",
            expertise=["testing"],
            availability={}
        )
        
        # Test different complexity levels
        test_cases = [
            ({"complexity": "low"}, 15),
            ({"complexity": "medium"}, 30),
            ({"complexity": "high"}, 60),
            ({"complexity": "critical"}, 90)
        ]
        
        for task, expected_base in test_cases:
            duration = agent.estimate_review_duration(task)
            assert duration >= expected_base * 0.8  # Allow for type multipliers
    
    def test_performance_summary(self):
        """Test performance summary generation"""
        agent = HumanReviewerAgent(
            role="Performance Test Agent",
            expertise=["performance"],
            availability={"timezone": "PST"}
        )
        
        summary = agent.get_performance_summary()
        
        assert summary["role"] == "Performance Test Agent"
        assert summary["expertise"] == ["performance"]
        assert summary["availability"]["timezone"] == "PST"
        assert "total_reviews" in summary
        assert "has_capacity" in summary


class TestHumanAgentRegistry:
    """Test HumanAgentRegistry functionality"""
    
    def test_registry_initialization(self):
        """Test registry initialization with default agents"""
        registry = HumanAgentRegistry()
        
        # Should have default agents
        assert len(registry.agents) >= 7  # At least 7 default agents
        assert "technical_lead" in registry.agents
        assert "ux_lead" in registry.agents
        assert "backend_engineer" in registry.agents
        assert len(registry.assignment_history) == 0
    
    def test_agent_registration(self):
        """Test manual agent registration"""
        registry = HumanAgentRegistry()
        initial_count = len(registry.agents)
        
        custom_agent = HumanReviewerAgent(
            role="Custom Specialist",
            expertise=["custom_skill"],
            availability={"timezone": "UTC"}
        )
        
        registry.register_agent("custom_specialist", custom_agent)
        
        assert len(registry.agents) == initial_count + 1
        assert "custom_specialist" in registry.agents
        assert registry.agents["custom_specialist"].role == "Custom Specialist"
    
    def test_best_reviewer_finding(self):
        """Test finding best reviewer for task"""
        registry = HumanAgentRegistry()
        
        task = {
            "required_expertise": ["security", "architecture"],
            "type": "security",
            "complexity": "high"
        }
        
        # Mock can_review to return True for specific agents
        with patch.object(registry.agents["technical_lead"], 'can_review', return_value=True), \
             patch.object(registry.agents["security_specialist"], 'can_review', return_value=True):
            
            result = registry.find_best_reviewer(task)
            
            assert result is not None
            agent_id, agent = result
            assert agent_id in ["technical_lead", "security_specialist"]
            assert isinstance(agent, HumanReviewerAgent)
    
    def test_review_assignment_workflow(self):
        """Test complete review assignment workflow"""
        registry = HumanAgentRegistry()
        
        task_context = {
            "required_expertise": ["api_design"],
            "type": "backend",
            "complexity": "medium"
        }
        
        # Mock can_review for backend engineer
        with patch.object(registry.agents["backend_engineer"], 'can_review', return_value=True):
            result = registry.assign_review("WORKFLOW-01", task_context, "high")
            
            assert result.success
            assert result.assignment is not None
            assert len(registry.assignment_history) == 1
            
            # Complete the assignment
            completion_success = registry.complete_assignment("WORKFLOW-01", "backend_engineer")
            assert completion_success
    
    def test_registry_status(self):
        """Test registry status reporting"""
        registry = HumanAgentRegistry()
        
        status = registry.get_registry_status()
        
        assert "total_agents" in status
        assert "total_capacity" in status
        assert "current_load" in status
        assert "utilization" in status
        assert "agents" in status
        assert status["total_agents"] >= 7
        assert isinstance(status["utilization"], float)
    
    def test_preferred_reviewer(self):
        """Test preferred reviewer assignment"""
        registry = HumanAgentRegistry()
        
        task_context = {
            "required_expertise": ["design"],
            "type": "frontend"
        }
        
        # Mock can_review for UX lead
        with patch.object(registry.agents["ux_lead"], 'can_review', return_value=True):
            result = registry.assign_review(
                "PREFERRED-01", 
                task_context, 
                preferred_reviewer="ux_lead"
            )
            
            assert result.success
            assert result.assignment.reviewer == "UX Lead"


class TestConvenienceFunctions:
    """Test convenience functions and global registry"""
    
    def test_global_registry_access(self):
        """Test global registry access"""
        registry = get_human_agent_registry()
        assert isinstance(registry, HumanAgentRegistry)
        assert registry is HUMAN_AGENT_REGISTRY
    
    def test_assign_human_review_function(self):
        """Test convenience assign_human_review function"""
        task_context = {
            "required_expertise": ["testing"],
            "type": "qa"
        }
        
        # Mock global registry
        with patch('agents.human_agents.HUMAN_AGENT_REGISTRY') as mock_registry:
            mock_result = AssignmentResult(success=True, reason="Test assignment")
            mock_registry.assign_review.return_value = mock_result
            
            result = assign_human_review("CONV-01", task_context, "normal")
            
            assert result.success
            mock_registry.assign_review.assert_called_once_with(
                "CONV-01", task_context, "normal", None
            )
    
    def test_complete_human_review_function(self):
        """Test convenience complete_human_review function"""
        with patch('agents.human_agents.HUMAN_AGENT_REGISTRY') as mock_registry:
            mock_registry.complete_assignment.return_value = True
            
            result = complete_human_review("CONV-02", "technical_lead")
            
            assert result is True
            mock_registry.complete_assignment.assert_called_once_with(
                "CONV-02", "technical_lead"
            )
    
    def test_get_available_reviewers_function(self):
        """Test get_available_reviewers function"""
        task_context = {"required_expertise": ["security"]}
        
        # Mock agents with some available
        mock_agents = {
            "agent1": Mock(),
            "agent2": Mock(),
            "agent3": Mock()
        }
        
        mock_agents["agent1"].can_review.return_value = True
        mock_agents["agent1"].role = "Security Expert"
        mock_agents["agent2"].can_review.return_value = False
        mock_agents["agent3"].can_review.return_value = True
        mock_agents["agent3"].role = "Tech Lead"
        
        with patch('agents.human_agents.HUMAN_AGENTS', mock_agents):
            available = get_available_reviewers(task_context)
            
            assert len(available) == 2
            assert ("agent1", "Security Expert") in available
            assert ("agent3", "Tech Lead") in available


class TestIntegrationScenarios:
    """Test realistic integration scenarios"""
    
    def test_high_load_scenario(self):
        """Test behavior under high load"""
        registry = HumanAgentRegistry()
        
        # Set low capacity for testing
        for agent in registry.agents.values():
            agent.workload.max_concurrent = 2
        
        task_context = {
            "required_expertise": ["architecture"],
            "type": "backend"
        }
        
        assignments = []
        
        # Mock can_review to always return True
        with patch.object(registry.agents["technical_lead"], 'can_review', return_value=True):
            # Assign up to capacity
            for i in range(3):  # One more than capacity
                result = registry.assign_review(f"LOAD-{i}", task_context)
                assignments.append(result)
        
        # First two should succeed, third should fail
        assert assignments[0].success
        assert assignments[1].success
        assert not assignments[2].success
        assert "capacity" in assignments[2].reason.lower()
    
    def test_no_available_reviewers_scenario(self):
        """Test scenario where no reviewers are available"""
        registry = HumanAgentRegistry()
        
        task_context = {
            "required_expertise": ["unknown_skill"],
            "type": "unknown_type"
        }
        
        # Mock all agents to return False for can_review using explicit patch calls
        with patch.object(registry.agents["technical_lead"], 'can_review', return_value=False), \
             patch.object(registry.agents["ux_lead"], 'can_review', return_value=False), \
             patch.object(registry.agents["backend_engineer"], 'can_review', return_value=False), \
             patch.object(registry.agents["frontend_engineer"], 'can_review', return_value=False), \
             patch.object(registry.agents["qa_analyst"], 'can_review', return_value=False), \
             patch.object(registry.agents["product_manager"], 'can_review', return_value=False), \
             patch.object(registry.agents["security_specialist"], 'can_review', return_value=False):
            
            result = registry.assign_review("NO-REVIEWERS", task_context)
            
            assert not result.success
            assert "no available reviewers" in result.reason.lower()
    
    def test_escalation_scenario(self):
        """Test escalation when assignments expire"""
        registry = HumanAgentRegistry()
        
        # Create assignment that's already expired
        past_time = datetime.now() - timedelta(hours=2)
        expired_assignment = ReviewAssignment(
            task_id="EXPIRED-ESCALATE",
            reviewer="technical_lead",
            assigned_at=past_time,
            deadline=past_time + timedelta(hours=1),
            urgency="critical"
        )
        
        # Add expired assignment to agent workload
        registry.agents["technical_lead"].workload.active_assignments.append(expired_assignment)
        
        # Check workload summary shows expired assignments
        summary = registry.agents["technical_lead"].workload.get_workload_summary()
        assert summary["expired_assignments"] > 0
    
    def test_cross_timezone_assignment(self):
        """Test assignment across different timezones"""
        registry = HumanAgentRegistry()
        
        # Get agents in different timezones
        pst_agent = registry.agents["technical_lead"]  # PST
        est_agent = registry.agents["ux_lead"]         # EST
        gmt_agent = registry.agents["backend_engineer"] # GMT
        
        assert pst_agent.availability["timezone"] == "PST"
        assert est_agent.availability["timezone"] == "EST"
        assert gmt_agent.availability["timezone"] == "GMT"
        
        # Test that timezone info is preserved
        task_context = {"required_expertise": ["architecture"]}
        
        with patch.object(pst_agent, 'can_review', return_value=True):
            result = registry.assign_review("TIMEZONE-01", task_context, preferred_reviewer="technical_lead")
            
            assert result.success
            assert result.assignment.reviewer == "Technical Lead"


class TestHITLIntegration:
    """Test integration with existing HITL system"""
    
    def test_hitl_checkpoint_integration(self):
        """Test integration with HITL checkpoint system"""
        from orchestration.hitl_engine import HITLPolicyEngine, HITLCheckpoint
        
        registry = HumanAgentRegistry()
        
        # Create HITL engine mock
        hitl_engine = Mock(spec=HITLPolicyEngine)
        
        # Test that human agents can be referenced in HITL system
        # Simulate checkpoint reviewers matching our registry
        test_reviewers = ["technical_lead", "backend_engineer"]
        
        # Verify reviewers exist in registry
        for reviewer_id in test_reviewers:
            assert reviewer_id in registry.agents
            
        # Test assignment integration
        task_context = {
            "required_expertise": ["api_design"],
            "type": "backend"
        }
        
        # Mock can_review for backend engineer
        with patch.object(registry.agents["backend_engineer"], 'can_review', return_value=True):
            result = registry.assign_review("HITL-INTEGRATION", task_context)
            assert result.success
    
    def test_notification_integration(self):
        """Test integration with notification system"""
        registry = HumanAgentRegistry()
        
        task_context = {
            "required_expertise": ["security"],
            "type": "security",
            "urgency": "critical"
        }
        
        # Mock notification system
        with patch('agents.human_agents.logger') as mock_logger:
            with patch.object(registry.agents["security_specialist"], 'can_review', return_value=True):
                result = registry.assign_review("NOTIFY-01", task_context, "critical")
                
                assert result.success
                # Verify logging (which could trigger notifications)
                mock_logger.info.assert_called()
                
                # Check that critical urgency is preserved
                assert result.assignment.urgency == "critical"


if __name__ == "__main__":
    # Run basic functionality test
    print("Testing Human Agent Role Integration System...")
    
    # Test basic assignment workflow
    registry = get_human_agent_registry()
    print(f"Registry initialized with {len(registry.agents)} agents")
    
    # Test task assignment
    test_task = {
        "type": "backend",
        "required_expertise": ["api_design"],
        "complexity": "medium"
    }
    
    result = assign_human_review("TEST-123", test_task, urgency="high")
    print(f"Assignment result: {result.success} - {result.reason}")
    
    if result.success:
        print(f"Assigned to: {result.assignment.reviewer}")
        print(f"Deadline: {result.assignment.deadline}")
        
        # Complete the assignment
        completion = complete_human_review("TEST-123", "backend_engineer")
        print(f"Completion successful: {completion}")
    
    # Print registry status
    status = registry.get_registry_status()
    print(f"Registry utilization: {status['utilization']:.1%}")
    
    print("Human Agent Role Integration System tests completed!")
