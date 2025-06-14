"""
Tests for Input Validation System

Comprehensive test suite for the input validation utilities to ensure
proper validation and sanitization of all inputs across the system.
"""

import pytest
import argparse
import tempfile
import json
from pathlib import Path
from unittest.mock import Mock

from src.platform.utils.input_validation import (
    InputValidator, ValidationError, validate_task_id, validate_checkpoint_id,
    validate_file_path, validate_string_content, validate_json_data,
    validate_command_args, get_validator
)


class TestInputValidator:
    """Test the InputValidator class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.validator = InputValidator()
    
    def test_validate_task_id_valid(self):
        """Test valid task ID validation."""
        # Valid task IDs
        valid_ids = ['BE-07', 'FE-123', 'TL-01', 'QA-999', 'DOC-1']
        
        for task_id in valid_ids:
            result = self.validator.validate_task_id(task_id)
            assert result == task_id.upper()
    
    def test_validate_task_id_invalid(self):
        """Test invalid task ID validation."""
        # Invalid task IDs
        invalid_ids = [
            '',  # Empty
            'INVALID',  # No number
            'BE',  # No number
            'BE-',  # No number after dash
            '123-BE',  # Wrong format
            'BE-07-08',  # Too many parts
            'X-12345',  # Number too long
            'TOOLONG-01',  # Prefix too long
            'be-07<script>',  # Injection attempt
        ]
        
        for task_id in invalid_ids:
            with pytest.raises(ValidationError):
                self.validator.validate_task_id(task_id)
    
    def test_validate_checkpoint_id_valid(self):
        """Test valid checkpoint ID validation."""
        valid_ids = [
            'hitl_BE-07_abc12345',
            'hitl_FE-123_1234567890abcdef',
            'hitl_TL-01_hash123456'
        ]
        
        for checkpoint_id in valid_ids:
            result = self.validator.validate_checkpoint_id(checkpoint_id)
            assert result == checkpoint_id
    
    def test_validate_checkpoint_id_invalid(self):
        """Test invalid checkpoint ID validation."""
        invalid_ids = [
            '',  # Empty
            'invalid',  # Wrong format
            'hitl_BE-07',  # Missing hash
            'BE-07_abc123',  # Missing hitl prefix
            'hitl_INVALID_abc123',  # Invalid task format
            'hitl_BE-07_short',  # Hash too short
        ]
        
        for checkpoint_id in invalid_ids:
            with pytest.raises(ValidationError):
                self.validator.validate_checkpoint_id(checkpoint_id)
    
    def test_validate_file_path_valid(self):
        """Test valid file path validation."""
        # Create temporary file for testing
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            f.write('{"test": "data"}')
            temp_file = f.name
        
        try:
            # Should validate successfully
            result = self.validator.validate_file_path(temp_file, must_exist=True)
            assert isinstance(result, Path)
            assert result.exists()
        finally:
            Path(temp_file).unlink()
    
    def test_validate_file_path_traversal_prevention(self):
        """Test path traversal prevention."""
        dangerous_paths = [
            '../../../etc/passwd',
            '..\\..\\windows\\system32\\config\\sam',
            '/etc/shadow',
            'C:\\Windows\\System32\\config\\SAM',
            './../../sensitive/file.txt',
            'file://../../etc/passwd',
        ]
        
        for path in dangerous_paths:
            with pytest.raises(ValidationError):
                self.validator.validate_file_path(path, must_exist=False)
    
    def test_validate_string_content_basic(self):
        """Test basic string content validation."""
        # Valid strings
        valid_strings = [
            'Simple text',
            'Text with numbers 123',
            'Special chars: !@#$%^&*()',
            'Multi\nline\ntext',
        ]
        
        for text in valid_strings:
            result = self.validator.validate_string_content(text)
            assert isinstance(result, str)
            assert len(result) <= len(text)  # May be sanitized
    
    def test_validate_string_content_dangerous(self):
        """Test dangerous string content sanitization."""
        dangerous_strings = [
            '<script>alert("xss")</script>',
            'javascript:void(0)',
            'onclick="malicious()"',
            'vbscript:msgbox("bad")',
        ]
        
        for text in dangerous_strings:
            result = self.validator.validate_string_content(text)
            # Should be sanitized, not rejected
            assert '<script>' not in result
            assert 'javascript:' not in result
    
    def test_validate_string_content_length_limit(self):
        """Test string length validation."""
        # String too long
        long_string = 'a' * 20000
        
        with pytest.raises(ValidationError):
            self.validator.validate_string_content(long_string, max_length=1000)
        
        # String within limit
        short_string = 'a' * 500
        result = self.validator.validate_string_content(short_string, max_length=1000)
        assert result == short_string
    
    def test_validate_json_data_valid(self):
        """Test valid JSON data validation."""
        valid_json_objects = [
            {'key': 'value'},
            {'nested': {'object': True}},
            {'array': [1, 2, 3]},
            {'mixed': {'string': 'value', 'number': 42, 'bool': True}},
        ]
        
        for obj in valid_json_objects:
            result = self.validator.validate_json_data(obj)
            assert result == obj
        
        # Test JSON string parsing
        json_string = '{"test": "value"}'
        result = self.validator.validate_json_data(json_string)
        assert result == {"test": "value"}
    
    def test_validate_json_data_invalid(self):
        """Test invalid JSON data validation."""
        # Invalid JSON string
        with pytest.raises(ValidationError):
            self.validator.validate_json_data('{"invalid": json}')
        
        # JSON too large
        large_object = {'key' + str(i): 'value' * 1000 for i in range(1000)}
        with pytest.raises(ValidationError):
            self.validator.validate_json_data(large_object, max_size=1000)
    
    def test_validate_integer_range(self):
        """Test integer range validation."""
        # Valid integers
        assert self.validator.validate_integer_range(5, 0, 10) == 5
        assert self.validator.validate_integer_range('7', 0, 10) == 7
        assert self.validator.validate_integer_range(0, 0, 10) == 0
        assert self.validator.validate_integer_range(10, 0, 10) == 10
        
        # Invalid integers
        with pytest.raises(ValidationError):
            self.validator.validate_integer_range(-1, 0, 10)
        
        with pytest.raises(ValidationError):
            self.validator.validate_integer_range(11, 0, 10)
        
        with pytest.raises(ValidationError):
            self.validator.validate_integer_range('not_a_number', 0, 10)
    
    def test_validate_command_args(self):
        """Test command line argument validation."""
        # Create mock args
        args = argparse.Namespace()
        args.task_id = 'BE-07'
        args.checkpoint_id = 'hitl_BE-07_abc123456'
        args.reviewer = 'john.doe'
        args.file_path = './test.json'
        args.level = 2
        args.comments = 'Valid comments'
        
        # Should validate without error
        result = self.validator.validate_command_args(args)
        assert result.task_id == 'BE-07'
        assert result.checkpoint_id == 'hitl_BE-07_abc123456'
        assert result.reviewer == 'john.doe'


class TestConvenienceFunctions:
    """Test convenience functions."""
    
    def test_validate_task_id_function(self):
        """Test standalone validate_task_id function."""
        result = validate_task_id('be-07')
        assert result == 'BE-07'
    
    def test_validate_checkpoint_id_function(self):
        """Test standalone validate_checkpoint_id function."""
        checkpoint_id = 'hitl_BE-07_abc123456'
        result = validate_checkpoint_id(checkpoint_id)
        assert result == checkpoint_id
    
    def test_validate_string_content_function(self):
        """Test standalone validate_string_content function."""
        result = validate_string_content('test string')
        assert result == 'test string'
    
    def test_validate_json_data_function(self):
        """Test standalone validate_json_data function."""
        data = {'test': 'data'}
        result = validate_json_data(data)
        assert result == data


class TestValidationSecurity:
    """Test security aspects of validation."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.validator = InputValidator()
    
    def test_sql_injection_prevention(self):
        """Test SQL injection attempt prevention."""
        sql_injections = [
            "'; DROP TABLE users; --",
            "' OR '1'='1",
            "UNION SELECT * FROM sensitive_data",
            "'; INSERT INTO logs VALUES ('hacked'); --",
        ]
        
        for injection in sql_injections:
            # Should not raise error but should sanitize
            result = self.validator.validate_string_content(injection)
            assert result != injection  # Should be modified
    
    def test_xss_prevention(self):
        """Test XSS prevention."""
        xss_attempts = [
            '<script>alert("xss")</script>',
            '<img src="x" onerror="alert(1)">',
            'javascript:alert("xss")',
            '<iframe src="javascript:alert(1)"></iframe>',
        ]
        
        for xss in xss_attempts:
            result = self.validator.validate_string_content(xss)
            # Should be sanitized
            assert '<script>' not in result
            assert 'javascript:' not in result
            assert 'onerror=' not in result
    
    def test_path_traversal_prevention(self):
        """Test comprehensive path traversal prevention."""
        traversal_attempts = [
            '../../../etc/passwd',
            '..\\..\\..\\windows\\system32',
            '/etc/shadow',
            '../../../../bin/sh',
            '..%2F..%2F..%2Fetc%2Fpasswd',  # URL encoded
            '....//....//....//etc/passwd',  # Double encoding
        ]
        
        for path in traversal_attempts:
            with pytest.raises(ValidationError):
                self.validator.validate_file_path(path, must_exist=False)
    
    def test_command_injection_prevention(self):
        """Test command injection prevention."""
        command_injections = [
            '; rm -rf /',
            '| cat /etc/passwd',
            '&& shutdown -h now',
            '$(cat /etc/shadow)',
            '`rm -rf /`',
        ]
        
        for injection in command_injections:
            result = self.validator.validate_string_content(injection)
            # Should be sanitized or rejected
            assert ';' not in result or '|' not in result or '&' not in result


