"""
Tests for Business Rules System

Tests the centralized business rule validation that replaces
scattered validation logic across 53 files.
"""

import pytest
import asyncio
from unittest.mock import Mock, patch
from src.core.validation import (
    BusinessRuleEngine, RuleContext, RuleViolation, 
    RuleSeverity, RuleCategory, IBusinessRule,
    RequiredFieldsRule, DataIntegrityRule, WorkflowStateRule,
    AuthorizationRule, TaskAssignmentRule, ConfigurationRule
)


class TestBusinessRuleEngine:
    """Test suite for BusinessRuleEngine"""
    
    def setup_method(self):
        """Setup test environment"""
        self.engine = BusinessRuleEngine()
    
    @pytest.mark.asyncio
    async def test_register_and_unregister_rule(self):
        """Test rule registration and unregistration"""
        # Create mock rule
        mock_rule = Mock(spec=IBusinessRule)
        mock_rule.rule_id = "test_rule"
        
        # Register rule
        self.engine.register_rule(mock_rule)
        assert "test_rule" in self.engine._rules
        
        # Unregister rule
        result = self.engine.unregister_rule("test_rule")
        assert result is True
        assert "test_rule" not in self.engine._rules
        
        # Try to unregister nonexistent rule
        result = self.engine.unregister_rule("nonexistent")
        assert result is False
    
    @pytest.mark.asyncio
    async def test_validate_with_applicable_rules(self):
        """Test validation with applicable rules"""
        # Create mock rule that applies to "test" data type
        mock_rule = Mock(spec=IBusinessRule)
        mock_rule.rule_id = "test_rule"
        mock_rule.rule_name = "Test Rule"
        mock_rule.can_validate.return_value = True
        mock_rule.validate.return_value = [
            RuleViolation(
                rule_id="test_rule",
                rule_name="Test Rule",
                severity=RuleSeverity.ERROR,
                category=RuleCategory.BUSINESS_LOGIC,
                message="Test violation"
            )
        ]
        
        self.engine.register_rule(mock_rule)
        
        context = RuleContext(operation="test")
        violations = await self.engine.validate({"test": "data"}, "test", context)
        
        assert len(violations) == 1
        assert violations[0].message == "Test violation"
        mock_rule.can_validate.assert_called_once_with("test", "test")
        mock_rule.validate.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_validate_with_rule_execution_error(self):
        """Test handling of rule execution errors"""
        # Create mock rule that throws exception
        mock_rule = Mock(spec=IBusinessRule)
        mock_rule.rule_id = "failing_rule"
        mock_rule.rule_name = "Failing Rule"
        mock_rule.can_validate.return_value = True
        mock_rule.validate.side_effect = Exception("Rule execution failed")
        
        self.engine.register_rule(mock_rule)
        
        violations = await self.engine.validate({"test": "data"}, "test")
        
        assert len(violations) == 1
        assert "Rule execution failed" in violations[0].message
        assert violations[0].severity == RuleSeverity.ERROR
    
    def test_add_rule_to_chain(self):
        """Test adding rules to data type chains"""
        self.engine.add_rule_to_chain("task", "rule1")
        self.engine.add_rule_to_chain("task", "rule2")
        self.engine.add_rule_to_chain("user", "rule1")
        
        assert self.engine._rule_chains["task"] == ["rule1", "rule2"]
        assert self.engine._rule_chains["user"] == ["rule1"]
        
        # Adding duplicate should not add again
        self.engine.add_rule_to_chain("task", "rule1")
        assert self.engine._rule_chains["task"] == ["rule1", "rule2"]
    
    def test_get_rules_by_category(self):
        """Test getting rules by category"""
        # Count existing security rules (ConfigurationRule is pre-registered)
        initial_security_rules = self.engine.get_rules_by_category(RuleCategory.SECURITY)
        initial_count = len(initial_security_rules)
        
        # Mock rules with different categories
        rule1 = Mock(spec=IBusinessRule)
        rule1.rule_id = "rule1"
        rule1.category = RuleCategory.SECURITY
        
        rule2 = Mock(spec=IBusinessRule)
        rule2.rule_id = "rule2"
        rule2.category = RuleCategory.BUSINESS_LOGIC
        
        rule3 = Mock(spec=IBusinessRule)
        rule3.rule_id = "rule3"
        rule3.category = RuleCategory.SECURITY
        
        self.engine.register_rule(rule1)
        self.engine.register_rule(rule2)
        self.engine.register_rule(rule3)
        
        security_rules = self.engine.get_rules_by_category(RuleCategory.SECURITY)
        assert len(security_rules) == initial_count + 2  # Initial + 2 new security rules
        assert all(rule.category == RuleCategory.SECURITY for rule in security_rules)
    
    def test_get_rule_stats(self):
        """Test rule statistics"""
        # Register some default rules (they're added in __init__)
        stats = self.engine.get_rule_stats()
        
        assert "total_rules" in stats
        assert "by_category" in stats
        assert "by_severity" in stats
        assert "rule_chains" in stats
        assert stats["total_rules"] > 0


