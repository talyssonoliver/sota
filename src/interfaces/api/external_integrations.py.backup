#!/usr/bin/env python3
"""
External API Integration - Step 7.7: API Integration & Webhooks

Comprehensive external system integration for review workflows including
GitHub PR reviews, Slack approvals, JIRA integrations, and custom external systems.
"""

import json
import logging
import requests
import time
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass, asdict
from enum import Enum
from pathlib import Path

import asyncio
from abc import ABC, abstractmethod


class ExternalSystemType(Enum):
    """Types of external systems."""
    GITHUB = "github"
    SLACK = "slack"
    JIRA = "jira"
    GITLAB = "gitlab"
    TEAMS = "teams"
    CUSTOM = "custom"


class IntegrationStatus(Enum):
    """Integration request status."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    TIMEOUT = "timeout"
    CANCELLED = "cancelled"


@dataclass
class ExternalSystemConfig:
    """Configuration for external system integration."""
    system_id: str
    system_type: ExternalSystemType
    name: str
    base_url: str
    auth_config: Dict[str, Any]
    default_timeout: int = 3600  # 1 hour
    enabled: bool = True
    rate_limit_per_hour: int = 1000
    retry_count: int = 3
    retry_delay: int = 30


@dataclass
class ExternalReviewRequest:
    """External review request."""
    request_id: str
    task_id: str
    checkpoint_id: str
    system_id: str
    external_id: Optional[str]  # External system's ID (e.g., PR number, issue ID)
    review_type: str
    title: str
    description: str
    reviewers: List[str]
    priority: str
    created_at: datetime
    timeout_at: datetime
    status: IntegrationStatus
    metadata: Dict[str, Any]
    response_data: Optional[Dict[str, Any]] = None
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None


class ExternalSystemIntegration(ABC):
    """Abstract base class for external system integrations."""
    
    def __init__(self, config: ExternalSystemConfig):
        """Initialize external system integration."""
        self.config = config
        self.logger = logging.getLogger(f"external.{config.system_type.value}")
        self.rate_limit_tracker = {}
    
    @abstractmethod
    async def create_review_request(self, request: ExternalReviewRequest) -> Dict[str, Any]:
        """Create a review request in the external system."""
        pass
    
    @abstractmethod
    async def check_review_status(self, request: ExternalReviewRequest) -> Dict[str, Any]:
        """Check the status of a review request."""
        pass
    
    @abstractmethod
    async def cancel_review_request(self, request: ExternalReviewRequest) -> Dict[str, Any]:
        """Cancel a review request in the external system."""
        pass
    
    def _check_rate_limit(self) -> bool:
        """Check if we're within rate limits."""
        now = datetime.now()
        hour_key = now.strftime("%Y-%m-%d-%H")
        
        if hour_key not in self.rate_limit_tracker:
            self.rate_limit_tracker[hour_key] = 0
        
        # Clean old entries
        for key in list(self.rate_limit_tracker.keys()):
            if key < (now - timedelta(hours=1)).strftime("%Y-%m-%d-%H"):
                del self.rate_limit_tracker[key]
        
        return self.rate_limit_tracker[hour_key] < self.config.rate_limit_per_hour
    
    def _increment_rate_limit(self):
        """Increment rate limit counter."""
        hour_key = datetime.now().strftime("%Y-%m-%d-%H")
        if hour_key not in self.rate_limit_tracker:
            self.rate_limit_tracker[hour_key] = 0
        self.rate_limit_tracker[hour_key] += 1


