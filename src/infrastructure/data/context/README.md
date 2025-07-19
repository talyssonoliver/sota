# Context Source Document Index

This directory contains all original raw knowledge documents for the Artesanato E-commerce project, organized by domain. These source documents serve as the foundation for generating curated knowledge summaries in the context-store directory.

## Directory Structure

- `/db/` - Database schemas and documentation
  - `schema.md` - Comprehensive database schema for the Artesanato E-commerce platform
  - `schema.sql` - SQL implementation of the database schema

- `/patterns/` - Code patterns and implementation guidelines
  - `api-route-integration.md` - Guide for integrating service functions with Next.js API routes
  - `error-handling-pattern.md` - Standard error handling approach for services
  - `service-layer-pattern.md` - Service layer pattern for backend interactions

- `/sprint/` - Sprint planning and execution documents
  - `pre_sprint0_tasks.md` - Detailed pre-sprint 0 tasks plan with roles and timelines
  - `sprint0_checklist.md` - Comprehensive checklist for Sprint 0 prerequisites

- `/technical/` - Technical architecture and system design
  - `knowledge_curation_workflow.md` - Process for creating and validating knowledge summaries
  - `system_architecture.md` - High-level overview of the AI Agent System architecture

- `/design/` - UI/UX designs and wireframes
  *No documents currently available*

- `/infra/` - Infrastructure and deployment information
  *No documents currently available*

## Usage

These raw documents serve as the source material for the knowledge curation process:

1. All original documentation should be added to the appropriate subdirectory here
2. The Documentation Agent processes these documents to create summaries in context-store/
3. Domain experts review the generated summaries for accuracy
4. Approved summaries are used by the AI agent system for context-aware tasks

For more details on the knowledge curation process, see [knowledge_curation_workflow.md](technical/knowledge_curation_workflow.md).