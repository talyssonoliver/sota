"""
Mock RateLimiter for memory_engine tests
"""


class MockRateLimiter:
    """
    Simple mock rate limiter for testing
    """

    def __init__(self, max_ops=1, per_seconds=1):
        self.max_ops = max_ops
        self.per_seconds = per_seconds
        self.requests_per_minute = 60
        self.allow_request = True  # Default to allow, can be changed in tests

    def check(self):
        """Always return True during tests"""
        return True

    def is_allowed(self, user_id: str) -> bool:
        # Simple mock: always returns what allow_request is set to
        # In a real test, you might want more sophisticated logic here
        return self.allow_request

    def set_allow_request(self, allow: bool):
        self.allow_request = allow
