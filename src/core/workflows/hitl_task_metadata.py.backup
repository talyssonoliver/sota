#!/usr/bin/env python3
"""
Task Metadata Extension for HITL Integration - Phase 7

Extends existing task metadata schema to support Human-in-the-Loop
checkpoints, approval workflows, and risk assessment.
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass, field, asdict
from enum import Enum

from orchestration.states import TaskStatus


class HITLStatus(str, Enum):
    """HITL-specific status for tasks."""
    NO_HITL = "no_hitl"                    # Task doesn't require HITL
    HITL_PENDING = "hitl_pending"          # HITL checkpoint created, awaiting review
    HITL_APPROVED = "hitl_approved"        # HITL checkpoint approved
    HITL_REJECTED = "hitl_rejected"        # HITL checkpoint rejected
    HITL_ESCALATED = "hitl_escalated"      # HITL checkpoint escalated
    HITL_TIMEOUT = "hitl_timeout"          # HITL checkpoint timed out


class HITLRiskLevel(str, Enum):
    """Risk levels for HITL assessment."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class HITLCheckpointMetadata:
    """Metadata for a HITL checkpoint in a task."""
    checkpoint_id: str
    checkpoint_type: str
    status: HITLStatus
    risk_level: HITLRiskLevel
    created_at: datetime
    reviewer: Optional[str] = None
    reviewed_at: Optional[datetime] = None
    timeout_at: Optional[datetime] = None
    notes: str = ""
    confidence_score: float = 0.0
    retry_count: int = 0
    escalation_reason: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        result = asdict(self)
        # Convert datetime objects to ISO strings
        if self.created_at:
            result['created_at'] = self.created_at.isoformat()
        if self.reviewed_at:
            result['reviewed_at'] = self.reviewed_at.isoformat()
        if self.timeout_at:
            result['timeout_at'] = self.timeout_at.isoformat()
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'HITLCheckpointMetadata':
        """Create from dictionary."""
        # Convert ISO strings back to datetime objects
        if 'created_at' in data and isinstance(data['created_at'], str):
            data['created_at'] = datetime.fromisoformat(data['created_at'])
        if 'reviewed_at' in data and isinstance(data['reviewed_at'], str):
            data['reviewed_at'] = datetime.fromisoformat(data['reviewed_at'])
        if 'timeout_at' in data and isinstance(data['timeout_at'], str):
            data['timeout_at'] = datetime.fromisoformat(data['timeout_at'])
        
        return cls(**data)


