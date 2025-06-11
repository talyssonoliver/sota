"""
Test suite for Phase 7 Step 7.4: Structured Feedback Integration System
Tests the feedback collection, storage, analytics, and integration components.
"""

import pytest
import json
import tempfile
import os
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path

# Test imports for the feedback system (to be implemented)
from utils.feedback_system import (
    FeedbackSystem,
    FeedbackStorage,
    FeedbackAnalytics,
    FeedbackEntry,
    FeedbackCategory,
    FeedbackExporter
)


class TestFeedbackEntry:
    """Test the FeedbackEntry data structure"""
    
    def test_feedback_entry_creation(self):
        """Test basic feedback entry creation"""
        entry = FeedbackEntry(
            task_id="BE-07",
            reviewer="human.reviewer",
            approval_decision=True,
            feedback_categories={
                "code_quality": {"score": 8, "comments": "Good structure"},
                "security": {"score": 9, "comments": "No issues found"}
            }
        )
        
        assert entry.task_id == "BE-07"
        assert entry.reviewer == "human.reviewer"
        assert entry.approval_decision is True
        assert entry.feedback_categories["code_quality"]["score"] == 8
        assert isinstance(entry.timestamp, datetime)
    
    def test_feedback_entry_validation(self):
        """Test feedback entry validation"""
        # Test invalid task_id
        with pytest.raises(ValueError, match="task_id cannot be empty"):
            FeedbackEntry(task_id="", reviewer="test", approval_decision=True)
        
        # Test invalid reviewer
        with pytest.raises(ValueError, match="reviewer cannot be empty"):
            FeedbackEntry(task_id="BE-07", reviewer="", approval_decision=True)
    
    def test_feedback_entry_serialization(self):
        """Test feedback entry to_dict and from_dict methods"""
        entry = FeedbackEntry(
            task_id="BE-07",
            reviewer="human.reviewer",
            approval_decision=True,
            feedback_categories={"code_quality": {"score": 8}},
            comments=["Well structured code"],
            suggested_improvements=["Add more tests"],
            risk_level="medium"
        )
        
        # Test serialization
        data = entry.to_dict()
        assert isinstance(data, dict)
        assert data["task_id"] == "BE-07"
        assert data["approval_decision"] is True
        
        # Test deserialization
        reconstructed = FeedbackEntry.from_dict(data)
        assert reconstructed.task_id == entry.task_id
        assert reconstructed.approval_decision == entry.approval_decision


class TestFeedbackCategory:
    """Test feedback category enumeration and validation"""
    
    def test_feedback_categories_exist(self):
        """Test that all required feedback categories are defined"""
        categories = FeedbackCategory.get_all_categories()
        
        required_categories = [
            "code_quality",
            "architecture", 
            "security",
            "performance",
            "documentation"
        ]
        
        for category in required_categories:
            assert category in categories
    
    def test_category_validation(self):
        """Test feedback category validation"""
        # Valid category
        assert FeedbackCategory.is_valid("code_quality")
        
        # Invalid category
        assert not FeedbackCategory.is_valid("invalid_category")
    
    def test_category_scoring_range(self):
        """Test that category scores are in valid range"""
        # Valid scores
        assert FeedbackCategory.is_valid_score(1)
        assert FeedbackCategory.is_valid_score(10)
        assert FeedbackCategory.is_valid_score(5)
        
        # Invalid scores
        assert not FeedbackCategory.is_valid_score(0)
        assert not FeedbackCategory.is_valid_score(11)
        assert not FeedbackCategory.is_valid_score(-1)


