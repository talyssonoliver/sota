#!/usr/bin/env python3

from src.infrastructure.utils.common_imports import hashlib, time
"""
Authentication Middleware for HITL API Security
"""

import functools
# import hashlib  # Consolidated to common_imports
import hmac
# import time  # Consolidated to common_imports
from typing import Optional, Tuple

from flask import g, jsonify, request
from src.infrastructure.utils.common_utils import EnvironmentConfig, is_production_mode


class AuthenticationError(Exception):
    """Authentication-related errors."""

    pass


# Default middleware instance
_default_auth = None


def get_default_auth():
    """Get or create default auth middleware instance."""
    global _default_auth
    if _default_auth is None:
        secret_key = EnvironmentConfig.get_secret_key()
        _default_auth = AuthMiddleware(secret_key)
    return _default_auth


def requires_auth(f):
    """Module-level decorator for requiring authentication."""
    return get_default_auth().require_auth(f)


def public_endpoint(f):
    """Decorator to mark an endpoint as public (no auth required)."""
    f._public_endpoint = True
    return f


class AuthMiddleware:
    """Authentication middleware for API endpoints."""

    def __init__(self, secret_key: Optional[str] = None):
        """Initialize auth middleware with secret key."""
        if secret_key is None:
            secret_key = EnvironmentConfig.get_secret_key()
        
        self.secret_key = secret_key.encode("utf-8")
        self.token_expiry = 3600  # 1 hour

    def generate_token(self, user_id: str) -> str:
        """Generate a secure authentication token."""
        timestamp = str(int(time.time()))
        message = f"{user_id}:{timestamp}"
        signature = hmac.new(
            self.secret_key, message.encode("utf-8"), hashlib.sha256
        ).hexdigest()
        return f"{user_id}:{timestamp}:{signature}"

    def verify_token(self, token: str) -> Tuple[bool, Optional[str]]:
        """Verify authentication token and return (is_valid, user_id)."""
        try:
            parts = token.split(":")
            if len(parts) < 3:
                return False, None

            # Last part is signature, second-to-last is timestamp
            signature = parts[-1]
            timestamp = parts[-2]
            # Everything before timestamp is the user_id (may contain colons)
            user_id = ":".join(parts[:-2])

            # Check token age
            token_time = int(timestamp)
            if time.time() - token_time > self.token_expiry:
                return False, None

            # Verify signature
            message = f"{user_id}:{timestamp}"
            expected_signature = hmac.new(
                self.secret_key, message.encode("utf-8"), hashlib.sha256
            ).hexdigest()

            if hmac.compare_digest(signature, expected_signature):
                return True, user_id
            else:
                return False, None

        except (ValueError, IndexError):
            return False, None

    def require_auth(self, f):
        """Decorator to require authentication for endpoints."""

        @functools.wraps(f)
        def decorated_function(*args, **kwargs):
            # Bypass authentication in testing mode
            from flask import current_app
            if current_app and current_app.config.get("TESTING", False):
                g.user_id = "test_user"
                return f(*args, **kwargs)
            
            # Check for Authorization header
            auth_header = request.headers.get("Authorization", "")

            if not auth_header.startswith("Bearer "):
                return (
                    jsonify(
                        {
                            "error": "Missing or invalid authorization header",
                            "code": "AUTH_MISSING",
                        }
                    ),
                    401,
                )

            token = auth_header[7:]  # Remove 'Bearer ' prefix
            is_valid, user_id = self.verify_token(token)

            if not is_valid:
                return (
                    jsonify(
                        {"error": "Invalid or expired token", "code": "AUTH_INVALID"}
                    ),
                    401,
                )

            # Store user info in Flask g object for use in endpoint
            g.current_user = user_id

            return f(*args, **kwargs)

        return decorated_function

    def optional_auth(self, f):
        """Decorator for optional authentication (sets g.current_user if authenticated)."""

        @functools.wraps(f)
        def decorated_function(*args, **kwargs):
            auth_header = request.headers.get("Authorization", "")

            if auth_header.startswith("Bearer "):
                token = auth_header[7:]
                is_valid, user_id = self.verify_token(token)
                if is_valid:
                    g.current_user = user_id
                else:
                    g.current_user = None
            else:
                g.current_user = None

            return f(*args, **kwargs)

        return decorated_function


# Global auth instance for easy import
auth = get_default_auth()
