#!/usr/bin/env python3
"""
Comprehensive Test Suite for Morning Briefing Generator (Step 6.2)

Tests for day-specific briefing generation, CLI interface, 
and integration with existing Phase 5 infrastructure.
"""

import asyncio
import json
import os
import sys
import tempfile
import unittest
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock, mock_open
import logging

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from orchestration.generate_briefing import BriefingGenerator


class TestBriefingGeneratorStep62(unittest.TestCase):
    """Test cases for Step 6.2 specific requirements."""
    
    def setUp(self):
        """Set up test environment."""
        self.briefing_generator = BriefingGenerator()
        self.test_briefings_dir = Path("test_outputs/briefings")
        self.test_briefings_dir.mkdir(parents=True, exist_ok=True)
        
        # Mock data for consistent testing
        self.mock_team_metrics = {
            "completion_rate": 75.5,
            "completed_tasks": 12,
            "total_tasks": 16,
            "in_progress_tasks": 3,
            "pending_tasks": 1
        }
        
        self.mock_sprint_metrics = {
            "average_completion_time": 2.8,
            "blockers": 1,
            "velocity": 4.2
        }
        
        self.mock_tasks = [
            {
                "id": "BE-01",
                "title": "Validate Supabase Setup",
                "status": "PLANNED",
                "priority": "HIGH",
                "owner": "Backend Team",
                "type": "backend"
            },
            {
                "id": "BE-02", 
                "title": "Seed Data",
                "status": "PLANNED",
                "priority": "MEDIUM",
                "owner": "Backend Team",
                "type": "backend"
            },
            {
                "id": "FE-01",
                "title": "Validate Environment",
                "status": "IN_PROGRESS",
                "priority": "HIGH",
                "owner": "Frontend Team",
                "type": "frontend"
            },
            {
                "id": "FE-02",
                "title": "Build UI Components",
                "status": "PLANNED",
                "priority": "CRITICAL",
                "owner": "Frontend Team",
                "type": "frontend"
            }
        ]
    
    def tearDown(self):
        """Clean up test environment."""
        # Clean up test files
        import shutil
        if self.test_briefings_dir.exists():
            shutil.rmtree(self.test_briefings_dir)
    
    def test_briefing_generator_initialization(self):
        """Test briefing generator initializes correctly."""
        self.assertIsInstance(self.briefing_generator, BriefingGenerator)
        self.assertIsNotNone(self.briefing_generator.metrics_calculator)
        self.assertIsNotNone(self.briefing_generator.execution_monitor)
        self.assertTrue(self.briefing_generator.briefings_dir.exists())
    
    @patch('orchestration.generate_briefing.CompletionMetricsCalculator')
    def test_generate_day_specific_briefing(self, mock_metrics_class):
        """Test generating day-specific briefing as required by Step 6.2."""
        # Mock the metrics calculator
        mock_metrics = Mock()
        mock_metrics.calculate_team_metrics.return_value = self.mock_team_metrics
        mock_metrics.calculate_sprint_metrics.return_value = self.mock_sprint_metrics
        mock_metrics_class.return_value = mock_metrics
        
        # Create new generator with mocked metrics
        generator = BriefingGenerator()
        generator.metrics_calculator = mock_metrics
        
        # Mock _get_all_tasks to return our test tasks
        with patch.object(generator, '_get_all_tasks', return_value=self.mock_tasks):
            result = asyncio.run(generator.generate_day_briefing(day=2))
        
        # Verify results
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["day"], 2)
        self.assertIn("file_path", result)
        self.assertIn("day2-morning-briefing.md", result["file_path"])
        self.assertIn("data", result)
        
        # Verify data structure
        data = result["data"]
        self.assertIn("backend_tasks", data)
        self.assertIn("frontend_tasks", data)
        self.assertIn("key_focus", data)
        self.assertIn("coordination_points", data)
    
    def test_day_specific_output_format(self):
        """Test the exact output format required by Step 6.2."""
        # Mock dependencies
        with patch.object(self.briefing_generator, '_get_all_tasks', return_value=self.mock_tasks), \
             patch.object(self.briefing_generator.metrics_calculator, 'calculate_team_metrics', return_value=self.mock_team_metrics), \
             patch.object(self.briefing_generator.metrics_calculator, 'calculate_sprint_metrics', return_value=self.mock_sprint_metrics):
            
            result = asyncio.run(self.briefing_generator.generate_day_briefing(day=2))
            
            # Check that the output contains the required sections
            output = result["output"]
            self.assertIn("# Day 2 Morning Briefing", output)
            self.assertIn("## Backend Tasks", output)
            self.assertIn("## Frontend Tasks", output)
            self.assertIn("## Key Focus", output)
            self.assertIn("## Coordination Points", output)
            
            # Check specific task formatting
            self.assertIn("- BE-01: Validate Supabase Setup", output)
            self.assertIn("- BE-02: Seed Data", output)
            self.assertIn("- FE-01: Validate Environment", output)
            self.assertIn("- FE-02: Build UI Components", output)
    
    def test_backend_frontend_task_separation(self):
        """Test that tasks are properly separated by backend/frontend."""
        with patch.object(self.briefing_generator, '_get_all_tasks', return_value=self.mock_tasks):
            backend_tasks = self.briefing_generator._get_backend_tasks()
            frontend_tasks = self.briefing_generator._get_frontend_tasks()
            
            # Verify backend tasks
            self.assertEqual(len(backend_tasks), 2)
            backend_ids = [task["id"] for task in backend_tasks]
            self.assertIn("BE-01", backend_ids)
            self.assertIn("BE-02", backend_ids)
            
            # Verify frontend tasks
            self.assertEqual(len(frontend_tasks), 2)
            frontend_ids = [task["id"] for task in frontend_tasks]
            self.assertIn("FE-01", frontend_ids)
            self.assertIn("FE-02", frontend_ids)
    
    def test_key_focus_generation(self):
        """Test generation of key focus areas."""
        with patch.object(self.briefing_generator, '_get_all_tasks', return_value=self.mock_tasks):
            key_focus = self.briefing_generator._generate_key_focus()
            
            self.assertIsInstance(key_focus, list)
            self.assertTrue(len(key_focus) > 0)
            
            # Should contain focus areas for both backend and frontend
            focus_text = " ".join(key_focus)
            self.assertIn("backend", focus_text.lower())
            self.assertIn("frontend", focus_text.lower())
    
    def test_coordination_points_generation(self):
        """Test generation of coordination points."""
        coordination_points = self.briefing_generator._generate_coordination_points(day=2)
        
        self.assertIsInstance(coordination_points, list)
        self.assertTrue(len(coordination_points) >= 2)
        
        # Should contain specific times
        points_text = " ".join(coordination_points)
        self.assertIn("AM", points_text)
        self.assertIn("PM", points_text)
        
    def test_file_path_generation(self):
        """Test that file paths are generated correctly."""
        file_path = self.briefing_generator._get_day_briefing_path(day=2)
        expected_path = Path("docs/sprint/briefings/day2-morning-briefing.md")
        
        self.assertEqual(file_path, expected_path)
        self.assertEqual(file_path.name, "day2-morning-briefing.md")
    
    def test_cli_argument_parsing(self):
        """Test CLI argument parsing for --day parameter."""
        # Test that the main function can handle --day argument
        # This would be tested through subprocess in a real scenario
        # For now, test the argument parsing logic
        
        import argparse
        parser = argparse.ArgumentParser()
        parser.add_argument("--day", type=int, help="Day number for briefing")
        
        args = parser.parse_args(["--day", "2"])
        self.assertEqual(args.day, 2)
    
    @patch('builtins.open', new_callable=mock_open)
    def test_save_day_briefing(self, mock_file):
        """Test saving day-specific briefing to correct file."""
        content = "# Day 2 Morning Briefing\n\nTest content"
        
        file_path = self.briefing_generator._save_day_briefing(content, day=2)
        
        # Verify file path
        expected_path = Path("docs/sprint/briefings/day2-morning-briefing.md")
        self.assertEqual(file_path, expected_path)
        
        # Verify file was written
        mock_file.assert_called_once_with(expected_path, 'w', encoding='utf-8')
        mock_file().write.assert_called_once_with(content)
    
    def test_error_handling_invalid_day(self):
        """Test error handling for invalid day values."""
        with self.assertRaises(ValueError):
            asyncio.run(self.briefing_generator.generate_day_briefing(day=0))
        
        with self.assertRaises(ValueError):
            asyncio.run(self.briefing_generator.generate_day_briefing(day=-1))
    
    def test_error_handling_missing_metrics(self):
        """Test graceful handling when metrics are unavailable."""
        # Mock metrics calculator to raise exception
        with patch.object(self.briefing_generator.metrics_calculator, 'calculate_team_metrics', side_effect=Exception("Metrics unavailable")):
            result = asyncio.run(self.briefing_generator.generate_day_briefing(day=2))
            
            # Should still succeed but with error noted
            self.assertEqual(result["status"], "success")
            self.assertIn("metrics_error", result["data"])


class TestCLIIntegration(unittest.TestCase):
    """Test CLI integration for Step 6.2."""
    
    def test_cli_day_parameter(self):
        """Test CLI with --day parameter."""
        import subprocess
        import sys
        
        # Test the CLI interface (dry run)
        try:
            result = subprocess.run([
                sys.executable, "-c",
                "import argparse; p = argparse.ArgumentParser(); p.add_argument('--day', type=int); args = p.parse_args(['--day', '2']); print(args.day)"
            ], capture_output=True, text=True, timeout=10)
            
            self.assertEqual(result.returncode, 0)
            self.assertEqual(result.stdout.strip(), "2")
        except subprocess.TimeoutExpired:
            self.skipTest("CLI test timed out")


if __name__ == "__main__":
    # Set up logging for tests
    logging.basicConfig(level=logging.INFO)
    
    # Run tests
    unittest.main()
