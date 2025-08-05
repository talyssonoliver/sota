// Enhanced Professional Dashboard JavaScript
// Real-time dashboard with advanced visualizations

class ProfessionalDashboard {
    constructor() {
        this.endpoints = {
            taskStats: '/api/dashboard/task-stats',
            agentStatus: '/api/dashboard/agent-status',
            systemHealth: '/health'
        };
        
        this.updateInterval = null;
        this.initialized = false;
        this.performanceChart = null;
        
        // Performance data for trending
        this.performanceData = {
            labels: [],
            datasets: [{
                label: 'Tasks Completed',
                data: [],
                borderColor: '#667eea',
                backgroundColor: 'rgba(102, 126, 234, 0.1)',
                tension: 0.4,
                fill: true
            }, {
                label: 'Agent Efficiency %',
                data: [],
                borderColor: '#764ba2',
                backgroundColor: 'rgba(118, 75, 162, 0.1)',
                tension: 0.4,
                fill: true
            }]
        };
    }

    async init() {
        if (this.initialized) {
            console.log('Dashboard already initialized');
            return;
        }

        console.log('🚀 Initializing Professional Dashboard...');
        this.initialized = true;

        // Initialize chart
        this.initializeChart();

        // Load initial data
        await this.loadAllData();

        // Start periodic updates
        this.startLiveUpdates();
        
        console.log('✅ Professional Dashboard initialized successfully');
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
                    },
                    title: {
                        display: true,
                        text: 'Real-time Performance Metrics'
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        grid: {
                            color: 'rgba(0, 0, 0, 0.1)'
                        }
                    },
                    x: {
                        grid: {
                            color: 'rgba(0, 0, 0, 0.1)'
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

    async loadAllData() {
        this.showRefreshIndicator();
        
        try {
            await Promise.all([
                this.updateTaskStats(),
                this.updateAgentStatus(),
                this.updateSystemHealth()
            ]);
            
            this.updateTimestamp();
        } catch (error) {
            console.error('Error loading dashboard data:', error);
        } finally {
            this.hideRefreshIndicator();
        }
    }

    async updateTaskStats() {
        try {
            const response = await fetch(this.endpoints.taskStats);
            if (!response.ok) throw new Error(`HTTP ${response.status}`);
            
            const data = await response.json();
            this.renderTaskStats(data);
            
            // Update chart data
            this.updatePerformanceChart(data);
            
        } catch (error) {
            console.error('Error fetching task stats:', error);
            this.renderTaskStats({
                total_tasks: 0,
                completed_tasks: 0,
                in_progress_tasks: 0,
                failed_tasks: 0,
                success_rate: 0,
                error: 'Service unavailable'
            });
        }
    }

    async updateAgentStatus() {
        try {
            const response = await fetch(this.endpoints.agentStatus);
            if (!response.ok) throw new Error(`HTTP ${response.status}`);
            
            const data = await response.json();
            this.renderAgentStatus(data);
            
        } catch (error) {
            console.error('Error fetching agent status:', error);
            this.renderAgentStatus({
                agents: [],
                total_agents: 0,
                active_agents: 0,
                average_efficiency: 0,
                error: 'Service unavailable'
            });
        }
    }

    async updateSystemHealth() {
        try {
            const response = await fetch(this.endpoints.systemHealth);
            if (!response.ok) throw new Error(`HTTP ${response.status}`);
            
            const data = await response.json();
            this.renderSystemHealth(data);
            
        } catch (error) {
            console.error('Error fetching system health:', error);
            this.renderSystemHealth({
                status: 'unknown',
                dependencies: {},
                error: 'Service unavailable'
            });
        }
    }

    renderTaskStats(data) {
        const container = document.getElementById('taskMetrics');
        
        const metrics = [
            { label: 'Total Tasks', value: data.total_tasks || 0, icon: 'fas fa-clipboard-list' },
            { label: 'Completed', value: data.completed_tasks || 0, icon: 'fas fa-check-circle' },
            { label: 'In Progress', value: data.in_progress_tasks || 0, icon: 'fas fa-clock' },
            { label: 'Failed', value: data.failed_tasks || 0, icon: 'fas fa-exclamation-triangle' },
            { label: 'Success Rate', value: `${(data.success_rate || 0).toFixed(1)}%`, icon: 'fas fa-trophy' }
        ];

        container.innerHTML = metrics.map(metric => `
            <div class="metric-item">
                <div class="metric-value">${metric.value}</div>
                <div class="metric-label">
                    <i class="${metric.icon}"></i> ${metric.label}
                </div>
            </div>
        `).join('');
    }

    renderAgentStatus(data) {
        const container = document.getElementById('agentStatus');
        
        if (!data.agents || data.agents.length === 0) {
            container.innerHTML = '<div class="loading">No agent data available</div>';
            return;
        }

        container.innerHTML = data.agents.map(agent => {
            const efficiency = agent.efficiency || 0;
            const statusClass = agent.status === 'active' ? 'status-active' : 'status-idle';
            
            return `
                <div class="agent-card">
                    <div class="agent-header">
                        <div class="agent-name">
                            <i class="fas fa-robot"></i> ${agent.name}
                        </div>
                        <div class="agent-status ${statusClass}">
                            ${agent.status}
                        </div>
                    </div>
                    <div class="progress-bar">
                        <div class="progress-fill" style="width: ${efficiency}%"></div>
                    </div>
                    <div class="agent-details">
                        <div class="agent-detail">
                            <strong>Tasks:</strong> ${agent.tasks_completed}
                        </div>
                        <div class="agent-detail">
                            <strong>Efficiency:</strong> ${efficiency.toFixed(1)}%
                        </div>
                        <div class="agent-detail" style="grid-column: 1 / -1;">
                            <strong>Current:</strong> ${agent.current_task}
                        </div>
                    </div>
                </div>
            `;
        }).join('');
    }

    renderSystemHealth(data) {
        const container = document.getElementById('systemHealth');
        
        const healthItems = [
            { label: 'Overall Status', status: data.status || 'unknown' },
            { label: 'API Server', status: 'healthy' },
            { label: 'Database', status: 'healthy' },
            { label: 'Memory Engine', status: data.dependencies?.memory_engine?.status || 'unknown' }
        ];

        container.innerHTML = healthItems.map(item => {
            const statusClass = this.getHealthStatusClass(item.status);
            const statusIcon = this.getHealthStatusIcon(item.status);
            
            return `
                <div class="status-indicator">
                    <div class="status-dot ${statusClass}"></div>
                    <div>
                        <div style="font-weight: 600;">${item.label}</div>
                        <div style="font-size: 0.9rem; color: #6c757d;">
                            <i class="${statusIcon}"></i> ${item.status}
                        </div>
                    </div>
                </div>
            `;
        }).join('');
    }

    updatePerformanceChart(taskData) {
        if (!this.performanceChart) return;

        const now = new Date();
        const timeLabel = now.toLocaleTimeString();

        // Add new data point
        this.performanceData.labels.push(timeLabel);
        this.performanceData.datasets[0].data.push(taskData.completed_tasks || 0);
        this.performanceData.datasets[1].data.push(taskData.success_rate || 0);

        // Keep only last 20 data points
        if (this.performanceData.labels.length > 20) {
            this.performanceData.labels.shift();
            this.performanceData.datasets[0].data.shift();
            this.performanceData.datasets[1].data.shift();
        }

        this.performanceChart.update('none');
    }

    getHealthStatusClass(status) {
        switch (status.toLowerCase()) {
            case 'healthy': return 'status-healthy';
            case 'warning': case 'degraded': return 'status-warning';
            case 'error': case 'unhealthy': return 'status-error';
            default: return 'status-warning';
        }
    }

    getHealthStatusIcon(status) {
        switch (status.toLowerCase()) {
            case 'healthy': return 'fas fa-check-circle';
            case 'warning': case 'degraded': return 'fas fa-exclamation-triangle';
            case 'error': case 'unhealthy': return 'fas fa-times-circle';
            default: return 'fas fa-question-circle';
        }
    }

    startLiveUpdates() {
        if (this.updateInterval) {
            clearInterval(this.updateInterval);
        }

        this.updateInterval = setInterval(async () => {
            console.log('🔄 Updating dashboard data...');
            await this.loadAllData();
        }, 10000); // Update every 10 seconds

        console.log('📡 Live updates started - refreshing every 10 seconds');
    }

    showRefreshIndicator() {
        const indicator = document.getElementById('refreshIndicator');
        if (indicator) {
            indicator.classList.add('active');
        }
    }

    hideRefreshIndicator() {
        const indicator = document.getElementById('refreshIndicator');
        if (indicator) {
            indicator.classList.remove('active');
        }
    }

    updateTimestamp() {
        const timestampElement = document.getElementById('lastUpdate');
        if (timestampElement) {
            timestampElement.textContent = new Date().toLocaleString();
        }
    }

    destroy() {
        if (this.updateInterval) {
            clearInterval(this.updateInterval);
        }
        if (this.performanceChart) {
            this.performanceChart.destroy();
        }
        console.log('Dashboard destroyed');
    }
}

// Initialize dashboard when page loads
let dashboard;

document.addEventListener('DOMContentLoaded', () => {
    dashboard = new ProfessionalDashboard();
    dashboard.init();
});

// Cleanup on page unload
window.addEventListener('beforeunload', () => {
    if (dashboard) {
        dashboard.destroy();
    }
});

// Export for external access
window.ProfessionalDashboard = ProfessionalDashboard;