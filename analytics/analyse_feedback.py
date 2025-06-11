"""
Feedback Analysis and Agent Refinement - Phase 7 Step 7.8 Implementation

This module implements the original plan's feedback loop for agent refinement:
- Aggregate human feedback to retrain prompt templates
- Adjust retrieval context based on feedback patterns
- Improve tool functions based on recurring edits
- Generate recommendations for system improvements

Original Plan Requirements:
```bash
python analytics/analyse_feedback.py --task BE-07
```

Outputs:
- Summary of recurring edits
- Prompt modifications needed
- Examples for fine-tuning
"""

import argparse
import json
import logging
import os
import sys
from collections import Counter, defaultdict
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import yaml

# Add parent directory to path to allow imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.feedback_system import FeedbackSystem

# Configure logger
logger = logging.getLogger("feedback_analysis")


class FeedbackAnalyzer:
    """Analyzes human feedback to improve agent performance"""
    
    def __init__(self, outputs_dir: str = "outputs", base_dir: str = "c:\\taly\\ai-system"):
        self.base_dir = Path(base_dir)
        self.outputs_dir = Path(outputs_dir)
        self.feedback_system = FeedbackSystem()
        self.analysis_results = {}
        
        # Create analytics output directory
        self.analytics_dir = self.base_dir / "analytics" / "results"
        self.analytics_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"FeedbackAnalyzer initialized with base_dir: {self.base_dir}")
    
    def analyze_task_feedback(self, task_id: str) -> Dict[str, Any]:
        """
        Analyze feedback for a specific task
        
        Args:
            task_id: Task identifier (e.g., BE-07)
            
        Returns:
            Analysis results including recommendations
        """
        logger.info(f"Analyzing feedback for task: {task_id}")
          # Get feedback for the task
        feedback_entries = self.feedback_system.get_feedback_by_task(task_id)
        
        if not feedback_entries:
            logger.warning(f"No feedback found for task {task_id}")
            return {"task_id": task_id, "status": "no_feedback", "recommendations": []}
        
        analysis = {
            "task_id": task_id,
            "analysis_timestamp": datetime.now().isoformat(),
            "feedback_count": len(feedback_entries),
            "summary": self._analyze_feedback_summary(feedback_entries),
            "recurring_edits": self._identify_recurring_edits(feedback_entries),
            "prompt_modifications": self._suggest_prompt_modifications(feedback_entries),
            "tool_improvements": self._suggest_tool_improvements(feedback_entries),
            "context_adjustments": self._suggest_context_adjustments(feedback_entries),
            "fine_tuning_examples": self._generate_fine_tuning_examples(feedback_entries),
            "overall_recommendations": []
        }
        
        # Generate overall recommendations
        analysis["overall_recommendations"] = self._generate_overall_recommendations(analysis)
        
        # Save analysis results
        self._save_analysis_results(task_id, analysis)
        
        return analysis
    
    def analyze_all_feedback(self, period_days: int = 30) -> Dict[str, Any]:
        """
        Analyze all feedback from the specified period
        
        Args:
            period_days: Number of days to look back for feedback
              Returns:
            Comprehensive analysis across all tasks
        """
        logger.info(f"Analyzing all feedback from the last {period_days} days")
        
        # Get feedback from the specified period
        all_feedback = self.feedback_system.get_feedback_by_period(f"{period_days}d")
        
        if not all_feedback:
            logger.warning("No feedback found in the specified period")
            return {"status": "no_feedback", "period_days": period_days}
        
        # Group feedback by task and agent
        feedback_by_task = defaultdict(list)
        feedback_by_agent = defaultdict(list)
        
        for feedback in all_feedback:
            feedback_by_task[feedback.task_id].append(feedback)
            if hasattr(feedback, 'agent_name') and feedback.agent_name:
                feedback_by_agent[feedback.agent_name].append(feedback)
        
        analysis = {
            "analysis_timestamp": datetime.now().isoformat(),
            "period_days": period_days,
            "total_feedback": len(all_feedback),
            "tasks_analyzed": len(feedback_by_task),
            "agents_analyzed": len(feedback_by_agent),
            "global_patterns": self._analyze_global_patterns(all_feedback),
            "agent_performance": self._analyze_agent_performance(feedback_by_agent),
            "task_patterns": self._analyze_task_patterns(feedback_by_task),
            "system_improvements": self._suggest_system_improvements(all_feedback),
            "training_recommendations": self._generate_training_recommendations(all_feedback)
        }
        
        # Save comprehensive analysis
        self._save_analysis_results("comprehensive_analysis", analysis)
        
        return analysis
    
    def _analyze_feedback_summary(self, feedback_entries: List[Any]) -> Dict[str, Any]:
        """Analyze feedback summary statistics"""
        if not feedback_entries:
            return {}
        
        # Calculate approval rates by category
        approval_rates = {}
        category_scores = defaultdict(list)
        
        for feedback in feedback_entries:
            if hasattr(feedback, 'category_scores'):
                for category, score in feedback.category_scores.items():
                    category_scores[category].append(score)
        
        for category, scores in category_scores.items():
            if scores:
                approval_rates[category] = {
                    "average_score": sum(scores) / len(scores),
                    "min_score": min(scores),
                    "max_score": max(scores),
                    "total_ratings": len(scores)
                }
        
        return {
            "total_feedback": len(feedback_entries),
            "approval_rates": approval_rates,
            "average_overall_score": self._calculate_average_score(feedback_entries)
        }
    
    def _identify_recurring_edits(self, feedback_entries: List[Any]) -> List[Dict[str, Any]]:
        """Identify patterns in human edits and corrections"""
        edit_patterns = Counter()
        edit_details = defaultdict(list)
        
        for feedback in feedback_entries:
            if hasattr(feedback, 'content') and feedback.content:
                # Extract common edit patterns from feedback content
                content_lower = feedback.content.lower()
                
                # Common patterns to look for
                patterns = {
                    "naming_conventions": ["rename", "naming", "should be called"],
                    "code_structure": ["refactor", "structure", "organize"],
                    "error_handling": ["error", "exception", "try-catch"],
                    "documentation": ["comment", "document", "explain"],
                    "performance": ["performance", "optimize", "slow"],
                    "security": ["security", "vulnerability", "safe"],
                    "best_practices": ["best practice", "convention", "standard"]
                }
                
                for pattern_type, keywords in patterns.items():
                    if any(keyword in content_lower for keyword in keywords):
                        edit_patterns[pattern_type] += 1
                        edit_details[pattern_type].append({
                            "task_id": feedback.task_id,
                            "content": feedback.content,
                            "timestamp": feedback.timestamp
                        })
        
        # Convert to list of dictionaries for output
        recurring_edits = []
        for pattern, count in edit_patterns.most_common():
            recurring_edits.append({
                "pattern": pattern,
                "frequency": count,
                "examples": edit_details[pattern][:3]  # Top 3 examples
            })
        
        return recurring_edits
    
    def _suggest_prompt_modifications(self, feedback_entries: List[Any]) -> List[Dict[str, Any]]:
        """Suggest prompt template modifications based on feedback"""
        suggestions = []
        
        # Analyze feedback for prompt-related issues
        prompt_issues = {
            "clarity": 0,
            "completeness": 0,
            "specificity": 0,
            "context": 0
        }
        
        for feedback in feedback_entries:
            if hasattr(feedback, 'content') and feedback.content:
                content_lower = feedback.content.lower()
                
                if any(word in content_lower for word in ["unclear", "confusing", "ambiguous"]):
                    prompt_issues["clarity"] += 1
                
                if any(word in content_lower for word in ["missing", "incomplete", "add"]):
                    prompt_issues["completeness"] += 1
                
                if any(word in content_lower for word in ["specific", "detail", "precise"]):
                    prompt_issues["specificity"] += 1
                
                if any(word in content_lower for word in ["context", "background", "explain"]):
                    prompt_issues["context"] += 1
        
        # Generate suggestions based on identified issues
        if prompt_issues["clarity"] > 2:
            suggestions.append({
                "type": "clarity",
                "priority": "high",
                "suggestion": "Add clearer instructions and examples to prompt templates",
                "frequency": prompt_issues["clarity"]
            })
        
        if prompt_issues["completeness"] > 2:
            suggestions.append({
                "type": "completeness", 
                "priority": "medium",
                "suggestion": "Include more comprehensive task requirements in prompts",
                "frequency": prompt_issues["completeness"]
            })
        
        if prompt_issues["specificity"] > 2:
            suggestions.append({
                "type": "specificity",
                "priority": "medium", 
                "suggestion": "Add more specific constraints and criteria to prompts",
                "frequency": prompt_issues["specificity"]
            })
        
        if prompt_issues["context"] > 2:
            suggestions.append({
                "type": "context",
                "priority": "high",
                "suggestion": "Enhance context injection and background information",
                "frequency": prompt_issues["context"]
            })
        
        return suggestions
    
    def _suggest_tool_improvements(self, feedback_entries: List[Any]) -> List[Dict[str, Any]]:
        """Suggest tool function improvements based on feedback"""
        suggestions = []
        tool_issues = Counter()
        
        for feedback in feedback_entries:
            if hasattr(feedback, 'content') and feedback.content:
                content_lower = feedback.content.lower()
                
                # Look for tool-related feedback
                if "tool" in content_lower or "function" in content_lower:
                    if any(word in content_lower for word in ["slow", "performance", "timeout"]):
                        tool_issues["performance"] += 1
                    
                    if any(word in content_lower for word in ["error", "failed", "broken"]):
                        tool_issues["reliability"] += 1
                    
                    if any(word in content_lower for word in ["missing", "need", "should have"]):
                        tool_issues["functionality"] += 1
        
        # Generate suggestions
        for issue_type, count in tool_issues.items():
            if count > 1:
                suggestions.append({
                    "type": issue_type,
                    "frequency": count,
                    "suggestion": self._get_tool_suggestion(issue_type)
                })
        
        return suggestions
    
    def _suggest_context_adjustments(self, feedback_entries: List[Any]) -> List[Dict[str, Any]]:
        """Suggest retrieval context adjustments"""
        suggestions = []
        context_issues = Counter()
        
        for feedback in feedback_entries:
            if hasattr(feedback, 'content') and feedback.content:
                content_lower = feedback.content.lower()
                
                if any(word in content_lower for word in ["context", "background", "related"]):
                    if "missing" in content_lower or "need more" in content_lower:
                        context_issues["insufficient_context"] += 1
                    
                    if "irrelevant" in content_lower or "not related" in content_lower:
                        context_issues["irrelevant_context"] += 1
                    
                    if "outdated" in content_lower or "old" in content_lower:
                        context_issues["outdated_context"] += 1
        
        # Generate suggestions
        for issue_type, count in context_issues.items():
            if count > 1:
                suggestions.append({
                    "type": issue_type,
                    "frequency": count,
                    "suggestion": self._get_context_suggestion(issue_type)
                })
        
        return suggestions
    
    def _generate_fine_tuning_examples(self, feedback_entries: List[Any]) -> List[Dict[str, Any]]:
        """Generate examples for fine-tuning based on feedback"""
        examples = []
        
        for feedback in feedback_entries:
            if hasattr(feedback, 'content') and feedback.content and len(feedback.content) > 50:
                # Create fine-tuning example from high-quality feedback
                if hasattr(feedback, 'overall_score') and feedback.overall_score >= 8:
                    examples.append({
                        "task_id": feedback.task_id,
                        "input": getattr(feedback, 'agent_output', ''),
                        "feedback": feedback.content,
                        "score": feedback.overall_score,
                        "category": "positive_example"
                    })
                elif hasattr(feedback, 'overall_score') and feedback.overall_score <= 5:
                    examples.append({
                        "task_id": feedback.task_id,
                        "input": getattr(feedback, 'agent_output', ''),
                        "feedback": feedback.content,
                        "score": feedback.overall_score,
                        "category": "improvement_needed"
                    })
        
        return examples[:10]  # Limit to top 10 examples
    
    def _analyze_global_patterns(self, all_feedback: List[Any]) -> Dict[str, Any]:
        """Analyze global patterns across all feedback"""
        patterns = {
            "common_issues": Counter(),
            "quality_trends": [],
            "agent_feedback_distribution": Counter()
        }
        
        for feedback in all_feedback:
            if hasattr(feedback, 'content') and feedback.content:
                content_lower = feedback.content.lower()
                
                # Identify common issues
                if "error" in content_lower:
                    patterns["common_issues"]["errors"] += 1
                if "performance" in content_lower:
                    patterns["common_issues"]["performance"] += 1
                if "documentation" in content_lower:
                    patterns["common_issues"]["documentation"] += 1
                if "test" in content_lower:
                    patterns["common_issues"]["testing"] += 1
        
        return patterns
    
    def _analyze_agent_performance(self, feedback_by_agent: Dict[str, List[Any]]) -> Dict[str, Dict[str, Any]]:
        """Analyze performance by agent"""
        agent_analysis = {}
        
        for agent_name, feedback_list in feedback_by_agent.items():
            scores = []
            for feedback in feedback_list:
                if hasattr(feedback, 'overall_score'):
                    scores.append(feedback.overall_score)
            
            if scores:
                agent_analysis[agent_name] = {
                    "average_score": sum(scores) / len(scores),
                    "feedback_count": len(feedback_list),
                    "improvement_areas": self._identify_agent_improvement_areas(feedback_list)
                }
        
        return agent_analysis
    
    def _analyze_task_patterns(self, feedback_by_task: Dict[str, List[Any]]) -> Dict[str, Any]:
        """Analyze patterns by task type"""
        task_patterns = {
            "by_task_type": defaultdict(list),
            "common_issues_by_type": defaultdict(Counter)
        }
        
        for task_id, feedback_list in feedback_by_task.items():
            task_type = task_id.split('-')[0] if '-' in task_id else 'UNKNOWN'
            
            scores = []
            for feedback in feedback_list:
                if hasattr(feedback, 'overall_score'):
                    scores.append(feedback.overall_score)
            
            if scores:
                task_patterns["by_task_type"][task_type].extend(scores)
        
        return task_patterns
    
    def _suggest_system_improvements(self, all_feedback: List[Any]) -> List[Dict[str, Any]]:
        """Suggest system-wide improvements"""
        improvements = []
        
        # Analyze system-wide issues
        system_issues = Counter()
        
        for feedback in all_feedback:
            if hasattr(feedback, 'content') and feedback.content:
                content_lower = feedback.content.lower()
                
                if any(word in content_lower for word in ["slow", "timeout", "performance"]):
                    system_issues["performance"] += 1
                
                if any(word in content_lower for word in ["error", "crash", "failed"]):
                    system_issues["reliability"] += 1
                
                if any(word in content_lower for word in ["interface", "ui", "ux"]):
                    system_issues["user_experience"] += 1
        
        # Generate improvement suggestions
        for issue_type, count in system_issues.most_common(5):
            if count > 2:
                improvements.append({
                    "area": issue_type,
                    "frequency": count,
                    "priority": "high" if count > 5 else "medium",
                    "suggestion": self._get_system_improvement_suggestion(issue_type)
                })
        
        return improvements
    
    def _generate_training_recommendations(self, all_feedback: List[Any]) -> List[Dict[str, Any]]:
        """Generate training recommendations for agents"""
        recommendations = []
        
        # Analyze training needs
        training_needs = {
            "prompt_engineering": 0,
            "code_quality": 0,
            "documentation": 0,
            "testing": 0
        }
        
        for feedback in all_feedback:
            if hasattr(feedback, 'content') and feedback.content:
                content_lower = feedback.content.lower()
                
                for need_type in training_needs.keys():
                    if need_type.replace('_', ' ') in content_lower:
                        training_needs[need_type] += 1
        
        # Generate recommendations
        for need_type, count in training_needs.items():
            if count > 3:
                recommendations.append({
                    "training_area": need_type,
                    "frequency": count,
                    "recommendation": self._get_training_recommendation(need_type)
                })
        
        return recommendations
    
    def _generate_overall_recommendations(self, analysis: Dict[str, Any]) -> List[str]:
        """Generate overall recommendations from analysis"""
        recommendations = []
        
        if analysis.get("recurring_edits"):
            recommendations.append("Focus on addressing recurring edit patterns in agent training")
        
        if analysis.get("prompt_modifications"):
            recommendations.append("Update prompt templates based on identified modification needs")
        
        if analysis.get("tool_improvements"):
            recommendations.append("Enhance tool functions based on user feedback")
        
        if analysis.get("context_adjustments"):
            recommendations.append("Improve context retrieval and injection mechanisms")
        
        return recommendations
    
    def _calculate_average_score(self, feedback_entries: List[Any]) -> float:
        """Calculate average overall score from feedback entries"""
        scores = []
        for feedback in feedback_entries:
            if hasattr(feedback, 'overall_score'):
                scores.append(feedback.overall_score)
        
        return sum(scores) / len(scores) if scores else 0.0
    
    def _identify_agent_improvement_areas(self, feedback_list: List[Any]) -> List[str]:
        """Identify improvement areas for a specific agent"""
        issues = Counter()
        
        for feedback in feedback_list:
            if hasattr(feedback, 'content') and feedback.content:
                content_lower = feedback.content.lower()
                
                if any(word in content_lower for word in ["accuracy", "correct", "wrong"]):
                    issues["accuracy"] += 1
                if any(word in content_lower for word in ["speed", "fast", "slow"]):
                    issues["speed"] += 1
                if any(word in content_lower for word in ["quality", "better"]):
                    issues["quality"] += 1
        
        return [issue for issue, count in issues.most_common(3)]
    
    def _get_tool_suggestion(self, issue_type: str) -> str:
        """Get tool improvement suggestion based on issue type"""
        suggestions = {
            "performance": "Optimize tool functions for better performance and reduce timeout issues",
            "reliability": "Add better error handling and retry mechanisms to tools",
            "functionality": "Expand tool capabilities based on user needs and feedback"
        }
        return suggestions.get(issue_type, "Improve tool based on feedback")
    
    def _get_context_suggestion(self, issue_type: str) -> str:
        """Get context adjustment suggestion based on issue type"""
        suggestions = {
            "insufficient_context": "Increase context window size and improve retrieval accuracy",
            "irrelevant_context": "Refine context filtering and relevance scoring",
            "outdated_context": "Implement context freshness checks and update mechanisms"
        }
        return suggestions.get(issue_type, "Improve context handling")
    
    def _get_system_improvement_suggestion(self, issue_type: str) -> str:
        """Get system improvement suggestion based on issue type"""
        suggestions = {
            "performance": "Implement performance monitoring and optimization strategies",
            "reliability": "Add comprehensive error handling and recovery mechanisms",
            "user_experience": "Improve user interface and interaction design"
        }
        return suggestions.get(issue_type, "General system improvement needed")
    
    def _get_training_recommendation(self, need_type: str) -> str:
        """Get training recommendation based on need type"""
        recommendations = {
            "prompt_engineering": "Provide training on effective prompt design and optimization",
            "code_quality": "Implement code quality training and best practices workshops",
            "documentation": "Train on documentation standards and technical writing",
            "testing": "Provide comprehensive testing methodology and framework training"
        }
        return recommendations.get(need_type, "General training recommended")
    
    def _save_analysis_results(self, identifier: str, analysis: Dict[str, Any]) -> None:
        """Save analysis results to file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{identifier}_analysis_{timestamp}.json"
        filepath = self.analytics_dir / filename
        
        try:
            with open(filepath, 'w') as f:
                json.dump(analysis, f, indent=2, default=str)
            
            logger.info(f"Analysis results saved to: {filepath}")
            
        except Exception as e:
            logger.error(f"Failed to save analysis results: {e}")
    
    def generate_report(self, analysis: Dict[str, Any], format: str = "markdown") -> str:
        """Generate a human-readable report from analysis results"""
        if format == "markdown":
            return self._generate_markdown_report(analysis)
        elif format == "json":
            return json.dumps(analysis, indent=2, default=str)
        else:
            return str(analysis)
    
    def _generate_markdown_report(self, analysis: Dict[str, Any]) -> str:
        """Generate markdown report from analysis"""
        report = []
        
        if "task_id" in analysis:
            report.append(f"# Feedback Analysis Report - Task {analysis['task_id']}")
        else:
            report.append("# Comprehensive Feedback Analysis Report")
        
        report.append(f"\n**Analysis Date:** {analysis.get('analysis_timestamp', 'Unknown')}")
        
        if "feedback_count" in analysis:
            report.append(f"**Feedback Entries:** {analysis['feedback_count']}")
        
        # Summary section
        if "summary" in analysis:
            report.append("\n## Summary")
            summary = analysis["summary"]
            report.append(f"- **Total Feedback:** {summary.get('total_feedback', 0)}")
            report.append(f"- **Average Score:** {summary.get('average_overall_score', 0):.2f}")
        
        # Recurring edits
        if "recurring_edits" in analysis and analysis["recurring_edits"]:
            report.append("\n## Recurring Edits")
            for edit in analysis["recurring_edits"]:
                report.append(f"- **{edit['pattern']}:** {edit['frequency']} occurrences")
        
        # Prompt modifications
        if "prompt_modifications" in analysis and analysis["prompt_modifications"]:
            report.append("\n## Prompt Modification Recommendations")
            for mod in analysis["prompt_modifications"]:
                report.append(f"- **{mod['type']}** (Priority: {mod['priority']}): {mod['suggestion']}")
        
        # Tool improvements
        if "tool_improvements" in analysis and analysis["tool_improvements"]:
            report.append("\n## Tool Improvement Suggestions")
            for improvement in analysis["tool_improvements"]:
                report.append(f"- **{improvement['type']}:** {improvement['suggestion']}")
        
        # Overall recommendations
        if "overall_recommendations" in analysis and analysis["overall_recommendations"]:
            report.append("\n## Overall Recommendations")
            for i, rec in enumerate(analysis["overall_recommendations"], 1):
                report.append(f"{i}. {rec}")
        
        return "\n".join(report)


def main():
    """Main CLI interface for feedback analysis"""
    parser = argparse.ArgumentParser(description="Analyze human feedback for agent refinement")
    parser.add_argument("--task", help="Specific task ID to analyze (e.g., BE-07)")
    parser.add_argument("--period", type=int, default=30, help="Period in days for comprehensive analysis")
    parser.add_argument("--format", choices=["json", "markdown"], default="markdown", help="Output format")
    parser.add_argument("--output", help="Output file path (optional)")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose logging")
    
    args = parser.parse_args()
    
    # Configure logging
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Initialize analyzer
    analyzer = FeedbackAnalyzer()
    
    # Perform analysis
    if args.task:
        print(f"Analyzing feedback for task: {args.task}")
        analysis = analyzer.analyze_task_feedback(args.task)
    else:
        print(f"Analyzing all feedback from the last {args.period} days")
        analysis = analyzer.analyze_all_feedback(args.period)
    
    # Generate report
    report = analyzer.generate_report(analysis, args.format)
    
    # Output results
    if args.output:
        with open(args.output, 'w') as f:
            f.write(report)
        print(f"Report saved to: {args.output}")
    else:
        print("\n" + "="*50)
        print(report)
        print("="*50)
    
    # Print summary of key findings
    print(f"\n📊 Analysis Summary:")
    if "feedback_count" in analysis:
        print(f"   • Analyzed {analysis['feedback_count']} feedback entries")
    if "recurring_edits" in analysis:
        print(f"   • Found {len(analysis['recurring_edits'])} recurring edit patterns")
    if "prompt_modifications" in analysis:
        print(f"   • Generated {len(analysis['prompt_modifications'])} prompt modification suggestions")
    if "overall_recommendations" in analysis:
        print(f"   • Created {len(analysis['overall_recommendations'])} overall recommendations")


if __name__ == "__main__":
    main()
