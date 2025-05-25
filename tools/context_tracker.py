#!/usr/bin/env python3
"""
Step 3.7 Implementation: Context Tracking per Task

This module implements context tracking functionality as specified in Step 3.7 
of the system implementation plan. It tracks which documents were used in each 
task run and stores the information under /outputs/[TASK-ID]/context_log.json.

Usage:
    from tools.context_tracker import track_context_usage, get_context_log
    
    # Track context usage during task execution
    track_context_usage(
        task_id="BE-07",
        context_topics=["db-schema", "service-pattern"],
        documents_used=documents,
        agent_role="backend"
    )
    
    # Retrieve context log for analysis
    log = get_context_log("BE-07")
"""

import os
import json
import logging
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional, Union

logger = logging.getLogger(__name__)

def track_context_usage(
    task_id: str,
    context_topics: List[str] = None,
    documents_used: List[Dict[str, Any]] = None,
    agent_role: str = "unknown",
    context_length: int = 0,
    additional_metadata: Dict[str, Any] = None
) -> bool:
    """
    Track context usage for a specific task execution.
    
    Args:
        task_id (str): The task identifier (e.g., "BE-07")
        context_topics (List[str]): Context topics that were requested
        documents_used (List[Dict]): List of documents that were retrieved and used
        agent_role (str): The role of the agent executing the task
        context_length (int): Total length of context used
        additional_metadata (Dict): Any additional metadata to store
        
    Returns:
        bool: True if logging was successful, False otherwise
    """
    try:
        # Create the output directory for this task
        output_dir = Path("outputs") / task_id
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Prepare context usage data according to Step 3.7 specification
        context_log = {
            "task": task_id,
            "context_used": context_topics or [],
            "timestamp": datetime.now().isoformat(),
            "agent_role": agent_role,
            "context_length": context_length,
            "documents_retrieved": len(documents_used) if documents_used else 0,
            "document_sources": []
        }
        
        # Extract document source information
        if documents_used:
            for doc in documents_used:
                metadata = doc.get("metadata", {})
                source_info = {
                    "source": metadata.get("source", "unknown"),
                    "topic": metadata.get("topic", "unknown"),
                    "query_used": metadata.get("query_used", ""),
                    "retrieved_at": metadata.get("retrieved_at", ""),
                    "content_length": len(doc.get("page_content", ""))
                }
                context_log["document_sources"].append(source_info)
        
        # Add any additional metadata
        if additional_metadata:
            context_log.update(additional_metadata)
        
        # Save to the context log file as specified in Step 3.7
        log_file = output_dir / "context_log.json"
        
        with open(log_file, 'w', encoding='utf-8') as f:
            json.dump(context_log, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Context usage tracked for task {task_id}: {len(context_topics or [])} topics, {len(documents_used or [])} documents")
        return True
        
    except Exception as e:
        logger.error(f"Failed to track context usage for task {task_id}: {e}")
        return False

def get_context_log(task_id: str) -> Optional[Dict[str, Any]]:
    """
    Retrieve the context log for a specific task.
    
    Args:
        task_id (str): The task identifier
        
    Returns:
        Dict[str, Any] or None: The context log data, or None if not found
    """
    try:
        log_file = Path("outputs") / task_id / "context_log.json"
        
        if not log_file.exists():
            logger.warning(f"Context log not found for task {task_id}")
            return None
        
        with open(log_file, 'r', encoding='utf-8') as f:
            return json.load(f)
            
    except Exception as e:
        logger.error(f"Failed to retrieve context log for task {task_id}: {e}")
        return None

def get_all_context_logs() -> Dict[str, Dict[str, Any]]:
    """
    Retrieve all context logs from the outputs directory.
    
    Returns:
        Dict[str, Dict]: Dictionary mapping task_id to context log data
    """
    logs = {}
    outputs_dir = Path("outputs")
    
    if not outputs_dir.exists():
        return logs
    
    try:
        for task_dir in outputs_dir.iterdir():
            if task_dir.is_dir():
                task_id = task_dir.name
                log_data = get_context_log(task_id)
                if log_data:
                    logs[task_id] = log_data
    except Exception as e:
        logger.error(f"Failed to retrieve all context logs: {e}")
    
    return logs

def analyze_context_usage(task_ids: List[str] = None) -> Dict[str, Any]:
    """
    Analyze context usage patterns across tasks.
    
    Args:
        task_ids (List[str]): Specific task IDs to analyze, or None for all tasks
        
    Returns:
        Dict[str, Any]: Analysis results including topic usage, document frequency, etc.
    """
    if task_ids:
        logs = {tid: get_context_log(tid) for tid in task_ids}
        logs = {k: v for k, v in logs.items() if v is not None}
    else:
        logs = get_all_context_logs()
    
    if not logs:
        return {"error": "No context logs found"}
    
    # Analyze topic usage
    topic_usage = {}
    document_usage = {}
    agent_usage = {}
    
    for task_id, log_data in logs.items():
        # Count topic usage
        for topic in log_data.get("context_used", []):
            topic_usage[topic] = topic_usage.get(topic, 0) + 1
        
        # Count document source usage
        for doc_source in log_data.get("document_sources", []):
            source = doc_source.get("source", "unknown")
            document_usage[source] = document_usage.get(source, 0) + 1
        
        # Count agent role usage
        agent_role = log_data.get("agent_role", "unknown")
        agent_usage[agent_role] = agent_usage.get(agent_role, 0) + 1
    
    return {
        "total_tasks_analyzed": len(logs),
        "topic_usage_frequency": topic_usage,
        "document_usage_frequency": document_usage,
        "agent_usage_frequency": agent_usage,
        "most_used_topics": sorted(topic_usage.items(), key=lambda x: x[1], reverse=True)[:5],
        "most_used_documents": sorted(document_usage.items(), key=lambda x: x[1], reverse=True)[:5]
    }

def export_context_usage_report(output_path: str = "reports/context_usage_report.json") -> bool:
    """
    Export a comprehensive context usage report.
    
    Args:
        output_path (str): Path where to save the report
        
    Returns:
        bool: True if export was successful
    """
    try:
        # Create reports directory
        report_file = Path(output_path)
        report_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Generate comprehensive analysis
        analysis = analyze_context_usage()
        all_logs = get_all_context_logs()
        
        report = {
            "generated_at": datetime.now().isoformat(),
            "step_3_7_implementation": "Context Tracking per Task",
            "summary": analysis,
            "detailed_logs": all_logs
        }
        
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Context usage report exported to {output_path}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to export context usage report: {e}")
        return False

def track_context_from_memory_engine(
    task_id: str,
    context_topics: List[str],
    documents: List[Dict[str, Any]],
    agent_role: str = "system",
    max_tokens: int = 2000
) -> bool:
    """
    Helper function to track context usage directly from memory engine operations.
    
    This integrates with the memory engine's get_documents and build_focused_context
    methods to automatically track context usage.
    
    Args:
        task_id (str): Task identifier
        context_topics (List[str]): Context topics requested
        documents (List[Dict]): Documents retrieved from memory engine
        agent_role (str): Agent role executing the task
        max_tokens (int): Token budget used
        
    Returns:
        bool: True if tracking was successful
    """
    # Calculate total context length
    total_length = sum(len(doc.get("page_content", "")) for doc in documents)
    
    # Additional metadata for memory engine integration
    additional_metadata = {
        "token_budget": max_tokens,
        "estimated_tokens": total_length // 4,  # Rough token estimation
        "within_budget": (total_length // 4) <= max_tokens,
        "step_3_5_integration": True,
        "step_3_6_integration": any(doc.get("metadata", {}).get("chunk_id") is not None for doc in documents)
    }
    
    return track_context_usage(
        task_id=task_id,
        context_topics=context_topics,
        documents_used=documents,
        agent_role=agent_role,
        context_length=total_length,
        additional_metadata=additional_metadata
    )

# CLI interface for Step 3.7 context tracking
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Step 3.7 Context Tracking CLI")
    parser.add_argument("command", choices=["analyze", "export", "list"], help="Command to execute")
    parser.add_argument("--task-id", help="Specific task ID to analyze")
    parser.add_argument("--output", default="reports/context_usage_report.json", help="Output file for export")
    
    args = parser.parse_args()
    
    if args.command == "analyze":
        if args.task_id:
            analysis = analyze_context_usage([args.task_id])
            print(f"Context analysis for task {args.task_id}:")
        else:
            analysis = analyze_context_usage()
            print("Context analysis for all tasks:")
        
        print(json.dumps(analysis, indent=2))
    
    elif args.command == "export":
        success = export_context_usage_report(args.output)
        if success:
            print(f"Context usage report exported to {args.output}")
        else:
            print("Failed to export context usage report")
    
    elif args.command == "list":
        logs = get_all_context_logs()
        print(f"Found context logs for {len(logs)} tasks:")
        for task_id, log_data in logs.items():
            timestamp = log_data.get("timestamp", "unknown")
            topics = log_data.get("context_used", [])
            print(f"  {task_id}: {len(topics)} topics at {timestamp}")
