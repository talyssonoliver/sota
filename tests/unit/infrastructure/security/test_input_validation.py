#!/usr/bin/env python3
"""
Comprehensive Tests for Input Validation Framework

Tests all validation rules, input sanitization, and security protection.
Critical for achieving 80% test coverage target.
"""

import pytest
import json
from unittest.mock import patch, MagicMock
from flask import Flask, request

from src.infrastructure.security.input_validation import (
    ValidationError,
    ValidationRule,
    StringLengthRule,
    RegexRule,
    EmailRule,
    URLRule,
    NumericRangeRule,
    SQLInjectionRule,
    XSSRule,
    FilePathRule,
    JSONRule,
    InputValidator,
    create_api_validator,
    create_hitl_validator,
    create_file_upload_validator,
    validate_request,
    api_validator,
    hitl_validator,
    file_validator,
    validate_email,
    validate_url,
    sanitize_html,
    is_safe_path
)


class TestValidationError:
    """Test ValidationError exception."""
    
    def test_validation_error_creation(self):
        """Test creating ValidationError with message only."""
        error = ValidationError("Test error message")
        assert str(error) == "Test error message"
        assert error.message == "Test error message"
        assert error.field is None
        assert error.value is None
    
    def test_validation_error_with_field_and_value(self):
        """Test creating ValidationError with field and value."""
        error = ValidationError("Invalid value", field="username", value="invalid_user")
        assert error.message == "Invalid value"
        assert error.field == "username"
        assert error.value == "invalid_user"


class TestValidationRule:
    """Test base ValidationRule class."""
    
    def test_validation_rule_initialization(self):
        """Test ValidationRule initialization."""
        rule = ValidationRule("Custom error message")
        assert rule.error_message == "Custom error message"
    
    def test_validation_rule_validate_not_implemented(self):
        """Test that validate method raises NotImplementedError."""
        rule = ValidationRule()
        with pytest.raises(NotImplementedError):
            rule.validate("test_value")
    
    def test_validation_rule_sanitize_default(self):
        """Test that sanitize method returns value unchanged by default."""
        rule = ValidationRule()
        test_value = "test_value"
        assert rule.sanitize(test_value) == test_value


class TestStringLengthRule:
    """Test StringLengthRule validation."""
    
    def test_string_length_rule_initialization(self):
        """Test StringLengthRule initialization."""
        rule = StringLengthRule(min_length=5, max_length=20)
        assert rule.min_length == 5
        assert rule.max_length == 20
        assert "between 5 and 20 characters" in rule.error_message
    
    def test_string_length_rule_min_only(self):
        """Test StringLengthRule with minimum length only."""
        rule = StringLengthRule(min_length=3)
        assert rule.min_length == 3
        assert rule.max_length is None
        assert "at least 3 characters" in rule.error_message
    
    def test_validate_valid_strings(self):
        """Test validation of valid strings."""
        rule = StringLengthRule(min_length=3, max_length=10)
        
        valid_strings = ["abc", "hello", "1234567890"]
        for string in valid_strings:
            assert rule.validate(string) is True
    
    def test_validate_invalid_strings(self):
        """Test validation of invalid strings."""
        rule = StringLengthRule(min_length=3, max_length=10)
        
        invalid_strings = ["ab", "12345678901", ""]
        for string in invalid_strings:
            assert rule.validate(string) is False
    
    def test_validate_non_string_input(self):
        """Test validation of non-string input."""
        rule = StringLengthRule(min_length=1, max_length=10)
        
        non_strings = [123, None, [], {}]
        for value in non_strings:
            assert rule.validate(value) is False


class TestRegexRule:
    """Test RegexRule validation."""
    
    def test_regex_rule_initialization(self):
        """Test RegexRule initialization."""
        pattern = r"^[a-zA-Z0-9]+$"
        rule = RegexRule(pattern, "Alphanumeric only")
        assert rule.pattern.pattern == pattern
        assert rule.error_message == "Alphanumeric only"
    
    def test_validate_matching_strings(self):
        """Test validation of strings that match regex."""
        rule = RegexRule(r"^[a-zA-Z0-9]+$")
        
        valid_strings = ["abc123", "ABC", "123", "testUser123"]
        for string in valid_strings:
            assert rule.validate(string) is True
    
    def test_validate_non_matching_strings(self):
        """Test validation of strings that don't match regex."""
        rule = RegexRule(r"^[a-zA-Z0-9]+$")
        
        invalid_strings = ["test@email.com", "user name", "test-user", ""]
        for string in invalid_strings:
            assert rule.validate(string) is False
    
    def test_validate_non_string_input(self):
        """Test validation of non-string input."""
        rule = RegexRule(r"^[a-zA-Z0-9]+$")
        
        non_strings = [123, None, [], {}]
        for value in non_strings:
            assert rule.validate(value) is False


