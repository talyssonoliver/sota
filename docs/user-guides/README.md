# User Guides

This directory contains user-friendly guides, tutorials, and examples for using the AI system effectively.

## 📁 Directory Structure

### 🎮 [Demos](./demos/)
Interactive demonstrations and example workflows
- **agent_output_demo.md** - Agent output generation examples
- **agent_summarization_demo.md** - Text summarization demonstrations  
- **register_agent_output_demo.md** - Output registration workflows
- **code_extraction_demo.md** - Code extraction and analysis examples
- **daily_cycle_demo.md** - Daily workflow cycle demonstrations
- **hitl_cli_demo.md** - Human-in-the-loop CLI examples
- **hitl_kanban_demo.md** - Kanban board integration demonstrations
- **qa_execution_demo.md** - Quality assurance workflow examples

### **Core User Documentation**
- **documentation_index.md** - Master documentation index and navigation
- **documentation_search_index.md** - Searchable documentation index
- **quick_reference_cards.md** - Quick reference cards for common operations

## 🚀 Getting Started

### **New Users**
1. **Start Here**: [documentation_index.md](./documentation_index.md) - Complete overview
2. **Quick Reference**: [quick_reference_cards.md](./quick_reference_cards.md) - Essential commands
3. **First Demo**: [demos/daily_cycle_demo.md](./demos/daily_cycle_demo.md) - Basic workflow

### **Common Workflows**
1. **Agent Management**: [demos/agent_output_demo.md](./demos/agent_output_demo.md)
2. **Task Execution**: [demos/qa_execution_demo.md](./demos/qa_execution_demo.md)  
3. **Human-in-the-Loop**: [demos/hitl_cli_demo.md](./demos/hitl_cli_demo.md)
4. **Code Processing**: [demos/code_extraction_demo.md](./demos/code_extraction_demo.md)

## 📚 User Guide Categories

### **Basic Operations**
Learn fundamental system operations and concepts

#### **Agent Management**
- Creating and configuring agents
- Agent types and specializations
- Agent communication patterns

#### **Task Management** 
- Submitting tasks to the system
- Monitoring task progress
- Retrieving task results

#### **Workflow Execution**
- Understanding workflow patterns
- Triggering workflow execution
- Monitoring workflow progress

### **Advanced Features**

#### **Human-in-the-Loop (HITL)**
- Interactive review processes
- Approval workflows
- Quality assurance integration

#### **Code Processing**
- Automated code extraction
- Code analysis and documentation
- Code quality assessment

#### **Knowledge Management**
- Context storage and retrieval
- Knowledge base curation
- Information organization

## 🎯 Quick Start Examples

### **Basic Agent Interaction**
```bash
# Create a new agent
python -c "from agents import create_agent; create_agent('backend', 'My Backend Agent')"

# Execute a simple task
python orchestration/execute_task.py --task BE-01

# Check agent status
python scripts/health_check.py --component agents
```

### **Workflow Execution**
```bash
# Start daily workflow cycle
python orchestration/daily_cycle.py --day 1 --start

# Monitor workflow progress  
python scripts/monitor_workflow.py

# Generate end-of-day report
python orchestration/daily_cycle.py --day 1 --end
```

### **Human-in-the-Loop Operations**
```bash
# Launch HITL CLI interface
python src/interfaces/cli/hitl_cli.py

# Check pending reviews
python scripts/list_pending_reviews.py

# Mark reviews complete
python scripts/mark_review_complete.py --task-id BE-07
```

## 📖 Tutorials by Use Case

### **For Project Managers**
- Sprint planning and management
- Progress tracking and reporting
- Team coordination workflows

### **For Developers**
- Code generation and analysis
- Automated testing integration
- Development workflow automation

### **For QA Engineers**
- Quality assurance workflows
- Test result analysis
- Error reporting and tracking

### **For Operations Teams**
- System monitoring and health checks
- Deployment and scaling procedures
- Performance optimization

## 🔍 Finding Information

### **Search Documentation**
Use [documentation_search_index.md](./documentation_search_index.md) to find specific topics quickly.

### **Browse by Category**
- **[API](../api/)** - API reference and integration guides
- **[Architecture](../architecture/)** - System design and patterns
- **[Development](../development/)** - Development procedures and testing
- **[Operations](../operations/)** - Deployment and operational procedures

### **Quick Reference**
Keep [quick_reference_cards.md](./quick_reference_cards.md) handy for common commands and procedures.

## 💡 Tips and Best Practices

### **Workflow Efficiency**
- Use daily cycle automation for consistent operations
- Implement HITL workflows for quality control
- Monitor system health proactively

### **Agent Configuration**
- Choose appropriate agent types for your tasks
- Configure agent context domains properly
- Monitor agent performance metrics

### **Task Management**
- Use descriptive task IDs and metadata
- Monitor task execution progress
- Review task outputs for quality

## 🆘 Getting Help

### **Documentation Navigation**
1. **Search**: Use search index for specific topics
2. **Browse**: Navigate by category for comprehensive coverage
3. **Demos**: Try interactive examples for hands-on learning

### **Common Issues**
- Check [development/troubleshooting.md](../development/troubleshooting.md) for common problems
- Review [operations/monitoring/](../operations/monitoring/) for system health
- Consult [reports/](../reports/) for system status updates

### **Community Support**
- Check existing documentation thoroughly
- Review demo examples for similar use cases
- Consult architecture documentation for design context

## 🔗 Related Resources

- **[API Documentation](../api/)** - Complete API reference
- **[Development Guides](../development/)** - Technical documentation
- **[Architecture Overview](../architecture/)** - System design principles
- **[Operational Procedures](../operations/)** - Deployment and operations

---

*For the latest features and updates, check [sprint briefings](../sprint/briefings/) and [completion reports](../reports/).*