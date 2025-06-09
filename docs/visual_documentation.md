# Visual Documentation

This document outlines useful diagrams to better understand the AI Agent System.

## 1. System Flow Diagram
Describe how a request flows from the orchestrator to individual agents and back. Illustrate the involvement of the Workflow Executor and tool layer.

## 2. Agent Interaction Diagram
Visualize communication among agents. Show task assignments from the Coordinator and how outputs feed into subsequent agents.

## 3. Task State Machine
Depict task states from creation through completion: CREATED, QUEUED, ASSIGNED, IN_PROGRESS, BLOCKED, REVIEW, COMPLETED, FAILED, CANCELLED.

## 4. Tool Architecture
Show how the base tool class is extended by specialized tools and how agents request tool functionality via the Tool Loader.

## 5. Workflow Examples
Provide visual representations (e.g., Mermaid diagrams) for common workflows such as Feature Development and Bug Fix.

These diagrams can be created using Mermaid syntax or external drawing tools and embedded in the documentation as needed.
