/**
 * Enhanced Dashboard Auto-Update System - Phase 6 Step 6.5
 * 
 * Real-time dashboard updates with auto-refresh capabilities,
 * progress charts, health indicators, and automation monitoring.
 */

class DashboardManager {
    constructor() {
        this.refreshInterval = 30000; // 30 seconds
        this.isRunning = false;
        this.isUpdating = false; // Prevent overlapping updates
        this.lastUpdate = null;
        this.charts = {};
        this.healthIndicators = {};
        this.automationStatus = {};
        this.apiBaseUrl = 'http://localhost:5000';
        this.endpoints = {
            metrics: '/api/metrics',
            sprintHealth: '/api/sprint/health',
            automationStatus: '/api/automation/status',
            recentActivity: '/api/tasks/recent',
            progressTrend: '/api/progress/trend'
        };
        
        this.initializeCharts();
        this.setupEventHandlers();
    }
    
    async initialize() {
        console.log('Initializing Dashboard Manager...');
        await this.loadInitialData();
        this.startAutoUpdate();
    }
    
    initializeCharts() {
        // Progress chart configuration
        this.progressChartConfig = {
            type: 'doughnut',
            data: {
                labels: ['Completed', 'In Progress', 'Pending', 'Failed'],
                datasets: [{
                    data: [0, 0, 0, 0],
                    backgroundColor: [
                        '#4CAF50',  // Green for completed
                        '#2196F3',  // Blue for in progress
                        '#FFC107',  // Yellow for pending
                        '#F44336'   // Red for failed
                    ],
                    borderWidth: 2,
                    borderColor: '#ffffff'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom'
                    },
                    title: {
                        display: true,
                        text: 'Sprint Progress Overview'
                    }
                }
            }
        };
        
        // Velocity trend chart configuration
        this.velocityChartConfig = {
            type: 'line',
            data: {
                labels: [],
                datasets: [{
                    label: 'Completion Rate %',
                    data: [],
                    borderColor: '#4CAF50',
                    backgroundColor: 'rgba(76, 175, 80, 0.1)',
                    fill: true
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true,
                        max: 100
                    }
                }
            }
        };
    }
    
    setupEventHandlers() {
        // Manual refresh button
        const refreshBtn = document.getElementById('manualRefresh');
        if (refreshBtn) {
            refreshBtn.addEventListener('click', () => this.manualRefresh());
        }
        
        // Auto-refresh toggle
        const autoRefreshToggle = document.getElementById('autoRefreshToggle');
        if (autoRefreshToggle) {
            autoRefreshToggle.addEventListener('change', (e) => {
                if (e.target.checked) {
                    this.startAutoUpdate();
                } else {
                    this.stopAutoUpdate();
                }
            });
        }
    }
    
    async loadInitialData() {
        try {
            console.log('Loading initial dashboard data...');
            
            // Load all data in parallel
            const [metrics, health, automation, activity] = await Promise.all([
                this.fetchData(this.endpoints.metrics),
                this.fetchData(this.endpoints.sprintHealth),
                this.fetchData(this.endpoints.automationStatus),
                this.fetchData(this.endpoints.recentActivity)
            ]);
            
            // Update dashboard with loaded data
            this.updateMetricsDisplay(metrics.data);
            this.updateHealthIndicators(health.data);
            this.updateAutomationStatus(automation.data);
            this.updateRecentActivity(activity.data);
            
            // Update charts
            const trends = await this.fetchData(this.endpoints.progressTrend);
            this.updateProgressCharts(metrics.data, trends.data);
            
            this.lastUpdate = new Date();
            this.updateLastRefreshTime();
            
            console.log('Initial data loaded successfully');
            
        } catch (error) {
            console.error('Error loading initial data:', error);
            this.showError('Failed to load dashboard data');
        }
    }
    
    async fetchData(endpoint) {
        try {
            const url = this.apiBaseUrl + endpoint;
            console.log(`Fetching data from: ${url}`);
            
            const response = await fetch(url);
            
            if (!response.ok) {
                throw new Error(`Failed to fetch ${endpoint}: ${response.statusText}`);
            }
            
            const data = await response.json();
            
            if (data.status !== 'success') {
                throw new Error(`API error: ${data.message || 'Unknown error'}`);
            }
            
            return data;
            
        } catch (error) {
            console.error(`Error fetching ${endpoint}:`, error);
            throw error;
        }
    }
    
