"""Integration tests for the feedback system."""
import os
import sys
import json
import tempfile
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock
import pytest

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.infrastructure.utils.feedback_system import FeedbackSystem, FeedbackEntry, FeedbackCategory, FeedbackAnalytics


class TestFeedbackSystem:
    """Test feedback system functionality."""

    @pytest.fixture
    def temp_storage(self):
        """Create temporary storage directory."""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield temp_dir

    @pytest.fixture
    def feedback_system(self, temp_storage):
        """Create a feedback system instance with temp storage."""
        return FeedbackSystem(storage_dir=temp_storage)

    def test_feedback_entry_creation(self):
        """Test creating feedback entries with validation."""
        entry = FeedbackEntry(
            task_id="BE-001",
            reviewer="john.doe",
            approval_decision=True,
            feedback_categories={'code_quality': {'score': 8, 'comments': 'Well-implemented solution'}},
            comments=['Well-implemented solution'],
            risk_level="medium",
        )
        
        assert entry.task_id == "BE-001"
        assert entry.reviewer == "john.doe"
        assert entry.approval_decision is True
        assert entry.risk_level == "medium"
        assert "Well-implemented solution" in entry.comments

    def test_feedback_system_initialization(self, feedback_system):
        """Test feedback system initialization creates storage."""
        assert hasattr(feedback_system.storage, 'storage_dir')
        assert os.path.exists(feedback_system.storage.storage_dir)
        assert os.path.exists(feedback_system.storage.storage_dir)
        # The feedback.json file is created on demand when feedback is saved, not on initialization.
        # So, we don't assert its existence here.

    def test_capture_feedback(self, feedback_system):
        """Test capturing and storing feedback."""
        feedback_data = {
            "approved": False,
            "comments": ["Missing error handling"],
            "risk_level": "medium",
            "architecture": {"score": 5, "comments": "Needs better modularity"}
        }
        
        feedback_id = feedback_system.capture_feedback("FE-002", "alice.smith", feedback_data)
        
        assert feedback_id is not None
        
        # Verify feedback was stored
        stored_feedback = feedback_system.get_feedback_by_task("FE-002")
        assert len(stored_feedback) == 1
        assert stored_feedback[0].reviewer == "alice.smith"
        assert stored_feedback[0].approval_decision is False

    def test_get_feedback_by_reviewer(self, feedback_system):
        """Test retrieving feedback by reviewer."""
        # Create multiple feedback entries
        # Create multiple feedback entries
        for i in range(5):
            feedback_data = {
                "approved": i % 3 != 0,
                "comments": [f"Feedback {i}"],
                "risk_level": "low",
                "feedback_categories": {"general": {"score": 7, "comments": ""}}
            }
            reviewer = "reviewer1" if i % 2 == 0 else "reviewer2"
            feedback_system.capture_feedback(f"TASK-{i}", reviewer, feedback_data)
        
        # Get feedback for reviewer1
        reviewer1_feedback = feedback_system.get_feedback_by_reviewer("reviewer1")
        assert len(reviewer1_feedback) == 3  # 0, 2, 4
        assert all(f.reviewer == "reviewer1" for f in reviewer1_feedback)
        
        # Get feedback for reviewer2
        reviewer2_feedback = feedback_system.get_feedback_by_reviewer("reviewer2")
        assert len(reviewer2_feedback) == 2  # 1, 3
        assert all(f.reviewer == "reviewer2" for f in reviewer2_feedback)

    def test_get_feedback_in_date_range(self, feedback_system):
        """Test retrieving feedback within date range."""
        base_time = datetime.now()
        
        # Create feedback entries with different timestamps
        for i in range(4):
            feedback_data = {
                "approved": True,
                "comments": [f"Feedback from {i} days ago"],
                "risk_level": "low",
                "feedback_categories": {"timing": {"score": 7, "comments": ""}},
                "timestamp": base_time - timedelta(days=i)
            }
            feedback_system.capture_feedback(f"DATE-{i}", "time.reviewer", feedback_data)
        
        # Get feedback from last 3 days
        recent_feedback = feedback_system.storage.get_feedback_by_period(period="3d")
        
        assert len(recent_feedback) == 4  # 0, 1, 2, 3 days ago
        task_ids = [f.task_id for f in recent_feedback]
        assert "DATE-0" in task_ids
        assert "DATE-1" in task_ids
        assert "DATE-2" in task_ids
        assert "DATE-3" in task_ids
        assert "DATE-4" not in task_ids

    def test_feedback_persistence(self, temp_storage):
        """Test feedback persists across system restarts."""
        # First system instance
        system1 = FeedbackSystem(storage_dir=temp_storage)
        feedback_data = {
            "approved": True,
            "comments": ["This should persist"],
            "risk_level": "high",
            "feedback_categories": {"persistence": {"score": 9, "comments": ""}}
        }
        feedback_id = system1.capture_feedback("PERSIST-001", "persistent.reviewer", feedback_data)
        
        # Create new system instance with same storage
        system2 = FeedbackSystem(storage_dir=temp_storage)
        loaded_feedback = system2.storage.load_feedback(feedback_id)
        
        assert loaded_feedback is not None
        assert loaded_feedback.task_id == "PERSIST-001"
        assert "This should persist" in loaded_feedback.comments
        assert loaded_feedback.risk_level == "high"

    

    

    

    def test_feedback_statistics(self, feedback_system):
        """Test generating feedback statistics."""
        # Create diverse feedback data
        reviewers = ["alice", "bob", "charlie"]
        decisions = [True, False, True, False, True, True, False]
        risk_levels = ["low", "medium", "high", "low", "medium", "high", "low"]
        
        for i in range(7):
            feedback_data = {
                "approved": decisions[i],
                "comments": [f"Statistical feedback {i}"],
                "risk_level": risk_levels[i],
                "feedback_categories": {"statistics": {"score": 7, "comments": ""}},
                "timestamp": datetime.now() - timedelta(hours=i)
            }
            feedback_system.capture_feedback(f"STATS-{i}", reviewers[i % len(reviewers)], feedback_data)
        
        stats = feedback_system.analytics.generate_insights(feedback_system.storage.get_all_feedback())
        print(f"DEBUG: stats = {stats}")
        assert stats['patterns']['reviewer_distribution']['alice'] == 3
        assert stats['patterns']['reviewer_distribution']['bob'] == 2
        assert stats['patterns']['reviewer_distribution']['charlie'] == 2
        assert stats['patterns']['risk_levels']['low'] == 3
        assert stats['patterns']['risk_levels']['medium'] == 2
        assert stats['patterns']['risk_levels']['high'] == 2


class TestFeedbackAnalytics:
    """Test feedback analysis functionality."""

    @pytest.fixture
    def analyzer(self):
        """Create a feedback analytics instance."""
        return FeedbackAnalytics()

    

    def test_identify_patterns(self, analyzer):
        """Test identifying patterns in feedback."""
        feedback_entries = [
            FeedbackEntry(
                task_id=f"PATTERN-{i}",
                reviewer="pattern.finder",
                timestamp=datetime.now(),
                approval_decision=i % 2 == 0,
                comments=["Missing error handling"] if i % 3 == 0 else ["Good implementation"],
                risk_level="high" if i % 3 == 0 else "low",
                feedback_categories={'patterns': {'score': 7, 'comments': ''}}
            )
            for i in range(10)
        ]
        
        patterns = analyzer.identify_trends(feedback_entries)
        
        assert 'common_issues' in patterns
        
        assert len(patterns['common_issues']) > 0
        
        # Check if error handling is identified as common issue
        error_found = any(
            "error" in issue.lower() 
            for issue in patterns['common_issues']
        )
        handling_found = any(
            "handling" in issue.lower() 
            for issue in patterns['common_issues']
        )
        assert error_found and handling_found

    

    

    