class TestFeedbackStorage:
    """Test feedback storage functionality"""
    
    def setup_method(self):
        """Setup test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.storage = FeedbackStorage(storage_dir=self.temp_dir)
    
    def teardown_method(self):
        """Cleanup test environment"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
      
    def test_storage_initialization(self):
        """Test feedback storage initialization"""
        assert str(self.storage.storage_dir) == self.temp_dir
        assert os.path.exists(self.storage.storage_dir)
    
    def test_save_feedback(self):
        """Test saving feedback to storage"""
        entry = FeedbackEntry(
            task_id="BE-07",
            reviewer="human.reviewer",
            approval_decision=True,
            feedback_categories={"code_quality": {"score": 8}}
        )
        
        feedback_id = self.storage.save_feedback(entry)
        assert feedback_id is not None
        assert isinstance(feedback_id, str)
        
        # Verify file was created
        feedback_files = list(Path(self.temp_dir).glob("*.json"))
        assert len(feedback_files) > 0
    
    def test_get_feedback_by_task(self):
        """Test retrieving feedback by task ID"""
        # Save multiple feedback entries
        entry1 = FeedbackEntry(task_id="BE-07", reviewer="reviewer1", approval_decision=True)
        entry2 = FeedbackEntry(task_id="BE-07", reviewer="reviewer2", approval_decision=False)
        entry3 = FeedbackEntry(task_id="FE-05", reviewer="reviewer1", approval_decision=True)
        
        self.storage.save_feedback(entry1)
        self.storage.save_feedback(entry2)
        self.storage.save_feedback(entry3)
        
        # Get feedback for BE-07
        be07_feedback = self.storage.get_feedback_by_task("BE-07")
        assert len(be07_feedback) == 2
        
        # Get feedback for FE-05
        fe05_feedback = self.storage.get_feedback_by_task("FE-05")
        assert len(fe05_feedback) == 1
    
    def test_get_feedback_by_reviewer(self):
        """Test retrieving feedback by reviewer"""
        entry1 = FeedbackEntry(task_id="BE-07", reviewer="reviewer1", approval_decision=True)
        entry2 = FeedbackEntry(task_id="FE-05", reviewer="reviewer1", approval_decision=False)
        entry3 = FeedbackEntry(task_id="BE-08", reviewer="reviewer2", approval_decision=True)
        
        self.storage.save_feedback(entry1)
        self.storage.save_feedback(entry2)
        self.storage.save_feedback(entry3)
        
        reviewer1_feedback = self.storage.get_feedback_by_reviewer("reviewer1")
        assert len(reviewer1_feedback) == 2
        
        reviewer2_feedback = self.storage.get_feedback_by_reviewer("reviewer2")
        assert len(reviewer2_feedback) == 1
    
    def test_get_feedback_by_period(self):
        """Test retrieving feedback by time period"""
        # Create entries with different timestamps
        now = datetime.now()
        yesterday = now - timedelta(days=1)
        last_week = now - timedelta(days=7)
        
        with patch('utils.feedback_system.datetime') as mock_datetime:
            # Entry from yesterday
            mock_datetime.now.return_value = yesterday
            entry1 = FeedbackEntry(task_id="BE-07", reviewer="reviewer1", approval_decision=True)
            self.storage.save_feedback(entry1)
            
            # Entry from last week
            mock_datetime.now.return_value = last_week
            entry2 = FeedbackEntry(task_id="BE-08", reviewer="reviewer1", approval_decision=True)
            self.storage.save_feedback(entry2)
        
        # Get feedback from last 3 days
        recent_feedback = self.storage.get_feedback_by_period("3d")
        assert len(recent_feedback) == 1  # Only yesterday's entry
        
        # Get feedback from last 10 days
        all_feedback = self.storage.get_feedback_by_period("10d")
        assert len(all_feedback) == 2  # Both entries


class TestFeedbackAnalytics:
    """Test feedback analytics functionality"""
    
    def setup_method(self):
        """Setup test environment"""
        self.analytics = FeedbackAnalytics()
        
        # Create sample feedback data
        self.sample_feedback = [
            FeedbackEntry(
                task_id="BE-07",
                reviewer="reviewer1",
                approval_decision=True,
                feedback_categories={
                    "code_quality": {"score": 8, "comments": "Good structure"},
                    "security": {"score": 9, "comments": "No issues"}
                }
            ),
            FeedbackEntry(
                task_id="BE-08",
                reviewer="reviewer2",
                approval_decision=False,
                feedback_categories={
                    "code_quality": {"score": 6, "comments": "Needs improvement"},
                    "security": {"score": 7, "comments": "Minor issues"}
                }
            ),
            FeedbackEntry(
                task_id="FE-05",
                reviewer="reviewer1",
                approval_decision=True,
                feedback_categories={
                    "code_quality": {"score": 9, "comments": "Excellent"},
                    "performance": {"score": 8, "comments": "Good performance"}
                }
            )
        ]
    
    def test_calculate_approval_rate(self):
        """Test approval rate calculation"""
        approval_rate = self.analytics.calculate_approval_rate(self.sample_feedback)
        
        # 2 out of 3 approved = 66.67%
        assert abs(approval_rate - 66.67) < 0.01
    
    def test_calculate_category_averages(self):
        """Test category score averages"""
        averages = self.analytics.calculate_category_averages(self.sample_feedback)
        
        # code_quality: (8 + 6 + 9) / 3 = 7.67
        assert abs(averages["code_quality"] - 7.67) < 0.01
        
        # security: (9 + 7) / 2 = 8.0
        assert abs(averages["security"] - 8.0) < 0.01
        
        # performance: 8 / 1 = 8.0
        assert abs(averages["performance"] - 8.0) < 0.01
    
    def test_identify_trends(self):
        """Test trend identification in feedback"""
        trends = self.analytics.identify_trends(self.sample_feedback)
        
        assert "approval_rate" in trends
        assert "category_scores" in trends
        assert "common_issues" in trends
        assert "improvement_areas" in trends
    
    def test_generate_insights(self):
        """Test insight generation from feedback data"""
        insights = self.analytics.generate_insights(self.sample_feedback)
        
        assert isinstance(insights, dict)
        assert "summary" in insights
        assert "recommendations" in insights
        assert "patterns" in insights
    
    def test_filter_by_reviewer(self):
        """Test filtering feedback by reviewer"""
        reviewer1_feedback = self.analytics.filter_by_reviewer(
            self.sample_feedback, "reviewer1"
        )
        
        assert len(reviewer1_feedback) == 2
        for feedback in reviewer1_feedback:
            assert feedback.reviewer == "reviewer1"
    
    def test_filter_by_approval_decision(self):
        """Test filtering feedback by approval decision"""
        approved_feedback = self.analytics.filter_by_approval_decision(
            self.sample_feedback, True
        )
        
        assert len(approved_feedback) == 2
        for feedback in approved_feedback:
            assert feedback.approval_decision is True


