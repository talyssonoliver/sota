"""
API Input Validation and Sanitization for AI Agent System

Provides Flask/FastAPI-specific validation middleware and decorators for
secure handling of API requests, JSON payloads, and query parameters.
"""

import json
import logging
from functools import wraps
from typing import Any, Callable, Dict, Optional

try:
    import werkzeug.exceptions
    from flask import jsonify, request

    FLASK_AVAILABLE = True
except ImportError:
    FLASK_AVAILABLE = False

    # Mock Flask objects for when Flask is not available
    class MockRequest:
        def get_json(self):
            return {}

        args = {}
        headers = {}

    request = MockRequest()

    def jsonify(data):
        return json.dumps(data)

    class werkzeug:
        class exceptions:
            class BadRequest(Exception):
                pass


from src.infrastructure.utils.input_validation import ValidationError, get_validator

logger = logging.getLogger(__name__)


class APIValidationError(Exception):
    """API-specific validation error with HTTP status codes."""

    def __init__(
        self,
        message: str,
        status_code: int = 400,
        errors: Optional[Dict] = None,
    ):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.errors = errors or {}


class APIValidator:
    """API request validation and sanitization."""

    def __init__(self):
        """Initialize API validator."""
        self.validator = get_validator()
        self.max_json_size = 10 * 1024 * 1024  # 10MB
        self.max_query_params = 50
        self.max_headers = 100

    def validate_json_payload(
        self, payload: Dict[str, Any], schema: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Validate JSON payload with optional schema validation.

        Args:
            payload: JSON payload to validate
            schema: Optional schema dictionary for validation

        Returns:
            Validated payload

        Raises:
            APIValidationError: If payload is invalid
        """
        try:
            # Size check
            payload_size = len(json.dumps(payload).encode("utf-8"))
            if payload_size > self.max_json_size:
                raise APIValidationError(
                    f"Payload too large: {payload_size} bytes (max {self.max_json_size})",
                    status_code=413,
                )

            # Validate using base validator
            validated_payload = self.validator.validate_json_data(payload)

            # Schema validation if provided
            if schema:
                validated_payload = self._validate_against_schema(
                    validated_payload, schema
                )

            return validated_payload

        except ValidationError as e:
            raise APIValidationError(f"Invalid JSON payload: {e}", status_code=400)
        except Exception as e:
            raise APIValidationError(f"Payload validation error: {e}", status_code=500)

    def validate_query_params(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate query parameters.

        Args:
            params: Query parameters to validate

        Returns:
            Validated parameters

        Raises:
            APIValidationError: If parameters are invalid
        """
        if len(params) > self.max_query_params:
            raise APIValidationError(
                f"Too many query parameters: {len(params)} (max {self.max_query_params})",
                status_code=400,
            )

        validated_params = {}
        errors = {}

        for key, value in params.items():
            try:
                # Validate parameter name
                clean_key = self.validator.validate_string_content(key, max_length=100)

                # Validate parameter value
                if isinstance(value, str):
                    clean_value = self.validator.validate_string_content(
                        value, max_length=1000
                    )
                elif isinstance(value, (int, float)):
                    clean_value = value
                elif isinstance(value, bool):
                    clean_value = value
                else:
                    # Convert to string and validate
                    clean_value = self.validator.validate_string_content(
                        str(value), max_length=1000
                    )

                validated_params[clean_key] = clean_value

            except ValidationError as e:
                errors[key] = str(e)

        if errors:
            raise APIValidationError(
                "Invalid query parameters", status_code=400, errors=errors
            )

        return validated_params

    def validate_path_params(self, params: Dict[str, str]) -> Dict[str, str]:
        """
        Validate URL path parameters.

        Args:
            params: Path parameters to validate

        Returns:
            Validated parameters

        Raises:
            APIValidationError: If parameters are invalid
        """
        validated_params = {}
        errors = {}

        for key, value in params.items():
            try:
                if "task_id" in key.lower():
                    validated_params[key] = self.validator.validate_task_id(value)
                elif "checkpoint_id" in key.lower():
                    validated_params[key] = self.validator.validate_checkpoint_id(value)
                elif "id" in key.lower():
                    # Generic ID validation
                    validated_params[key] = self.validator.validate_string_content(
                        value, max_length=100
                    )
                else:
                    validated_params[key] = self.validator.validate_string_content(
                        value, max_length=500
                    )

            except ValidationError as e:
                errors[key] = str(e)

        if errors:
            raise APIValidationError(
                "Invalid path parameters", status_code=400, errors=errors
            )

        return validated_params

    def validate_headers(self, headers: Dict[str, str]) -> Dict[str, str]:
        """
        Validate HTTP headers for security.

        Args:
            headers: Headers to validate

        Returns:
            Validated headers

        Raises:
            APIValidationError: If headers are invalid
        """
        if len(headers) > self.max_headers:
            raise APIValidationError(
                f"Too many headers: {len(headers)} (max {self.max_headers})",
                status_code=400,
            )

        validated_headers = {}
        dangerous_headers = {"x-forwarded-for", "x-real-ip", "host"}

        for key, value in headers.items():
            try:
                clean_key = key.lower().strip()
                clean_value = self.validator.validate_string_content(
                    value, max_length=2000
                )

                # Special validation for sensitive headers
                if clean_key in dangerous_headers:
                    # Log but don't reject - might be legitimate
                    logger.warning(f"Potentially spoofed header: {clean_key}")

                validated_headers[clean_key] = clean_value

            except ValidationError:
                # Skip invalid headers rather than rejecting request
                logger.warning(f"Skipping invalid header: {key}")
                continue

        return validated_headers

    def _validate_against_schema(
        self, payload: Dict[str, Any], schema: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Validate payload against a simple schema.

        Args:
            payload: Payload to validate
            schema: Schema definition

        Returns:
            Validated payload

        Raises:
            APIValidationError: If payload doesn't match schema
        """
        errors = {}
        validated = {}

        # Check required fields
        required_fields = schema.get("required", [])
        for field in required_fields:
            if field not in payload:
                errors[field] = "Required field missing"

        # Validate field types and constraints
        field_specs = schema.get("properties", {})
        for field, value in payload.items():
            if field in field_specs:
                spec = field_specs[field]
                try:
                    validated[field] = self._validate_field(field, value, spec)
                except ValidationError as e:
                    errors[field] = str(e)
            else:
                # Unknown field - log warning but allow
                logger.warning(f"Unknown field in payload: {field}")
                validated[field] = value

        if errors:
            raise APIValidationError(
                "Schema validation failed", status_code=422, errors=errors
            )

        return validated

    def _validate_field(self, field_name: str, value: Any, spec: Dict[str, Any]) -> Any:
        """
        Validate individual field against specification.

        Args:
            field_name: Name of the field
            value: Field value
            spec: Field specification

        Returns:
            Validated value

        Raises:
            ValidationError: If field is invalid
        """
        field_type = spec.get("type", "string")

        if field_type == "string":
            max_length = spec.get("maxLength", 1000)
            return self.validator.validate_string_content(
                str(value), max_length=max_length
            )

        elif field_type == "integer":
            min_val = spec.get("minimum", -2147483648)
            max_val = spec.get("maximum", 2147483647)
            return self.validator.validate_integer_range(
                value, min_val=min_val, max_val=max_val
            )

        elif field_type == "boolean":
            if isinstance(value, bool):
                return value
            elif isinstance(value, str):
                if value.lower() in ("true", "1", "yes"):
                    return True
                elif value.lower() in ("false", "0", "no"):
                    return False
            raise ValidationError(f"Invalid boolean value: {value}")

        elif field_type == "array":
            if not isinstance(value, list):
                raise ValidationError(f"Expected array, got {type(value)}")
            max_items = spec.get("maxItems", 100)
            if len(value) > max_items:
                raise ValidationError(f"Array too long: {len(value)} (max {max_items})")
            return value

        elif field_type == "object":
            if not isinstance(value, dict):
                raise ValidationError(f"Expected object, got {type(value)}")
            return value

        else:
            logger.warning(f"Unknown field type: {field_type}")
            return value


# Global API validator instance
_api_validator_instance: Optional[APIValidator] = None


def get_api_validator() -> APIValidator:
    """Get global API validator instance."""
    global _api_validator_instance
    if _api_validator_instance is None:
        _api_validator_instance = APIValidator()
    return _api_validator_instance


# Flask decorators
def validate_json(schema: Optional[Dict[str, Any]] = None):
    """
    Decorator to validate JSON payload in Flask routes.

    Args:
        schema: Optional schema for validation

    Example:
        @app.route('/api/tasks', methods=['POST'])
        @validate_json({
            'required': ['task_id', 'description'],
            'properties': {
                'task_id': {'type': 'string', 'maxLength': 20},
                'description': {'type': 'string', 'maxLength': 1000}
            }
        })
        def create_task():
            data = request.get_json()
            # data is now validated
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                validator = get_api_validator()

                # Check if request has JSON
                if not request.is_json:
                    return (
                        jsonify({"error": "Content-Type must be application/json"}),
                        400,
                    )

                # Get and validate JSON
                try:
                    payload = request.get_json()
                except Exception as e:
                    return jsonify({"error": f"Invalid JSON: {e}"}), 400

                if payload is None:
                    return jsonify({"error": "JSON payload required"}), 400

                # Validate payload
                validated_payload = validator.validate_json_payload(payload, schema)

                # Replace request JSON with validated data
                request._cached_json = (validated_payload, None)

                return func(*args, **kwargs)

            except APIValidationError as e:
                return (
                    jsonify({"error": e.message, "errors": e.errors}),
                    e.status_code,
                )
            except Exception as e:
                logger.error(f"Validation error: {e}")
                return jsonify({"error": "Internal validation error"}), 500

        return wrapper

    return decorator


def validate_query_params():
    """
    Decorator to validate query parameters in Flask routes.

    Example:
        @app.route('/api/tasks')
        @validate_query_params()
        def list_tasks():
            # Query params are validated and accessible via request.args
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                validator = get_api_validator()

                # Validate query parameters
                params = dict(request.args)
                validated_params = validator.validate_query_params(params)
                
                # Log successful validation
                print(f"✅ Query parameters validated: {len(validated_params)} params")

                # Update request args with validated params
                # Note: This is for validation only, original request.args remains unchanged

                return func(*args, **kwargs)

            except APIValidationError as e:
                return (
                    jsonify({"error": e.message, "errors": e.errors}),
                    e.status_code,
                )
            except Exception as e:
                logger.error(f"Query parameter validation error: {e}")
                return jsonify({"error": "Invalid query parameters"}), 400

        return wrapper

    return decorator


def validate_path_params(**param_validators):
    """
    Decorator to validate path parameters in Flask routes.

    Args:
        **param_validators: Validator functions for specific parameters

    Example:
        @app.route('/api/tasks/<task_id>')
        @validate_path_params(task_id=validate_task_id)
        def get_task(task_id):
            # task_id is validated
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                validator = get_api_validator()

                # Apply custom validators if provided
                for param_name, param_validator in param_validators.items():
                    if param_name in kwargs:
                        try:
                            kwargs[param_name] = param_validator(kwargs[param_name])
                        except ValidationError as e:
                            return (
                                jsonify({"error": f"Invalid {param_name}: {e}"}),
                                400,
                            )

                # General path parameter validation
                if kwargs:
                    validated_params = validator.validate_path_params(kwargs)
                    kwargs.update(validated_params)

                return func(*args, **kwargs)

            except APIValidationError as e:
                return (
                    jsonify({"error": e.message, "errors": e.errors}),
                    e.status_code,
                )
            except Exception as e:
                logger.error(f"Path parameter validation error: {e}")
                return jsonify({"error": "Invalid path parameters"}), 400

        return wrapper

    return decorator


def secure_headers():
    """
    Decorator to add security headers to Flask responses.

    Example:
        @app.route('/api/data')
        @secure_headers()
        def get_data():
            return jsonify({'data': 'value'})
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            response = func(*args, **kwargs)

            # Add security headers
            if hasattr(response, "headers"):
                response.headers["X-Content-Type-Options"] = "nosniff"
                response.headers["X-Frame-Options"] = "DENY"
                response.headers["X-XSS-Protection"] = "1; mode=block"
                response.headers["Strict-Transport-Security"] = (
                    "max-age=31536000; includeSubDomains"
                )
                response.headers["Content-Security-Policy"] = "default-src 'self'"
                response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

            return response

        return wrapper

    return decorator


# Common validation schemas
HITL_CHECKPOINT_SCHEMA = {
    "required": ["checkpoint_id", "task_id", "checkpoint_type"],
    "properties": {
        "checkpoint_id": {"type": "string", "maxLength": 100},
        "task_id": {"type": "string", "maxLength": 20},
        "checkpoint_type": {"type": "string", "maxLength": 50},
        "description": {"type": "string", "maxLength": 2000},
        "risk_level": {"type": "string", "maxLength": 20},
        "reviewers": {"type": "array", "maxItems": 10},
        "metadata": {"type": "object"},
    },
}

TASK_EXECUTION_SCHEMA = {
    "required": ["task_id", "description"],
    "properties": {
        "task_id": {"type": "string", "maxLength": 20},
        "description": {"type": "string", "maxLength": 5000},
        "agent_type": {"type": "string", "maxLength": 50},
        "context": {"type": "string", "maxLength": 10000},
        "priority": {"type": "string", "maxLength": 20},
        "metadata": {"type": "object"},
    },
}

QA_VALIDATION_SCHEMA = {
    "required": ["task_id", "validation_type"],
    "properties": {
        "task_id": {"type": "string", "maxLength": 20},
        "validation_type": {"type": "string", "maxLength": 50},
        "criteria": {"type": "array", "maxItems": 20},
        "threshold": {"type": "integer", "minimum": 0, "maximum": 100},
        "metadata": {"type": "object"},
    },
}
