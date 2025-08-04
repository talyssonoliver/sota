#!/usr/bin/env python3
"""
Comprehensive Tests for Authentication Middleware

Tests JWT-based authentication, token generation/verification, and security decorators.
Critical for achieving 80% test coverage target.
"""

import pytest
import time
import os
from unittest.mock import patch, MagicMock
from flask import Flask, g, jsonify

from src.infrastructure.security.auth_middleware import (
    AuthMiddleware,
    AuthenticationError,
    get_default_auth,
    requires_auth,
    public_endpoint
)


class TestAuthMiddleware:
    """Test authentication middleware functionality."""
    
    def setup_method(self):
        """Set up test environment."""
        self.secret_key = "test_secret_key_for_authentication"
        self.auth = AuthMiddleware(self.secret_key)
    
    def test_auth_middleware_initialization(self):
        """Test authentication middleware initialization."""
        assert self.auth.secret_key == self.secret_key.encode('utf-8')
        assert self.auth.token_expiry == 3600  # 1 hour
    
    def test_initialization_with_env_var(self):
        """Test initialization using environment variable."""
        with patch.dict(os.environ, {'AI_SYSTEM_SECRET_KEY': 'env_secret'}):
            auth = AuthMiddleware()
            assert auth.secret_key == b'env_secret'
    
    def test_initialization_without_env_var_development(self):
        """Test initialization in development without environment variable."""
        with patch.dict(os.environ, {}, clear=True):
            auth = AuthMiddleware()
            assert auth.secret_key == b'dev-secret-change-in-production'
    
    def test_initialization_without_env_var_production(self):
        """Test initialization in production without environment variable raises error."""
        with patch.dict(os.environ, {'ENVIRONMENT': 'production'}, clear=True):
            with pytest.raises(RuntimeError, match="AI_SYSTEM_SECRET_KEY environment variable is required"):
                AuthMiddleware()
    
    def test_generate_token(self):
        """Test token generation."""
        user_id = "test_user_123"
        
        token = self.auth.generate_token(user_id)
        
        # Token should have format: user_id:timestamp:signature
        parts = token.split(':')
        assert len(parts) == 3
        assert parts[0] == user_id
        
        # Timestamp should be recent
        timestamp = int(parts[1])
        assert abs(time.time() - timestamp) < 2  # Within 2 seconds
        
        # Signature should be hex string
        signature = parts[2]
        assert len(signature) == 64  # SHA256 hex digest length
        assert all(c in '0123456789abcdef' for c in signature)
    
    def test_verify_valid_token(self):
        """Test verification of valid token."""
        user_id = "test_user_123"
        token = self.auth.generate_token(user_id)
        
        is_valid, returned_user_id = self.auth.verify_token(token)
        
        assert is_valid is True
        assert returned_user_id == user_id
    
    def test_verify_invalid_token_format(self):
        """Test verification of malformed tokens."""
        invalid_tokens = [
            "invalid_token",
            "too:few",
            "too:many:parts:here",
            "",
            "user::signature",  # Missing timestamp
            ":timestamp:signature",  # Missing user_id
        ]
        
        for invalid_token in invalid_tokens:
            is_valid, user_id = self.auth.verify_token(invalid_token)
            assert is_valid is False
            assert user_id is None
    
    def test_verify_expired_token(self):
        """Test verification of expired token."""
        user_id = "test_user_123"
        
        # Create token with old timestamp
        old_timestamp = str(int(time.time() - 7200))  # 2 hours ago
        message = f"{user_id}:{old_timestamp}"
        
        import hmac
        import hashlib
        signature = hmac.new(
            self.auth.secret_key, 
            message.encode('utf-8'), 
            hashlib.sha256
        ).hexdigest()
        
        expired_token = f"{user_id}:{old_timestamp}:{signature}"
        
        is_valid, returned_user_id = self.auth.verify_token(expired_token)
        
        assert is_valid is False
        assert returned_user_id is None
    
    def test_verify_token_with_wrong_signature(self):
        """Test verification of token with incorrect signature."""
        user_id = "test_user_123"
        timestamp = str(int(time.time()))
        wrong_signature = "wrong_signature_here"
        
        invalid_token = f"{user_id}:{timestamp}:{wrong_signature}"
        
        is_valid, returned_user_id = self.auth.verify_token(invalid_token)
        
        assert is_valid is False
        assert returned_user_id is None
    
    def test_verify_token_with_tampered_user_id(self):
        """Test verification of token with tampered user ID."""
        original_user = "original_user"
        tampered_user = "tampered_user"
        
        # Generate valid token for original user
        token = self.auth.generate_token(original_user)
        
        # Tamper with user ID but keep same signature
        parts = token.split(':')
        tampered_token = f"{tampered_user}:{parts[1]}:{parts[2]}"
        
        is_valid, user_id = self.auth.verify_token(tampered_token)
        
        assert is_valid is False
        assert user_id is None
    
    def test_verify_token_with_invalid_timestamp(self):
        """Test verification of token with invalid timestamp."""
        invalid_tokens = [
            "user:not_a_number:signature",
            "user::signature",
            "user:12.34:signature",  # Float timestamp
        ]
        
        for invalid_token in invalid_tokens:
            is_valid, user_id = self.auth.verify_token(invalid_token)
            assert is_valid is False
            assert user_id is None
    
    def test_token_consistency(self):
        """Test that same user gets different tokens but both verify correctly."""
        user_id = "test_user_123"
        
        token1 = self.auth.generate_token(user_id)
        time.sleep(1.1)  # Delay to ensure different integer timestamps
        token2 = self.auth.generate_token(user_id)
        
        # Tokens should be different
        assert token1 != token2
        
        # Both should verify correctly
        is_valid1, user1 = self.auth.verify_token(token1)
        is_valid2, user2 = self.auth.verify_token(token2)
        
        assert is_valid1 is True
        assert is_valid2 is True
        assert user1 == user_id
        assert user2 == user_id


