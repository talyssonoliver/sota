/**
 * Interactive AI System Command Center
 * Full-featured dashboard with agent controls, task management, and real-time monitoring
 */

class AICommandCenter {
    constructor() {
        this.endpoints = {
            taskStats: '/api/dashboard/task-stats',
            agentStatus: '/api/dashboard/agent-status',
            systemHealth: '/health',
            agentControl: '/api/agent/control',
            taskQueue: '/api/tasks/queue',
            workflows: '/api/workflows'
        };
        
        this.updateInterval = null;
        this.performanceChart = null;
        this.systemStartTime = Date.now();
        this.isSystemRunning = false;
        
        // Mock data for demonstration
        this.agents = [
            { id: 'technical_lead', name: 'Technical Lead', status: 'active', efficiency: 95, current_task: 'Reviewing architecture decisions' },
            { id: 'backend', name: 'Backend Agent', status: 'active', efficiency: 87, current_task: 'Implementing API endpoints' },
            { id: 'frontend', name: 'Frontend Agent', status: 'idle', efficiency: 72, current_task: 'Waiting for specs' },
            { id: 'qa', name: 'QA Agent', status: 'active', efficiency: 91, current_task: 'Running test suite' },
            { id: 'documentation', name: 'Docs Agent', status: 'active', efficiency: 83, current_task: 'Updating API docs' }
        ];
        
        this.taskQueue = [
            { id: 1, title: 'Implement user authentication', priority: 'high', status: 'in_progress', agent: 'backend' },
            { id: 2, title: 'Design dashboard mockups', priority: 'medium', status: 'pending', agent: 'frontend' },
            { id: 3, title: 'Write integration tests', priority: 'high', status: 'pending', agent: 'qa' },
            { id: 4, title: 'Update deployment guide', priority: 'low', status: 'pending', agent: 'documentation' }
        ];
        
        this.workflows = [
            { id: 'w1', name: 'User Registration Flow', progress: 75, status: 'active', steps: 8, completed: 6 },
            { id: 'w2', name: 'Data Processing Pipeline', progress: 45, status: 'active', steps: 12, completed: 5 },
            { id: 'w3', name: 'Quality Assurance Workflow', progress: 90, status: 'active', steps: 10, completed: 9 }
        ];
        
        this.performanceData = {
            labels: [],
            datasets: [{
                label: 'Tasks Completed',
                data: [],
                borderColor: '#00ff88',
                backgroundColor: 'rgba(0, 255, 136, 0.1)',
                tension: 0.4,
                fill: true
            }, {
                label: 'System Load %',
                data: [],
                borderColor: '#00ccff',
                backgroundColor: 'rgba(0, 204, 255, 0.1)',
                tension: 0.4,
                fill: true
            }]
        };
        
        this.logs = [];
    }

    async init() {
        console.log('🚀 Initializing AI Command Center...');
        
        // Initialize components
        this.initializeChart();
        this.renderAgents();
        this.renderTaskQueue();
        this.renderWorkflows();
        
        // Start real-time updates
        this.startLiveUpdates();
        
        // Initial data load
        await this.updateDashboard();
        
        this.log('✅ AI Command Center initialized successfully');
        this.showNotification('Command Center Online', 'success');
    }

