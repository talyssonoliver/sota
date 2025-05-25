import time
from datetime import datetime, timedelta
import logging
from typing import Dict

class RateLimiter:
    """
    A rate limiter that restricts the number of operations within a time window.
    """
    def __init__(self, max_calls=10, time_window=60):
        """
        Initialize the rate limiter.
        
        Args:
            max_calls (int): Maximum number of calls allowed within the time window
            time_window (int): Time window in seconds
        """
        self.max_calls = max_calls
        self.time_window = time_window  # in seconds
        self.calls = []
        self.logger = logging.getLogger(__name__)
        
    def check(self):
        """
        Check if a new call is allowed within the current rate limits.
        
        Returns:
            bool: True if call is allowed, False otherwise
        """
        now = datetime.now()
        # Remove expired timestamps
        self.calls = [ts for ts in self.calls if ts > now - timedelta(seconds=self.time_window)]
        
        # Check if we're within limits
        if len(self.calls) < self.max_calls:
            self.calls.append(now)
            return True
            
        self.logger.warning(f"Rate limit exceeded: {len(self.calls)} calls in {self.time_window}s")
        return False
    
    def wait_if_needed(self):
        """
        Wait until a new call is allowed if rate limit is currently exceeded.
        
        Returns:
            bool: True if wait was required, False otherwise
        """
        if self.check():
            return False
            
        # Calculate how long to wait
        oldest_call = min(self.calls)
        wait_time = (oldest_call + timedelta(seconds=self.time_window) - datetime.now()).total_seconds()
        
        if wait_time > 0:
            self.logger.info(f"Rate limited, waiting {wait_time:.2f} seconds")
            time.sleep(wait_time + 0.1)  # Add a small buffer
            
        return True

class RetrievalQARateLimiter(RateLimiter):
    """
    A rate limiter specifically for the retrieval_qa method.
    """
    def __init__(self, max_calls=5, time_window=60):
        """
        Initialize the retrieval QA rate limiter with stricter limits.
        
        Args:
            max_calls (int): Maximum number of calls allowed within the time window
            time_window (int): Time window in seconds
        """
        super().__init__(max_calls, time_window)

class UserRateLimiter:
    """
    A rate limiter that restricts the number of requests a user can make within a minute.
    """
    def __init__(self, requests_per_minute: int):
        """
        Initialize the user rate limiter.
        
        Args:
            requests_per_minute (int): Maximum number of requests allowed per minute per user
        """
        self.requests_per_minute = requests_per_minute
        self.user_requests: Dict[str, list[float]] = {}

    def is_allowed(self, user_id: str) -> bool:
        """
        Checks if a user is allowed to make a request.
        
        Args:
            user_id (str): The ID of the user
        
        Returns:
            bool: True if the user is allowed to make the request, False otherwise
        """
        current_time = time.time()
        if user_id not in self.user_requests:
            self.user_requests[user_id] = []

        # Remove timestamps older than 60 seconds
        self.user_requests[user_id] = [
            ts for ts in self.user_requests[user_id] if current_time - ts < 60
        ]

        if len(self.user_requests[user_id]) < self.requests_per_minute:
            self.user_requests[user_id].append(current_time)
            return True
        return False

    def reset_user(self, user_id: str):
        """Resets the request count for a specific user."""
        if user_id in self.user_requests:
            self.user_requests[user_id] = []

    def reset_all(self):
        """Resets the request count for all users."""
        self.user_requests = {}
