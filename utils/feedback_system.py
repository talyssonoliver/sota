"""
Phase 7 Step 7.4: Structured Feedback Integration System
Comprehensive feedback collection, storage, analytics, and export capabilities.
"""

import json
import csv
import os
import uuid
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict
from enum import Enum
import logging


# Configure logging
logger = logging.getLogger(__name__)


class FeedbackCategory:
    """Feedback category definitions and validation"""
    
    CATEGORIES = {
        "code_quality": {
            "name": "Code Quality",
            "description": "Readability, maintainability, best practices",
            "weight": 0.25
        },
        "architecture": {
            "name": "Architecture",
            "description": "Design patterns, scalability, modularity",
            "weight": 0.20
        },
        "security": {
            "name": "Security", 
            "description": "Vulnerabilities, compliance, access control",
            "weight": 0.25
        },
        "performance": {
            "name": "Performance",
            "description": "Efficiency, resource usage, optimization",
            "weight": 0.15
        },
        "documentation": {
            "name": "Documentation",
            "description": "Clarity, completeness, accuracy",
            "weight": 0.15
        }
    }
    
    @classmethod
    def get_all_categories(cls) -> List[str]:
        """Get all available feedback categories"""
        return list(cls.CATEGORIES.keys())
    
    @classmethod
    def is_valid(cls, category: str) -> bool:
        """Check if category is valid"""
        return category in cls.CATEGORIES
    
    @classmethod
    def is_valid_score(cls, score: Union[int, float]) -> bool:
        """Check if score is in valid range (1-10)"""
        try:
            score = float(score)
            return 1 <= score <= 10
        except (TypeError, ValueError):
            return False
    
    @classmethod
    def get_category_info(cls, category: str) -> Optional[Dict]:
        """Get category information"""
        return cls.CATEGORIES.get(category)


@dataclass
class FeedbackEntry:
    """Structured feedback entry data structure"""
    
    task_id: str
    reviewer: str
    approval_decision: bool
    feedback_categories: Dict[str, Dict[str, Any]] = None
    comments: List[str] = None
    suggested_improvements: List[str] = None
    risk_level: str = "medium"
    timestamp: datetime = None
    feedback_id: str = None
    
    def __post_init__(self):
        """Initialize computed fields"""
        if not self.task_id:
            raise ValueError("task_id cannot be empty")
        
        if not self.reviewer:
            raise ValueError("reviewer cannot be empty")
        
        if self.timestamp is None:
            self.timestamp = datetime.now()
        
        if self.feedback_id is None:
            self.feedback_id = str(uuid.uuid4())
        
        if self.feedback_categories is None:
            self.feedback_categories = {}
        
        if self.comments is None:
            self.comments = []
        
        if self.suggested_improvements is None:
            self.suggested_improvements = []
        
        # Validate feedback categories
        for category, data in self.feedback_categories.items():
            if not FeedbackCategory.is_valid(category):
                logger.warning(f"Invalid feedback category: {category}")
            
            if isinstance(data, dict) and "score" in data:
                if not FeedbackCategory.is_valid_score(data["score"]):
                    raise ValueError(f"Invalid score for {category}: {data['score']}")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        data = asdict(self)
        data["timestamp"] = self.timestamp.isoformat()
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "FeedbackEntry":
        """Create from dictionary"""
        data = data.copy()
        if "timestamp" in data and isinstance(data["timestamp"], str):
            data["timestamp"] = datetime.fromisoformat(data["timestamp"])
        
        return cls(**data)
    
    def get_overall_score(self) -> Optional[float]:
        """Calculate overall weighted score"""
        if not self.feedback_categories:
            return None
        
        total_score = 0.0
        total_weight = 0.0
        
        for category, data in self.feedback_categories.items():
            if isinstance(data, dict) and "score" in data:
                category_info = FeedbackCategory.get_category_info(category)
                if category_info:
                    weight = category_info["weight"]
                    total_score += data["score"] * weight
                    total_weight += weight
        
        return total_score / total_weight if total_weight > 0 else None