    startAutoUpdate() {
        if (this.isRunning) return;
        
        this.isRunning = true;
        console.log('Starting auto-update...');
        
        this.updateLoop();
    }
    
    stopAutoUpdate() {
        this.isRunning = false;
        console.log('Auto-update stopped');
    }
    
    async updateLoop() {
        if (!this.isRunning) return;
        
        try {
            await this.refreshData();
        } catch (error) {
            console.error('Update loop error:', error);
        }
        
        // Schedule next update
        setTimeout(() => this.updateLoop(), this.refreshInterval);
    }
    
    async refreshData() {
        if (this.isUpdating) return;
        
        this.isUpdating = true;
        
        try {
            // Show updating indicator
            this.showRefreshIndicator();
            
            // Fetch updated data
            const [metrics, health, automation, activity] = await Promise.all([
                this.fetchData(this.endpoints.metrics),
                this.fetchData(this.endpoints.sprintHealth),
                this.fetchData(this.endpoints.automationStatus),
                this.fetchData(this.endpoints.recentActivity)
            ]);
            
            // Update dashboard
            this.updateMetricsDisplay(metrics.data);
            this.updateHealthIndicators(health.data);
            this.updateAutomationStatus(automation.data);
            this.updateRecentActivity(activity.data);
            
            this.lastUpdate = new Date();
            this.updateLastRefreshTime();
            this.showRefreshSuccess();
            
        } catch (error) {
            console.error('Refresh error:', error);
            this.showRefreshError();
        } finally {
            this.isUpdating = false;
        }
    }
    
    async manualRefresh() {
        console.log('Manual refresh triggered');
        await this.refreshData();
    }
    
    updateMetricsDisplay(metrics) {
        try {
            // Update completion rate
            this.updateElement('completionRate', `${metrics.completion_rate.toFixed(1)}%`);
            
            // Update task counts
            this.updateElement('totalTasks', metrics.total_tasks);
            this.updateElement('completedTasks', metrics.completed_tasks);
            this.updateElement('inProgressTasks', metrics.in_progress_tasks);
            this.updateElement('pendingTasks', metrics.pending_tasks || 0);
            
            // Update velocity
            if (metrics.velocity) {
                this.updateElement('dailyVelocity', metrics.velocity.daily_average);
                this.updateElement('weeklyVelocity', metrics.velocity.weekly_average);
            }
            
            // Update progress bar
            this.updateProgressBar('completionProgress', metrics.completion_rate);
            
        } catch (error) {
            console.error('Error updating metrics display:', error);
        }
    }
    
    updateHealthIndicators(health) {
        try {
            const healthCard = document.getElementById('healthCard');
            const healthStatus = document.querySelector('.health-status');
            const healthIndicator = document.querySelector('.health-indicator');
            const healthText = document.querySelector('.health-text');
            const healthMessage = document.querySelector('.health-message');
            
            if (healthStatus && health) {
                // Update status indicator
                if (healthIndicator) {
                    healthIndicator.style.backgroundColor = health.color || '#6c757d';
                }
                
                // Update status text
                if (healthText) {
                    healthText.textContent = health.status.toUpperCase().replace('_', ' ');
                }
                
                // Update message
                if (healthMessage) {
                    healthMessage.textContent = health.message || 'Status unknown';
                }
                
                // Update recommendations
                if (health.recommendations && health.recommendations.length > 0) {
                    const recommendationsSection = document.getElementById('recommendationsSection');
                    if (recommendationsSection) {
                        const ul = recommendationsSection.querySelector('ul');
                        if (ul) {
                            ul.innerHTML = health.recommendations
                                .map(rec => `<li>${rec}</li>`)
                                .join('');
                            recommendationsSection.style.display = 'block';
                        }
                    }
                }
            }
            
        } catch (error) {
            console.error('Error updating health indicators:', error);
        }
    }
    
    updateAutomationStatus(automation) {
        try {
            const statusGrid = document.getElementById('automationStatusGrid');
            if (statusGrid && automation) {
                statusGrid.innerHTML = `
                    <div class="status-item">
                        <div class="status-value">${automation.daily_cycle_active ? 'Active' : 'Inactive'}</div>
                        <div class="status-label">Daily Cycle</div>
                    </div>
                    <div class="status-item">
                        <div class="status-value">${automation.current_task || 'None'}</div>
                        <div class="status-label">Current Task</div>
                    </div>
                    <div class="status-item">
                        <div class="status-value">${automation.system_uptime || '0%'}</div>
                        <div class="status-label">Uptime</div>
                    </div>
                    <div class="status-item">
                        <div class="status-value">${automation.error_count || 0}</div>
                        <div class="status-label">Errors</div>
                    </div>
                `;
            }
        } catch (error) {
            console.error('Error updating automation status:', error);
        }
    }
    