class TestFeedbackExporter:
    """Test feedback export functionality"""
    
    def setup_method(self):
        """Setup test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.exporter = FeedbackExporter()
        
        # Sample feedback data
        self.sample_feedback = [
            FeedbackEntry(
                task_id="BE-07",
                reviewer="reviewer1",
                approval_decision=True,
                feedback_categories={"code_quality": {"score": 8}},
                comments=["Good work"],
                suggested_improvements=["Add tests"]
            )
        ]
    
    def teardown_method(self):
        """Cleanup test environment"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_export_to_json(self):
        """Test exporting feedback to JSON format"""
        output_path = os.path.join(self.temp_dir, "feedback_export.json")
        
        result = self.exporter.export_to_json(self.sample_feedback, output_path)
        
        assert result is True
        assert os.path.exists(output_path)
        
        # Verify JSON content
        with open(output_path, 'r') as f:
            data = json.load(f)
        
        assert isinstance(data, list)
        assert len(data) == 1
        assert data[0]["task_id"] == "BE-07"
    
    def test_export_to_csv(self):
        """Test exporting feedback to CSV format"""
        output_path = os.path.join(self.temp_dir, "feedback_export.csv")
        
        result = self.exporter.export_to_csv(self.sample_feedback, output_path)
        
        assert result is True
        assert os.path.exists(output_path)
    
    def test_generate_summary_report(self):
        """Test generating summary report"""
        output_path = os.path.join(self.temp_dir, "feedback_summary.md")
        
        result = self.exporter.generate_summary_report(self.sample_feedback, output_path)
        
        assert result is True
        assert os.path.exists(output_path)
        
        # Verify content
        with open(output_path, 'r') as f:
            content = f.read()
        
        assert "# Feedback Summary Report" in content
        assert "BE-07" in content