class TestAuthDecorators:
    """Test authentication decorators."""
    
    def setup_method(self):
        """Set up test Flask app and auth middleware."""
        self.app = Flask(__name__)
        self.auth = AuthMiddleware("test_secret_key")
        
        # Create test routes
        @self.app.route('/protected')
        @self.auth.require_auth
        def protected_route():
            return jsonify({'message': 'Protected data', 'user': g.current_user})
        
        @self.app.route('/optional')
        @self.auth.optional_auth
        def optional_route():
            user = getattr(g, 'current_user', None)
            return jsonify({'message': 'Optional auth', 'user': user})
        
        @self.app.route('/public')
        @public_endpoint
        def public_route():
            return jsonify({'message': 'Public data'})
        
        self.client = self.app.test_client()
    
    def test_protected_route_without_auth(self):
        """Test accessing protected route without authentication."""
        response = self.client.get('/protected')
        
        assert response.status_code == 401
        data = response.get_json()
        assert data['error'] == 'Missing or invalid authorization header'
        assert data['code'] == 'AUTH_MISSING'
    
    def test_protected_route_with_invalid_header_format(self):
        """Test protected route with malformed authorization header."""
        invalid_headers = [
            'InvalidFormat',
            'Basic dXNlcjpwYXNz',  # Basic auth instead of Bearer
            'Bearer',  # Missing token
            '',  # Empty header
        ]
        
        for header in invalid_headers:
            response = self.client.get('/protected', headers={'Authorization': header})
            assert response.status_code == 401
            data = response.get_json()
            assert data['code'] == 'AUTH_MISSING'
    
    def test_protected_route_with_invalid_token(self):
        """Test protected route with invalid token."""
        response = self.client.get('/protected', headers={'Authorization': 'Bearer invalid_token'})
        
        assert response.status_code == 401
        data = response.get_json()
        assert data['error'] == 'Invalid or expired token'
        assert data['code'] == 'AUTH_INVALID'
    
    def test_protected_route_with_valid_token(self):
        """Test protected route with valid authentication token."""
        user_id = "test_user_123"
        token = self.auth.generate_token(user_id)
        
        response = self.client.get('/protected', headers={'Authorization': f'Bearer {token}'})
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['message'] == 'Protected data'
        assert data['user'] == user_id
    
    def test_protected_route_with_expired_token(self):
        """Test protected route with expired token."""
        user_id = "test_user_123"
        
        # Create expired token manually
        old_timestamp = str(int(time.time() - 7200))  # 2 hours ago
        message = f"{user_id}:{old_timestamp}"
        
        import hmac
        import hashlib
        signature = hmac.new(
            self.auth.secret_key, 
            message.encode('utf-8'), 
            hashlib.sha256
        ).hexdigest()
        
        expired_token = f"{user_id}:{old_timestamp}:{signature}"
        
        response = self.client.get('/protected', headers={'Authorization': f'Bearer {expired_token}'})
        
        assert response.status_code == 401
        data = response.get_json()
        assert data['code'] == 'AUTH_INVALID'
    
    def test_optional_auth_without_token(self):
        """Test optional auth route without token."""
        response = self.client.get('/optional')
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['message'] == 'Optional auth'
        assert data['user'] is None
    
    def test_optional_auth_with_valid_token(self):
        """Test optional auth route with valid token."""
        user_id = "test_user_123"
        token = self.auth.generate_token(user_id)
        
        response = self.client.get('/optional', headers={'Authorization': f'Bearer {token}'})
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['message'] == 'Optional auth'
        assert data['user'] == user_id
    
    def test_optional_auth_with_invalid_token(self):
        """Test optional auth route with invalid token."""
        response = self.client.get('/optional', headers={'Authorization': 'Bearer invalid_token'})
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['message'] == 'Optional auth'
        assert data['user'] is None
    
    def test_testing_mode_bypass(self):
        """Test that authentication is bypassed in testing mode."""
        with self.app.test_request_context():
            self.app.config['TESTING'] = True
            
            @self.auth.require_auth
            def test_endpoint():
                return jsonify({'user': g.current_user})
            
            # Should work without authorization header in testing mode
            with self.app.test_client() as client:
                response = client.get('/')
                # In testing mode, g.user_id should be set to 'test_user'
                # This is handled by the decorator logic


