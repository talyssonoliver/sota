
from src.infrastructure.utils.common_imports import Enum, dataclass, datetime
"""
External Service Interfaces

Abstract interfaces for external API clients and webhook management,
breaking dependency on specific external service implementations.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Union, Callable
# from dataclasses import dataclass  # Consolidated to common_imports
# from enum import Enum  # Consolidated to common_imports
# from datetime import datetime  # Consolidated to common_imports


class HttpMethod(Enum):
    """HTTP methods"""
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"
    PATCH = "PATCH"
    HEAD = "HEAD"
    OPTIONS = "OPTIONS"


class WebhookStatus(Enum):
    """Webhook delivery status"""
    PENDING = "pending"
    SENT = "sent"
    DELIVERED = "delivered"
    FAILED = "failed"
    RETRY = "retry"
    TIMEOUT = "timeout"


class APIResponseFormat(Enum):
    """API response formats"""
    JSON = "json"
    XML = "xml"
    TEXT = "text"
    BINARY = "binary"


@dataclass
class APIRequest:
    """API request specification"""
    url: str
    method: HttpMethod = HttpMethod.GET
    headers: Optional[Dict[str, str]] = None
    params: Optional[Dict[str, Any]] = None
    data: Optional[Any] = None
    timeout: Optional[int] = None
    retries: int = 0
    auth: Optional[Dict[str, str]] = None


@dataclass
class APIResponse:
    """API response data"""
    status_code: int
    data: Any
    headers: Dict[str, str]
    response_time_ms: float
    request_id: Optional[str] = None
    error: Optional[str] = None


@dataclass
class WebhookEvent:
    """Webhook event data"""
    id: str
    event_type: str
    payload: Dict[str, Any]
    source: str
    timestamp: datetime
    headers: Optional[Dict[str, str]] = None
    signature: Optional[str] = None


@dataclass
class WebhookSubscription:
    """Webhook subscription configuration"""
    id: str
    url: str
    event_types: List[str]
    secret: Optional[str] = None
    active: bool = True
    retry_config: Optional[Dict[str, Any]] = None
    filters: Optional[Dict[str, Any]] = None
    headers: Optional[Dict[str, str]] = None


@dataclass
class WebhookDelivery:
    """Webhook delivery attempt"""
    id: str
    subscription_id: str
    event_id: str
    status: WebhookStatus
    attempt_number: int
    sent_at: datetime
    response_code: Optional[int] = None
    response_body: Optional[str] = None
    error_message: Optional[str] = None
    next_retry_at: Optional[datetime] = None


class IExternalAPIClient(ABC):
    """Interface for external API clients"""
    
    @abstractmethod
    async def make_request(self, request: APIRequest) -> APIResponse:
        """Make API request"""
        pass
    
    @abstractmethod
    async def get(self, url: str, params: Optional[Dict[str, Any]] = None,
                 headers: Optional[Dict[str, str]] = None, timeout: Optional[int] = None) -> APIResponse:
        """Make GET request"""
        pass
    
    @abstractmethod
    async def post(self, url: str, data: Optional[Any] = None,
                  headers: Optional[Dict[str, str]] = None, timeout: Optional[int] = None) -> APIResponse:
        """Make POST request"""
        pass
    
    @abstractmethod
    async def put(self, url: str, data: Optional[Any] = None,
                 headers: Optional[Dict[str, str]] = None, timeout: Optional[int] = None) -> APIResponse:
        """Make PUT request"""
        pass
    
    @abstractmethod
    async def delete(self, url: str, headers: Optional[Dict[str, str]] = None,
                    timeout: Optional[int] = None) -> APIResponse:
        """Make DELETE request"""
        pass
    
    @abstractmethod
    async def patch(self, url: str, data: Optional[Any] = None,
                   headers: Optional[Dict[str, str]] = None, timeout: Optional[int] = None) -> APIResponse:
        """Make PATCH request"""
        pass
    
    @abstractmethod
    async def batch_requests(self, requests: List[APIRequest]) -> List[APIResponse]:
        """Make multiple requests in batch"""
        pass
    
    @abstractmethod
    async def stream_request(self, request: APIRequest) -> AsyncGenerator[bytes, None]:
        """Make streaming request"""
        pass
    
    @abstractmethod
    async def download_file(self, url: str, destination: str,
                           headers: Optional[Dict[str, str]] = None) -> bool:
        """Download file from URL"""
        pass
    
    @abstractmethod
    async def upload_file(self, url: str, file_path: str,
                         headers: Optional[Dict[str, str]] = None) -> APIResponse:
        """Upload file to URL"""
        pass
    
    @abstractmethod
    async def set_authentication(self, auth_config: Dict[str, Any]) -> bool:
        """Set authentication configuration"""
        pass
    
    @abstractmethod
    async def get_request_history(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get request history"""
        pass
    
    @abstractmethod
    async def get_client_stats(self) -> Dict[str, Any]:
        """Get client statistics"""
        pass