class TestEmailRule:
    """Test EmailRule validation."""
    
    def test_email_rule_initialization(self):
        """Test EmailRule initialization."""
        rule = EmailRule()
        assert "Invalid email address format" in rule.error_message
    
    def test_validate_valid_emails(self):
        """Test validation of valid email addresses."""
        rule = EmailRule()
        
        valid_emails = [
            "user@example.com",
            "test.email@domain.co.uk",
            "user+tag@example.org",
            "firstname.lastname@company.com",
            "user123@test123.com"
        ]
        
        for email in valid_emails:
            assert rule.validate(email) is True, f"Email {email} should be valid"
    
    def test_validate_invalid_emails(self):
        """Test validation of invalid email addresses."""
        rule = EmailRule()
        
        invalid_emails = [
            "notanemail",
            "@example.com",
            "user@",
            "user..name@example.com",
            "user@.com",
            "user@com",
            "",
            None
        ]
        
        for email in invalid_emails:
            assert rule.validate(email) is False, f"Email {email} should be invalid"


class TestURLRule:
    """Test URLRule validation."""
    
    def test_url_rule_initialization(self):
        """Test URLRule initialization."""
        rule = URLRule()
        assert rule.allowed_schemes == ['http', 'https']
        assert "Invalid URL format" in rule.error_message
    
    def test_url_rule_custom_schemes(self):
        """Test URLRule with custom allowed schemes."""
        rule = URLRule(allowed_schemes=['ftp', 'sftp'])
        assert rule.allowed_schemes == ['ftp', 'sftp']
    
    def test_validate_valid_urls(self):
        """Test validation of valid URLs."""
        rule = URLRule()
        
        valid_urls = [
            "http://example.com",
            "https://www.example.com",
            "https://example.com/path/to/resource",
            "http://subdomain.example.com:8080/path?param=value",
            "https://example.com/path#anchor"
        ]
        
        for url in valid_urls:
            assert rule.validate(url) is True, f"URL {url} should be valid"
    
    def test_validate_invalid_urls(self):
        """Test validation of invalid URLs."""
        rule = URLRule()
        
        invalid_urls = [
            "not_a_url",
            "ftp://example.com",  # Wrong scheme
            "http://",
            "https://",
            "://example.com",
            "",
            None
        ]
        
        for url in invalid_urls:
            assert rule.validate(url) is False, f"URL {url} should be invalid"
    
    def test_validate_custom_scheme_urls(self):
        """Test validation with custom schemes."""
        rule = URLRule(allowed_schemes=['ftp'])
        
        assert rule.validate("ftp://files.example.com") is True
        assert rule.validate("http://example.com") is False


class TestNumericRangeRule:
    """Test NumericRangeRule validation."""
    
    def test_numeric_range_rule_initialization(self):
        """Test NumericRangeRule initialization."""
        rule = NumericRangeRule(min_value=0, max_value=100)
        assert rule.min_value == 0
        assert rule.max_value == 100
        assert "minimum 0" in rule.error_message
        assert "maximum 100" in rule.error_message
    
    def test_validate_valid_numbers(self):
        """Test validation of valid numbers."""
        rule = NumericRangeRule(min_value=0, max_value=100)
        
        valid_numbers = [0, 50, 100, 25.5, 0.1, 99.9]
        for number in valid_numbers:
            assert rule.validate(number) is True, f"Number {number} should be valid"
    
    def test_validate_invalid_numbers(self):
        """Test validation of invalid numbers."""
        rule = NumericRangeRule(min_value=0, max_value=100)
        
        invalid_numbers = [-1, 101, -0.1, 100.1]
        for number in invalid_numbers:
            assert rule.validate(number) is False, f"Number {number} should be invalid"
    
    def test_validate_string_numbers(self):
        """Test validation of numeric strings."""
        rule = NumericRangeRule(min_value=0, max_value=100)
        
        assert rule.validate("50") is True
        assert rule.validate("25.5") is True
        assert rule.validate("101") is False
        assert rule.validate("-1") is False
        assert rule.validate("not_a_number") is False
    
    def test_validate_min_only(self):
        """Test validation with minimum value only."""
        rule = NumericRangeRule(min_value=10)
        
        assert rule.validate(10) is True
        assert rule.validate(100) is True
        assert rule.validate(9) is False
    
    def test_validate_max_only(self):
        """Test validation with maximum value only."""
        rule = NumericRangeRule(max_value=10)
        
        assert rule.validate(10) is True
        assert rule.validate(-100) is True
        assert rule.validate(11) is False