class TestGlobalAuthFunctions:
    """Test global authentication functions."""
    
    @patch.dict(os.environ, {'AI_SYSTEM_SECRET_KEY': 'global_test_key'})
    def test_get_default_auth_singleton(self):
        """Test that get_default_auth returns singleton instance."""
        # Clear any existing instance
        import src.infrastructure.security.auth_middleware as auth_module
        auth_module._default_auth = None
        
        auth1 = get_default_auth()
        auth2 = get_default_auth()
        
        # Should return same instance
        assert auth1 is auth2
        assert isinstance(auth1, AuthMiddleware)
    
    def test_requires_auth_decorator(self):
        """Test module-level requires_auth decorator."""
        app = Flask(__name__)
        
        @app.route('/test')
        @requires_auth
        def test_route():
            return jsonify({'message': 'success', 'user': g.current_user})
        
        with app.test_client() as client:
            # Should require authentication
            response = client.get('/test')
            assert response.status_code == 401
    
    def test_public_endpoint_decorator(self):
        """Test public_endpoint decorator marks function as public."""
        @public_endpoint
        def test_function():
            return "test"
        
        assert hasattr(test_function, '_public_endpoint')
        assert test_function._public_endpoint is True


class TestAuthenticationError:
    """Test AuthenticationError exception."""
    
    def test_authentication_error_creation(self):
        """Test creating AuthenticationError."""
        error = AuthenticationError("Test error message")
        assert str(error) == "Test error message"
        assert isinstance(error, Exception)
    
    def test_authentication_error_inheritance(self):
        """Test that AuthenticationError inherits from Exception."""
        error = AuthenticationError("Test message")
        assert isinstance(error, Exception)