class FeedbackStorage:
    """Feedback storage and retrieval system"""
    
    def __init__(self, storage_dir: str = "storage/feedback"):
        """Initialize storage system"""
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"Feedback storage initialized: {self.storage_dir}")
    
    def save_feedback(self, entry: FeedbackEntry) -> str:
        """Save feedback entry to storage"""
        try:
            filename = f"feedback_{entry.feedback_id}.json"
            filepath = self.storage_dir / filename
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(entry.to_dict(), f, indent=2, ensure_ascii=False)
            
            logger.info(f"Feedback saved: {entry.feedback_id} for task {entry.task_id}")
            return entry.feedback_id
            
        except Exception as e:
            logger.error(f"Error saving feedback: {str(e)}")
            raise
    
    def load_feedback(self, feedback_id: str) -> Optional[FeedbackEntry]:
        """Load specific feedback entry"""
        try:
            filename = f"feedback_{feedback_id}.json"
            filepath = self.storage_dir / filename
            
            if not filepath.exists():
                return None
            
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            return FeedbackEntry.from_dict(data)
            
        except Exception as e:
            logger.error(f"Error loading feedback {feedback_id}: {str(e)}")
            return None
    
    def get_all_feedback(self) -> List[FeedbackEntry]:
        """Get all feedback entries"""
        feedback_entries = []
        
        try:
            for filepath in self.storage_dir.glob("feedback_*.json"):
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                entry = FeedbackEntry.from_dict(data)
                feedback_entries.append(entry)
        
        except Exception as e:
            logger.error(f"Error loading feedback entries: {str(e)}")
        
        return feedback_entries
    
    def get_feedback_by_task(self, task_id: str) -> List[FeedbackEntry]:
        """Get all feedback for a specific task"""
        all_feedback = self.get_all_feedback()
        return [entry for entry in all_feedback if entry.task_id == task_id]
    
    def get_feedback_by_reviewer(self, reviewer: str) -> List[FeedbackEntry]:
        """Get all feedback from a specific reviewer"""
        all_feedback = self.get_all_feedback()
        return [entry for entry in all_feedback if entry.reviewer == reviewer]
    
    def get_feedback_by_period(self, period: str) -> List[FeedbackEntry]:
        """Get feedback from a specific time period"""
        # Parse period (e.g., "7d", "30d", "1h")
        if period.endswith('d'):
            days = int(period[:-1])
            cutoff = datetime.now() - timedelta(days=days)
        elif period.endswith('h'):
            hours = int(period[:-1])
            cutoff = datetime.now() - timedelta(hours=hours)
        else:
            raise ValueError(f"Invalid period format: {period}")
        
        all_feedback = self.get_all_feedback()
        return [entry for entry in all_feedback if entry.timestamp >= cutoff]