class TestRequiredFieldsRule:
    """Test suite for RequiredFieldsRule"""
    
    def setup_method(self):
        """Setup test environment"""
        self.rule = RequiredFieldsRule()
    
    @pytest.mark.asyncio
    async def test_can_validate(self):
        """Test rule applicability"""
        assert await self.rule.can_validate("task", "create")
        assert await self.rule.can_validate("user", "update")
        assert not await self.rule.can_validate("unknown", "read")
    
    @pytest.mark.asyncio
    async def test_validate_task_with_required_fields(self):
        """Test task validation with all required fields"""
        context = RuleContext(entity_type="task")
        data = {
            "title": "Test Task",
            "status": "pending",
            "priority": "high"
        }
        
        violations = await self.rule.validate(data, context)
        assert len(violations) == 0
    
    @pytest.mark.asyncio
    async def test_validate_task_missing_required_fields(self):
        """Test task validation with missing required fields"""
        context = RuleContext(entity_type="task")
        data = {
            "title": "Test Task"
            # Missing status and priority
        }
        
        violations = await self.rule.validate(data, context)
        assert len(violations) == 2
        
        violation_fields = [v.field for v in violations]
        assert "status" in violation_fields
        assert "priority" in violation_fields
    
    @pytest.mark.asyncio
    async def test_validate_user_with_empty_required_field(self):
        """Test user validation with empty required field"""
        context = RuleContext(entity_type="user")
        data = {
            "username": "testuser",
            "email": ""  # Empty required field
        }
        
        violations = await self.rule.validate(data, context)
        assert len(violations) == 1
        assert violations[0].field == "email"
        assert "empty" in violations[0].message
    
    @pytest.mark.asyncio
    async def test_validate_non_dict_data(self):
        """Test validation with non-dictionary data"""
        context = RuleContext(entity_type="task")
        
        violations = await self.rule.validate("not a dict", context)
        assert len(violations) == 0  # Should handle gracefully


class TestDataIntegrityRule:
    """Test suite for DataIntegrityRule"""
    
    def setup_method(self):
        """Setup test environment"""
        self.rule = DataIntegrityRule()
    
    @pytest.mark.asyncio
    async def test_validate_valid_email(self):
        """Test validation with valid email"""
        context = RuleContext()
        data = {"email": "test@example.com"}
        
        violations = await self.rule.validate(data, context)
        assert len(violations) == 0
    
    @pytest.mark.asyncio
    async def test_validate_invalid_email(self):
        """Test validation with invalid email"""
        context = RuleContext()
        data = {"email": "invalid-email"}
        
        violations = await self.rule.validate(data, context)
        assert len(violations) == 1
        assert violations[0].field == "email"
        assert "Invalid email format" in violations[0].message
    
    @pytest.mark.asyncio
    async def test_validate_task_status(self):
        """Test task status validation"""
        context = RuleContext(entity_type="task")
        
        # Valid status
        data = {"status": "pending"}
        violations = await self.rule.validate(data, context)
        assert len(violations) == 0
        
        # Invalid status
        data = {"status": "invalid_status"}
        violations = await self.rule.validate(data, context)
        assert len(violations) == 1
        assert violations[0].field == "status"
        assert "Invalid task status" in violations[0].message
    
    @pytest.mark.asyncio
    async def test_can_validate_all_types(self):
        """Test that rule applies to all data types"""
        assert await self.rule.can_validate("any_type", "any_operation")