class TestSQLInjectionRule:
    """Test SQLInjectionRule validation."""
    
    def test_sql_injection_rule_initialization(self):
        """Test SQLInjectionRule initialization."""
        rule = SQLInjectionRule()
        assert "Potentially dangerous input detected" in rule.error_message
        assert len(rule.compiled_patterns) > 0
    
    def test_validate_safe_inputs(self):
        """Test validation of safe inputs."""
        rule = SQLInjectionRule()
        
        safe_inputs = [
            "normal text",
            "user@example.com",
            "Product Name",
            "Description with spaces",
            "123456",
            ""
        ]
        
        for input_text in safe_inputs:
            assert rule.validate(input_text) is True, f"Input '{input_text}' should be safe"
    
    def test_validate_sql_injection_attempts(self):
        """Test detection of SQL injection attempts."""
        rule = SQLInjectionRule()
        
        malicious_inputs = [
            "'; DROP TABLE users; --",
            "1' OR '1'='1",
            "UNION SELECT * FROM passwords",
            "INSERT INTO users VALUES",
            "DELETE FROM table",
            "UPDATE users SET password",
            "EXEC sp_executesql",
            "<script>alert('xss')</script>",
            "javascript:alert(1)"
        ]
        
        for malicious_input in malicious_inputs:
            assert rule.validate(malicious_input) is False, f"Input '{malicious_input}' should be detected as malicious"
    
    def test_validate_non_string_input(self):
        """Test validation of non-string input."""
        rule = SQLInjectionRule()
        
        non_strings = [123, None, [], {}]
        for value in non_strings:
            assert rule.validate(value) is True  # Non-strings are safe from SQL injection


class TestXSSRule:
    """Test XSSRule validation."""
    
    def test_xss_rule_initialization(self):
        """Test XSSRule initialization."""
        rule = XSSRule()
        assert "Potentially dangerous HTML/JavaScript detected" in rule.error_message
        assert len(rule.compiled_patterns) > 0
    
    def test_validate_safe_inputs(self):
        """Test validation of safe inputs."""
        rule = XSSRule()
        
        safe_inputs = [
            "normal text",
            "user@example.com",
            "Product description",
            "Price: $29.99",
            "Copyright © 2023",
            ""
        ]
        
        for input_text in safe_inputs:
            assert rule.validate(input_text) is True, f"Input '{input_text}' should be safe"
    
    def test_validate_xss_attempts(self):
        """Test detection of XSS attempts."""
        rule = XSSRule()
        
        malicious_inputs = [
            "<script>alert('xss')</script>",
            "<img src=x onerror=alert(1)>",
            "javascript:alert(1)",
            "vbscript:msgbox(1)",
            "<iframe src='malicious.com'></iframe>",
            "<object data='malicious.swf'></object>",
            "<embed src='malicious.swf'>",
            "<link rel='stylesheet' href='malicious.css'>",
            "<meta http-equiv='refresh' content='0;url=malicious.com'>"
        ]
        
        for malicious_input in malicious_inputs:
            assert rule.validate(malicious_input) is False, f"Input '{malicious_input}' should be detected as XSS"
    
    def test_sanitize_html_content(self):
        """Test HTML sanitization."""
        rule = XSSRule()
        
        html_input = "<p>Hello <strong>world</strong> & friends</p>"
        sanitized = rule.sanitize(html_input)
        
        assert "&lt;" in sanitized
        assert "&gt;" in sanitized
        assert "&amp;" in sanitized
        assert "<" not in sanitized
        assert ">" not in sanitized
    
    def test_sanitize_non_string_input(self):
        """Test sanitization of non-string input."""
        rule = XSSRule()
        
        non_strings = [123, None, [], {}]
        for value in non_strings:
            assert rule.sanitize(value) == value