class TestFeedbackSystem:
    """Test the main FeedbackSystem class integration"""
    
    def setup_method(self):
        """Setup test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.system = FeedbackSystem(storage_dir=self.temp_dir)
    
    def teardown_method(self):
        """Cleanup test environment"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_system_initialization(self):
        """Test feedback system initialization"""
        assert isinstance(self.system.storage, FeedbackStorage)
        assert isinstance(self.system.analytics, FeedbackAnalytics)
        assert isinstance(self.system.exporter, FeedbackExporter)
    
    def test_capture_feedback(self):
        """Test capturing structured feedback"""
        feedback_data = {
            "approved": True,
            "code_quality": {"score": 8, "comments": "Good structure"},
            "architecture": {"score": 7, "comments": "Could be better"},
            "security": {"score": 9, "comments": "No issues found"},
            "comments": ["Overall good work"],
            "improvements": ["Add more tests", "Improve documentation"],
            "risk_level": "medium"
        }
        
        feedback_id = self.system.capture_feedback(
            task_id="BE-07",
            reviewer="human.reviewer",
            feedback_data=feedback_data
        )
        
        assert feedback_id is not None
        assert isinstance(feedback_id, str)
    
    def test_get_feedback_summary(self):
        """Test getting feedback summary for a task"""
        # Capture some feedback first
        feedback_data = {
            "approved": True,
            "code_quality": {"score": 8, "comments": "Good"},
            "comments": ["Nice work"]
        }
        
        self.system.capture_feedback("BE-07", "reviewer1", feedback_data)
        
        summary = self.system.get_feedback_summary("BE-07")
        
        assert isinstance(summary, dict)
        assert "task_id" in summary
        assert "total_feedback_count" in summary
        assert "approval_rate" in summary
        assert "category_averages" in summary
    
    def test_generate_analytics_report(self):
        """Test generating analytics report"""
        # Capture multiple feedback entries
        feedback_data_1 = {
            "approved": True,
            "code_quality": {"score": 8, "comments": "Good"},
        }
        feedback_data_2 = {
            "approved": False,
            "code_quality": {"score": 6, "comments": "Needs work"},
        }
        
        self.system.capture_feedback("BE-07", "reviewer1", feedback_data_1)
        self.system.capture_feedback("BE-08", "reviewer2", feedback_data_2)
        
        report = self.system.generate_analytics_report(period="7d")
        
        assert isinstance(report, dict)
        assert "period" in report
        assert "total_feedback" in report
        assert "approval_rate" in report
        assert "trends" in report
    
    def test_export_feedback_data(self):
        """Test exporting feedback data"""
        # Capture some feedback
        feedback_data = {
            "approved": True,
            "code_quality": {"score": 8, "comments": "Good"},
        }
        
        self.system.capture_feedback("BE-07", "reviewer1", feedback_data)
        
        output_path = os.path.join(self.temp_dir, "export.json")
        result = self.system.export_feedback_data(
            format="json",
            output_path=output_path,
            period="7d"
        )
        
        assert result is True
        assert os.path.exists(output_path)


class TestHITLIntegration:
    """Test integration with existing HITL system"""
    
    def test_integration_with_hitl_engine(self):
        """Test integration with HITL engine"""
        system = FeedbackSystem()
        
        # Test checkpoint feedback integration
        checkpoint_data = {
            "checkpoint_id": "cp-1",
            "task_id": "BE-07",
            "status": "pending_review"
        }
        
        feedback_data = {
            "approved": True,
            "code_quality": {"score": 8, "comments": "Good"},
        }
        
        result = system.integrate_with_checkpoint(
            checkpoint_data=checkpoint_data,
            feedback_data=feedback_data,
            reviewer="human.reviewer"
        )
        
        assert result is not None
    
    def test_review_workflow_integration(self):
        """Test integration with review workflow"""
        system = FeedbackSystem()
        
        # Mock review workflow
        workflow_data = {
            "task_id": "BE-07",
            "review_stage": "human_review",
            "reviewer": "human.reviewer"
        }
        
        feedback_data = {
            "approved": True,
            "code_quality": {"score": 8, "comments": "Good structure"},
            "security": {"score": 9, "comments": "No issues"},
            "comments": ["Overall excellent work"],
            "improvements": ["Add integration tests"]
        }
        
        result = system.process_review_feedback(
            workflow_data=workflow_data,
            feedback_data=feedback_data
        )
        
        assert result["status"] == "success"
        assert "feedback_id" in result


class TestFeedbackSystemCLI:
    """Test CLI interface for feedback system"""
    
    def test_cli_feedback_summary(self):
        """Test CLI command for feedback summary"""
        from cli.feedback_cli import FeedbackCLI
        
        cli = FeedbackCLI()
        
        # Mock the system
        with patch.object(cli, 'system') as mock_system:
            mock_system.get_feedback_summary.return_value = {
                "task_id": "BE-07",
                "total_feedback_count": 3,
                "approval_rate": 66.67
            }
            
            result = cli.get_summary("BE-07")
            assert result is not None
    
    def test_cli_analytics_report(self):
        """Test CLI command for analytics report"""
        from cli.feedback_cli import FeedbackCLI
        
        cli = FeedbackCLI()
        
        with patch.object(cli, 'system') as mock_system:
            mock_system.generate_analytics_report.return_value = {
                "period": "7d",
                "total_feedback": 10,
                "approval_rate": 80.0
            }
            
            result = cli.generate_report("7d")
            assert result is not None
    
    def test_cli_export_data(self):
        """Test CLI command for data export"""
        from cli.feedback_cli import FeedbackCLI
        
        cli = FeedbackCLI()
        
        with patch.object(cli, 'system') as mock_system:
            mock_system.export_feedback_data.return_value = True
            
            result = cli.export_data("json", "/tmp/export.json", "30d")
            assert result is True


