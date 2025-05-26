#!/usr/bin/env python3
"""
Test suite for QA Agent Execution (Step 5.3)

Tests the QA execution system that triggers when tasks reach QA_PENDING state.
"""

import pytest
import json
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from orchestration.qa_execution import QAExecutionEngine, execute_qa_validation
from orchestration.langgraph_qa_integration import LangGraphQAIntegration


class TestQAExecutionEngine:
    """Test cases for QA execution engine"""
    
    @pytest.fixture
    def temp_outputs_dir(self):
        """Create temporary outputs directory with mock task"""
        temp_dir = tempfile.mkdtemp()
        outputs_path = Path(temp_dir)
        
        # Create mock task structure
        task_dir = outputs_path / "BE-07"
        task_dir.mkdir(parents=True)
        
        # Create code directory with sample files
        code_dir = task_dir / "code"
        code_dir.mkdir()
        
        # Sample Python file
        (code_dir / "customer_service.py").write_text("""
class CustomerService:
    def __init__(self, supabase_client):
        self.client = supabase_client
    
    def get_customer(self, customer_id):
        return self.client.table('customers').select('*').eq('id', customer_id).execute()
    
    def create_customer(self, customer_data):
        return self.client.table('customers').insert(customer_data).execute()
""")
        
        # Sample TypeScript file
        (code_dir / "order_service.ts").write_text("""
export class OrderService {
    constructor(private supabaseClient: any) {}
    
    async getOrders(userId: string) {
        const { data, error } = await this.supabaseClient
            .from('orders')
            .select('*')
            .eq('user_id', userId);
        
        if (error) throw error;
        return data;
    }
    
    async createOrder(orderData: any) {
        const { data, error } = await this.supabaseClient
            .from('orders')
            .insert(orderData);
            
        if (error) throw error;
        return data;
    }
}
""")
        
        yield outputs_path
        
        # Cleanup
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def qa_engine(self, temp_outputs_dir):
        """Create QA execution engine with temporary directory"""
        return QAExecutionEngine(str(temp_outputs_dir))
    
    def test_qa_engine_initialization(self, temp_outputs_dir):
        """Test QA engine initializes correctly"""
        qa_engine = QAExecutionEngine(str(temp_outputs_dir))
        
        assert qa_engine.outputs_dir == temp_outputs_dir
        assert qa_engine.logger is not None
    
    def test_read_agent_output(self, qa_engine):
        """Test reading agent output code files"""
        code_files = qa_engine._read_agent_output("BE-07")
        
        assert len(code_files) == 2
        assert any("customer_service.py" in f for f in code_files)
        assert any("order_service.ts" in f for f in code_files)
    
    def test_read_agent_output_no_code_dir(self, qa_engine):
        """Test reading agent output when no code directory exists"""
        code_files = qa_engine._read_agent_output("NONEXISTENT-TASK")
        
        assert len(code_files) == 0
    
    @patch('orchestration.qa_execution.EnhancedQAAgent')
    def test_auto_generate_tests(self, mock_qa_agent, qa_engine):
        """Test automatic test generation"""
        # Mock QA agent
        mock_agent_instance = Mock()
        mock_agent_instance.generate_comprehensive_tests.return_value = {
            "generated_tests": [
                {"status": "success", "test_count": 5},
                {"status": "success", "test_count": 3},
                {"status": "error", "error": "Complex dependency"}
            ]
        }
        mock_qa_agent.return_value = mock_agent_instance
        
        code_files = ["customer_service.py", "order_service.ts"]
        result = qa_engine._auto_generate_tests("BE-07", code_files)
        
        assert result["generated_tests"] == 3
        assert result["successful"] == 2
        assert result["failed"] == 1
        assert "details" in result
    
    def test_run_static_analysis_python(self, qa_engine):
        """Test static analysis on Python files"""
        # Create a temp file with linting issues
        temp_file = qa_engine.outputs_dir / "BE-07" / "code" / "test_lint.py"
        temp_file.write_text("def very_long_function_name_that_exceeds_line_limit_and_should_trigger_warning():\n    print('test')   \n")
        
        issues = qa_engine._run_static_analysis("BE-07", [str(temp_file)])
        
        assert len(issues) >= 1
        assert any("Line too long" in issue["message"] for issue in issues)
        assert any("Trailing whitespace" in issue["message"] for issue in issues)
    
    def test_run_static_analysis_javascript(self, qa_engine):
        """Test static analysis on JavaScript files"""
        # Create a temp file with linting issues
        temp_file = qa_engine.outputs_dir / "BE-07" / "code" / "test_lint.js"
        temp_file.write_text("function test() { console.log('this is a very long line that should trigger a line length warning'); }")
        
        issues = qa_engine._run_static_analysis("BE-07", [str(temp_file)])
        
        assert len(issues) >= 1
        assert any("console.log" in issue["message"] for issue in issues)
        assert any("Line too long" in issue["message"] for issue in issues)
    
    def test_execute_tests_no_tests(self, qa_engine):
        """Test test execution when no tests exist"""
        result = qa_engine._execute_tests("BE-07")
        
        assert result["passed"] == 0
        assert result["failed"] == 0
        assert result["total"] == 0
    
    def test_execute_tests_with_mock_tests(self, qa_engine):
        """Test test execution with mock test files"""
        # Create test directory and files
        test_dir = qa_engine.outputs_dir / "BE-07" / "tests" / "generated"
        test_dir.mkdir(parents=True)
        
        # Create mock test files
        (test_dir / "test_customer_service.py").write_text("def test_customer(): pass")
        (test_dir / "test_order_service.js").write_text("test('order test', () => {});")
        
        result = qa_engine._execute_tests("BE-07")
        
        assert result["passed"] > 0
        assert result["total"] > 0
        assert result["test_files"] == 2
    
    def test_generate_qa_report_passed(self, qa_engine):
        """Test QA report generation with passing status"""
        test_results = {"successful": 2, "failed": 0}
        test_execution = {"passed": 6, "failed": 0}
        linting_issues = [{"severity": "warning", "message": "Minor issue"}]
        code_files = ["file1.py", "file2.py"]
        
        report = qa_engine._generate_qa_report("BE-07", test_results, test_execution, linting_issues, code_files)
        
        assert report["tests_passed"] == 6
        assert report["tests_failed"] == 0
        assert report["coverage"] == 100.0  # 2/2 files
        assert report["status"] == "PASSED"
        assert len(report["issues"]) == 0  # No critical issues
    
    def test_generate_qa_report_failed(self, qa_engine):
        """Test QA report generation with failing status"""
        test_results = {"successful": 1, "failed": 1}
        test_execution = {"passed": 3, "failed": 2}
        linting_issues = [{"severity": "error", "message": "Critical issue"}]
        code_files = ["file1.py", "file2.py"]
        
        report = qa_engine._generate_qa_report("BE-07", test_results, test_execution, linting_issues, code_files)
        
        assert report["tests_passed"] == 3
        assert report["tests_failed"] == 2
        assert report["status"] == "FAILED"
        assert len(report["issues"]) == 1  # One critical issue
    
    def test_save_qa_report(self, qa_engine):
        """Test saving QA report to file"""
        qa_report = {
            "tests_passed": 6,
            "tests_failed": 0,
            "coverage": 92.4,
            "issues": [],
            "status": "PASSED"
        }
        
        qa_engine._save_qa_report("BE-07", qa_report)
        
        report_file = qa_engine.outputs_dir / "BE-07" / "qa_report.json"
        assert report_file.exists()
        
        # Verify content
        with open(report_file) as f:
            saved_report = json.load(f)
        
        assert saved_report["tests_passed"] == 6
        assert saved_report["status"] == "PASSED"
        assert "task_id" in saved_report
        assert "timestamp" in saved_report
    
    @patch('orchestration.qa_execution.EnhancedQAAgent')
    def test_execute_qa_for_task_success(self, mock_qa_agent, qa_engine):
        """Test full QA execution for a task"""
        # Mock QA agent
        mock_agent_instance = Mock()
        mock_agent_instance.generate_comprehensive_tests.return_value = {
            "generated_tests": [
                {"status": "success", "test_count": 5},
                {"status": "success", "test_count": 3}
            ]
        }
        mock_qa_agent.return_value = mock_agent_instance
        
        result = qa_engine.execute_qa_for_task("BE-07")
        
        assert result["status"] == "PASSED"
        assert result["tests_passed"] > 0
        assert "coverage" in result
        assert isinstance(result["issues"], list)
        
        # Verify report was saved
        report_file = qa_engine.outputs_dir / "BE-07" / "qa_report.json"
        assert report_file.exists()
    
    def test_execute_qa_for_task_no_directory(self, qa_engine):
        """Test QA execution when task directory doesn't exist"""
        result = qa_engine.execute_qa_for_task("NONEXISTENT-TASK")
        
        assert result["status"] == "ERROR"
        assert len(result["issues"]) > 0
        assert "Task directory not found" in result["issues"][0]["message"]
    
    def test_create_error_report(self, qa_engine):
        """Test error report creation"""
        result = qa_engine._create_error_report("BE-07", "Test error message")
        
        assert result["status"] == "ERROR"
        assert result["tests_passed"] == 0
        assert result["tests_failed"] == 0
        assert len(result["issues"]) == 1
        assert "Test error message" in result["issues"][0]["message"]
    
    def test_create_minimal_report(self, qa_engine):
        """Test minimal report creation"""
        result = qa_engine._create_minimal_report("BE-07", "No code files")
        
        assert result["status"] == "SKIPPED"
        assert "message" in result
        assert result["message"] == "No code files"


