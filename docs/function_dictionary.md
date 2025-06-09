# Function Dictionary

This list highlights common functions used across the project.

## B

### build_coordinator_agent(task_metadata: Dict = None, **kwargs)
- **Module:** `agents/coordinator.py`
- **Purpose:** Construct the CoordinatorAgent with provided metadata.

### build_doc_agent(task_metadata: Dict = None, **kwargs)
- **Module:** `agents/doc.py`
- **Purpose:** Create a DocumentationAgent instance.

### build_qa_agent(task_metadata: Dict = None, **kwargs)
- **Module:** `agents/qa.py`
- **Purpose:** Create a QAAgent with optional task metadata.

## C

### create_documentation_agent()
- **Module:** `agents/doc.py`
- **Purpose:** Convenience function to return a default documentation agent.

### create_enhanced_qa_workflow()
- **Module:** `agents/qa.py`
- **Purpose:** Build a specialized QA workflow.

## G

### get_doc_context(task_id: str = None) -> list
- **Module:** `agents/doc.py`
- **Purpose:** Retrieve context documents for the documentation agent.

### get_coordinator_context(task_id: str = None) -> list
- **Module:** `agents/coordinator.py`
- **Purpose:** Fetch coordinator-specific context documents.