class FeedbackAnalytics:
    """Feedback analytics and trend analysis"""
    
    def __init__(self):
        """Initialize analytics engine"""
        logger.info("Feedback analytics initialized")
    
    def calculate_approval_rate(self, feedback_entries: List[FeedbackEntry]) -> float:
        """Calculate approval rate percentage"""
        if not feedback_entries:
            return 0.0
        
        approved_count = sum(1 for entry in feedback_entries if entry.approval_decision)
        return (approved_count / len(feedback_entries)) * 100
    
    def calculate_category_averages(self, feedback_entries: List[FeedbackEntry]) -> Dict[str, float]:
        """Calculate average scores for each category"""
        category_scores = {}
        category_counts = {}
        
        for entry in feedback_entries:
            for category, data in entry.feedback_categories.items():
                if isinstance(data, dict) and "score" in data:
                    if category not in category_scores:
                        category_scores[category] = 0.0
                        category_counts[category] = 0
                    
                    category_scores[category] += data["score"]
                    category_counts[category] += 1
        
        averages = {}
        for category in category_scores:
            if category_counts[category] > 0:
                averages[category] = category_scores[category] / category_counts[category]
        
        return averages
    
    def identify_trends(self, feedback_entries: List[FeedbackEntry]) -> Dict[str, Any]:
        """Identify trends in feedback data"""
        trends = {
            "approval_rate": self.calculate_approval_rate(feedback_entries),
            "category_scores": self.calculate_category_averages(feedback_entries),
            "common_issues": self._extract_common_issues(feedback_entries),
            "improvement_areas": self._identify_improvement_areas(feedback_entries)
        }
        
        return trends
    
    def generate_insights(self, feedback_entries: List[FeedbackEntry]) -> Dict[str, Any]:
        """Generate insights from feedback data"""
        if not feedback_entries:
            return {
                "summary": "No feedback data available",
                "recommendations": [],
                "patterns": {}
            }
        
        trends = self.identify_trends(feedback_entries)
        
        insights = {
            "summary": f"Analyzed {len(feedback_entries)} feedback entries",
            "recommendations": self._generate_recommendations(trends),
            "patterns": self._analyze_patterns(feedback_entries)
        }
        
        return insights
    
    def filter_by_reviewer(self, feedback_entries: List[FeedbackEntry], reviewer: str) -> List[FeedbackEntry]:
        """Filter feedback by reviewer"""
        return [entry for entry in feedback_entries if entry.reviewer == reviewer]
    
    def filter_by_approval_decision(self, feedback_entries: List[FeedbackEntry], approved: bool) -> List[FeedbackEntry]:
        """Filter feedback by approval decision"""
        return [entry for entry in feedback_entries if entry.approval_decision == approved]
    
    def _extract_common_issues(self, feedback_entries: List[FeedbackEntry]) -> List[str]:
        """Extract common issues from feedback comments"""
        # Simple keyword extraction - could be enhanced with NLP
        issue_keywords = {}
        
        for entry in feedback_entries:
            for comment in entry.comments:
                words = comment.lower().split()
                for word in words:
                    if len(word) > 3:  # Filter short words
                        issue_keywords[word] = issue_keywords.get(word, 0) + 1
        
        # Return top issues
        sorted_issues = sorted(issue_keywords.items(), key=lambda x: x[1], reverse=True)
        return [issue for issue, count in sorted_issues[:5]]
    
    def _identify_improvement_areas(self, feedback_entries: List[FeedbackEntry]) -> List[str]:
        """Identify areas for improvement"""
        category_averages = self.calculate_category_averages(feedback_entries)
        
        # Find categories with scores below 7
        improvement_areas = []
        for category, average in category_averages.items():
            if average < 7.0:
                improvement_areas.append(category)
        
        return improvement_areas
    
    def _generate_recommendations(self, trends: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on trends"""
        recommendations = []
        
        # Approval rate recommendations
        if trends["approval_rate"] < 70:
            recommendations.append("Consider improving code review process - approval rate is below 70%")
        
        # Category-specific recommendations
        for category, score in trends["category_scores"].items():
            if score < 6:
                category_info = FeedbackCategory.get_category_info(category)
                if category_info:
                    recommendations.append(f"Focus on {category_info['name']} - average score is {score:.1f}")
        
        return recommendations
    
    def _analyze_patterns(self, feedback_entries: List[FeedbackEntry]) -> Dict[str, Any]:
        """Analyze patterns in feedback data"""
        patterns = {
            "reviewer_distribution": {},
            "task_types": {},
            "risk_levels": {}
        }
        
        for entry in feedback_entries:
            # Reviewer patterns
            reviewer = entry.reviewer
            patterns["reviewer_distribution"][reviewer] = patterns["reviewer_distribution"].get(reviewer, 0) + 1
            
            # Task type patterns (extract from task_id prefix)
            task_prefix = entry.task_id.split('-')[0] if '-' in entry.task_id else "unknown"
            patterns["task_types"][task_prefix] = patterns["task_types"].get(task_prefix, 0) + 1
            
            # Risk level patterns
            risk_level = entry.risk_level
            patterns["risk_levels"][risk_level] = patterns["risk_levels"].get(risk_level, 0) + 1
        
        return patterns


class FeedbackExporter:
    """Feedback data export functionality"""
    
    def __init__(self):
        """Initialize exporter"""
        logger.info("Feedback exporter initialized")
    
    def export_to_json(self, feedback_entries: List[FeedbackEntry], output_path: str) -> bool:
        """Export feedback to JSON format"""
        try:
            data = [entry.to_dict() for entry in feedback_entries]
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Exported {len(feedback_entries)} entries to JSON: {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error exporting to JSON: {str(e)}")
            return False
    
    def export_to_csv(self, feedback_entries: List[FeedbackEntry], output_path: str) -> bool:
        """Export feedback to CSV format"""
        try:
            if not feedback_entries:
                return True
            
            with open(output_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                
                # Write header
                header = [
                    "feedback_id", "task_id", "reviewer", "timestamp", 
                    "approval_decision", "risk_level", "overall_score",
                    "comments", "improvements"
                ]
                
                # Add category score columns
                all_categories = set()
                for entry in feedback_entries:
                    all_categories.update(entry.feedback_categories.keys())
                
                for category in sorted(all_categories):
                    header.append(f"{category}_score")
                    header.append(f"{category}_comments")
                
                writer.writerow(header)
                
                # Write data
                for entry in feedback_entries:
                    row = [
                        entry.feedback_id,
                        entry.task_id,
                        entry.reviewer,
                        entry.timestamp.isoformat(),
                        entry.approval_decision,
                        entry.risk_level,
                        entry.get_overall_score(),
                        "; ".join(entry.comments),
                        "; ".join(entry.suggested_improvements)
                    ]
                    
                    # Add category data
                    for category in sorted(all_categories):
                        category_data = entry.feedback_categories.get(category, {})
                        row.append(category_data.get("score", ""))
                        row.append(category_data.get("comments", ""))
                    
                    writer.writerow(row)
            
            logger.info(f"Exported {len(feedback_entries)} entries to CSV: {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error exporting to CSV: {str(e)}")
            return False
    
    def generate_summary_report(self, feedback_entries: List[FeedbackEntry], output_path: str) -> bool:
        """Generate markdown summary report"""
        try:
            analytics = FeedbackAnalytics()
            trends = analytics.identify_trends(feedback_entries)
            insights = analytics.generate_insights(feedback_entries)
            
            content = self._generate_report_content(feedback_entries, trends, insights)
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            logger.info(f"Generated summary report: {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error generating summary report: {str(e)}")
            return False
    
    def _generate_report_content(self, feedback_entries: List[FeedbackEntry], 
                               trends: Dict[str, Any], insights: Dict[str, Any]) -> str:
        """Generate report content"""
        content = f"""# Feedback Summary Report

Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Overview

- **Total Feedback Entries**: {len(feedback_entries)}
- **Approval Rate**: {trends['approval_rate']:.1f}%
- **Analysis Period**: Recent feedback data

## Category Scores

"""
        
        for category, score in trends['category_scores'].items():
            category_info = FeedbackCategory.get_category_info(category)
            if category_info:
                content += f"- **{category_info['name']}**: {score:.1f}/10\n"
        
        content += f"""

## Key Insights

{insights['summary']}

### Recommendations

"""
        
        for recommendation in insights['recommendations']:
            content += f"- {recommendation}\n"
        
        content += """

## Recent Feedback Entries

"""
        
        # Add recent entries (last 5)
        recent_entries = sorted(feedback_entries, key=lambda x: x.timestamp, reverse=True)[:5]
        
        for entry in recent_entries:
            status = "✅ Approved" if entry.approval_decision else "❌ Rejected"
            content += f"""
### {entry.task_id} - {status}

- **Reviewer**: {entry.reviewer}
- **Date**: {entry.timestamp.strftime('%Y-%m-%d %H:%M')}
- **Overall Score**: {entry.get_overall_score():.1f}/10
- **Risk Level**: {entry.risk_level}

"""
            
            if entry.comments:
                content += "**Comments**:\n"
                for comment in entry.comments:
                    content += f"- {comment}\n"
            
            if entry.suggested_improvements:
                content += "**Improvements**:\n"
                for improvement in entry.suggested_improvements:
                    content += f"- {improvement}\n"
        
        return content


class FeedbackSystem:
    """Main feedback system orchestrator"""
    
    def __init__(self, storage_dir: str = "storage/feedback"):
        """Initialize feedback system"""
        self.storage = FeedbackStorage(storage_dir)
        self.analytics = FeedbackAnalytics()
        self.exporter = FeedbackExporter()
        
        logger.info("Feedback system initialized")
    
    def capture_feedback(self, task_id: str, reviewer: str, feedback_data: Dict[str, Any]) -> str:
        """Capture structured feedback with metadata"""
        try:
            # Process feedback data
            feedback_entry = FeedbackEntry(
                task_id=task_id,
                reviewer=reviewer,
                approval_decision=feedback_data.get("approved", False),
                feedback_categories={},
                comments=feedback_data.get("comments", []),
                suggested_improvements=feedback_data.get("improvements", []),
                risk_level=feedback_data.get("risk_level", "medium")
            )
            
            # Process category feedback
            for category in FeedbackCategory.get_all_categories():
                if category in feedback_data:
                    feedback_entry.feedback_categories[category] = feedback_data[category]
            
            # Save feedback
            feedback_id = self.storage.save_feedback(feedback_entry)
            
            logger.info(f"Captured feedback for task {task_id} by {reviewer}")
            return feedback_id
            
        except Exception as e:
            logger.error(f"Error capturing feedback: {str(e)}")
            raise
    
    def get_feedback_summary(self, task_id: str) -> Dict[str, Any]:
        """Get feedback summary for a specific task"""
        try:
            task_feedback = self.storage.get_feedback_by_task(task_id)
            
            if not task_feedback:
                return {
                    "task_id": task_id,
                    "total_feedback_count": 0,
                    "approval_rate": 0.0,
                    "category_averages": {},
                    "recent_feedback": []
                }
            
            approval_rate = self.analytics.calculate_approval_rate(task_feedback)
            category_averages = self.analytics.calculate_category_averages(task_feedback)
            
            # Get recent feedback (last 3)
            recent_feedback = sorted(task_feedback, key=lambda x: x.timestamp, reverse=True)[:3]
            recent_data = []
            
            for entry in recent_feedback:
                recent_data.append({
                    "reviewer": entry.reviewer,
                    "timestamp": entry.timestamp.isoformat(),
                    "approved": entry.approval_decision,
                    "overall_score": entry.get_overall_score()
                })
            
            return {
                "task_id": task_id,
                "total_feedback_count": len(task_feedback),
                "approval_rate": approval_rate,
                "category_averages": category_averages,
                "recent_feedback": recent_data
            }
            
        except Exception as e:
            logger.error(f"Error getting feedback summary for {task_id}: {str(e)}")
            raise
    
    def generate_analytics_report(self, period: str = "7d") -> Dict[str, Any]:
        """Generate analytics report for specified period"""
        try:
            feedback_entries = self.storage.get_feedback_by_period(period)
            
            if not feedback_entries:
                return {
                    "period": period,
                    "total_feedback": 0,
                    "approval_rate": 0.0,
                    "trends": {},
                    "insights": {}
                }
            
            trends = self.analytics.identify_trends(feedback_entries)
            insights = self.analytics.generate_insights(feedback_entries)
            
            return {
                "period": period,
                "total_feedback": len(feedback_entries),
                "approval_rate": trends["approval_rate"],
                "category_averages": trends["category_scores"],
                "trends": trends,
                "insights": insights
            }
            
        except Exception as e:
            logger.error(f"Error generating analytics report: {str(e)}")
            raise
    
    def export_feedback_data(self, format: str, output_path: str, period: str = "30d") -> bool:
        """Export feedback data in specified format"""
        try:
            feedback_entries = self.storage.get_feedback_by_period(period)
            
            if format.lower() == "json":
                return self.exporter.export_to_json(feedback_entries, output_path)
            elif format.lower() == "csv":
                return self.exporter.export_to_csv(feedback_entries, output_path)
            elif format.lower() == "summary":
                return self.exporter.generate_summary_report(feedback_entries, output_path)
            else:
                raise ValueError(f"Unsupported export format: {format}")
            
        except Exception as e:
            logger.error(f"Error exporting feedback data: {str(e)}")
            return False
    
    def integrate_with_checkpoint(self, checkpoint_data: Dict[str, Any], 
                                feedback_data: Dict[str, Any], reviewer: str) -> Dict[str, Any]:
        """Integrate feedback with HITL checkpoint"""
        try:
            task_id = checkpoint_data.get("task_id")
            checkpoint_id = checkpoint_data.get("checkpoint_id")
            
            if not task_id:
                raise ValueError("task_id is required in checkpoint_data")
            
            # Capture feedback
            feedback_id = self.capture_feedback(task_id, reviewer, feedback_data)
            
            # Update checkpoint with feedback reference
            result = {
                "status": "success",
                "feedback_id": feedback_id,
                "checkpoint_id": checkpoint_id,
                "task_id": task_id,
                "approved": feedback_data.get("approved", False)
            }
            
            logger.info(f"Integrated feedback {feedback_id} with checkpoint {checkpoint_id}")
            return result
            
        except Exception as e:
            logger.error(f"Error integrating with checkpoint: {str(e)}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    def process_review_feedback(self, workflow_data: Dict[str, Any], 
                              feedback_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process feedback as part of review workflow"""
        try:
            task_id = workflow_data.get("task_id")
            reviewer = workflow_data.get("reviewer")
            
            if not task_id or not reviewer:
                raise ValueError("task_id and reviewer are required in workflow_data")
            
            # Capture feedback
            feedback_id = self.capture_feedback(task_id, reviewer, feedback_data)
            
            return {
                "status": "success",
                "feedback_id": feedback_id,
                "task_id": task_id,
                "reviewer": reviewer
            }
            
        except Exception as e:
            logger.error(f"Error processing review feedback: {str(e)}")
            return {
                "status": "error",
                "error": str(e)
            }


# Global feedback system instance
_feedback_system = None

def get_feedback_system() -> FeedbackSystem:
    """Get global feedback system instance"""
    global _feedback_system
    if _feedback_system is None:
        _feedback_system = FeedbackSystem()
    return _feedback_system
