# /agent-status - Check AI Agent System Status

Get comprehensive status of all AI agents and system components.

## Steps:

1. **Memory Engine Status**
   ```bash
   echo "🧠 Memory Engine Status:"
   PYTHONPATH=. python -c "
   try:
       from src.infrastructure.memory.engines.memory_engine import MemoryEngine
       engine = MemoryEngine()
       print('✅ Memory Engine: Active')
       print(f'   Storage tiers: {engine.config.storage_tiers if hasattr(engine, \"config\") else \"Standard\"}')
       print(f'   Security: {\"Enabled\" if hasattr(engine, \"encryption\") else \"Basic\"}')
   except Exception as e:
       print(f'❌ Memory Engine: Failed - {e}')
   "
   ```

2. **Agent Factory Status**
   ```bash
   echo "🤖 Agent Factory Status:"
   PYTHONPATH=. python -c "
   try:
       from src.core.agents.factory import create_backend_agent, create_coordinator_agent
       print('✅ Agent Factory: Active')
       
       # Test agent creation
       backend = create_backend_agent([])
       print('✅ Backend Agent: Available')
       
       coordinator = create_coordinator_agent()
       print('✅ Coordinator Agent: Available')
       
   except Exception as e:
       print(f'❌ Agent Factory: Failed - {e}')
   "
   ```

3. **Workflow Engine Status**
   ```bash
   echo "🔄 Workflow Engine Status:"
   PYTHONPATH=. python -c "
   try:
       from src.core.workflows.execute_workflow import execute_workflow
       from src.core.workflows.registry import get_registry
       print('✅ Workflow Engine: Active')
       
       registry = get_registry()
       print(f'✅ Registry: Active with {len(registry._agents) if hasattr(registry, \"_agents\") else \"N/A\"} agents')
       
   except Exception as e:
       print(f'❌ Workflow Engine: Failed - {e}')
   "
   ```

4. **Tool System Status**
   ```bash
   echo "🛠️ Tool System Status:"
   TOOLS_COUNT=$(find src/infrastructure/tools/ -name "*.py" -type f | wc -l)
   echo "✅ Tools Available: $TOOLS_COUNT"
   
   echo "📁 Tool Categories:"
   for category in core external frontend development documentation; do
       if [ -d "src/infrastructure/tools/$category" ]; then
           COUNT=$(find "src/infrastructure/tools/$category" -name "*.py" -type f | wc -l)
           echo "   $category: $COUNT tools"
       fi
   done
   ```

5. **Configuration Status**
   ```bash
   echo "⚙️ Configuration Status:"
   if [ -f "config/agents.yaml" ]; then
       echo "✅ Agent Config: Present"
   else
       echo "❌ Agent Config: Missing"
   fi
   
   if [ -f "config/tools.yaml" ]; then
       echo "✅ Tool Config: Present"
   else
       echo "❌ Tool Config: Missing"
   fi
   
   if [ -f "CLAUDE.md" ]; then
       echo "✅ Project Config: Present"
   else
       echo "❌ Project Config: Missing"
   fi
   ```

6. **Task System Status**
   ```bash
   echo "📋 Task System Status:"
   TASK_COUNT=$(find src/core/tasks/ -name "*.yaml" -type f | wc -l)
   echo "✅ Tasks Available: $TASK_COUNT"
   
   echo "📊 Task Categories:"
   for prefix in BE FE TL QA PM UX; do
       COUNT=$(find src/core/tasks/ -name "${prefix}-*.yaml" -type f | wc -l)
       if [ $COUNT -gt 0 ]; then
           echo "   $prefix: $COUNT tasks"
       fi
   done
   ```

7. **System Health Summary**
   ```bash
   echo "🏥 System Health Summary:"
   echo "================================="
   echo "Status check completed at: $(date)"
   echo "Project root: $(pwd)"
   echo "Python path: $PYTHONPATH"
   echo "Git branch: $(git branch --show-current 2>/dev/null || echo 'N/A')"
   echo "Last commit: $(git log -1 --oneline 2>/dev/null || echo 'N/A')"
   ```