class TestLangGraphQAIntegration:
    """Test cases for LangGraph QA integration"""
    
    @pytest.fixture
    def temp_outputs_dir(self):
        """Create temporary outputs directory"""
        temp_dir = tempfile.mkdtemp()
        yield Path(temp_dir)
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def qa_integration(self, temp_outputs_dir):
        """Create QA integration instance"""
        return LangGraphQAIntegration(str(temp_outputs_dir))
    
    @patch('orchestration.langgraph_qa_integration.QAExecutionEngine')
    def test_handle_qa_pending_state_success(self, mock_qa_engine, qa_integration):
        """Test handling QA_PENDING state with successful validation"""
        # Mock QA engine
        mock_engine_instance = Mock()
        mock_engine_instance.execute_qa_for_task.return_value = {
            "tests_passed": 6,
            "tests_failed": 0,
            "coverage": 92.4,
            "issues": [],
            "status": "PASSED"
        }
        mock_qa_engine.return_value = mock_engine_instance
        
        result = qa_integration.handle_qa_pending_state("BE-07", {"agent": "backend"})
        
        assert result["task_id"] == "BE-07"
        assert result["current_state"] == "QA_PENDING"
        assert result["next_state"] == "DOCUMENTATION"
        assert result["qa_result"]["status"] == "PASSED"
        assert "timestamp" in result
    
    @patch('orchestration.langgraph_qa_integration.QAExecutionEngine')
    def test_handle_qa_pending_state_failed(self, mock_qa_engine, qa_integration):
        """Test handling QA_PENDING state with failed validation"""
        # Mock QA engine
        mock_engine_instance = Mock()
        mock_engine_instance.execute_qa_for_task.return_value = {
            "tests_passed": 3,
            "tests_failed": 2,
            "coverage": 45.0,
            "issues": [{"severity": "error", "message": "Critical issue"}],
            "status": "FAILED"
        }
        mock_qa_engine.return_value = mock_engine_instance
        
        result = qa_integration.handle_qa_pending_state("BE-07")
        
        assert result["next_state"] == "FIXES_REQUIRED"
        assert result["qa_result"]["status"] == "FAILED"
    
    def test_determine_next_state(self, qa_integration):
        """Test next state determination logic"""
        # Test PASSED status
        qa_result = {"status": "PASSED"}
        assert qa_integration._determine_next_state(qa_result) == "DOCUMENTATION"
        
        # Test FAILED status
        qa_result = {"status": "FAILED"}
        assert qa_integration._determine_next_state(qa_result) == "FIXES_REQUIRED"
        
        # Test WARNING status
        qa_result = {"status": "WARNING"}
        assert qa_integration._determine_next_state(qa_result) == "REVIEW_REQUIRED"
        
        # Test ERROR status
        qa_result = {"status": "ERROR"}
        assert qa_integration._determine_next_state(qa_result) == "ERROR"
    
    def test_get_transition_reason(self, qa_integration):
        """Test transition reason generation"""
        qa_result = {
            "status": "PASSED",
            "tests_passed": 6,
            "tests_failed": 0,
            "coverage": 92.4,
            "issues": []
        }
        
        reason = qa_integration._get_transition_reason(qa_result)
        
        assert "passed" in reason.lower()
        assert "6 tests passed" in reason
        assert "92.4% coverage" in reason
    
    def test_log_state_transition(self, qa_integration):
        """Test state transition logging"""
        qa_integration._log_state_transition("BE-07", "QA_PENDING", {"agent": "backend"})
        
        log_file = Path("logs/langgraph/BE-07_transitions.jsonl")
        assert log_file.exists()
        
        # Verify log content
        with open(log_file) as f:
            log_entry = json.loads(f.readline())
        
        assert log_entry["task_id"] == "BE-07"
        assert log_entry["event"] == "state_transition"
        assert log_entry["state"] == "QA_PENDING"


class TestQAExecutionCLI:
    """Test cases for QA execution CLI interface"""
    
    def test_execute_qa_validation_function(self):
        """Test main execute_qa_validation function"""
        # This would typically be mocked in a real test
        # For now, just test that the function is callable
        assert callable(execute_qa_validation)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
