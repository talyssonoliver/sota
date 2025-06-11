"""
Test Suite for Step 7.5: Automated Escalation System
Tests comprehensive escalation functionality with policy-driven notifications and timeouts.
"""

import pytest
import json
import os
import tempfile
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, List, Optional

# Import the escalation system components (to be implemented)
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.escalation_system import (
    EscalationLevel,
    EscalationRule,
    EscalationEvent,
    EscalationEngine,
    EscalationNotifier,
    EscalationTracker,
    EscalationPolicy,
    EscalationTimer
)


class TestEscalationLevel:
    """Test escalation level definitions and validation"""
    
    def test_escalation_levels_exist(self):
        """Test that all required escalation levels are defined"""
        assert hasattr(EscalationLevel, 'LEVEL_1')
        assert hasattr(EscalationLevel, 'LEVEL_2') 
        assert hasattr(EscalationLevel, 'LEVEL_3')
        assert hasattr(EscalationLevel, 'LEVEL_4')
        
    def test_escalation_level_ordering(self):
        """Test that escalation levels have proper ordering"""
        assert EscalationLevel.LEVEL_1.value < EscalationLevel.LEVEL_2.value
        assert EscalationLevel.LEVEL_2.value < EscalationLevel.LEVEL_3.value
        assert EscalationLevel.LEVEL_3.value < EscalationLevel.LEVEL_4.value
        
    def test_escalation_level_attributes(self):
        """Test that escalation levels have required attributes"""
        for level in EscalationLevel:
            assert hasattr(level, 'timeout_hours')
            assert hasattr(level, 'recipients')
            assert hasattr(level, 'notification_channels')


class TestEscalationRule:
    """Test escalation rule definition and validation"""
    
    def test_escalation_rule_creation(self):
        """Test creating escalation rules with proper validation"""
        rule = EscalationRule(
            task_type="backend",
            risk_level="high",
            trigger_conditions=["timeout", "rejection"],
            escalation_path=[EscalationLevel.LEVEL_1, EscalationLevel.LEVEL_2],
            auto_escalate=True,
            notification_template="high_risk_escalation"
        )
        
        assert rule.task_type == "backend"
        assert rule.risk_level == "high" 
        assert "timeout" in rule.trigger_conditions
        assert len(rule.escalation_path) == 2
        assert rule.auto_escalate is True
        
    def test_escalation_rule_validation(self):
        """Test escalation rule validation"""
        # Test invalid task type
        with pytest.raises(ValueError, match="Invalid task type"):
            EscalationRule(
                task_type="invalid",
                risk_level="high",
                trigger_conditions=["timeout"],
                escalation_path=[EscalationLevel.LEVEL_1]
            )
            
        # Test invalid risk level
        with pytest.raises(ValueError, match="Invalid risk level"):
            EscalationRule(
                task_type="backend",
                risk_level="invalid",
                trigger_conditions=["timeout"],
                escalation_path=[EscalationLevel.LEVEL_1]
            )


class TestEscalationEvent:
    """Test escalation event tracking and management"""
    
    def test_escalation_event_creation(self):
        """Test creating escalation events"""
        event = EscalationEvent(
            task_id="BE-123",
            trigger="timeout",
            level=EscalationLevel.LEVEL_1,
            triggered_at=datetime.now(),
            triggered_by="system",
            context={"review_duration": 120, "reviewer": "john.doe"}
        )
        
        assert event.task_id == "BE-123"
        assert event.trigger == "timeout"
        assert event.level == EscalationLevel.LEVEL_1
        assert event.triggered_by == "system"
        assert event.context["review_duration"] == 120
        
    def test_escalation_event_serialization(self):
        """Test escalation event serialization for persistence"""
        event = EscalationEvent(
            task_id="FE-456",
            trigger="rejection",
            level=EscalationLevel.LEVEL_2,
            triggered_at=datetime.now(),
            triggered_by="reviewer",
            context={"rejection_reason": "security_concerns"}
        )
        
        serialized = event.to_dict()
        assert serialized["task_id"] == "FE-456"
        assert serialized["trigger"] == "rejection"
        assert "triggered_at" in serialized
        
        # Test deserialization
        restored = EscalationEvent.from_dict(serialized)
        assert restored.task_id == event.task_id
        assert restored.trigger == event.trigger