class IWebhookManager(ABC):
    """Interface for webhook management"""
    
    @abstractmethod
    async def create_subscription(self, subscription: WebhookSubscription) -> str:
        """Create webhook subscription"""
        pass
    
    @abstractmethod
    async def update_subscription(self, subscription_id: str, updates: Dict[str, Any]) -> bool:
        """Update webhook subscription"""
        pass
    
    @abstractmethod
    async def delete_subscription(self, subscription_id: str) -> bool:
        """Delete webhook subscription"""
        pass
    
    @abstractmethod
    async def get_subscription(self, subscription_id: str) -> Optional[WebhookSubscription]:
        """Get webhook subscription"""
        pass
    
    @abstractmethod
    async def list_subscriptions(self, active_only: bool = True) -> List[WebhookSubscription]:
        """List webhook subscriptions"""
        pass
    
    @abstractmethod
    async def deliver_webhook(self, event: WebhookEvent, subscription_id: str) -> WebhookDelivery:
        """Deliver webhook event"""
        pass
    
    @abstractmethod
    async def retry_delivery(self, delivery_id: str) -> WebhookDelivery:
        """Retry webhook delivery"""
        pass
    
    @abstractmethod
    async def get_delivery_status(self, delivery_id: str) -> Optional[WebhookDelivery]:
        """Get webhook delivery status"""
        pass
    
    @abstractmethod
    async def get_delivery_history(self, subscription_id: str, limit: int = 100) -> List[WebhookDelivery]:
        """Get webhook delivery history"""
        pass
    
    @abstractmethod
    async def validate_webhook_signature(self, payload: str, signature: str, secret: str) -> bool:
        """Validate webhook signature"""
        pass
    
    @abstractmethod
    async def test_webhook_endpoint(self, url: str, test_payload: Dict[str, Any]) -> Dict[str, Any]:
        """Test webhook endpoint"""
        pass
    
    @abstractmethod
    async def pause_subscription(self, subscription_id: str) -> bool:
        """Pause webhook subscription"""
        pass
    
    @abstractmethod
    async def resume_subscription(self, subscription_id: str) -> bool:
        """Resume webhook subscription"""
        pass
    
    @abstractmethod
    async def get_webhook_stats(self, subscription_id: Optional[str] = None) -> Dict[str, Any]:
        """Get webhook statistics"""
        pass