class GitHubIntegration(ExternalSystemIntegration):
    """GitHub Pull Request integration."""
    
    async def create_review_request(self, request: ExternalReviewRequest) -> Dict[str, Any]:
        """Create a GitHub PR review request."""
        try:
            if not self._check_rate_limit():
                raise Exception("Rate limit exceeded")
            
            # Extract GitHub-specific config
            auth_token = self.config.auth_config.get("token")
            repo_owner = request.metadata.get("repo_owner")
            repo_name = request.metadata.get("repo_name")
            pr_number = request.metadata.get("pr_number")
            
            if not all([auth_token, repo_owner, repo_name, pr_number]):
                raise ValueError("Missing required GitHub configuration")
            
            # Create PR review request
            url = f"{self.config.base_url}/repos/{repo_owner}/{repo_name}/pulls/{pr_number}/requested_reviewers"
            headers = {
                "Authorization": f"Bearer {auth_token}",
                "Accept": "application/vnd.github.v3+json",
                "Content-Type": "application/json"
            }
            
            data = {
                "reviewers": request.reviewers,
                "team_reviewers": request.metadata.get("team_reviewers", [])
            }
            
            response = requests.post(url, headers=headers, json=data, timeout=30)
            response.raise_for_status()
            
            self._increment_rate_limit()
            
            return {
                "status": "success",
                "external_id": f"pr-{pr_number}",
                "response": response.json()
            }
            
        except Exception as e:
            self.logger.error(f"Failed to create GitHub review request: {e}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    async def check_review_status(self, request: ExternalReviewRequest) -> Dict[str, Any]:
        """Check GitHub PR review status."""
        try:
            auth_token = self.config.auth_config.get("token")
            repo_owner = request.metadata.get("repo_owner")
            repo_name = request.metadata.get("repo_name")
            pr_number = request.metadata.get("pr_number")
            
            # Get PR reviews
            url = f"{self.config.base_url}/repos/{repo_owner}/{repo_name}/pulls/{pr_number}/reviews"
            headers = {
                "Authorization": f"Bearer {auth_token}",
                "Accept": "application/vnd.github.v3+json"
            }
            
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            
            reviews = response.json()
            
            # Analyze review status
            approved_by = []
            rejected_by = []
            
            for review in reviews:
                if review["state"] == "APPROVED":
                    approved_by.append(review["user"]["login"])
                elif review["state"] == "REQUEST_CHANGES":
                    rejected_by.append(review["user"]["login"])
            
            # Determine overall status
            if any(reviewer in approved_by for reviewer in request.reviewers):
                status = "approved"
            elif any(reviewer in rejected_by for reviewer in request.reviewers):
                status = "rejected"
            else:
                status = "pending"
            
            return {
                "status": status,
                "approved_by": approved_by,
                "rejected_by": rejected_by,
                "reviews": reviews
            }
            
        except Exception as e:
            self.logger.error(f"Failed to check GitHub review status: {e}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    async def cancel_review_request(self, request: ExternalReviewRequest) -> Dict[str, Any]:
        """Cancel GitHub PR review request."""
        try:
            # GitHub doesn't have a direct API to cancel review requests,
            # but we can remove reviewers
            auth_token = self.config.auth_config.get("token")
            repo_owner = request.metadata.get("repo_owner")
            repo_name = request.metadata.get("repo_name")
            pr_number = request.metadata.get("pr_number")
            
            url = f"{self.config.base_url}/repos/{repo_owner}/{repo_name}/pulls/{pr_number}/requested_reviewers"
            headers = {
                "Authorization": f"Bearer {auth_token}",
                "Accept": "application/vnd.github.v3+json",
                "Content-Type": "application/json"
            }
            
            data = {
                "reviewers": request.reviewers
            }
            
            response = requests.delete(url, headers=headers, json=data, timeout=30)
            response.raise_for_status()
            
            return {
                "status": "cancelled",
                "response": response.json()
            }
            
        except Exception as e:
            self.logger.error(f"Failed to cancel GitHub review request: {e}")
            return {
                "status": "error",
                "error": str(e)
            }


class SlackIntegration(ExternalSystemIntegration):
    """Slack approval integration."""
    
    async def create_review_request(self, request: ExternalReviewRequest) -> Dict[str, Any]:
        """Create a Slack approval request."""
        try:
            if not self._check_rate_limit():
                raise Exception("Rate limit exceeded")
            
            bot_token = self.config.auth_config.get("bot_token")
            channel = request.metadata.get("channel", "#reviews")
            
            # Create interactive message with approval buttons
            blocks = [
                {
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": f"Review Request: {request.title}"
                    }
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*Task:* {request.task_id}\n*Type:* {request.review_type}\n*Priority:* {request.priority}\n\n{request.description}"
                    }
                },
                {
                    "type": "actions",
                    "elements": [
                        {
                            "type": "button",
                            "text": {
                                "type": "plain_text",
                                "text": "Approve ✅"
                            },
                            "style": "primary",
                            "action_id": "approve_review",
                            "value": request.request_id
                        },
                        {
                            "type": "button",
                            "text": {
                                "type": "plain_text",
                                "text": "Reject ❌"
                            },
                            "style": "danger",
                            "action_id": "reject_review",
                            "value": request.request_id
                        },
                        {
                            "type": "button",
                            "text": {
                                "type": "plain_text",
                                "text": "View Details 📋"
                            },
                            "action_id": "view_details",
                            "value": request.request_id
                        }
                    ]
                }
            ]
            
            headers = {
                "Authorization": f"Bearer {bot_token}",
                "Content-Type": "application/json"
            }
            
            data = {
                "channel": channel,
                "text": f"Review Request: {request.title}",
                "blocks": blocks
            }
            
            response = requests.post(
                f"{self.config.base_url}/chat.postMessage",
                headers=headers,
                json=data,
                timeout=30
            )
            response.raise_for_status()
            
            result = response.json()
            self._increment_rate_limit()
            
            return {
                "status": "success",
                "external_id": result.get("ts"),  # Slack message timestamp
                "response": result
            }
            
        except Exception as e:
            self.logger.error(f"Failed to create Slack review request: {e}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    async def check_review_status(self, request: ExternalReviewRequest) -> Dict[str, Any]:
        """Check Slack approval status."""
        # Slack status is typically handled via interactive callbacks
        # This would be updated when users click buttons
        return {
            "status": "pending",
            "message": "Slack reviews are handled via interactive callbacks"
        }
    
    async def cancel_review_request(self, request: ExternalReviewRequest) -> Dict[str, Any]:
        """Cancel Slack approval request."""
        try:
            bot_token = self.config.auth_config.get("bot_token")
            channel = request.metadata.get("channel", "#reviews")
            message_ts = request.external_id
            
            # Update message to show cancelled status
            blocks = [
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"~~Review Request: {request.title}~~\n\n*CANCELLED*"
                    }
                }
            ]
            
            headers = {
                "Authorization": f"Bearer {bot_token}",
                "Content-Type": "application/json"
            }
            
            data = {
                "channel": channel,
                "ts": message_ts,
                "text": f"Review Request Cancelled: {request.title}",
                "blocks": blocks
            }
            
            response = requests.post(
                f"{self.config.base_url}/chat.update",
                headers=headers,
                json=data,
                timeout=30
            )
            response.raise_for_status()
            
            return {
                "status": "cancelled",
                "response": response.json()
            }
            
        except Exception as e:
            self.logger.error(f"Failed to cancel Slack review request: {e}")
            return {
                "status": "error",
                "error": str(e)
            }