@dataclass
class HITLTaskMetadata:
    """Extended task metadata with HITL integration."""
    # Original task metadata fields
    task_id: str
    title: str = ""
    description: str = ""
    status: TaskStatus = TaskStatus.CREATED
    owner: str = ""
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    # HITL-specific fields
    hitl_enabled: bool = False
    hitl_status: HITLStatus = HITLStatus.NO_HITL
    overall_risk_level: HITLRiskLevel = HITLRiskLevel.LOW
    checkpoints: List[HITLCheckpointMetadata] = field(default_factory=list)  # Using checkpoints instead of hitl_checkpoints
    hitl_policy_version: str = "1.0"
    requires_approval: bool = False
    auto_approval_eligible: bool = True
    human_reviewer: Optional[str] = None
    escalation_contacts: List[str] = field(default_factory=list)
    
    # Workflow phase tracking for HITL triggers
    current_phase: str = "created"
    phase_history: List[Dict[str, Any]] = field(default_factory=list)
    
    # Risk assessment context - using risk_assessment to match test expectations
    risk_assessment: Dict[str, Any] = field(default_factory=dict)
    risk_factors: Dict[str, Any] = field(default_factory=dict)
    confidence_metrics: Dict[str, float] = field(default_factory=dict)
    
    # Integration metadata
    external_ids: Dict[str, str] = field(default_factory=dict)  # GitHub, Jira, etc.
    tags: List[str] = field(default_factory=list)
    
    def add_hitl_checkpoint(self, checkpoint: HITLCheckpointMetadata) -> None:
        """Add a HITL checkpoint to the task."""
        self.hitl_checkpoints.append(checkpoint)
        self.hitl_enabled = True
        
        # Update overall HITL status
        if checkpoint.status == HITLStatus.HITL_PENDING:
            self.hitl_status = HITLStatus.HITL_PENDING
        
        # Update overall risk level if checkpoint is higher risk
        risk_hierarchy = {
            HITLRiskLevel.LOW: 1,
            HITLRiskLevel.MEDIUM: 2,
            HITLRiskLevel.HIGH: 3,
            HITLRiskLevel.CRITICAL: 4
        }
        
        if risk_hierarchy[checkpoint.risk_level] > risk_hierarchy[self.overall_risk_level]:
            self.overall_risk_level = checkpoint.risk_level
            
        self.updated_at = datetime.now()
    
    def get_active_checkpoints(self) -> List[HITLCheckpointMetadata]:
        """Get checkpoints that are currently pending review."""
        return [cp for cp in self.hitl_checkpoints if cp.status == HITLStatus.HITL_PENDING]
    
    def get_checkpoint_by_id(self, checkpoint_id: str) -> Optional[HITLCheckpointMetadata]:
        """Get a checkpoint by its ID."""
        for checkpoint in self.hitl_checkpoints:
            if checkpoint.checkpoint_id == checkpoint_id:
                return checkpoint
        return None
    
    def update_checkpoint_status(self, checkpoint_id: str, status: HITLStatus, 
                                reviewer: str = None, notes: str = "") -> bool:
        """Update the status of a checkpoint."""
        checkpoint = self.get_checkpoint_by_id(checkpoint_id)
        if not checkpoint:
            return False
        
        checkpoint.status = status
        checkpoint.reviewed_at = datetime.now()
        if reviewer:
            checkpoint.reviewer = reviewer
        if notes:
            checkpoint.notes = notes
        
        # Update overall HITL status
        active_checkpoints = self.get_active_checkpoints()
        if not active_checkpoints:
            if status == HITLStatus.HITL_APPROVED:
                self.hitl_status = HITLStatus.HITL_APPROVED
            elif status == HITLStatus.HITL_REJECTED:
                self.hitl_status = HITLStatus.HITL_REJECTED
            elif status == HITLStatus.HITL_ESCALATED:
                self.hitl_status = HITLStatus.HITL_ESCALATED
        
        self.updated_at = datetime.now()
        return True
    
    def update_phase(self, new_phase: str, context: Dict[str, Any] = None) -> None:
        """Update the current workflow phase."""
        # Add previous phase to history
        phase_entry = {
            "phase": self.current_phase,
            "timestamp": datetime.now().isoformat(),
            "context": context or {}
        }
        self.phase_history.append(phase_entry)
        
        # Update current phase
        self.current_phase = new_phase
        self.updated_at = datetime.now()
    
    def calculate_risk_score(self) -> float:
        """Calculate overall risk score for the task."""
        base_scores = {
            HITLRiskLevel.LOW: 0.2,
            HITLRiskLevel.MEDIUM: 0.5,
            HITLRiskLevel.HIGH: 0.8,
            HITLRiskLevel.CRITICAL: 1.0
        }
        
        base_score = base_scores[self.overall_risk_level]
        
        # Factor in risk factors
        risk_adjustments = 0.0
        for factor, value in self.risk_factors.items():
            if isinstance(value, (int, float)):
                risk_adjustments += value * 0.1  # Weight each factor
        
        # Factor in confidence metrics
        confidence_adjustment = 0.0
        if self.confidence_metrics:
            avg_confidence = sum(self.confidence_metrics.values()) / len(self.confidence_metrics)
            confidence_adjustment = (1.0 - avg_confidence) * 0.2  # Lower confidence = higher risk
        
        final_score = min(1.0, base_score + risk_adjustments + confidence_adjustment)
        return final_score
    
    def is_blocked_on_hitl(self) -> bool:
        """Check if task is currently blocked on HITL review."""
        return (self.hitl_enabled and 
                self.hitl_status == HITLStatus.HITL_PENDING and 
                len(self.get_active_checkpoints()) > 0)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        result = asdict(self)
        
        # Convert datetime objects to ISO strings
        result['created_at'] = self.created_at.isoformat()
        result['updated_at'] = self.updated_at.isoformat()
        
        # Convert enum values to strings
        result['status'] = self.status.value if isinstance(self.status, TaskStatus) else str(self.status)
        result['hitl_status'] = self.hitl_status.value
        result['overall_risk_level'] = self.overall_risk_level.value
          # Convert checkpoints
        result['hitl_checkpoints'] = [cp.to_dict() for cp in self.checkpoints]
        
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'HITLTaskMetadata':
        """Create from dictionary."""
        # Convert ISO strings back to datetime objects
        if 'created_at' in data and isinstance(data['created_at'], str):
            data['created_at'] = datetime.fromisoformat(data['created_at'])
        if 'updated_at' in data and isinstance(data['updated_at'], str):
            data['updated_at'] = datetime.fromisoformat(data['updated_at'])
        
        # Convert string values back to enums
        if 'status' in data and isinstance(data['status'], str):
            data['status'] = TaskStatus.from_string(data['status'])
        if 'hitl_status' in data and isinstance(data['hitl_status'], str):
            data['hitl_status'] = HITLStatus(data['hitl_status'])
        if 'overall_risk_level' in data and isinstance(data['overall_risk_level'], str):
            data['overall_risk_level'] = HITLRiskLevel(data['overall_risk_level'])
          # Convert checkpoints (handle both old 'hitl_checkpoints' and new 'checkpoints' keys)
        if 'checkpoints' in data:
            data['checkpoints'] = [
                HITLCheckpointMetadata.from_dict(cp) 
                for cp in data['checkpoints']
            ]
        elif 'hitl_checkpoints' in data:
            # Handle old format for backward compatibility
            data['checkpoints'] = [
                HITLCheckpointMetadata.from_dict(cp) 
                for cp in data['hitl_checkpoints']
            ]
            del data['hitl_checkpoints']  # Remove old key
        
        return cls(**data)