class TestEscalationNotifier:
    """Test escalation notification system"""
    
    def setUp(self):
        self.notifier = EscalationNotifier()
        
    def test_notifier_initialization(self):
        """Test escalation notifier initialization"""
        notifier = EscalationNotifier()
        assert hasattr(notifier, 'notification_channels')
        assert hasattr(notifier, 'templates')
        
    def test_send_escalation_notification(self):
        """Test sending escalation notifications"""
        notifier = EscalationNotifier()
        
        event = EscalationEvent(
            task_id="BE-789",
            trigger="timeout",
            level=EscalationLevel.LEVEL_1,
            triggered_at=datetime.now(),
            triggered_by="system",
            context={"timeout_duration": 3600}
        )
        
        recipients = ["team.lead@company.com", "senior.engineer@company.com"]
        channels = ["email", "slack"]
        
        # Mock the notification methods
        with patch.object(notifier, '_send_email', return_value=True) as mock_email, \
             patch.object(notifier, '_send_slack', return_value=True) as mock_slack:
            
            result = notifier.send_notification(event, recipients, channels)
            
            assert result["success"] is True
            assert "email" in result["channels_used"]
            assert "slack" in result["channels_used"]
            mock_email.assert_called_once()
            mock_slack.assert_called_once()
        
    def test_notification_template_rendering(self):
        """Test escalation notification template rendering"""
        notifier = EscalationNotifier()
        
        context = {
            "task_id": "BE-101",
            "trigger": "timeout",
            "timeout_duration": 7200,
            "reviewer": "alice.smith",
            "escalation_level": "Level 2"
        }
        
        rendered = notifier.render_template("timeout_escalation", context)
        
        assert "BE-101" in rendered
        assert "timeout" in rendered
        assert "Level 2" in rendered


class TestEscalationTracker:
    """Test escalation tracking and persistence"""
    
    def setUp(self):
        self.tracker = EscalationTracker()
        
    def test_tracker_initialization(self):
        """Test escalation tracker initialization"""
        with tempfile.TemporaryDirectory() as temp_dir:
            tracker = EscalationTracker(storage_path=temp_dir)
            assert os.path.exists(os.path.join(temp_dir, "escalations.json"))
            
    def test_track_escalation_event(self):
        """Test tracking escalation events"""
        with tempfile.TemporaryDirectory() as temp_dir:
            tracker = EscalationTracker(storage_path=temp_dir)
            
            event = EscalationEvent(
                task_id="QA-202",
                trigger="rejection",
                level=EscalationLevel.LEVEL_1,
                triggered_at=datetime.now(),
                triggered_by="reviewer",
                context={"rejection_count": 2}
            )
            
            tracker.track_event(event)
            
            # Verify event was stored
            events = tracker.get_events_for_task("QA-202")
            assert len(events) == 1
            assert events[0].trigger == "rejection"
            
    def test_get_escalation_history(self):
        """Test retrieving escalation history"""
        with tempfile.TemporaryDirectory() as temp_dir:
            tracker = EscalationTracker(storage_path=temp_dir)
              # Add multiple events
            for i in range(3):
                event = EscalationEvent(
                    task_id=f"TASK-{i}",
                    trigger="timeout",
                    level=EscalationLevel.LEVEL_1,
                    triggered_at=datetime.now() - timedelta(hours=i),
                    triggered_by="system",
                    context={}
                )
                tracker.track_event(event)
                
            history = tracker.get_escalation_history(days=1)
            assert len(history) == 3
            
    def test_escalation_metrics(self):
        """Test escalation metrics calculation"""
        with tempfile.TemporaryDirectory() as temp_dir:
            tracker = EscalationTracker(storage_path=temp_dir)
            # Add test events
            events = [
                EscalationEvent("TASK-1", "timeout", EscalationLevel.LEVEL_1, datetime.now(), "system", {}),
                EscalationEvent("TASK-2", "rejection", EscalationLevel.LEVEL_2, datetime.now(), "reviewer", {}),
                EscalationEvent("TASK-3", "timeout", EscalationLevel.LEVEL_1, datetime.now(), "system", {})
            ]
            
            for event in events:
                tracker.track_event(event)
                
            metrics = tracker.calculate_metrics(days=1)
            
            assert metrics["total_escalations"] == 3
            assert metrics["timeout_escalations"] == 2
            assert metrics["rejection_escalations"] == 1
            assert metrics["level_1_escalations"] == 2
            assert metrics["level_2_escalations"] == 1