class IAPIRateLimiter(ABC):
    """Interface for API rate limiting"""
    
    @abstractmethod
    async def can_make_request(self, api_key: str, endpoint: str) -> bool:
        """Check if request can be made within rate limits"""
        pass
    
    @abstractmethod
    async def record_request(self, api_key: str, endpoint: str) -> None:
        """Record API request for rate limiting"""
        pass
    
    @abstractmethod
    async def get_rate_limit_status(self, api_key: str, endpoint: str) -> Dict[str, Any]:
        """Get rate limit status"""
        pass
    
    @abstractmethod
    async def reset_rate_limit(self, api_key: str, endpoint: str) -> bool:
        """Reset rate limit for API key/endpoint"""
        pass
    
    @abstractmethod
    async def configure_rate_limit(self, endpoint: str, requests_per_minute: int,
                                  requests_per_hour: int, requests_per_day: int) -> bool:
        """Configure rate limits for endpoint"""
        pass
    
    @abstractmethod
    async def get_rate_limit_violations(self, api_key: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get rate limit violations"""
        pass


class IAPICache(ABC):
    """Interface for API response caching"""
    
    @abstractmethod
    async def get_cached_response(self, cache_key: str) -> Optional[APIResponse]:
        """Get cached API response"""
        pass
    
    @abstractmethod
    async def cache_response(self, cache_key: str, response: APIResponse, ttl: int) -> bool:
        """Cache API response"""
        pass
    
    @abstractmethod
    async def invalidate_cache(self, pattern: str) -> int:
        """Invalidate cached responses matching pattern"""
        pass
    
    @abstractmethod
    async def generate_cache_key(self, request: APIRequest) -> str:
        """Generate cache key for request"""
        pass
    
    @abstractmethod
    async def should_cache_response(self, request: APIRequest, response: APIResponse) -> bool:
        """Determine if response should be cached"""
        pass
    
    @abstractmethod
    async def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        pass


class IAPIAuthentication(ABC):
    """Interface for API authentication"""
    
    @abstractmethod
    async def authenticate_request(self, request: APIRequest) -> APIRequest:
        """Add authentication to request"""
        pass
    
    @abstractmethod
    async def refresh_token(self, auth_config: Dict[str, Any]) -> Dict[str, Any]:
        """Refresh authentication token"""
        pass
    
    @abstractmethod
    async def validate_credentials(self, auth_config: Dict[str, Any]) -> bool:
        """Validate authentication credentials"""
        pass
    
    @abstractmethod
    async def get_auth_headers(self, auth_config: Dict[str, Any]) -> Dict[str, str]:
        """Get authentication headers"""
        pass
    
    @abstractmethod
    async def handle_auth_error(self, response: APIResponse, auth_config: Dict[str, Any]) -> bool:
        """Handle authentication error"""
        pass


class IWebhookSecurity(ABC):
    """Interface for webhook security"""
    
    @abstractmethod
    async def generate_signature(self, payload: str, secret: str) -> str:
        """Generate webhook signature"""
        pass
    
    @abstractmethod
    async def verify_signature(self, payload: str, signature: str, secret: str) -> bool:
        """Verify webhook signature"""
        pass
    
    @abstractmethod
    async def validate_webhook_origin(self, request_headers: Dict[str, str],
                                     allowed_origins: List[str]) -> bool:
        """Validate webhook origin"""
        pass
    
    @abstractmethod
    async def encrypt_webhook_payload(self, payload: Dict[str, Any], key: str) -> str:
        """Encrypt webhook payload"""
        pass
    
    @abstractmethod
    async def decrypt_webhook_payload(self, encrypted_payload: str, key: str) -> Dict[str, Any]:
        """Decrypt webhook payload"""
        pass
    
    @abstractmethod
    async def generate_webhook_secret(self) -> str:
        """Generate secure webhook secret"""
        pass


class IExternalServiceRegistry(ABC):
    """Interface for external service registry"""
    
    @abstractmethod
    async def register_service(self, service_name: str, config: Dict[str, Any]) -> bool:
        """Register external service"""
        pass
    
    @abstractmethod
    async def unregister_service(self, service_name: str) -> bool:
        """Unregister external service"""
        pass
    
    @abstractmethod
    async def get_service_config(self, service_name: str) -> Optional[Dict[str, Any]]:
        """Get service configuration"""
        pass
    
    @abstractmethod
    async def update_service_config(self, service_name: str, updates: Dict[str, Any]) -> bool:
        """Update service configuration"""
        pass
    
    @abstractmethod
    async def list_services(self) -> List[str]:
        """List registered services"""
        pass
    
    @abstractmethod
    async def check_service_health(self, service_name: str) -> Dict[str, Any]:
        """Check service health"""
        pass
    
    @abstractmethod
    async def get_service_metrics(self, service_name: str) -> Dict[str, Any]:
        """Get service metrics"""
        pass
    
    @abstractmethod
    async def enable_service(self, service_name: str) -> bool:
        """Enable service"""
        pass
    
    @abstractmethod
    async def disable_service(self, service_name: str) -> bool:
        """Disable service"""
        pass


class ICircuitBreaker(ABC):
    """Interface for circuit breaker pattern"""
    
    @abstractmethod
    async def call(self, service_name: str, operation: Callable) -> Any:
        """Execute operation with circuit breaker protection"""
        pass
    
    @abstractmethod
    async def get_state(self, service_name: str) -> str:
        """Get circuit breaker state (CLOSED, OPEN, HALF_OPEN)"""
        pass
    
    @abstractmethod
    async def force_open(self, service_name: str) -> bool:
        """Force circuit breaker open"""
        pass
    
    @abstractmethod
    async def force_close(self, service_name: str) -> bool:
        """Force circuit breaker closed"""
        pass
    
    @abstractmethod
    async def get_failure_count(self, service_name: str) -> int:
        """Get failure count for service"""
        pass
    
    @abstractmethod
    async def reset_failure_count(self, service_name: str) -> bool:
        """Reset failure count for service"""
        pass
    
    @abstractmethod
    async def configure_thresholds(self, service_name: str, failure_threshold: int,
                                  recovery_timeout: int, success_threshold: int) -> bool:
        """Configure circuit breaker thresholds"""
        pass
    
    @abstractmethod
    async def get_circuit_breaker_stats(self, service_name: str) -> Dict[str, Any]:
        """Get circuit breaker statistics"""
        pass