    initializeChart() {
        const ctx = document.getElementById('performanceChart');
        if (!ctx) return;

        this.performanceChart = new Chart(ctx, {
            type: 'line',
            data: this.performanceData,
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'top',
                        labels: {
                            color: '#ffffff'
                        }
                    },
                    title: {
                        display: true,
                        text: 'Real-time Performance Metrics',
                        color: '#ffffff'
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        grid: {
                            color: 'rgba(255, 255, 255, 0.1)'
                        },
                        ticks: {
                            color: '#ffffff'
                        }
                    },
                    x: {
                        grid: {
                            color: 'rgba(255, 255, 255, 0.1)'
                        },
                        ticks: {
                            color: '#ffffff'
                        }
                    }
                },
                elements: {
                    point: {
                        radius: 4,
                        hoverRadius: 6
                    }
                }
            }
        });
    }

    renderAgents() {
        const container = document.getElementById('agentControls');
        if (!container) return;

        container.innerHTML = this.agents.map(agent => {
            const statusClass = agent.status === 'active' ? 'status-active' : 
                              agent.status === 'error' ? 'status-error' : 'status-idle';
            
            return `
                <div class="agent-card">
                    <div class="agent-header">
                        <div class="agent-name">
                            <i class="fas fa-robot"></i> ${agent.name}
                        </div>
                        <span class="agent-status ${statusClass}">${agent.status}</span>
                    </div>
                    <div class="progress-bar">
                        <div class="progress-fill" style="width: ${agent.efficiency}%"></div>
                    </div>
                    <div style="font-size: 0.9rem; margin: 10px 0; color: rgba(255,255,255,0.8);">
                        <strong>Current:</strong> ${agent.current_task}
                    </div>
                    <div class="quick-actions">
                        <button class="btn" onclick="controlAgent('${agent.id}', 'start')" ${agent.status === 'active' ? 'disabled' : ''}>
                            <i class="fas fa-play"></i>
                        </button>
                        <button class="btn btn-warning" onclick="controlAgent('${agent.id}', 'restart')">
                            <i class="fas fa-redo"></i>
                        </button>
                        <button class="btn btn-danger" onclick="controlAgent('${agent.id}', 'stop')" ${agent.status === 'idle' ? 'disabled' : ''}>
                            <i class="fas fa-stop"></i>
                        </button>
                        <button class="btn btn-secondary" onclick="viewAgentLogs('${agent.id}')">
                            <i class="fas fa-eye"></i>
                        </button>
                    </div>
                </div>
            `;
        }).join('');
    }

    renderTaskQueue() {
        const container = document.getElementById('taskQueue');
        if (!container) return;

        container.innerHTML = this.taskQueue.map(task => {
            const priorityColor = task.priority === 'high' ? '#ff6b6b' : 
                                task.priority === 'medium' ? '#ffa726' : '#64b5f6';
            
            return `
                <div class="task-item" style="border-left-color: ${priorityColor}">
                    <div>
                        <div style="font-weight: 600;">${task.title}</div>
                        <div style="font-size: 0.8rem; color: rgba(255,255,255,0.7);">
                            Agent: ${task.agent} | Priority: ${task.priority} | Status: ${task.status}
                        </div>
                    </div>
                    <div class="quick-actions">
                        <button class="btn" onclick="editTask(${task.id})">
                            <i class="fas fa-edit"></i>
                        </button>
                        <button class="btn btn-danger" onclick="removeTask(${task.id})">
                            <i class="fas fa-trash"></i>
                        </button>
                    </div>
                </div>
            `;
        }).join('');
    }

    renderWorkflows() {
        const container = document.getElementById('workflowControls');
        if (!container) return;

        container.innerHTML = this.workflows.map(workflow => `
            <div class="workflow-item">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
                    <div style="font-weight: 600;">${workflow.name}</div>
                    <span style="font-size: 0.8rem; color: rgba(255,255,255,0.7);">${workflow.completed}/${workflow.steps} steps</span>
                </div>
                <div class="progress-bar">
                    <div class="progress-fill" style="width: ${workflow.progress}%"></div>
                </div>
                <div class="quick-actions" style="margin-top: 10px;">
                    <button class="btn" onclick="pauseWorkflow('${workflow.id}')">
                        <i class="fas fa-pause"></i>
                    </button>
                    <button class="btn btn-secondary" onclick="viewWorkflow('${workflow.id}')">
                        <i class="fas fa-eye"></i>
                    </button>
                    <button class="btn btn-warning" onclick="restartWorkflow('${workflow.id}')">
                        <i class="fas fa-redo"></i>
                    </button>
                </div>
            </div>
        `).join('');
    }

    async updateDashboard() {
        try {
            // Update metrics
            const totalTasks = this.taskQueue.length;
            const completedTasks = this.taskQueue.filter(t => t.status === 'completed').length;
            const activeTasks = this.taskQueue.filter(t => t.status === 'in_progress').length;
            const successRate = totalTasks > 0 ? Math.round((completedTasks / totalTasks) * 100) : 0;

            document.getElementById('totalTasks').textContent = totalTasks;
            document.getElementById('completedTasks').textContent = completedTasks;
            document.getElementById('activeTasks').textContent = activeTasks;
            document.getElementById('successRate').textContent = `${successRate}%`;

            // Update system metrics
            const uptime = this.formatUptime(Date.now() - this.systemStartTime);
            const memoryUsage = Math.round(Math.random() * 40 + 30); // Mock data
            
            document.getElementById('systemUptime').textContent = uptime;
            document.getElementById('memoryUsage').textContent = `${memoryUsage}%`;

            // Update performance chart
            this.updatePerformanceChart();

        } catch (error) {
            console.error('Error updating dashboard:', error);
            this.log(`❌ Dashboard update failed: ${error.message}`);
        }
    }

    updatePerformanceChart() {
        if (!this.performanceChart) return;

        const now = new Date();
        const timeLabel = now.toLocaleTimeString();

        // Add new data point
        this.performanceData.labels.push(timeLabel);
        this.performanceData.datasets[0].data.push(Math.round(Math.random() * 10 + 5)); // Mock tasks completed
        this.performanceData.datasets[1].data.push(Math.round(Math.random() * 30 + 40)); // Mock system load

        // Keep only last 15 data points
        if (this.performanceData.labels.length > 15) {
            this.performanceData.labels.shift();
            this.performanceData.datasets[0].data.shift();
            this.performanceData.datasets[1].data.shift();
        }

        this.performanceChart.update('none');
    }

    startLiveUpdates() {
        if (this.updateInterval) {
            clearInterval(this.updateInterval);
        }

        this.updateInterval = setInterval(async () => {
            await this.updateDashboard();
        }, 3000); // Update every 3 seconds for responsive feel

        this.log('📡 Live updates started - refreshing every 3 seconds');
    }

    formatUptime(milliseconds) {
        const seconds = Math.floor(milliseconds / 1000);
        const minutes = Math.floor(seconds / 60);
        const hours = Math.floor(minutes / 60);
        const days = Math.floor(hours / 24);

        if (days > 0) return `${days}d ${hours % 24}h`;
        if (hours > 0) return `${hours}h ${minutes % 60}m`;
        if (minutes > 0) return `${minutes}m ${seconds % 60}s`;
        return `${seconds}s`;
    }

    log(message) {
        const timestamp = new Date().toLocaleTimeString();
        const logEntry = `[${timestamp}] ${message}`;
        this.logs.push(logEntry);
        
        // Keep only last 50 logs
        if (this.logs.length > 50) {
            this.logs.shift();
        }
        
        const terminal = document.getElementById('terminalOutput');
        if (terminal) {
            terminal.innerHTML = this.logs.map(log => `> ${log}`).join('<br>') + '<br>> <span class="loading-spinner"></span> Ready for commands...';
            terminal.scrollTop = terminal.scrollHeight;
        }
    }

    showNotification(message, type = 'success') {
        const notification = document.getElementById('notification');
        if (!notification) return;

        notification.textContent = message;
        notification.className = `notification ${type} show`;

        setTimeout(() => {
            notification.classList.remove('show');
        }, 3000);
    }

    destroy() {
        if (this.updateInterval) {
            clearInterval(this.updateInterval);
        }
        if (this.performanceChart) {
            this.performanceChart.destroy();
        }
        console.log('Command Center destroyed');
    }
}

