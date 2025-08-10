// Enhanced Dashboard JavaScript
// Real-time dashboard functionality

const DashboardAPI = {
    // API endpoints
    endpoints: {
        taskStats: '/api/dashboard/task-stats',
        agentStatus: '/api/dashboard/agent-status',
        liveExecution: '/api/dashboard/live-execution'
    },

    // Initialize dashboard
    init: function() {
        // Prevent multiple initializations
        if (this.initialized) {
            console.log('Dashboard already initialized');
            return;
        }
        
        console.log('Initializing dashboard...');
        this.initialized = true;
        
        // Initial data load
        this.updateTaskStats();
        this.updateAgentStatus();
        
        // Start periodic updates
        this.startLiveUpdates();
    },

    // Update task statistics
    updateTaskStats: async function() {
        try {
            console.log('Fetching task stats from:', this.endpoints.taskStats);
            const response = await fetch(this.endpoints.taskStats);
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            const data = await response.json();
            console.log('Task stats response:', data);
            this.renderTaskStats(data);
        } catch (error) {
            console.error('Error fetching task stats:', error);
            // Show fallback data
            this.renderTaskStats({
                total_tasks: 0,
                completed_tasks: 0,
                in_progress_tasks: 0,
                failed_tasks: 0,
                success_rate: 0,
                error: 'Failed to load data'
            });
        }
    },

    // Update agent status
    updateAgentStatus: async function() {
        try {
            console.log('Fetching agent status from:', this.endpoints.agentStatus);
            const response = await fetch(this.endpoints.agentStatus);
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            const data = await response.json();
            console.log('Agent status response:', data);
            this.renderAgentStatus(data);
        } catch (error) {
            console.error('Error fetching agent status:', error);
            // Show fallback data
            this.renderAgentStatus({
                agents: [],
                total_agents: 0,
                active_agents: 0,
                average_efficiency: 0,
                error: 'Failed to load data'
            });
        }
    },

    // Start live updates
    startLiveUpdates: function() {
        // Clear any existing intervals first
        if (this.updateInterval) {
            clearInterval(this.updateInterval);
        }
        
        // Set up new interval - update every 5 seconds
        this.updateInterval = setInterval(() => {
            console.log('Updating dashboard data...');
            this.updateTaskStats();
            this.updateAgentStatus();
        }, 5000);
        
        console.log('Live updates started - refreshing every 5 seconds');
    },

    // Render task statistics
    renderTaskStats: function(data) {
        const container = document.getElementById('task-counts');
        container.innerHTML = `
            <div class="metric-card">
                <h3>Total Tasks</h3>
                <p>${data.total_tasks || 0}</p>
            </div>
            <div class="metric-card">
                <h3>Completed</h3>
                <p>${data.completed_tasks || 0}</p>
            </div>
            <div class="metric-card">
                <h3>In Progress</h3>
                <p>${data.in_progress_tasks || 0}</p>
            </div>
            <div class="metric-card">
                <h3>Failed</h3>
                <p>${data.failed_tasks || 0}</p>
            </div>
            <div class="metric-card">
                <h3>Success Rate</h3>
                <p>${data.success_rate ? data.success_rate.toFixed(1) : 0}%</p>
            </div>
        `;
    },

    // Render agent status
    renderAgentStatus: function(data) {
        const container = document.getElementById('agent-list');
        if (data.agents && data.agents.length > 0) {
            let html = '<div class="agents-grid">';
            data.agents.forEach(agent => {
                html += `
                    <div class="metric-card">
                        <h4>${agent.name}</h4>
                        <p>Status: <span class="status-${agent.status}">${agent.status}</span></p>
                        <p>Tasks: ${agent.tasks_completed}</p>
                        <p>Current: ${agent.current_task}</p>
                        <p>Efficiency: ${agent.efficiency.toFixed(1)}%</p>
                    </div>
                `;
            });
            html += '</div>';
            html += `
                <div class="summary">
                    <p><strong>Total Agents:</strong> ${data.total_agents}</p>
                    <p><strong>Active Agents:</strong> ${data.active_agents}</p>
                    <p><strong>Average Efficiency:</strong> ${data.average_efficiency.toFixed(1)}%</p>
                </div>
            `;
            container.innerHTML = html;
        } else {
            container.innerHTML = '<p>No agent data available</p>';
        }
    }
};

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    DashboardAPI.init();
});

// Cleanup on page unload
window.addEventListener('beforeunload', () => {
    if (DashboardAPI.updateInterval) {
        clearInterval(DashboardAPI.updateInterval);
        console.log('Dashboard intervals cleared');
    }
});