class TestEscalationTimer:
    """Test escalation timer functionality"""
    
    def test_timer_creation(self):
        """Test creating escalation timers"""
        timer = EscalationTimer(
            task_id="BE-303",
            timeout_hours=2,
            callback=lambda: None,
            level=EscalationLevel.LEVEL_1
        )
        
        assert timer.task_id == "BE-303"
        assert timer.timeout_hours == 2
        assert timer.level == EscalationLevel.LEVEL_1
        assert not timer.is_expired()
        
    def test_timer_expiration(self):
        """Test timer expiration detection"""
        # Create timer with past start time
        timer = EscalationTimer(
            task_id="BE-404",
            timeout_hours=1,
            callback=lambda: None,
            level=EscalationLevel.LEVEL_1,
            start_time=datetime.now() - timedelta(hours=2)
        )
        
        assert timer.is_expired()
        
    @patch('utils.escalation_system.threading.Timer')
    def test_timer_scheduling(self, mock_timer):
        """Test timer scheduling and execution"""
        callback = Mock()
        
        timer = EscalationTimer(
            task_id="BE-505",
            timeout_hours=1,
            callback=callback,
            level=EscalationLevel.LEVEL_1
        )
        
        timer.start()
        
        mock_timer.assert_called_once()
        assert timer.is_active()


class TestEscalationPolicy:
    """Test escalation policy management"""
    
    def test_policy_loading(self):
        """Test loading escalation policies from configuration"""
        policy = EscalationPolicy()
        
        # Test default policies exist
        assert "backend" in policy.policies
        assert "frontend" in policy.policies
        assert "default" in policy.policies
        
    def test_policy_evaluation(self):
        """Test evaluating escalation policies for tasks"""
        policy = EscalationPolicy()
        
        # Test backend task policy
        rule = policy.get_escalation_rule("backend", "high")
        assert rule is not None
        assert rule.task_type == "backend"
        assert rule.risk_level == "high"
        
    def test_policy_customization(self):
        """Test customizing escalation policies"""
        policy = EscalationPolicy()
        
        custom_rule = EscalationRule(
            task_type="custom",
            risk_level="critical",
            trigger_conditions=["immediate"],
            escalation_path=[EscalationLevel.LEVEL_4],
            auto_escalate=True
        )
        
        policy.add_custom_rule("custom_critical", custom_rule)
        
        retrieved_rule = policy.get_escalation_rule("custom", "critical")
        assert retrieved_rule.task_type == "custom"
        assert retrieved_rule.escalation_path[0] == EscalationLevel.LEVEL_4