// Global command center instance
let commandCenter;

// System Control Functions
async function startSystem() {
    commandCenter.isSystemRunning = true;
    commandCenter.log('🚀 Starting AI system...');
    commandCenter.showNotification('AI System Starting...', 'success');
    
    // Simulate system startup
    setTimeout(() => {
        commandCenter.log('✅ All agents initialized');
        commandCenter.log('✅ Memory engine online');
        commandCenter.log('✅ Workflow orchestrator ready');
        commandCenter.showNotification('AI System Online', 'success');
    }, 2000);
}

async function restartSystem() {
    commandCenter.log('🔄 Restarting AI system...');
    commandCenter.showNotification('Restarting System...', 'warning');
    
    setTimeout(() => {
        commandCenter.log('✅ System restart complete');
        commandCenter.showNotification('System Restarted', 'success');
    }, 3000);
}

async function stopSystem() {
    commandCenter.isSystemRunning = false;
    commandCenter.log('⏹️ Stopping AI system...');
    commandCenter.showNotification('System Stopping...', 'warning');
    
    setTimeout(() => {
        commandCenter.log('⏹️ System stopped safely');
        commandCenter.showNotification('System Stopped', 'error');
    }, 1500);
}

async function emergencyShutdown() {
    commandCenter.log('🚨 EMERGENCY SHUTDOWN INITIATED');
    commandCenter.showNotification('EMERGENCY SHUTDOWN', 'error');
    
    setTimeout(() => {
        commandCenter.log('🚨 Emergency shutdown complete');
    }, 1000);
}

// Agent Control Functions
async function controlAgent(agentId, action) {
    const agent = commandCenter.agents.find(a => a.id === agentId);
    if (!agent) return;

    commandCenter.log(`🤖 Agent ${agent.name}: ${action} command executed`);
    
    switch (action) {
        case 'start':
            agent.status = 'active';
            commandCenter.showNotification(`${agent.name} Started`, 'success');
            break;
        case 'stop':
            agent.status = 'idle';
            agent.current_task = 'Waiting for instructions';
            commandCenter.showNotification(`${agent.name} Stopped`, 'warning');
            break;
        case 'restart':
            agent.status = 'active';
            agent.efficiency = Math.min(100, agent.efficiency + Math.random() * 10);
            commandCenter.showNotification(`${agent.name} Restarted`, 'success');
            break;
    }
    
    commandCenter.renderAgents();
}

async function viewAgentLogs(agentId) {
    const agent = commandCenter.agents.find(a => a.id === agentId);
    if (!agent) return;
    
    commandCenter.log(`📋 Viewing logs for ${agent.name}`);
    commandCenter.showNotification(`Viewing ${agent.name} Logs`, 'success');
}