class TestEndToEndWorkflow:
    """Test end-to-end feedback workflow"""
    
    def setup_method(self):
        """Setup test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.system = FeedbackSystem(storage_dir=self.temp_dir)
    
    def teardown_method(self):
        """Cleanup test environment"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_complete_feedback_workflow(self):
        """Test complete feedback workflow from capture to export"""
        # Step 1: Capture feedback for multiple tasks
        tasks_feedback = [
            {
                "task_id": "BE-07",
                "reviewer": "senior.dev",
                "feedback_data": {
                    "approved": True,
                    "code_quality": {"score": 8, "comments": "Good structure"},
                    "security": {"score": 9, "comments": "No security issues"},
                    "performance": {"score": 7, "comments": "Could be optimized"},
                    "comments": ["Great work overall"],
                    "improvements": ["Add performance tests"]
                }
            },
            {
                "task_id": "FE-05",
                "reviewer": "ui.expert",
                "feedback_data": {
                    "approved": True,
                    "code_quality": {"score": 9, "comments": "Excellent"},
                    "documentation": {"score": 8, "comments": "Well documented"},
                    "comments": ["Perfect implementation"],
                    "improvements": []
                }
            },
            {
                "task_id": "BE-08",
                "reviewer": "senior.dev",
                "feedback_data": {
                    "approved": False,
                    "code_quality": {"score": 5, "comments": "Needs refactoring"},
                    "security": {"score": 6, "comments": "Some vulnerabilities"},
                    "comments": ["Requires significant changes"],
                    "improvements": ["Fix security issues", "Refactor code"]
                }
            }
        ]
        
        # Capture all feedback
        feedback_ids = []
        for task_feedback in tasks_feedback:
            feedback_id = self.system.capture_feedback(
                task_id=task_feedback["task_id"],
                reviewer=task_feedback["reviewer"],
                feedback_data=task_feedback["feedback_data"]
            )
            feedback_ids.append(feedback_id)
        
        assert len(feedback_ids) == 3
        
        # Step 2: Generate analytics report
        analytics_report = self.system.generate_analytics_report(period="7d")
        
        assert analytics_report["total_feedback"] == 3
        assert abs(analytics_report["approval_rate"] - 66.67) < 0.01  # 2/3 approved
        
        # Step 3: Get task-specific summary
        be07_summary = self.system.get_feedback_summary("BE-07")
        
        assert be07_summary["task_id"] == "BE-07"
        assert be07_summary["total_feedback_count"] == 1
        assert be07_summary["approval_rate"] == 100.0
        
        # Step 4: Export data
        export_path = os.path.join(self.temp_dir, "feedback_export.json")
        export_result = self.system.export_feedback_data(
            format="json",
            output_path=export_path,
            period="7d"
        )
        
        assert export_result is True
        assert os.path.exists(export_path)
        
        # Verify exported data
        with open(export_path, 'r') as f:
            exported_data = json.load(f)
        
        assert len(exported_data) == 3
        assert any(item["task_id"] == "BE-07" for item in exported_data)
        assert any(item["task_id"] == "FE-05" for item in exported_data)
        assert any(item["task_id"] == "BE-08" for item in exported_data)


# Integration test with existing HITL components
class TestHITLSystemIntegration:
    """Test integration with existing HITL system components"""
    
    def test_feedback_system_hitl_integration(self):
        """Test that feedback system integrates with HITL engine"""
        # This test verifies the feedback system works with existing HITL infrastructure
        system = FeedbackSystem()
        
        # Mock HITL checkpoint
        checkpoint = {
            "checkpoint_id": "cp-1",
            "task_id": "BE-07",
            "checkpoint_type": "human_review",
            "status": "pending",
            "metadata": {"requires_feedback": True}
        }
        
        # Capture feedback for the checkpoint
        feedback_data = {
            "approved": True,
            "code_quality": {"score": 8, "comments": "Good implementation"},
            "security": {"score": 9, "comments": "Secure code"},
            "comments": ["Approved for production"],
            "improvements": []
        }
        
        # Integrate with checkpoint
        result = system.integrate_with_checkpoint(
            checkpoint_data=checkpoint,
            feedback_data=feedback_data,
            reviewer="human.reviewer"
        )
        
        assert result is not None
        assert result["status"] == "success"
        assert "feedback_id" in result


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