class TestWorkflowStateRule:
    """Test suite for WorkflowStateRule"""
    
    def setup_method(self):
        """Setup test environment"""
        self.rule = WorkflowStateRule()
    
    @pytest.mark.asyncio
    async def test_can_validate(self):
        """Test rule applicability"""
        assert await self.rule.can_validate("task", "update")
        assert await self.rule.can_validate("workflow", "transition")
        assert not await self.rule.can_validate("user", "create")
        assert not await self.rule.can_validate("task", "read")
    
    @pytest.mark.asyncio
    async def test_valid_status_transition(self):
        """Test valid status transition"""
        context = RuleContext()
        data = {
            "current_status": "pending",
            "status": "in_progress"
        }
        
        violations = await self.rule.validate(data, context)
        assert len(violations) == 0
    
    @pytest.mark.asyncio
    async def test_invalid_status_transition(self):
        """Test invalid status transition"""
        context = RuleContext()
        data = {
            "current_status": "completed",
            "status": "in_progress"  # Can't go back from completed
        }
        
        violations = await self.rule.validate(data, context)
        assert len(violations) == 1
        assert "Invalid status transition" in violations[0].message
        assert violations[0].field == "status"
    
    @pytest.mark.asyncio
    async def test_no_current_status(self):
        """Test transition without current status"""
        context = RuleContext()
        data = {"status": "in_progress"}
        
        violations = await self.rule.validate(data, context)
        assert len(violations) == 0  # Should handle gracefully


class TestAuthorizationRule:
    """Test suite for AuthorizationRule"""
    
    def setup_method(self):
        """Setup test environment"""
        self.rule = AuthorizationRule()
    
    @pytest.mark.asyncio
    async def test_can_validate(self):
        """Test rule applicability"""
        assert await self.rule.can_validate("any", "create")
        assert await self.rule.can_validate("any", "update") 
        assert await self.rule.can_validate("any", "delete")
        assert not await self.rule.can_validate("any", "read")
    
    @pytest.mark.asyncio
    async def test_admin_user_authorization(self):
        """Test admin user has all permissions"""
        context = RuleContext(user_id="admin", operation="delete")
        
        violations = await self.rule.validate({}, context)
        assert len(violations) == 0
    
    @pytest.mark.asyncio
    async def test_regular_user_unauthorized_operation(self):
        """Test regular user unauthorized for delete"""
        context = RuleContext(user_id="regular_user", operation="delete")
        
        violations = await self.rule.validate({}, context)
        assert len(violations) == 1
        assert violations[0].severity == RuleSeverity.CRITICAL
        assert "not authorized" in violations[0].message
    
    @pytest.mark.asyncio
    async def test_regular_user_authorized_operation(self):
        """Test regular user authorized for allowed operations"""
        context = RuleContext(
            user_id="regular_user", 
            operation="update", 
            entity_type="task"
        )
        
        violations = await self.rule.validate({}, context)
        assert len(violations) == 0


class TestTaskAssignmentRule:
    """Test suite for TaskAssignmentRule"""
    
    def setup_method(self):
        """Setup test environment"""
        self.rule = TaskAssignmentRule()
    
    @pytest.mark.asyncio
    async def test_can_validate(self):
        """Test rule applicability"""
        assert await self.rule.can_validate("task", "any")
        assert not await self.rule.can_validate("user", "any")
    
    @pytest.mark.asyncio
    async def test_high_priority_task_should_be_assigned(self):
        """Test high priority task should be assigned"""
        context = RuleContext()
        data = {
            "priority": "high",
            "assigned_to": None
        }
        
        violations = await self.rule.validate(data, context)
        assert len(violations) == 1
        assert violations[0].severity == RuleSeverity.WARNING
        assert "High priority tasks should be assigned" in violations[0].message
    
    @pytest.mark.asyncio
    async def test_in_progress_task_must_be_assigned(self):
        """Test in-progress task must be assigned"""
        context = RuleContext()
        data = {
            "status": "in_progress",
            "assigned_to": None
        }
        
        violations = await self.rule.validate(data, context)
        assert len(violations) == 1
        assert violations[0].severity == RuleSeverity.ERROR
        assert "In-progress tasks must be assigned" in violations[0].message
    
    @pytest.mark.asyncio
    async def test_properly_assigned_task(self):
        """Test properly assigned task"""
        context = RuleContext()
        data = {
            "priority": "high",
            "status": "in_progress",
            "assigned_to": "developer1"
        }
        
        violations = await self.rule.validate(data, context)
        assert len(violations) == 0