class TestErrorHandling:
    """Test error handling and edge cases."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.validator = InputValidator()
    
    def test_none_inputs(self):
        """Test handling of None inputs."""
        with pytest.raises(ValidationError):
            self.validator.validate_task_id(None)
        
        with pytest.raises(ValidationError):
            self.validator.validate_string_content(None)
    
    def test_empty_inputs(self):
        """Test handling of empty inputs."""
        with pytest.raises(ValidationError):
            self.validator.validate_task_id('')
        
        with pytest.raises(ValidationError):
            self.validator.validate_checkpoint_id('')
    
    def test_wrong_type_inputs(self):
        """Test handling of wrong type inputs."""
        with pytest.raises(ValidationError):
            self.validator.validate_task_id(123)
        
        with pytest.raises(ValidationError):
            self.validator.validate_string_content(['not', 'a', 'string'])
    
    def test_unicode_handling(self):
        """Test Unicode string handling."""
        unicode_strings = [
            'Hello 世界',
            'Café ñoño',
            '🚀 emoji test',
            'русский текст',
        ]
        
        for text in unicode_strings:
            result = self.validator.validate_string_content(text)
            assert isinstance(result, str)
            # Should preserve Unicode characters
            assert len(result) > 0


class TestGlobalValidator:
    """Test global validator instance."""
    
    def test_singleton_behavior(self):
        """Test that get_validator returns same instance."""
        validator1 = get_validator()
        validator2 = get_validator()
        assert validator1 is validator2
    
    def test_global_validator_functionality(self):
        """Test that global validator works correctly."""
        validator = get_validator()
        result = validator.validate_task_id('BE-07')
        assert result == 'BE-07'


class TestPerformance:
    """Test performance aspects of validation."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.validator = InputValidator()
    
    def test_large_string_performance(self):
        """Test validation performance with large strings."""
        import time
        
        # Test with moderately large string
        large_string = 'a' * 10000
        
        start_time = time.time()
        result = self.validator.validate_string_content(large_string)
        end_time = time.time()
        
        # Should complete in reasonable time (< 1 second)
        assert end_time - start_time < 1.0
        assert result == large_string
    
    def test_many_validations_performance(self):
        """Test performance with many validations."""
        import time
        
        task_ids = [f'BE-{i:03d}' for i in range(100)]
        
        start_time = time.time()
        for task_id in task_ids:
            self.validator.validate_task_id(task_id)
        end_time = time.time()
        
        # Should complete 100 validations quickly (< 0.1 seconds)
        assert end_time - start_time < 0.1


if __name__ == '__main__':
    pytest.main([__file__])