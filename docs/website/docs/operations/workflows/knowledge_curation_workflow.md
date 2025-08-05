# Knowledge Curation Workflow

This document describes the detailed process for creating, reviewing, and validating knowledge summaries in /context-store/ from source documents in /context-source/.

## Process Overview

1. **Source Material Management**
2. **Automated Summary Generation**
3. **Domain Expert Review**
4. **Approval & Marking**
5. **Maintenance & Updates**

## 1. Source Material Management
- All original source documents are stored in the /context-source/ directory
- Documents are organized into domain-specific subdirectories:
  - /context-source/db/ - Database schemas and documentation
  - /context-source/infra/ - Infrastructure and deployment information
  - /context-source/design/ - UI/UX designs and wireframes
  - /context-source/patterns/ - Code patterns and implementation guidelines
  - /context-source/sprint/ - Sprint planning and execution documents
  - /context-source/technical/ - Technical architecture and system design
- Project Team Members must place new documentation in the appropriate /context-source/ subdirectory

## 2. Automated Summary Generation
- **Primary Responsibility**: Documentation Agent (doc_agent)
- The doc_agent processes source documents using the MemoryEngine's scan_and_summarize method:
  ```python
  from tools.memory_engine import memory
  memory.scan_and_summarize(source_dirs=["context-source/"], summary_dir="context-store/")
  ```
- Generated summaries follow domain-specific templates with consistent formats
- Each summary includes a "Reviewed: Not yet reviewed" marker at the top
- Summaries are automatically indexed into the vector store for retrieval

## 3. Domain Review
- **Primary Responsibility**: Domain Engineers (backend, frontend, technical, etc.)
- Each summary must be reviewed by the appropriate domain expert:
  - Database schemas → Backend Engineer
  - Service patterns → Backend Engineer
  - UI components → Frontend Engineer
  - Architecture decisions → Technical Lead
  - Sprint plans → Product/Project Manager
- Domain experts review for:
  - **Technical accuracy**: All technical details correctly represented
  - **Completeness**: No critical information missing
  - **Conciseness**: Information is presented efficiently
  - **Clarity**: Information is understandable to other agents

## 4. Approval
- Once validated, the domain expert updates the summary:
  - Changes "Reviewed: Not yet reviewed" to "Reviewed: [Name], [Date]" at the top of the file
  - Example: "**Reviewed: Sarah Chen (Backend Engineer), May 16, 2025**"
- The Technical Lead is notified when a significant number of summaries have been reviewed
- Reviews are tracked in a log (reviews/knowledge_review_log.csv)

## 5. Maintenance
- When source documents in /context-source/ change:
  1. The doc_agent detects the changes via timestamp or content hash
  2. The doc_agent regenerates the corresponding summary in /context-store/
  3. The "Reviewed" status is reset to "Not yet reviewed"
  4. Domain experts are notified about summaries needing review
- A monthly audit ensures all summaries remain current

## Validation Methods

### Automatic Validation
- **Keyword Extraction**: Key terms from source docs must appear in summaries
- **Coverage Analysis**: Critical sections from source must be represented
- **Length Checking**: Summaries should be 25-35% of original document length

### Manual Validation
- Domain experts perform detailed review using their specialized knowledge
- Technical accuracy is prioritized over conciseness
- Review comments are preserved in a special section at the bottom of each document

## Responsibility Matrix

| Task | Primary Responsibility | Support |
|------|------------------------|--------|
| Source document creation | Project Team | Technical Lead |
| Source document placement | Project Team | doc_agent |
| Summary generation | doc_agent | Technical Lead |
| DB/Backend summaries review | Backend Engineer | Technical Lead |
| Frontend summaries review | Frontend Engineer | UX Designer |
| Architecture summaries review | Technical Lead | Backend/Frontend Engineers |
| Sprint summaries review | Product Manager | Technical Lead |
| Maintenance scheduling | Technical Lead | doc_agent |

## Running the Knowledge Workflow

To run the automated summary generation process:

```python
# Generate summaries from all documents in context-source/
from tools.memory_engine import memory
memory.scan_and_summarize()

# Generate summaries from specific directories
memory.scan_and_summarize(source_dirs=["context-source/db/", "context-source/patterns/"])

# Generate summaries with a custom output directory
memory.scan_and_summarize(summary_dir="context-store/special/")
```

This workflow ensures that all agent-accessible knowledge is accurate, up-to-date, and validated by subject matter experts.
