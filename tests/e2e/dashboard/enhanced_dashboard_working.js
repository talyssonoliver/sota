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
        this.updateTaskStats();
        this.updateAgentStatus();
        this.startLiveUpdates();
    },

    // Update task statistics
    updateTaskStats: async function() {
        try {
            const response = await fetch(this.endpoints.taskStats);
            const data = await response.json();
            this.renderTaskStats(data);
        } catch (error) {
            console.error('Error fetching task stats:', error);
        }
    },

    // Update agent status
    updateAgentStatus: async function() {
        try {
            const response = await fetch(this.endpoints.agentStatus);
            const data = await response.json();
            this.renderAgentStatus(data);
        } catch (error) {
            console.error('Error fetching agent status:', error);
        }
    },

    // Start live updates
    startLiveUpdates: function() {
        setInterval(() => {
            this.updateTaskStats();
            this.updateAgentStatus();
        }, 5000);
    },

    // Render task statistics
    renderTaskStats: function(data) {
        const container = document.getElementById('task-counts');
        container.innerHTML = `
            <div class="metric-card">
                <h3>Total Tasks</h3>
                <p>${data.total || 0}</p>
            </div>
            <div class="metric-card">
                <h3>Completed</h3>
                <p>${data.completed || 0}</p>
            </div>
            <div class="metric-card">
                <h3>In Progress</h3>
                <p>${data.in_progress || 0}</p>
            </div>
        `;
    },

    // Render agent status
    renderAgentStatus: function(data) {
        const container = document.getElementById('agent-list');
        let html = '<ul>';
        for (const [agent, status] of Object.entries(data)) {
            html += `<li>${agent}: ${status}</li>`;
        }
        html += '</ul>';
        container.innerHTML = html;
    }
};

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    DashboardAPI.init();
});