    updateRecentActivity(activity) {
        try {
            const activityList = document.getElementById('recentActivityList');
            if (activityList && activity) {
                const activityHtml = activity.map(item => `
                    <div class="activity-item">
                        <div class="activity-icon">
                            <span class="status-indicator ${this.getStatusClass(item.status)}"></span>
                        </div>
                        <div class="activity-content">
                            <div class="activity-title">${item.title}</div>
                            <div class="activity-time">${this.formatRelativeTime(new Date(item.updated_at))}</div>
                        </div>
                    </div>
                `).join('');
                
                activityList.innerHTML = activityHtml;
            }
        } catch (error) {
            console.error('Error updating recent activity:', error);
        }
    }
    
    updateProgressCharts(metrics, trends) {
        try {
            // Update progress doughnut chart
            const progressCanvas = document.getElementById('progress-chart');
            if (progressCanvas) {
                if (!this.charts.progress) {
                    const ctx = progressCanvas.getContext('2d');
                    this.charts.progress = new Chart(ctx, this.progressChartConfig);
                }
                
                // Update data without recreating chart
                this.charts.progress.data.datasets[0].data = [
                    metrics.completed_tasks || 0,
                    metrics.in_progress_tasks || 0,
                    metrics.pending_tasks || 0,
                    metrics.team_metrics?.failed_tasks || 0
                ];
                this.charts.progress.update('none');
            }
            
            // Update velocity chart
            const velocityCanvas = document.getElementById('velocity-chart');
            if (velocityCanvas && trends) {
                if (!this.charts.velocity) {
                    const ctx = velocityCanvas.getContext('2d');
                    this.charts.velocity = new Chart(ctx, this.velocityChartConfig);
                }
                
                // Update trend data
                if (trends.dates && trends.completion_rates) {
                    this.charts.velocity.data.labels = trends.dates;
                    this.charts.velocity.data.datasets[0].data = trends.completion_rates;
                    this.charts.velocity.update('none');
                }
            }
            
        } catch (error) {
            console.error('Error updating charts:', error);
        }
    }
    
    updateElement(id, value) {
        const element = document.getElementById(id);
        if (element) {
            element.textContent = value;
        }
    }
    
    updateProgressBar(id, percentage) {
        const progressBar = document.getElementById(id);
        if (progressBar) {
            progressBar.style.width = `${percentage}%`;
            progressBar.setAttribute('aria-valuenow', percentage);
        }
    }
    
    updateLastRefreshTime() {
        const lastUpdated = document.getElementById('lastUpdated');
        if (lastUpdated && this.lastUpdate) {
            lastUpdated.textContent = `Last updated: ${this.formatRelativeTime(this.lastUpdate)}`;
        }
    }
    
    formatRelativeTime(date) {
        const now = new Date();
        const diffInSeconds = Math.floor((now - date) / 1000);
        
        if (diffInSeconds < 60) {
            return 'just now';
        } else if (diffInSeconds < 3600) {
            const minutes = Math.floor(diffInSeconds / 60);
            return `${minutes} minute${minutes > 1 ? 's' : ''} ago`;
        } else if (diffInSeconds < 86400) {
            const hours = Math.floor(diffInSeconds / 3600);
            return `${hours} hour${hours > 1 ? 's' : ''} ago`;
        } else {
            return date.toLocaleDateString();
        }
    }
    
    getStatusClass(status) {
        const statusMap = {
            'COMPLETED': 'status-online',
            'RUNNING': 'status-updating',
            'IN_PROGRESS': 'status-updating',
            'FAILED': 'status-error',
            'ERROR': 'status-error'
        };
        return statusMap[status] || 'status-updating';
    }
    
    showRefreshIndicator() {
        const liveDot = document.querySelector('.live-dot');
        if (liveDot) {
            liveDot.style.backgroundColor = '#ffc107'; // Yellow while updating
        }
    }
    
