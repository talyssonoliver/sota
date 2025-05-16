"""
Test Utilities Module

This module provides utilities for consistent test output formatting
and other helper functions for test scripts.
"""

import os
import sys
import json
import time
from datetime import datetime
from typing import Dict, Any, Optional, List, Union, Tuple

class TestFeedback:
    """Class for providing standardized test execution feedback."""
    
    @staticmethod
    def print_header(test_name: str, test_type: str = "Test") -> None:
        """Print a standardized test header."""
        print(f"\n{'='*20} {test_name.upper()} {test_type.upper()} {'='*20}")
        print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*60}")
    
    @staticmethod
    def print_section(section_name: str) -> None:
        """Print a section header within a test."""
        print(f"\n{'-'*3} {section_name} {'-'*3}")
    
    @staticmethod
    def print_result(test_name: str, passed: bool, details: Optional[Dict[str, Any]] = None, 
                    execution_time: Optional[float] = None) -> bool:
        """
        Print standardized test result feedback.
        
        Args:
            test_name: Name of the test or test suite
            passed: Whether the test passed or failed
            details: Additional details about test execution
            execution_time: Time taken to execute tests in seconds
            
        Returns:
            bool: The passed value (for convenience in function calls)
        """
        status = "✅ PASSED" if passed else "❌ FAILED"
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Header
        print(f"\n{'='*20} TEST RESULTS {'='*20}")
        print(f"Test: {test_name}")
        print(f"Status: {status}")
        print(f"Timestamp: {timestamp}")
        
        # Execution time
        if execution_time is not None:
            print(f"Execution time: {execution_time:.2f}s")
        
        # Details
        if details:
            print("\nDetails:")
            for key, value in details.items():
                if isinstance(value, list):
                    print(f"- {key}:")
                    for item in value:
                        print(f"  - {item}")
                else:
                    print(f"- {key}: {value}")
        
        # Footer
        print('='*55)
        
        return passed
    
    @staticmethod
    def print_summary(results: List[Tuple[str, bool]], start_time: float) -> int:
        """
        Print an overall test summary.
        
        Args:
            results: List of (test_name, passed) tuples
            start_time: Start time in seconds since epoch
            
        Returns:
            int: Exit code (0 for all passed, 1 if any failed)
        """
        execution_time = time.time() - start_time
        passed_count = sum(1 for _, result in results if result)
        failed_count = len(results) - passed_count
        
        print("\n" + "="*25 + " TEST SUMMARY " + "="*25)
        print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Total execution time: {execution_time:.2f}s")
        print(f"Tests run: {len(results)}")
        print(f"Tests passed: {passed_count}")
        print(f"Tests failed: {failed_count}")
        
        if results:
            print("\nTest Results:")
            for test_name, passed in results:
                status = "✅ PASSED" if passed else "❌ FAILED"
                print(f"- {test_name}: {status}")
        
        exit_code = 0 if failed_count == 0 else 1
        print(f"\nOverall status: {'✅ PASSED' if exit_code == 0 else '❌ FAILED'}")
        print("="*60)
        
        return exit_code
    
    @staticmethod
    def save_results(results: List[Tuple[str, bool]], details: Dict[str, Any], 
                    output_dir: str = "test_results") -> str:
        """
        Save test results to a JSON file.
        
        Args:
            results: List of (test_name, passed) tuples
            details: Additional details to include
            output_dir: Directory to save results to
            
        Returns:
            str: Path to the results file
        """
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        # Generate results data
        results_data = {
            "timestamp": datetime.now().isoformat(),
            "tests_run": len(results),
            "tests_passed": sum(1 for _, result in results if result),
            "tests_failed": sum(1 for _, result in results if not result),
            "details": details,
            "results": {name: "passed" if passed else "failed" for name, passed in results}
        }
        
        # Generate filename with timestamp
        timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_path = os.path.join(output_dir, f"test_results_{timestamp_str}.json")
        
        # Write results to file
        with open(file_path, "w") as f:
            json.dump(results_data, f, indent=2)
        
        print(f"\nTest results saved to: {file_path}")
        return file_path


class Timer:
    """Simple timer for measuring test execution time."""
    
    def __init__(self):
        self.start_time = None
        self.end_time = None
    
    def start(self):
        """Start the timer."""
        self.start_time = time.time()
        return self
    
    def stop(self):
        """Stop the timer."""
        self.end_time = time.time()
        return self
    
    def elapsed(self):
        """Get elapsed time in seconds."""
        if self.start_time is None:
            return 0
        end = self.end_time if self.end_time is not None else time.time()
        return end - self.start_time