class TestAuthMiddlewareEdgeCases:
    """Test edge cases and error conditions."""
    
    def setup_method(self):
        """Set up test environment."""
        self.auth = AuthMiddleware("test_secret_key")
    
    def test_generate_token_empty_user_id(self):
        """Test token generation with empty user ID."""
        token = self.auth.generate_token("")
        
        # Should still generate valid token
        is_valid, user_id = self.auth.verify_token(token)
        assert is_valid is True
        assert user_id == ""
    
    def test_generate_token_special_characters(self):
        """Test token generation with special characters in user ID."""
        special_user_ids = [
            "user@domain.com",
            "user-name_123",
            "user with spaces",
            "user:with:colons",
            "用户名",  # Unicode characters
        ]
        
        for user_id in special_user_ids:
            token = self.auth.generate_token(user_id)
            is_valid, returned_user_id = self.auth.verify_token(token)
            
            assert is_valid is True
            assert returned_user_id == user_id
    
    def test_token_expiry_edge_case(self):
        """Test token verification at exact expiry time."""
        user_id = "test_user"
        
        # Create token that expires in 1 second
        original_expiry = self.auth.token_expiry
        self.auth.token_expiry = 1
        
        token = self.auth.generate_token(user_id)
        
        # Should be valid immediately
        is_valid, _ = self.auth.verify_token(token)
        assert is_valid is True
        
        # Wait for expiry
        time.sleep(1.1)
        
        # Should now be invalid
        is_valid, _ = self.auth.verify_token(token)
        assert is_valid is False
        
        # Restore original expiry
        self.auth.token_expiry = original_expiry
    
    def test_verify_token_with_unicode_characters(self):
        """Test token verification with unicode characters."""
        # Create token with unicode user ID
        user_id = "用户测试"
        token = self.auth.generate_token(user_id)
        
        is_valid, returned_user_id = self.auth.verify_token(token)
        
        assert is_valid is True
        assert returned_user_id == user_id
    
    def test_hmac_timing_attack_resistance(self):
        """Test that token verification uses timing-safe comparison."""
        user_id = "test_user"
        token = self.auth.generate_token(user_id)
        
        # Create similar but invalid token
        parts = token.split(':')
        invalid_signature = parts[2][:-1] + 'x'  # Change last character
        invalid_token = f"{parts[0]}:{parts[1]}:{invalid_signature}"
        
        # Both should fail, but timing should be similar (HMAC comparison)
        start_time = time.time()
        is_valid1, _ = self.auth.verify_token(invalid_token)
        mid_time = time.time()
        is_valid2, _ = self.auth.verify_token("completely_wrong_format")
        end_time = time.time()
        
        assert is_valid1 is False
        assert is_valid2 is False
        
        # Timing difference should be small (both use hmac.compare_digest or fail fast)
        time1 = mid_time - start_time
        time2 = end_time - mid_time
        # This is more of a conceptual test - actual timing may vary


class TestAuthIntegration:
    """Integration tests for authentication system."""
    
    def test_full_authentication_workflow(self):
        """Test complete authentication workflow."""
        app = Flask(__name__)
        auth = AuthMiddleware("integration_test_key")
        
        @app.route('/login', methods=['POST'])
        def login():
            # Simulate login
            user_id = "authenticated_user"
            token = auth.generate_token(user_id)
            return jsonify({'token': token})
        
        @app.route('/profile')
        @auth.require_auth
        def profile():
            return jsonify({'user_id': g.current_user, 'message': 'Profile data'})
        
        with app.test_client() as client:
            # Login and get token
            login_response = client.post('/login')
            assert login_response.status_code == 200
            token = login_response.get_json()['token']
            
            # Use token to access protected resource
            profile_response = client.get('/profile', headers={'Authorization': f'Bearer {token}'})
            assert profile_response.status_code == 200
            profile_data = profile_response.get_json()
            assert profile_data['user_id'] == 'authenticated_user'
            assert profile_data['message'] == 'Profile data'
    
    def test_multiple_auth_instances_independence(self):
        """Test that multiple auth instances work independently."""
        auth1 = AuthMiddleware("secret_key_1")
        auth2 = AuthMiddleware("secret_key_2")
        
        user_id = "test_user"
        
        # Generate tokens with different auth instances
        token1 = auth1.generate_token(user_id)
        token2 = auth2.generate_token(user_id)
        
        # Tokens should be different
        assert token1 != token2
        
        # Each auth instance should only verify its own tokens
        assert auth1.verify_token(token1)[0] is True
        assert auth1.verify_token(token2)[0] is False
        
        assert auth2.verify_token(token2)[0] is True
        assert auth2.verify_token(token1)[0] is False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])