    showRefreshSuccess() {
        const liveDot = document.querySelector('.live-dot');
        if (liveDot) {
            liveDot.style.backgroundColor = '#28a745'; // Green for success
        }
        this.showNotification('Dashboard updated successfully', 'success');
    }
    
    showRefreshError() {
        const liveDot = document.querySelector('.live-dot');
        if (liveDot) {
            liveDot.style.backgroundColor = '#dc3545'; // Red for error
        }
        this.showError('Failed to update dashboard');
    }
    
    showError(message) {
        console.error(message);
        this.showNotification(message, 'error');
    }
    
    showNotification(message, type = 'info') {
        // Simple notification system
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.textContent = message;
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 12px 20px;
            border-radius: 4px;
            color: white;
            font-weight: 500;
            z-index: 1000;
            opacity: 0;
            transition: opacity 0.3s ease;
        `;
        
        // Set background color based on type
        const colors = {
            success: '#28a745',
            error: '#dc3545',
            warning: '#ffc107',
            info: '#17a2b8'
        };
        notification.style.backgroundColor = colors[type] || colors.info;
        
        document.body.appendChild(notification);
        
        // Fade in
        setTimeout(() => notification.style.opacity = '1', 100);
        
        // Auto remove
        setTimeout(() => {
            notification.style.opacity = '0';
            setTimeout(() => document.body.removeChild(notification), 300);
        }, 3000);
    }
}

// Enhanced Timeline Component
class TimelineManager {
    constructor() {
        this.timeline = [];
        this.maxItems = 50;
    }
    
    async loadTimelineData() {
        try {
            // This would fetch timeline data from API
            // For now, return empty array to prevent 404 errors
            return [];
        } catch (error) {
            console.error('Error loading timeline data:', error);
            return [];
        }
    }
    
    renderTimeline() {
        // Timeline rendering logic would go here
        console.log('Timeline rendered');
    }
}

// Sprint Health Analyzer
class HealthAnalyzer {
    constructor() {
        this.thresholds = {
            excellent: 80,
            good: 60,
            fair: 40
        };
    }
    
    analyzeSprintHealth(metrics, trends) {
        const completion_rate = metrics.completion_rate || 0;
        
        if (completion_rate >= this.thresholds.excellent) {
            return { status: 'excellent', score: completion_rate };
        } else if (completion_rate >= this.thresholds.good) {
            return { status: 'good', score: completion_rate };
        } else if (completion_rate >= this.thresholds.fair) {
            return { status: 'fair', score: completion_rate };
        } else {
            return { status: 'needs_attention', score: completion_rate };
        }
    }
    
    analyzeVelocity(velocity, trends) {
        // Velocity analysis logic
        return { trend: 'stable', score: velocity };
    }
    
    analyzeCompletion(rate) {
        return rate >= 80 ? 'on_track' : 'behind';
    }
    
    analyzeBlockers(blockedCount) {
        return blockedCount === 0 ? 'clear' : 'blocked';
    }
    
    generateRecommendations(score, metrics) {
        if (score >= 80) {
            return ['Maintain current pace', 'Consider additional tasks'];
        } else if (score >= 60) {
            return ['Continue steady progress', 'Monitor for blockers'];
        } else {
            return ['Review priorities', 'Address blockers', 'Reassess scope'];
        }
    }
}

// Initialize dashboard when DOM is loaded
document.addEventListener('DOMContentLoaded', async () => {
    try {
        console.log('DOM loaded, initializing dashboard...');
        
        // Create dashboard manager
        const dashboard = new DashboardManager();
        
        // Initialize dashboard
        await dashboard.initialize();
        
        // Create timeline manager
        const timeline = new TimelineManager();
        await timeline.loadTimelineData();
        
        console.log('Dashboard initialization complete!');
        
    } catch (error) {
        console.error('Failed to initialize dashboard:', error);
        
        // Show error message to user
        const errorDiv = document.createElement('div');
        errorDiv.className = 'error-message';
        errorDiv.innerHTML = `
            <h3>Dashboard Initialization Error</h3>
            <p>Failed to initialize the dashboard: ${error.message}</p>
            <p>Please check the console for more details and ensure the API server is running.</p>
        `;
        errorDiv.style.cssText = `
            position: fixed;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            background: #f8d7da;
            color: #721c24;
            padding: 20px;
            border: 1px solid #f5c6cb;
            border-radius: 4px;
            z-index: 1000;
            max-width: 500px;
        `;
        
        document.body.appendChild(errorDiv);
    }
});
