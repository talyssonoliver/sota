# Agent Architecture

Individual agent specifications and implementation details for the AI Agent System.

## 🤖 Core Development Agents

- **[Backend Agent](./backend_agent.md)** - Server-side development and API implementation
- **[Frontend Agent](./frontend_agent.md)** - User interface and client-side development
- **[QA Agent](./qa_agent.md)** - Quality assurance, testing, and validation
- **[Documentation Agent](./documentation_agent.md)** - Technical documentation and guides

## 🧠 Coordination Agents

- **[Coordinator Agent](./coordinator_agent.md)** - Task orchestration and workflow management
- **[Technical Lead Agent](./technical_lead_agent.md)** - Architecture decisions and technical leadership

## 👥 Human Interface Agents

- **[Human Agents](./human_agents.md)** - Human-in-the-loop integration and collaboration

## 🏗️ Agent Infrastructure

- **[Agent Factory](./factory.md)** - Agent creation and lifecycle management
- **[Agent Builder](./agent_builder.md)** - Base agent construction patterns
- **[Agent Factory Refactoring](./agent_factory_refactoring_summary.md)** - Factory improvements and optimizations

## 📋 Agent Specializations

### **Backend Development**
- **[Backend Implementation](./backend.md)** - Backend agent technical details
- **Focus**: API development, database design, performance optimization
- **Tools**: Supabase, GitHub, testing frameworks

### **Frontend Development**
- **[Frontend Implementation](./frontend.md)** - Frontend agent technical details
- **Focus**: UI development, component design, user experience
- **Tools**: Design system, Tailwind, Cypress testing

### **Quality Assurance**
- **[QA Implementation](./qa.md)** - QA agent technical details
- **Focus**: Test automation, quality validation, bug detection
- **Tools**: Jest, Cypress, coverage analysis

### **Documentation**
- **[Documentation Implementation](./doc.md)** - Documentation agent technical details
- **Focus**: Technical documentation, API documentation, guides
- **Tools**: Markdown processing, symbol extraction

### **Technical Leadership**
- **[Technical Implementation](./technical.md)** - Technical lead agent details
- **Focus**: Architecture decisions, technology choices, integration design
- **Authority**: System design, tech stack, patterns

### **Coordination**
- **[Coordinator Implementation](./coordinator.md)** - Coordinator agent details
- **Focus**: Task planning, resource allocation, progress tracking
- **Authority**: Task assignment, priority, scheduling

## 🔄 Agent Communication

All agents follow the unified communication protocol:

```python
@dataclass
class AgentMessage:
    sender: str                    # Source agent identifier
    recipient: str                 # Target agent identifier
    message_type: MessageType      # Task, completion, review, etc.
    payload: Dict[str, Any]        # Message content
    timestamp: datetime            # Message timestamp
    correlation_id: str            # Request correlation
    security_context: SecurityContext  # Access control
```

## 🎯 Agent Capabilities Matrix

| Agent | Primary Skills | Tools | Context Domains |
|-------|---------------|-------|-----------------|
| **Backend** | API development, Database design, Performance | Supabase, GitHub, Testing | API, Database, Performance |
| **Frontend** | UI development, Component design, UX | Design System, Tailwind, Cypress | UI, Components, Styling |
| **QA** | Test automation, Quality validation, Bug detection | Jest, Cypress, Coverage | Testing, Quality, Validation |
| **Documentation** | Technical docs, API docs, Guides | Markdown, Symbol extraction | Documentation, APIs |
| **Technical Lead** | Architecture, Technology choices, Integration | System design tools | Architecture, Patterns |
| **Coordinator** | Task planning, Resource allocation, Tracking | Orchestration tools | Planning, Coordination |

## Navigation

- **[Architecture Overview](../)** - Main architecture documentation
- **[System Overview](../system-overview.md)** - Complete system architecture
- **[Tools System](../tools_system.md)** - Tool integration framework