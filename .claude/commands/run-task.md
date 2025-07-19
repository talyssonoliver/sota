# /run-task - Execute AI System Task

Execute a specific task using the AI system's task orchestration engine.

## Usage:
`/run-task <TASK_ID>` where TASK_ID is like BE-01, FE-02, TL-03, etc.

## Steps:

1. **Validate Task ID**
   ```bash
   TASK_ID="$1"
   if [ -z "$TASK_ID" ]; then
       echo "❌ Error: Please provide a task ID (e.g., BE-01, FE-02, TL-03)"
       exit 1
   fi
   
   if [ ! -f "src/core/tasks/${TASK_ID}.yaml" ]; then
       echo "❌ Error: Task file src/core/tasks/${TASK_ID}.yaml not found"
       echo "Available tasks:"
       ls src/core/tasks/*.yaml | head -10
       exit 1
   fi
   
   echo "📋 Executing task: $TASK_ID"
   ```

2. **Show Task Details**
   ```bash
   echo "📄 Task details:"
   cat src/core/tasks/${TASK_ID}.yaml
   ```

3. **Execute Task**
   ```bash
   echo "🚀 Starting task execution..."
   PYTHONPATH=. python -c "
   from src.core.workflows.execute_task import execute_task_workflow
   import sys
   
   task_id = '${TASK_ID}'
   print(f'Executing task: {task_id}')
   
   try:
       result = execute_task_workflow(task_id)
       print(f'✅ Task {task_id} completed successfully')
       print(f'Result: {result}')
   except Exception as e:
       print(f'❌ Task {task_id} failed: {e}')
       sys.exit(1)
   "
   ```

4. **Check Output**
   ```bash
   echo "📁 Checking outputs..."
   OUTPUT_DIR="outputs/${TASK_ID}"
   if [ -d "$OUTPUT_DIR" ]; then
       echo "✅ Output directory created:"
       ls -la "$OUTPUT_DIR"
   else
       echo "⚠️ No output directory found"
   fi
   ```

5. **Log Results**
   ```bash
   echo "📝 Task execution completed at $(date)"
   echo "Task: $TASK_ID" >> logs/task_execution.log
   echo "Status: $(date)" >> logs/task_execution.log
   ```

## Examples:
- `/run-task BE-01` - Execute backend task 1
- `/run-task FE-02` - Execute frontend task 2
- `/run-task TL-03` - Execute technical lead task 3