class TestConfigurationRule:
    """Test suite for ConfigurationRule"""
    
    def setup_method(self):
        """Setup test environment"""
        self.rule = ConfigurationRule()
    
    @pytest.mark.asyncio
    async def test_can_validate(self):
        """Test rule applicability"""
        assert await self.rule.can_validate("configuration", "any")
        assert not await self.rule.can_validate("task", "any")
    
    @pytest.mark.asyncio
    async def test_sensitive_config_weak_value(self):
        """Test sensitive configuration with weak value"""
        context = RuleContext()
        data = {
            "key": "api_secret",
            "value": "weak"  # Too short
        }
        
        violations = await self.rule.validate(data, context)
        assert len(violations) == 1
        assert violations[0].severity == RuleSeverity.CRITICAL
        assert "too short" in violations[0].message
    
    @pytest.mark.asyncio
    async def test_sensitive_config_strong_value(self):
        """Test sensitive configuration with strong value"""
        context = RuleContext()
        data = {
            "key": "api_secret",
            "value": "strong_secret_value_123"
        }
        
        violations = await self.rule.validate(data, context)
        assert len(violations) == 0
    
    @pytest.mark.asyncio
    async def test_url_config_invalid_format(self):
        """Test URL configuration with invalid format"""
        context = RuleContext()
        data = {
            "key": "api_url",
            "value": "not-a-url"
        }
        
        violations = await self.rule.validate(data, context)
        assert len(violations) == 1
        assert violations[0].severity == RuleSeverity.ERROR
        assert "must start with http" in violations[0].message
    
    @pytest.mark.asyncio
    async def test_url_config_valid_format(self):
        """Test URL configuration with valid format"""
        context = RuleContext()
        data = {
            "key": "api_url",
            "value": "https://api.example.com"
        }
        
        violations = await self.rule.validate(data, context)
        assert len(violations) == 0


class TestBusinessRuleIntegration:
    """Integration tests for business rule system"""
    
    def setup_method(self):
        """Setup test environment"""
        self.engine = BusinessRuleEngine()
    
    @pytest.mark.asyncio
    async def test_multiple_rules_validation(self):
        """Test validation with multiple rules"""
        context = RuleContext(
            entity_type="task",
            operation="create",
            user_id="regular_user"
        )
        
        # Data that violates multiple rules
        data = {
            "title": "",  # Required field empty
            "status": "invalid_status",  # Invalid status
            "priority": "high",  # High priority but unassigned
            "assigned_to": None
        }
        
        violations = await self.engine.validate(data, "task", context)
        
        # Should have violations from multiple rules
        assert len(violations) > 1
        
        # Check for specific violations
        violation_messages = [v.message for v in violations]
        assert any("Required field" in msg for msg in violation_messages)
        assert any("Invalid task status" in msg for msg in violation_messages)
        assert any("High priority tasks should be assigned" in msg for msg in violation_messages)
    
    @pytest.mark.asyncio
    async def test_rule_chain_execution(self):
        """Test rule chain execution for specific data type"""
        # Add specific rules to task chain
        self.engine.add_rule_to_chain("task", "required_fields")
        self.engine.add_rule_to_chain("task", "task_assignment")
        
        context = RuleContext(entity_type="task")
        data = {"title": "Test"}  # Missing required fields
        
        violations = await self.engine.validate(data, "task", context)
        
        # Should execute rules in the chain
        assert len(violations) > 0
    
    @pytest.mark.asyncio
    async def test_rule_performance_with_large_dataset(self):
        """Test rule performance with larger dataset"""
        context = RuleContext(entity_type="task")
        
        # Create data that should pass all rules
        data = {
            "title": "Performance Test Task",
            "status": "pending",
            "priority": "normal",
            "assigned_to": "developer1"
        }
        
        # Run validation multiple times to test performance
        import time
        start_time = time.time()
        
        for _ in range(100):
            await self.engine.validate(data, "task", context)
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        # Should complete within reasonable time (adjust threshold as needed)
        assert execution_time < 1.0  # 1 second for 100 validations
    
    @pytest.mark.asyncio
    async def test_custom_rule_registration(self):
        """Test registering and using custom rules"""
        # Create custom rule
        class CustomRule(IBusinessRule):
            @property
            def rule_id(self):
                return "custom_rule"
            
            @property
            def rule_name(self):
                return "Custom Test Rule"
            
            @property
            def category(self):
                return RuleCategory.BUSINESS_LOGIC
            
            @property
            def severity(self):
                return RuleSeverity.WARNING
            
            async def validate(self, data, context):
                if isinstance(data, dict) and data.get("custom_field") == "invalid":
                    return [RuleViolation(
                        rule_id=self.rule_id,
                        rule_name=self.rule_name,
                        severity=self.severity,
                        category=self.category,
                        message="Custom validation failed",
                        field="custom_field",
                        context=context
                    )]
                return []
            
            async def can_validate(self, data_type, operation):
                return data_type == "custom"
        
        # Register custom rule
        custom_rule = CustomRule()
        self.engine.register_rule(custom_rule)
        
        # Test custom rule
        context = RuleContext()
        data = {"custom_field": "invalid"}
        
        violations = await self.engine.validate(data, "custom", context)
        assert len(violations) == 1
        assert violations[0].rule_id == "custom_rule"
        assert "Custom validation failed" in violations[0].message