class TestFilePathRule:
    """Test FilePathRule validation."""
    
    def test_file_path_rule_initialization(self):
        """Test FilePathRule initialization."""
        rule = FilePathRule()
        assert rule.allowed_extensions == []
        assert "Invalid or dangerous file path" in rule.error_message
    
    def test_file_path_rule_with_extensions(self):
        """Test FilePathRule with allowed extensions."""
        rule = FilePathRule(allowed_extensions=['txt', 'json', 'py'])
        assert rule.allowed_extensions == ['txt', 'json', 'py']
    
    def test_validate_safe_paths(self):
        """Test validation of safe file paths."""
        rule = FilePathRule()
        
        safe_paths = [
            "document.txt",
            "folder/file.json",
            "config.yaml",
            "script.py",
            "image.png"
        ]
        
        for path in safe_paths:
            assert rule.validate(path) is True, f"Path '{path}' should be safe"
    
    def test_validate_dangerous_paths(self):
        """Test detection of dangerous file paths."""
        rule = FilePathRule()
        
        dangerous_paths = [
            "../etc/passwd",
            "../../config/secrets.txt",
            "/etc/shadow",
            "C:\\Windows\\System32\\config",
            "file:///etc/passwd",
            "\\..\\..\\config.ini"
        ]
        
        for path in dangerous_paths:
            assert rule.validate(path) is False, f"Path '{path}' should be detected as dangerous"
    
    def test_validate_with_extension_restrictions(self):
        """Test validation with file extension restrictions."""
        rule = FilePathRule(allowed_extensions=['txt', 'json'])
        
        assert rule.validate("document.txt") is True
        assert rule.validate("config.json") is True
        assert rule.validate("script.py") is False
        assert rule.validate("malware.exe") is False
    
    def test_validate_non_string_input(self):
        """Test validation of non-string input."""
        rule = FilePathRule()
        
        non_strings = [123, None, [], {}]
        for value in non_strings:
            assert rule.validate(value) is False


class TestJSONRule:
    """Test JSONRule validation."""
    
    def test_json_rule_initialization(self):
        """Test JSONRule initialization."""
        rule = JSONRule()
        assert rule.max_depth == 10
        assert "Invalid JSON format" in rule.error_message
    
    def test_json_rule_custom_depth(self):
        """Test JSONRule with custom max depth."""
        rule = JSONRule(max_depth=5)
        assert rule.max_depth == 5
    
    def test_validate_valid_json_strings(self):
        """Test validation of valid JSON strings."""
        rule = JSONRule()
        
        valid_json = [
            '{"key": "value"}',
            '[1, 2, 3]',
            '"simple string"',
            'true',
            'null',
            '{"nested": {"object": {"value": 123}}}',
            '{"array": [{"item": 1}, {"item": 2}]}'
        ]
        
        for json_str in valid_json:
            assert rule.validate(json_str) is True, f"JSON '{json_str}' should be valid"
    
    def test_validate_invalid_json_strings(self):
        """Test validation of invalid JSON strings."""
        rule = JSONRule()
        
        invalid_json = [
            '{"key": "value"',  # Missing closing brace
            '[1, 2, 3',  # Missing closing bracket
            '{key: "value"}',  # Unquoted key
            "{'key': 'value'}",  # Single quotes
            '{"key": undefined}',  # Invalid value
            '',  # Empty string
            'not json at all'
        ]
        
        for json_str in invalid_json:
            assert rule.validate(json_str) is False, f"JSON '{json_str}' should be invalid"
    
    def test_validate_deeply_nested_json(self):
        """Test validation of deeply nested JSON."""
        rule = JSONRule(max_depth=3)
        
        # Create JSON that exceeds max depth
        deep_json = '{"a": {"b": {"c": {"d": "too deep"}}}}'
        assert rule.validate(deep_json) is False
        
        # Create JSON within depth limit
        shallow_json = '{"a": {"b": {"c": "ok"}}}'
        assert rule.validate(shallow_json) is True
    
    def test_validate_non_string_input(self):
        """Test validation of non-string input."""
        rule = JSONRule()
        
        non_strings = [123, None, {"key": "value"}, [1, 2, 3]]
        for value in non_strings:
            assert rule.validate(value) is True  # Non-strings pass through