class JIRAIntegration(ExternalSystemIntegration):
    """JIRA issue integration."""
    
    async def create_review_request(self, request: ExternalReviewRequest) -> Dict[str, Any]:
        """Create a JIRA issue for review."""
        try:
            if not self._check_rate_limit():
                raise Exception("Rate limit exceeded")
            
            username = self.config.auth_config.get("username")
            api_token = self.config.auth_config.get("api_token")
            project_key = request.metadata.get("project_key")
            issue_type = request.metadata.get("issue_type", "Task")
            
            issue_data = {
                "fields": {
                    "project": {"key": project_key},
                    "summary": request.title,
                    "description": request.description,
                    "issuetype": {"name": issue_type},
                    "priority": {"name": request.priority.title()},
                    "assignee": {"name": request.reviewers[0]} if request.reviewers else None,
                    "labels": ["hitl-review", f"task-{request.task_id}"]
                }
            }
            
            response = requests.post(
                f"{self.config.base_url}/rest/api/3/issue",
                auth=(username, api_token),
                json=issue_data,
                timeout=30
            )
            response.raise_for_status()
            
            result = response.json()
            self._increment_rate_limit()
            
            return {
                "status": "success",
                "external_id": result["key"],
                "response": result
            }
            
        except Exception as e:
            self.logger.error(f"Failed to create JIRA review request: {e}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    async def check_review_status(self, request: ExternalReviewRequest) -> Dict[str, Any]:
        """Check JIRA issue status."""
        try:
            username = self.config.auth_config.get("username")
            api_token = self.config.auth_config.get("api_token")
            issue_key = request.external_id
            
            response = requests.get(
                f"{self.config.base_url}/rest/api/3/issue/{issue_key}",
                auth=(username, api_token),
                timeout=30
            )
            response.raise_for_status()
            
            issue = response.json()
            status_name = issue["fields"]["status"]["name"].lower()
            
            # Map JIRA status to our status
            if status_name in ["done", "closed", "resolved"]:
                status = "approved"
            elif status_name in ["rejected", "cancelled"]:
                status = "rejected"
            else:
                status = "pending"
            
            return {
                "status": status,
                "jira_status": status_name,
                "issue": issue
            }
            
        except Exception as e:
            self.logger.error(f"Failed to check JIRA review status: {e}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    async def cancel_review_request(self, request: ExternalReviewRequest) -> Dict[str, Any]:
        """Cancel JIRA issue."""
        try:
            username = self.config.auth_config.get("username")
            api_token = self.config.auth_config.get("api_token")
            issue_key = request.external_id
            
            # Transition to cancelled status
            transition_data = {
                "transition": {"id": "2"}  # Typically "Close" transition
            }
            
            response = requests.post(
                f"{self.config.base_url}/rest/api/3/issue/{issue_key}/transitions",
                auth=(username, api_token),
                json=transition_data,
                timeout=30
            )
            response.raise_for_status()
            
            return {
                "status": "cancelled",
                "response": "Issue closed"
            }
            
        except Exception as e:
            self.logger.error(f"Failed to cancel JIRA review request: {e}")
            return {
                "status": "error",
                "error": str(e)
            }


class ExternalAPIManager:
    """Manager for external API integrations."""
    
    def __init__(self, config_path: str = "config/external_apis.json"):
        """Initialize external API manager."""
        self.config_path = Path(config_path)
        self.logger = logging.getLogger("external.api.manager")
        self.systems: Dict[str, ExternalSystemIntegration] = {}
        self.requests: Dict[str, ExternalReviewRequest] = {}
          # Load configuration
        self._load_config()
        
        # Start background task for monitoring requests (only if event loop is running)
        try:
            asyncio.create_task(self._monitor_requests())
        except RuntimeError:
            # No event loop running, task will be started when needed
            pass
    
    def _load_config(self):
        """Load external system configurations."""
        try:
            if self.config_path.exists():
                with open(self.config_path, 'r') as f:
                    config = json.load(f)
                    
                for system_data in config.get("systems", []):
                    system_config = ExternalSystemConfig(
                        system_id=system_data["system_id"],
                        system_type=ExternalSystemType(system_data["system_type"]),
                        name=system_data["name"],
                        base_url=system_data["base_url"],
                        auth_config=system_data["auth_config"],
                        default_timeout=system_data.get("default_timeout", 3600),
                        enabled=system_data.get("enabled", True),
                        rate_limit_per_hour=system_data.get("rate_limit_per_hour", 1000),
                        retry_count=system_data.get("retry_count", 3),
                        retry_delay=system_data.get("retry_delay", 30)
                    )
                    
                    # Create integration instance
                    integration = self._create_integration(system_config)
                    if integration:
                        self.systems[system_config.system_id] = integration
                        
        except Exception as e:
            self.logger.error(f"Failed to load external API config: {e}")
    
    def _create_integration(self, config: ExternalSystemConfig) -> Optional[ExternalSystemIntegration]:
        """Create integration instance based on system type."""
        try:
            if config.system_type == ExternalSystemType.GITHUB:
                return GitHubIntegration(config)
            elif config.system_type == ExternalSystemType.SLACK:
                return SlackIntegration(config)
            elif config.system_type == ExternalSystemType.JIRA:
                return JIRAIntegration(config)
            else:
                self.logger.warning(f"Unsupported system type: {config.system_type}")
                return None
        except Exception as e:
            self.logger.error(f"Failed to create integration for {config.system_id}: {e}")
            return None
    
    async def create_external_review(
        self,
        task_id: str,
        checkpoint_id: str,
        system_id: str,
        review_type: str,
        title: str,
        description: str,
        reviewers: List[str],
        priority: str = "medium",
        timeout_hours: int = 24,
        metadata: Dict[str, Any] = None
    ) -> ExternalReviewRequest:
        """Create an external review request."""
        
        if system_id not in self.systems:
            raise ValueError(f"Unknown system: {system_id}")
        
        request_id = f"ext_{system_id}_{int(time.time())}_{len(self.requests)}"
        
        request = ExternalReviewRequest(
            request_id=request_id,
            task_id=task_id,
            checkpoint_id=checkpoint_id,
            system_id=system_id,
            external_id=None,
            review_type=review_type,
            title=title,
            description=description,
            reviewers=reviewers,
            priority=priority,
            created_at=datetime.now(),
            timeout_at=datetime.now() + timedelta(hours=timeout_hours),
            status=IntegrationStatus.PENDING,
            metadata=metadata or {}
        )
        
        try:
            # Create request in external system
            integration = self.systems[system_id]
            result = await integration.create_review_request(request)
            
            if result["status"] == "success":
                request.external_id = result.get("external_id")
                request.status = IntegrationStatus.IN_PROGRESS
                request.response_data = result
            else:
                request.status = IntegrationStatus.FAILED
                request.error_message = result.get("error", "Unknown error")
            
            self.requests[request_id] = request
            self.logger.info(f"Created external review request: {request_id}")
            
            return request
            
        except Exception as e:
            request.status = IntegrationStatus.FAILED
            request.error_message = str(e)
            self.requests[request_id] = request
            self.logger.error(f"Failed to create external review request: {e}")
            raise
    
    async def check_request_status(self, request_id: str) -> Optional[ExternalReviewRequest]:
        """Check the status of an external review request."""
        if request_id not in self.requests:
            return None
        
        request = self.requests[request_id]
        
        if request.status in [IntegrationStatus.COMPLETED, IntegrationStatus.FAILED, IntegrationStatus.CANCELLED]:
            return request
        
        try:
            integration = self.systems[request.system_id]
            result = await integration.check_review_status(request)
            
            if result["status"] == "approved":
                request.status = IntegrationStatus.COMPLETED
                request.completed_at = datetime.now()
                request.response_data = result
                
                # Send webhook notification
                from api.webhook_manager import send_review_approved_webhook
                send_review_approved_webhook(
                    request.task_id,
                    request.checkpoint_id,
                    {
                        "reviewer": "external_system",
                        "external_system": request.system_id,
                        "external_id": request.external_id,
                        "approved_at": request.completed_at.isoformat(),
                        "metadata": result
                    }
                )
                
            elif result["status"] == "rejected":
                request.status = IntegrationStatus.FAILED
                request.completed_at = datetime.now()
                request.error_message = "Review rejected by external system"
                request.response_data = result
                
                # Send webhook notification
                from api.webhook_manager import send_review_rejected_webhook
                send_review_rejected_webhook(
                    request.task_id,
                    request.checkpoint_id,
                    {
                        "reviewer": "external_system",
                        "external_system": request.system_id,
                        "external_id": request.external_id,
                        "rejected_at": request.completed_at.isoformat(),
                        "reason": "External system rejection",
                        "metadata": result
                    }
                )
            
            return request
            
        except Exception as e:
            self.logger.error(f"Failed to check external review status: {e}")
            return request
    
    async def cancel_request(self, request_id: str) -> bool:
        """Cancel an external review request."""
        if request_id not in self.requests:
            return False
        
        request = self.requests[request_id]
        
        try:
            integration = self.systems[request.system_id]
            result = await integration.cancel_review_request(request)
            
            if result["status"] == "cancelled":
                request.status = IntegrationStatus.CANCELLED
                request.completed_at = datetime.now()
                self.logger.info(f"Cancelled external review request: {request_id}")
                return True
            else:
                self.logger.error(f"Failed to cancel external review request: {request_id}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error cancelling external review request: {e}")
            return False
    
    async def _monitor_requests(self):
        """Background task to monitor external review requests."""
        while True:
            try:
                now = datetime.now()
                
                for request_id, request in list(self.requests.items()):
                    # Check for timeouts
                    if request.status == IntegrationStatus.IN_PROGRESS and now > request.timeout_at:
                        request.status = IntegrationStatus.TIMEOUT
                        request.completed_at = now
                        request.error_message = "Request timed out"
                        
                        self.logger.warning(f"External review request timed out: {request_id}")
                        
                        # Try to cancel in external system
                        try:
                            await self.cancel_request(request_id)
                        except Exception as e:
                            self.logger.error(f"Failed to cancel timed-out request: {e}")
                    
                    # Check status of pending requests
                    elif request.status == IntegrationStatus.IN_PROGRESS:
                        await self.check_request_status(request_id)
                
                # Wait before next check
                await asyncio.sleep(60)  # Check every minute
                
            except Exception as e:
                self.logger.error(f"Error in request monitoring: {e}")
                await asyncio.sleep(60)
    
    def get_request(self, request_id: str) -> Optional[ExternalReviewRequest]:
        """Get external review request by ID."""
        return self.requests.get(request_id)
    
    def list_requests(self, system_id: str = None, status: IntegrationStatus = None) -> List[ExternalReviewRequest]:
        """List external review requests with optional filters."""
        requests = list(self.requests.values())
        
        if system_id:
            requests = [r for r in requests if r.system_id == system_id]
        
        if status:
            requests = [r for r in requests if r.status == status]
        
        return requests
    
    def get_system_stats(self, system_id: str) -> Dict[str, Any]:
        """Get statistics for an external system."""
        if system_id not in self.systems:
            return {}
        
        system_requests = [r for r in self.requests.values() if r.system_id == system_id]
        
        total = len(system_requests)
        completed = len([r for r in system_requests if r.status == IntegrationStatus.COMPLETED])
        failed = len([r for r in system_requests if r.status == IntegrationStatus.FAILED])
        pending = len([r for r in system_requests if r.status == IntegrationStatus.IN_PROGRESS])
        
        return {
            "system_id": system_id,
            "total_requests": total,
            "completed_requests": completed,
            "failed_requests": failed,
            "pending_requests": pending,
            "success_rate": (completed / total * 100) if total > 0 else 0
        }


# Global external API manager instance
_external_api_manager = None

def get_external_api_manager() -> ExternalAPIManager:
    """Get global external API manager instance."""
    global _external_api_manager
    if _external_api_manager is None:
        _external_api_manager = ExternalAPIManager()
    return _external_api_manager


# Convenience functions
async def create_github_review(
    task_id: str,
    checkpoint_id: str,
    repo_owner: str,
    repo_name: str,
    pr_number: int,
    reviewers: List[str],
    title: str = None,
    description: str = None
) -> ExternalReviewRequest:
    """Create a GitHub PR review request."""
    manager = get_external_api_manager()
    
    return await manager.create_external_review(
        task_id=task_id,
        checkpoint_id=checkpoint_id,
        system_id="github",
        review_type="github_pr",
        title=title or f"Review PR #{pr_number}",
        description=description or f"Please review PR #{pr_number} for task {task_id}",
        reviewers=reviewers,
        metadata={
            "repo_owner": repo_owner,
            "repo_name": repo_name,
            "pr_number": pr_number
        }
    )


async def create_slack_approval(
    task_id: str,
    checkpoint_id: str,
    channel: str,
    title: str,
    description: str,
    priority: str = "medium"
) -> ExternalReviewRequest:
    """Create a Slack approval request."""
    manager = get_external_api_manager()
    
    return await manager.create_external_review(
        task_id=task_id,
        checkpoint_id=checkpoint_id,
        system_id="slack",
        review_type="slack_approval",
        title=title,
        description=description,
        reviewers=[],  # Slack doesn't need specific reviewers
        priority=priority,
        metadata={"channel": channel}
    )


# Module-level exports for integration
external_api_manager = get_external_api_manager()
