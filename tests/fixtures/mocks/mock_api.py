"""
Mock API Components for Tests
"""

from typing import List

try:
    pass
except ImportError:
    pass
try:
    pass
except ImportError:
    pass


class MockFlaskApp:
    """Mock Flask app for testing."""

    def __init__(self):
        self.routes = {}
        self.responses = {}

    def route(self, path: str, methods: List[str] = None):
        """Mock route decorator."""

        def decorator(func):
            self.routes[path] = func
            return func

        return decorator

    def test_client(self):
        """Return mock test client."""
        return MockTestClient(self)


class MockTestClient:
    """Mock test client."""

    def __init__(self, app: MockFlaskApp):
        self.app = app

    def get(self, path: str, **kwargs):
        """Mock GET request."""
        return MockResponse(200, {"path": path, "method": "GET"})

    def post(self, path: str, **kwargs):
        """Mock POST request."""
        return MockResponse(200, {"path": path, "method": "POST"})


class MockResponse:
    """Mock HTTP response."""

    def __init__(self, status_code: int, data: dict):
        self.status_code = status_code
        self.data = data

    def get_json(self):
        return self.data