class TestEscalationEngine:
    """Test main escalation engine functionality"""
    
    def setUp(self):
        self.engine = EscalationEngine()
        
    def test_engine_initialization(self):
        """Test escalation engine initialization"""
        engine = EscalationEngine()
        
        assert hasattr(engine, 'policy')
        assert hasattr(engine, 'notifier')
        assert hasattr(engine, 'tracker')
        assert hasattr(engine, 'timers')
        
    @patch('utils.escalation_system.EscalationNotifier')
    @patch('utils.escalation_system.EscalationTracker')
    def test_handle_timeout_escalation(self, mock_tracker, mock_notifier):
        """Test handling timeout-based escalations"""
        engine = EscalationEngine()
        
        task_data = {
            "task_id": "BE-606",
            "task_type": "backend",
            "risk_level": "high",
            "reviewer": "john.doe",
            "review_start": datetime.now() - timedelta(hours=3)
        }
        
        result = engine.handle_timeout_escalation(task_data)
        
        assert result["escalated"] is True
        assert result["level"] == EscalationLevel.LEVEL_1
        mock_tracker.return_value.track_event.assert_called_once()
        mock_notifier.return_value.send_notification.assert_called_once()
        
    @patch('utils.escalation_system.EscalationNotifier')
    @patch('utils.escalation_system.EscalationTracker')
    def test_handle_rejection_escalation(self, mock_tracker, mock_notifier):
        """Test handling rejection-based escalations"""
        engine = EscalationEngine()
        
        rejection_data = {
            "task_id": "FE-707",
            "task_type": "frontend",
            "risk_level": "medium",
            "reviewer": "alice.smith",
            "rejection_reason": "code_quality_issues",
            "rejection_count": 2
        }
        
        result = engine.handle_rejection_escalation(rejection_data)
        
        assert result["escalated"] is True
        assert result["reason"] == "multiple_rejections"
        
    def test_determine_escalation_level(self):
        """Test determining appropriate escalation level"""
        engine = EscalationEngine()
        
        # Test Level 1 escalation
        level = engine.determine_escalation_level("backend", "medium", "timeout", {"duration": 3600})
        assert level == EscalationLevel.LEVEL_1
        
        # Test Level 2 escalation  
        level = engine.determine_escalation_level("backend", "high", "timeout", {"duration": 7200})
        assert level == EscalationLevel.LEVEL_2
        
        # Test Level 3 escalation
        level = engine.determine_escalation_level("backend", "critical", "rejection", {"rejection_count": 3})
        assert level == EscalationLevel.LEVEL_3
        
    def test_schedule_escalation_timer(self):
        """Test scheduling escalation timers"""
        engine = EscalationEngine()
        
        task_data = {
            "task_id": "QA-808",
            "task_type": "qa",
            "risk_level": "low",
            "timeout_hours": 24
        }
        
        timer_id = engine.schedule_escalation_timer(task_data)
        
        assert timer_id is not None
        assert timer_id in engine.timers
        assert engine.timers[timer_id].task_id == "QA-808"
        
    def test_cancel_escalation_timer(self):
        """Test canceling escalation timers"""
        engine = EscalationEngine()
        
        # Schedule a timer
        task_data = {
            "task_id": "UX-909",
            "task_type": "design",
            "risk_level": "low",
            "timeout_hours": 12
        }
        
        timer_id = engine.schedule_escalation_timer(task_data)
        assert timer_id in engine.timers
        
        # Cancel the timer
        result = engine.cancel_escalation_timer(timer_id)
        assert result is True
        assert timer_id not in engine.timers


class TestEscalationIntegration:
    """Test escalation system integration with HITL engine"""
    
    def test_hitl_integration(self):
        """Test integration with HITL engine"""
        engine = EscalationEngine()
        
        # Mock HITL engine manually
        mock_hitl_instance = Mock()
        mock_hitl_instance.get_pending_reviews.return_value = [
            {"task_id": "BE-111", "started_at": datetime.now() - timedelta(hours=3)},
            {"task_id": "FE-222", "started_at": datetime.now() - timedelta(hours=1)}
        ]
        
        # Test escalation integration - mock the hitl_engine attribute
        engine.hitl_engine = mock_hitl_instance
        escalations = engine.check_pending_reviews_for_escalation()
        
        assert len(escalations) >= 1  # At least one timeout escalation
        mock_hitl_instance.get_pending_reviews.assert_called_once()
        
    def test_feedback_system_integration(self):
        """Test integration with feedback system"""
        engine = EscalationEngine()
        
        # Test escalation event affects feedback
        escalation_data = {
            "task_id": "BE-333",
            "escalation_level": EscalationLevel.LEVEL_2,
            "escalation_reason": "timeout"
        }
        
        feedback_impact = engine.calculate_feedback_impact(escalation_data)
        
        assert feedback_impact["severity_score"] > 0
        assert "escalation" in feedback_impact["categories"]
        
    @patch('utils.escalation_system.FeedbackSystem')
    def test_escalation_feedback_capture(self, mock_feedback):
        """Test capturing feedback from escalation events"""
        engine = EscalationEngine()
        
        escalation_event = EscalationEvent(
            task_id="DATA-444",
            trigger="timeout",
            level=EscalationLevel.LEVEL_1,
            triggered_at=datetime.now(),
            triggered_by="system",
            context={"timeout_duration": 3600}
        )
        
        engine.capture_escalation_feedback(escalation_event)
        
        mock_feedback.return_value.capture_feedback.assert_called_once()