class TestInputValidator:
    """Test InputValidator class."""
    
    def setup_method(self):
        """Set up test validator."""
        self.validator = InputValidator()
    
    def test_input_validator_initialization(self):
        """Test InputValidator initialization."""
        assert isinstance(self.validator.rules, dict)
        assert len(self.validator.global_rules) == 2  # SQL injection and XSS rules
    
    def test_add_rule(self):
        """Test adding validation rule for specific field."""
        rule = StringLengthRule(1, 10)
        self.validator.add_rule('username', rule)
        
        assert 'username' in self.validator.rules
        assert rule in self.validator.rules['username']
    
    def test_add_global_rule(self):
        """Test adding global validation rule."""
        rule = NumericRangeRule(0, 100)
        original_count = len(self.validator.global_rules)
        
        self.validator.add_global_rule(rule)
        
        assert len(self.validator.global_rules) == original_count + 1
        assert rule in self.validator.global_rules
    
    def test_validate_field_valid(self):
        """Test validation of valid field."""
        self.validator.add_rule('username', StringLengthRule(3, 20))
        
        is_valid, sanitized, errors = self.validator.validate_field('username', 'testuser')
        
        assert is_valid is True
        assert sanitized == 'testuser'
        assert len(errors) == 0
    
    def test_validate_field_invalid(self):
        """Test validation of invalid field."""
        self.validator.add_rule('username', StringLengthRule(3, 20))
        
        is_valid, sanitized, errors = self.validator.validate_field('username', 'ab')
        
        assert is_valid is False
        assert len(errors) > 0
        assert 'username' in errors[0]
    
    def test_validate_field_with_sanitization(self):
        """Test field validation with sanitization."""
        is_valid, sanitized, errors = self.validator.validate_field(
            'content', '<script>alert("xss")</script>', sanitize=True
        )
        
        assert '&lt;script&gt;' in sanitized
        assert '<script>' not in sanitized
    
    def test_validate_dict_valid(self):
        """Test validation of valid dictionary."""
        self.validator.add_rule('username', StringLengthRule(3, 20))
        self.validator.add_rule('email', EmailRule())
        
        data = {
            'username': 'testuser',
            'email': 'test@example.com'
        }
        
        is_valid, sanitized_data, errors = self.validator.validate_dict(data)
        
        assert is_valid is True
        assert sanitized_data['username'] == 'testuser'
        assert sanitized_data['email'] == 'test@example.com'
        assert len(errors) == 0
    
    def test_validate_dict_invalid(self):
        """Test validation of invalid dictionary."""
        self.validator.add_rule('username', StringLengthRule(3, 20))
        self.validator.add_rule('email', EmailRule())
        
        data = {
            'username': 'ab',  # Too short
            'email': 'invalid_email'  # Invalid format
        }
        
        is_valid, sanitized_data, errors = self.validator.validate_dict(data)
        
        assert is_valid is False
        assert len(errors) >= 2  # At least username and email errors


class TestPreConfiguredValidators:
    """Test pre-configured validator functions."""
    
    def test_create_api_validator(self):
        """Test creation of API validator."""
        validator = create_api_validator()
        
        assert isinstance(validator, InputValidator)
        assert 'email' in validator.rules
        assert 'url' in validator.rules
        assert 'name' in validator.rules
        assert 'id' in validator.rules
    
    def test_create_hitl_validator(self):
        """Test creation of HITL validator."""
        validator = create_hitl_validator()
        
        assert isinstance(validator, InputValidator)
        assert 'checkpoint_type' in validator.rules
        assert 'risk_score' in validator.rules
        assert 'action' in validator.rules
        assert 'data' in validator.rules
    
    def test_create_file_upload_validator(self):
        """Test creation of file upload validator."""
        validator = create_file_upload_validator()
        
        assert isinstance(validator, InputValidator)
        assert 'filename' in validator.rules
        assert 'path' in validator.rules
        assert 'content' in validator.rules