class HITLTaskMetadataManager:
    """Manager for HITL task metadata operations."""
    
    def __init__(self, storage_path: str = "storage/hitl_tasks"):
        """Initialize the metadata manager."""
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        self.logger = logging.getLogger("hitl.metadata.manager")
        
    def save_task_metadata(self, task_metadata: HITLTaskMetadata) -> bool:
        """Save task metadata to storage."""
        try:
            file_path = self.storage_path / f"{task_metadata.task_id}.json"
            with open(file_path, 'w') as f:
                json.dump(task_metadata.to_dict(), f, indent=2, default=str)
            return True
        except Exception as e:
            self.logger.error(f"Failed to save task metadata {task_metadata.task_id}: {e}")
            return False
    
    def load_task_metadata(self, task_id: str) -> Optional[HITLTaskMetadata]:
        """Load task metadata from storage."""
        try:
            file_path = self.storage_path / f"{task_id}.json"
            if not file_path.exists():
                return None
                
            with open(file_path, 'r') as f:
                data = json.load(f)
            
            return HITLTaskMetadata.from_dict(data)
        except Exception as e:
            self.logger.error(f"Failed to load task metadata {task_id}: {e}")
            return None
    
    def get_all_tasks(self) -> List[HITLTaskMetadata]:
        """Get all task metadata."""
        tasks = []
        try:
            for file_path in self.storage_path.glob("*.json"):
                task_id = file_path.stem
                task_metadata = self.load_task_metadata(task_id)
                if task_metadata:
                    tasks.append(task_metadata)
        except Exception as e:
            self.logger.error(f"Failed to get all tasks: {e}")
        
        return tasks
    
    def get_tasks_with_active_hitl(self) -> List[HITLTaskMetadata]:
        """Get tasks that have active HITL checkpoints."""
        all_tasks = self.get_all_tasks()
        return [task for task in all_tasks if task.is_blocked_on_hitl()]
    
    def get_tasks_by_status(self, status: TaskStatus) -> List[HITLTaskMetadata]:
        """Get tasks by their status."""
        all_tasks = self.get_all_tasks()
        return [task for task in all_tasks if task.status == status]
    
    def get_tasks_by_hitl_status(self, hitl_status: HITLStatus) -> List[HITLTaskMetadata]:
        """Get tasks by their HITL status."""
        all_tasks = self.get_all_tasks()
        return [task for task in all_tasks if task.hitl_status == hitl_status]
    
    def get_tasks_by_risk_level(self, risk_level: HITLRiskLevel) -> List[HITLTaskMetadata]:
        """Get tasks by their risk level."""
        all_tasks = self.get_all_tasks()
        return [task for task in all_tasks if task.overall_risk_level == risk_level]
    
    def update_task_status(self, task_id: str, status: TaskStatus) -> bool:
        """Update task status."""
        task_metadata = self.load_task_metadata(task_id)
        if not task_metadata:
            return False
        
        task_metadata.status = status
        task_metadata.updated_at = datetime.now()
        return self.save_task_metadata(task_metadata)
    
    def add_checkpoint_to_task(self, task_id: str, checkpoint: HITLCheckpointMetadata) -> bool:
        """Add a HITL checkpoint to a task."""
        task_metadata = self.load_task_metadata(task_id)
        if not task_metadata:
            return False
        
        task_metadata.add_hitl_checkpoint(checkpoint)
        return self.save_task_metadata(task_metadata)
    
    def update_checkpoint_status(self, task_id: str, checkpoint_id: str, 
                                status: HITLStatus, reviewer: str = None, 
                                notes: str = "") -> bool:
        """Update checkpoint status."""
        task_metadata = self.load_task_metadata(task_id)
        if not task_metadata:
            return False
        
        success = task_metadata.update_checkpoint_status(checkpoint_id, status, reviewer, notes)
        if success:
            return self.save_task_metadata(task_metadata)
        return False
    
    def create_task_from_legacy(self, task_data: Dict[str, Any]) -> HITLTaskMetadata:
        """Create HITL task metadata from legacy task data."""
        # Map legacy fields to HITL task metadata
        task_metadata = HITLTaskMetadata(
            task_id=task_data.get('id', task_data.get('task_id', 'unknown')),
            title=task_data.get('title', task_data.get('name', 'Untitled Task')),
            description=task_data.get('description', ''),
            status=TaskStatus.from_string(task_data.get('status', 'CREATED')),
            owner=task_data.get('owner', task_data.get('assigned_to', 'unknown')),
            created_at=datetime.now(),
            updated_at=datetime.now(),
            tags=task_data.get('tags', []),
            external_ids=task_data.get('external_ids', {})
        )
        
        # Set up HITL configuration based on task properties
        task_type = task_data.get('type', 'general')
        if task_type in ['backend', 'infrastructure', 'security']:
            task_metadata.overall_risk_level = HITLRiskLevel.MEDIUM
            task_metadata.requires_approval = True
        elif task_type in ['critical', 'production']:
            task_metadata.overall_risk_level = HITLRiskLevel.HIGH
            task_metadata.requires_approval = True
            task_metadata.auto_approval_eligible = False
        
        return task_metadata
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get statistics about HITL tasks."""
        all_tasks = self.get_all_tasks()
        
        if not all_tasks:
            return {
                "total_tasks": 0,
                "hitl_enabled_tasks": 0,
                "active_checkpoints": 0,
                "status_distribution": {},
                "risk_distribution": {},
                "hitl_status_distribution": {}
            }
        
        # Calculate distributions
        status_dist = {}
        risk_dist = {}
        hitl_status_dist = {}
        
        hitl_enabled_count = 0
        active_checkpoints_count = 0
        
        for task in all_tasks:
            # Status distribution
            status_key = task.status.value
            status_dist[status_key] = status_dist.get(status_key, 0) + 1
            
            # Risk distribution
            risk_key = task.overall_risk_level.value
            risk_dist[risk_key] = risk_dist.get(risk_key, 0) + 1
            
            # HITL status distribution
            hitl_key = task.hitl_status.value
            hitl_status_dist[hitl_key] = hitl_status_dist.get(hitl_key, 0) + 1
            
            # HITL metrics
            if task.hitl_enabled:
                hitl_enabled_count += 1
            
            active_checkpoints_count += len(task.get_active_checkpoints())
        
        return {
            "total_tasks": len(all_tasks),
            "hitl_enabled_tasks": hitl_enabled_count,
            "active_checkpoints": active_checkpoints_count,
            "status_distribution": status_dist,
            "risk_distribution": risk_dist,
            "hitl_status_distribution": hitl_status_dist
        }


# Global metadata manager instance
hitl_metadata_manager = HITLTaskMetadataManager()