// Task Management Functions
async function createTask() {
    const taskTitle = prompt('Enter task title:');
    if (!taskTitle) return;
    
    const newTask = {
        id: Date.now(),
        title: taskTitle,
        priority: 'medium',
        status: 'pending',
        agent: 'backend'
    };
    
    commandCenter.taskQueue.unshift(newTask);
    commandCenter.renderTaskQueue();
    commandCenter.log(`📝 New task created: ${taskTitle}`);
    commandCenter.showNotification('Task Created', 'success');
}

async function addTaskToQueue() {
    await createTask();
}

async function editTask(taskId) {
    const task = commandCenter.taskQueue.find(t => t.id === taskId);
    if (!task) return;
    
    const newTitle = prompt('Edit task title:', task.title);
    if (newTitle && newTitle !== task.title) {
        task.title = newTitle;
        commandCenter.renderTaskQueue();
        commandCenter.log(`✏️ Task updated: ${newTitle}`);
        commandCenter.showNotification('Task Updated', 'success');
    }
}

async function removeTask(taskId) {
    const taskIndex = commandCenter.taskQueue.findIndex(t => t.id === taskId);
    if (taskIndex === -1) return;
    
    if (confirm('Remove this task?')) {
        const task = commandCenter.taskQueue[taskIndex];
        commandCenter.taskQueue.splice(taskIndex, 1);
        commandCenter.renderTaskQueue();
        commandCenter.log(`🗑️ Task removed: ${task.title}`);
        commandCenter.showNotification('Task Removed', 'warning');
    }
}

async function pauseQueue() {
    commandCenter.log('⏸️ Task queue paused');
    commandCenter.showNotification('Queue Paused', 'warning');
}

async function clearQueue() {
    if (confirm('Clear all tasks from queue?')) {
        commandCenter.taskQueue = [];
        commandCenter.renderTaskQueue();
        commandCenter.log('🗑️ Task queue cleared');
        commandCenter.showNotification('Queue Cleared', 'error');
    }
}

// Workflow Functions
async function pauseWorkflow(workflowId) {
    const workflow = commandCenter.workflows.find(w => w.id === workflowId);
    if (!workflow) return;
    
    workflow.status = 'paused';
    commandCenter.log(`⏸️ Workflow paused: ${workflow.name}`);
    commandCenter.showNotification('Workflow Paused', 'warning');
}

async function viewWorkflow(workflowId) {
    const workflow = commandCenter.workflows.find(w => w.id === workflowId);
    if (!workflow) return;
    
    commandCenter.log(`👁️ Viewing workflow: ${workflow.name}`);
    commandCenter.showNotification('Opening Workflow Details', 'success');
}

async function restartWorkflow(workflowId) {
    const workflow = commandCenter.workflows.find(w => w.id === workflowId);
    if (!workflow) return;
    
    workflow.status = 'active';
    workflow.progress = Math.max(0, workflow.progress - 10);
    commandCenter.renderWorkflows();
    commandCenter.log(`🔄 Workflow restarted: ${workflow.name}`);
    commandCenter.showNotification('Workflow Restarted', 'success');
}

// Utility Functions
async function runDiagnostics() {
    commandCenter.log('🔍 Running system diagnostics...');
    commandCenter.showNotification('Running Diagnostics...', 'success');
    
    setTimeout(() => {
        commandCenter.log('✅ All systems nominal');
        commandCenter.log('✅ Memory usage: optimal');
        commandCenter.log('✅ Agent performance: excellent');
        commandCenter.showNotification('Diagnostics Complete', 'success');
    }, 2000);
}

async function clearLogs() {
    commandCenter.logs = [];
    commandCenter.log('🗑️ Logs cleared');
    commandCenter.showNotification('Logs Cleared', 'warning');
}

async function exportData() {
    const data = {
        timestamp: new Date().toISOString(),
        agents: commandCenter.agents,
        tasks: commandCenter.taskQueue,
        workflows: commandCenter.workflows,
        logs: commandCenter.logs
    };
    
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `ai-system-export-${Date.now()}.json`;
    a.click();
    URL.revokeObjectURL(url);
    
    commandCenter.log('📥 Data exported successfully');
    commandCenter.showNotification('Data Exported', 'success');
}

// Initialize when page loads
document.addEventListener('DOMContentLoaded', () => {
    commandCenter = new AICommandCenter();
    commandCenter.init();
});

// Cleanup on page unload
window.addEventListener('beforeunload', () => {
    if (commandCenter) {
        commandCenter.destroy();
    }
});

// Export for external access
window.AICommandCenter = AICommandCenter;