class TestValidateRequestDecorator:
    """Test validate_request decorator."""
    
    def test_validate_request_decorator_valid_data(self):
        """Test decorator with valid request data."""
        app = Flask(__name__)
        
        @app.route('/test', methods=['POST'])
        @validate_request()
        def test_endpoint():
            return {'status': 'success'}
        
        with app.test_client() as client:
            response = client.post('/test', 
                                 json={'name': 'testuser', 'email': 'test@example.com'},
                                 content_type='application/json')
            
            assert response.status_code == 200
    
    def test_validate_request_decorator_invalid_data(self):
        """Test decorator with invalid request data."""
        app = Flask(__name__)
        
        @app.route('/test', methods=['POST'])
        @validate_request()
        def test_endpoint():
            return {'status': 'success'}
        
        with app.test_client() as client:
            response = client.post('/test', 
                                 json={'name': 'a', 'email': 'invalid_email'},
                                 content_type='application/json')
            
            assert response.status_code == 400
            data = response.get_json()
            assert data['status'] == 'error'
            assert 'errors' in data


class TestConvenienceFunctions:
    """Test convenience functions."""
    
    def test_validate_email_function(self):
        """Test validate_email convenience function."""
        assert validate_email('test@example.com') is True
        assert validate_email('invalid_email') is False
    
    def test_validate_url_function(self):
        """Test validate_url convenience function."""
        assert validate_url('https://example.com') is True
        assert validate_url('not_a_url') is False
    
    def test_sanitize_html_function(self):
        """Test sanitize_html convenience function."""
        html = '<script>alert("xss")</script>'
        sanitized = sanitize_html(html)
        
        assert '&lt;script&gt;' in sanitized
        assert '<script>' not in sanitized
    
    def test_is_safe_path_function(self):
        """Test is_safe_path convenience function."""
        assert is_safe_path('document.txt') is True
        assert is_safe_path('../etc/passwd') is False


class TestGlobalValidatorInstances:
    """Test global validator instances."""
    
    def test_api_validator_instance(self):
        """Test global api_validator instance."""
        assert isinstance(api_validator, InputValidator)
        assert 'email' in api_validator.rules
    
    def test_hitl_validator_instance(self):
        """Test global hitl_validator instance."""
        assert isinstance(hitl_validator, InputValidator)
        assert 'risk_score' in hitl_validator.rules
    
    def test_file_validator_instance(self):
        """Test global file_validator instance."""
        assert isinstance(file_validator, InputValidator)
        assert 'filename' in file_validator.rules


class TestValidationIntegration:
    """Integration tests for validation system."""
    
    def test_complete_validation_workflow(self):
        """Test complete validation workflow."""
        # Create custom validator
        validator = InputValidator()
        validator.add_rule('username', StringLengthRule(3, 20))
        validator.add_rule('email', EmailRule())
        validator.add_rule('age', NumericRangeRule(0, 120))
        validator.add_rule('bio', StringLengthRule(0, 500))
        
        # Test valid data
        valid_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'age': 25,
            'bio': 'Software developer'
        }
        
        is_valid, sanitized, errors = validator.validate_dict(valid_data)
        assert is_valid is True
        assert len(errors) == 0
        
        # Test invalid data
        invalid_data = {
            'username': 'ab',  # Too short
            'email': 'invalid',  # Invalid format
            'age': 150,  # Too high
            'bio': '<script>alert("xss")</script>'  # XSS attempt
        }
        
        is_valid, sanitized, errors = validator.validate_dict(invalid_data)
        assert is_valid is False
        assert len(errors) >= 3  # Multiple validation failures
        
        # XSS content should be sanitized
        assert '&lt;script&gt;' in sanitized['bio']
    
    def test_security_protection_integration(self):
        """Test that security protections work together."""
        validator = InputValidator()
        
        # Test data with multiple security threats
        malicious_data = {
            'comment': '<script>alert("xss")</script>',
            'query': "'; DROP TABLE users; --",
            'filename': '../../../etc/passwd'
        }
        
        is_valid, sanitized, errors = validator.validate_dict(malicious_data)
        
        # Should detect multiple security issues
        assert is_valid is False
        assert len(errors) >= 2  # SQL injection and XSS detected
        
        # Content should be sanitized
        assert '&lt;script&gt;' in sanitized['comment']


if __name__ == "__main__":
    pytest.main([__file__, "-v"])