class TestEscalationCLI:
    """Test escalation system CLI interface"""
    
    def test_cli_list_escalations(self):
        """Test CLI listing active escalations"""
        from cli.escalation_cli import list_active_escalations
        
        result = list_active_escalations()
        assert "escalations" in result
        
    def test_cli_escalation_status(self):
        """Test CLI escalation status command"""
        from cli.escalation_cli import get_escalation_status
        
        status = get_escalation_status("BE-555")
        assert "task_id" in status
        
    def test_cli_manual_escalation(self):
        """Test CLI manual escalation trigger"""
        from cli.escalation_cli import trigger_manual_escalation
        
        result = trigger_manual_escalation(
            task_id="FE-666",
            reason="urgent_deadline",
            level="level_2"
        )
        
        assert result["success"] is True


class TestEscalationEndToEnd:
    """End-to-end escalation workflow tests"""
    
    @patch('utils.escalation_system.EscalationNotifier')
    @patch('utils.escalation_system.EscalationTracker')
    def test_complete_timeout_escalation_workflow(self, mock_tracker, mock_notifier):
        """Test complete timeout escalation workflow"""
        engine = EscalationEngine()
        
        # Simulate pending review timeout
        task_data = {
            "task_id": "BE-777",
            "task_type": "backend",
            "risk_level": "high",
            "reviewer": "john.reviewer",
            "review_started": datetime.now() - timedelta(hours=4),
            "timeout_threshold": 2
        }
        
        # 1. Schedule initial timer
        timer_id = engine.schedule_escalation_timer(task_data)
        assert timer_id is not None
        
        # 2. Simulate timeout trigger
        escalation_result = engine.handle_timeout_escalation(task_data)
        assert escalation_result["escalated"] is True
        
        # 3. Verify notification sent
        mock_notifier.return_value.send_notification.assert_called()
        
        # 4. Verify event tracked
        mock_tracker.return_value.track_event.assert_called()
        
        # 5. Verify timer cleanup
        engine.cancel_escalation_timer(timer_id)
        assert timer_id not in engine.timers
        
    def test_complete_rejection_escalation_workflow(self):
        """Test complete rejection escalation workflow"""
        engine = EscalationEngine()
        
        # Simulate multiple rejections
        rejection_data = {
            "task_id": "FE-888",
            "task_type": "frontend", 
            "risk_level": "medium",
            "reviewer": "alice.reviewer",
            "rejection_reason": "design_guidelines",
            "rejection_count": 3,
            "original_submission": datetime.now() - timedelta(days=2)
        }
        
        result = engine.handle_rejection_escalation(rejection_data)
        
        # Verify escalation was triggered
        assert result["escalated"] is True
        assert result["level"] in [EscalationLevel.LEVEL_2, EscalationLevel.LEVEL_3]
        assert "escalation_event" in result
        
    @patch('utils.escalation_system.threading.Timer')
    def test_escalation_timer_cascade(self, mock_timer):
        """Test cascading escalation levels"""
        engine = EscalationEngine()
        
        # Level 1 escalation
        level1_data = {
            "task_id": "QA-999",
            "task_type": "qa",
            "risk_level": "high",
            "timeout_hours": 2
        }
        
        timer1 = engine.schedule_escalation_timer(level1_data)
        
        # Simulate Level 1 timeout
        level1_result = engine.handle_timeout_escalation(level1_data)
        assert level1_result["level"] == EscalationLevel.LEVEL_1
        
        # Level 2 escalation should be scheduled
        level2_data = level1_data.copy()
        level2_data["timeout_hours"] = 6
        
        timer2 = engine.schedule_escalation_timer(level2_data)
        level2_result = engine.handle_timeout_escalation(level2_data)
        assert level2_result["level"] == EscalationLevel.LEVEL_2
        
        # Verify cascading behavior
        assert timer1 != timer2
        mock_timer.assert_called()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
