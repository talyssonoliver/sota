/**
 * Enhanced Dashboard Auto-Update System - Phase 6 Step 6.5
 * 
 * Real-time dashboard updates with auto-refresh capabilities,
 * progress charts, health indicators, and automation monitoring.
 */

class DashboardManager {
    constructor() {        this.refreshInterval = 30000; // 30 seconds
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
            progressTrend: '/api/progress/trend',
            systemHealth: '/api/system/health',
            timelineData: '/api/timeline/data'
        };
        
        // Enhanced automation monitoring state
        this.automationMonitoring = {
            lastHealthCheck: null,
            systemComponents: {},
            performanceMetrics: {},
            alertsEnabled: true
        };
        
        this.initializeCharts();
        this.setupEventHandlers();
        this.initializeAutomationMonitoring();
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
                labels: ['Completed', 'In Progress', 'Pending', 'Blocked'],
                datasets: [{
                    data: [0, 0, 0, 0],
                    backgroundColor: [
                        '#4CAF50',  // Green for completed
                        '#2196F3',  // Blue for in progress
                        '#FFC107',  // Yellow for pending
                        '#F44336'   // Red for blocked
                    ],
                    borderWidth: 2,
                    borderColor: '#ffffff'
                }]
            },            options: {
                responsive: true,
                maintainAspectRatio: false,
                animation: { duration: 0 }, // Disable animations to prevent performance issues
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
                    label: 'Daily Velocity',
                    data: [],
                    borderColor: '#2196F3',
                    backgroundColor: 'rgba(33, 150, 243, 0.1)',
                    fill: true,
                    tension: 0.4
                }, {
                    label: 'Target Velocity',
                    data: [],
                    borderColor: '#4CAF50',
                    backgroundColor: 'transparent',
                    borderDash: [5, 5]
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                animation: { // ADDED: Disable animations
                    duration: 0
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: 'Tasks per Day'
                        }
                    },
                    x: {
                        title: {
                            display: true,
                            text: 'Date'
                        }
                    }
                },
                plugins: {
                    title: {
                        display: true,
                        text: 'Team Velocity Trend'
                    }
                }
            }
        };
    }
    
    setupEventHandlers() {
        // Auto-refresh toggle
        const toggle = document.getElementById('auto-refresh-toggle');
        if (toggle) {
            toggle.addEventListener('change', (e) => {
                if (e.target.checked) {
                    this.startAutoUpdate();
                } else {
                    this.stopAutoUpdate();
                }
            });
        }
        
        // Manual refresh button
        const refreshBtn = document.getElementById('manual-refresh');
        if (refreshBtn) {
            refreshBtn.addEventListener('click', () => {
                this.manualRefresh();
            });
        }
        
        // System health drill-down
        const healthCard = document.getElementById('healthCard');
        if (healthCard) {
            healthCard.addEventListener('click', () => {
                this.showSystemHealthDetails();
            });
        }
        
        // Automation status details
        const automationSection = document.querySelector('.automation-status');
        if (automationSection) {
            automationSection.addEventListener('click', () => {
                this.showAutomationDetails();
            });
        }
    }
    
    initializeAutomationMonitoring() {
        // Set up enhanced automation monitoring
        this.automationMonitoring.alertsEnabled = true;
        this.automationMonitoring.lastHealthCheck = null;
        
        // Initialize component status tracking
        this.automationMonitoring.systemComponents = {
            'dashboard_api': 'unknown',
            'metrics_engine': 'unknown', 
            'automation_system': 'unknown',
            'reporting_system': 'unknown'
        };
        
        console.log('Automation monitoring initialized');
    }
    
    async loadInitialData() {
        try {
            const [metrics, health, automation, activity, trends] = await Promise.all([
                this.fetchData(this.endpoints.metrics),
                this.fetchData(this.endpoints.sprintHealth),
                this.fetchData(this.endpoints.automationStatus),
                this.fetchData(this.endpoints.recentActivity),
                this.fetchData(this.endpoints.progressTrend)
            ]);
            
            this.updateMetricsDisplay(metrics);
            this.updateHealthIndicators(health);
            this.updateAutomationStatus(automation);
            this.updateRecentActivity(activity);
            this.updateProgressCharts(metrics, trends);
            
            this.lastUpdate = new Date();
            this.updateLastRefreshTime();
            
        } catch (error) {
            console.error('Error loading initial data:', error);
            this.showError('Failed to load dashboard data');
        }
    }
    
    async fetchData(endpoint) {
        const response = await fetch(`${this.apiBaseUrl}${endpoint}`);
        if (!response.ok) {
            throw new Error(`Failed to fetch ${endpoint}: ${response.statusText}`);
        }
        return response.json();
    }
    
    startAutoUpdate() {
        if (this.isRunning) return;
        
        this.isRunning = true;
        console.log(`Auto-update started (${this.refreshInterval/1000}s interval)`);
        this.updateLoop();
        
        // Update UI
        const toggle = document.getElementById('auto-refresh-toggle');
        if (toggle) toggle.checked = true;
        
        const status = document.getElementById('auto-refresh-status');
        if (status) {
            status.textContent = 'ON';
            status.className = 'status-indicator status-active';
        }
    }
    
    stopAutoUpdate() {
        this.isRunning = false;
        console.log('Auto-update stopped');
        
        // Update UI
        const toggle = document.getElementById('auto-refresh-toggle');
        if (toggle) toggle.checked = false;
        
        const status = document.getElementById('auto-refresh-status');
        if (status) {
            status.textContent = 'OFF';
            status.className = 'status-indicator status-inactive';
        }
    }
    
    async updateLoop() {
        if (!this.isRunning) return;
        
        try {
            await this.refreshData();
        } catch (error) {
            console.error('Update loop error:', error);
        }
        
        if (this.isRunning) {
            setTimeout(() => this.updateLoop(), this.refreshInterval);
        }
    }
      async refreshData() {
        if (this.isUpdating) return;
        
        this.isUpdating = true;
        
        try {
            // Fetch all data in parallel for better performance
            const [metricsData, healthData, automationData, activityData, trendsData, systemHealthData] = await Promise.all([
                this.fetchData(this.endpoints.metrics).catch(e => ({ error: e.message })),
                this.fetchData(this.endpoints.sprintHealth).catch(e => ({ error: e.message })),
                this.fetchData(this.endpoints.automationStatus).catch(e => ({ error: e.message })),
                this.fetchData(this.endpoints.recentActivity).catch(e => ({ error: e.message })),
                this.fetchData(this.endpoints.progressTrend).catch(e => ({ error: e.message })),
                this.fetchData(this.endpoints.systemHealth).catch(e => ({ error: e.message }))
            ]);
            
            // Update UI components
            if (metricsData && !metricsData.error) {
                this.updateMetricsDisplay(metricsData);
            }
            
            if (healthData && !healthData.error) {
                this.updateHealthIndicators(healthData);
            }
            
            if (automationData && !automationData.error) {
                this.updateAutomationStatus(automationData);
            }
            
            if (activityData && !activityData.error) {
                this.updateRecentActivity(activityData);
            }
            
            if (trendsData && !trendsData.error && metricsData && !metricsData.error) {
                this.updateProgressCharts(metricsData, trendsData);
            }
            
            // Update enhanced system health monitoring
            if (systemHealthData && !systemHealthData.error) {
                this.updateSystemHealthMonitoring(systemHealthData);
            }
            
            // Update automation monitoring
            this.updateAutomationMonitoring(automationData, systemHealthData);
            
            this.lastUpdate = new Date();
            this.updateElement('lastUpdated', `Last updated: ${this.lastUpdate.toLocaleTimeString()}`);
            
        } catch (error) {
            console.error('Error refreshing dashboard data:', error);
            this.showRefreshError();
        } finally {
            this.isUpdating = false;
        }
    }
    
    async manualRefresh() {
        const button = document.getElementById('manual-refresh');
        if (button) {
            button.disabled = true;
            button.textContent = 'Refreshing...';
        }
        
        try {
            await this.loadInitialData();
            this.showRefreshSuccess();
        } catch (error) {
            console.error('Manual refresh error:', error);
            this.showRefreshError();
        } finally {
            if (button) {
                button.disabled = false;
                button.textContent = '🔄 Refresh';
            }
        }
    }
      updateMetricsDisplay(metrics) {
        if (!metrics || !metrics.data) return;
        
        const data = metrics.data;
          // Update main metrics using correct HTML element IDs
        this.updateElement('totalTasks', data.completed_tasks + data.in_progress_tasks + data.pending_tasks || 0);
        this.updateElement('activeTasks', data.in_progress_tasks || 0);
        this.updateElement('completionRate', `${(data.completion_rate || 0).toFixed(1)}%`);
        
        // Fix velocity display to use correct data structure
        const velocityData = data.velocity || {};
        this.updateElement('velocity', velocityData.daily_average || '--');
        
        // Update subtitle elements
        this.updateElement('completionSubtitle', `${data.completed_tasks || 0} of ${data.completed_tasks + data.in_progress_tasks + data.pending_tasks || 0} tasks completed`);
        this.updateElement('tasksBreakdown', `${data.in_progress_tasks || 0} active, ${data.pending_tasks || 0} pending`);
        
        // Update health status
        this.updateElement('healthStatus', metrics.status || 'Unknown');
    }
    
    updateHealthIndicators(health) {
        const indicator = document.getElementById('sprint-health-indicator');
        const text = document.getElementById('sprint-health-text');
        
        if (indicator && text) {
            const status = health.status || 'UNKNOWN';
            const healthClasses = {
                'HEALTHY': 'health-good',
                'NEEDS_ATTENTION': 'health-warning',
                'AT_RISK': 'health-danger',
                'CRITICAL': 'health-critical'
            };
            
            const healthIcons = {
                'HEALTHY': '✅',
                'NEEDS_ATTENTION': '⚠️',
                'AT_RISK': '🔴',
                'CRITICAL': '🚨'
            };
            
            indicator.className = `health-indicator ${healthClasses[status] || 'health-unknown'}`;
            text.textContent = `${healthIcons[status] || '❓'} ${status}`;
        }
        
        // Update health details
        if (health.details) {
            this.updateElement('health-score', `${health.details.score || 0}/10`);
            this.updateElement('blockers-count', health.details.blockers_count || 0);
            this.updateElement('risk-level', health.details.risk_level || 'Unknown');
        }
    }    updateAutomationStatus(automation) {
        if (!automation || !automation.data) return;
        
        const data = automation.data;
        
        // Update the automation status grid elements with correct IDs from HTML
        this.updateElement('systemUptime', data.system_uptime || 'N/A');
        this.updateElement('dailyCycleStatus', data.daily_cycle_active ? 'Active' : 'Inactive');
        this.updateElement('errorCount', data.error_count || 0);
        this.updateElement('activeJobs', Array.isArray(data.active_jobs) ? data.active_jobs.length : 0);
        
        // Update system health
        this.updateElement('automation-errors', data.error_count || 0);
    }
      updateRecentActivity(activity) {
        const container = document.getElementById('recentActivityList'); // Fixed: correct element ID
        if (!container) return;
        
        // Handle different API response formats
        const activityData = activity.data || activity.tasks || activity;
        if (!activityData || !Array.isArray(activityData)) {
            console.warn('No recent activity data available');
            return;
        }
        
        container.innerHTML = '';
        
        activityData.slice(0, 5).forEach(task => {
            const item = document.createElement('div');
            item.className = 'activity-item';
            
            const timestamp = new Date(task.updated_at || task.timestamp);
            const timeAgo = this.formatRelativeTime(timestamp);
            
            item.innerHTML = `
                <div class="activity-icon" style="background: #17a2b8;">📊</div>
                <div class="activity-content">
                    <div class="activity-title">${task.title || task.id} - ${task.action}</div>
                    <div class="activity-time">${timeAgo}</div>
                </div>
            `;
            
            container.appendChild(item);
        });
    }      updateProgressCharts(metrics, trends) {
        // Update progress donut chart
        const progressCanvas = document.getElementById('progress-chart');
        if (progressCanvas) {
            // Only create chart if it doesn't exist
            if (!this.charts.progress) {
                const ctx = progressCanvas.getContext('2d');
                const data = metrics.data || metrics;
                this.progressChartConfig.data.datasets[0].data = [
                    data.completed_tasks || 0,
                    data.in_progress_tasks || 0,
                    data.pending_tasks || 0,
                    0  // blocked tasks (not in current API)
                ];
                
                this.charts.progress = new Chart(ctx, this.progressChartConfig);
            } else {
                // Update existing chart data
                const data = metrics.data || metrics;
                this.charts.progress.data.datasets[0].data = [
                    data.completed_tasks || 0,
                    data.in_progress_tasks || 0,
                    data.pending_tasks || 0,
                    0  // blocked tasks (not in current API)
                ];
                this.charts.progress.update();
            }
        }
        
        // Update Progress Trend chart (now shows task status distribution over time)
        const velocityCanvas = document.getElementById('velocity-chart');
        if (velocityCanvas && trends && trends.data) {
            const trendData = trends.data;
            
            // Check if we have the new datasets structure
            if (trendData.datasets) {
                // Only create chart if it doesn't exist
                if (!this.charts.velocity) {
                    const ctx = velocityCanvas.getContext('2d');
                    
                    // Update chart config to show stacked area chart of task status
                    this.velocityChartConfig = {
                        type: 'line',
                        data: {
                            labels: trendData.dates || [],
                            datasets: [{
                                label: 'Completed',
                                data: trendData.datasets.completed || [],
                                borderColor: '#4CAF50',
                                backgroundColor: 'rgba(76, 175, 80, 0.6)',
                                fill: true
                            }, {
                                label: 'In Progress',
                                data: trendData.datasets.in_progress || [],
                                borderColor: '#2196F3',
                                backgroundColor: 'rgba(33, 150, 243, 0.6)',
                                fill: true
                            }, {
                                label: 'Pending',
                                data: trendData.datasets.pending || [],
                                borderColor: '#FFC107',
                                backgroundColor: 'rgba(255, 193, 7, 0.6)',
                                fill: true
                            }, {
                                label: 'Blocked',
                                data: trendData.datasets.blocked || [],
                                borderColor: '#F44336',
                                backgroundColor: 'rgba(244, 67, 54, 0.6)',
                                fill: true
                            }]
                        },
                        options: {
                            responsive: true,
                            maintainAspectRatio: false,
                            animation: { duration: 0 },
                            scales: {
                                y: {
                                    beginAtZero: true,
                                    stacked: true,
                                    title: {
                                        display: true,
                                        text: 'Tasks Count'
                                    }
                                },
                                x: {
                                    stacked: true,
                                    title: {
                                        display: true,
                                        text: 'Date'
                                    }
                                }
                            },
                            plugins: {
                                title: {
                                    display: true,
                                    text: 'Progress Trend (Task Status Over Time)'
                                },
                                legend: {
                                    position: 'top'
                                }
                            }
                        }
                    };
                    
                    this.charts.velocity = new Chart(ctx, this.velocityChartConfig);
                } else {
                    // Update existing chart data
                    this.charts.velocity.data.labels = trendData.dates || [];
                    this.charts.velocity.data.datasets[0].data = trendData.datasets.completed || [];
                    this.charts.velocity.data.datasets[1].data = trendData.datasets.in_progress || [];
                    this.charts.velocity.data.datasets[2].data = trendData.datasets.pending || [];
                    this.charts.velocity.data.datasets[3].data = trendData.datasets.blocked || [];
                    this.charts.velocity.update();
                }
            } else if (trendData.velocities) {
                // Fallback to old velocity structure if new datasets not available
                if (!this.charts.velocity) {
                    const ctx = velocityCanvas.getContext('2d');
                    this.velocityChartConfig.data.labels = trendData.dates || [];
                    this.velocityChartConfig.data.datasets[0].data = trendData.velocities || [];
                    this.velocityChartConfig.data.datasets[1].data = trendData.velocities?.map(() => 2.5) || [];
                    this.charts.velocity = new Chart(ctx, this.velocityChartConfig);
                } else {
                    this.charts.velocity.data.labels = trendData.dates || [];
                    this.charts.velocity.data.datasets[0].data = trendData.velocities || [];
                    this.charts.velocity.data.datasets[1].data = trendData.velocities?.map(() => 2.5) || [];
                    this.charts.velocity.update();
                }
            }
        }
    }
    
    updateDistributionChart(metrics) {
        // Ensure this chart is initialized in initializeCharts if it's meant to be always present
        // For now, assuming it might be dynamically added or is the same as 'progress-chart'
        const distributionCanvas = document.getElementById('progress-chart'); // Assuming this is the distribution chart for now
        if (!distributionCanvas) {
            console.warn('Distribution chart canvas not found.');
            return;
        }

        if (!this.charts.distribution) {
             // Attempt to use the progress chart's instance if it's the same canvas
            if (this.charts.progress && this.charts.progress.canvas === distributionCanvas) {
                this.charts.distribution = this.charts.progress;
            } else {
                // If it's a different chart, it needs its own config and initialization
                console.warn('Distribution chart not properly initialized. Ensure it has a config and is created in initializeCharts.');
                // As a fallback, if it's the same canvas as progress, let's try to update that.
                // This part might need adjustment based on actual HTML and intended chart structure.
                if (this.charts.progress && metrics.detailed) {
                     this.charts.progress.data.datasets[0].data = [
                        metrics.completed_tasks || 0,
                        metrics.detailed.in_progress || 0,
                        metrics.detailed.pending || 0,
                        metrics.detailed.blocked || 0 
                    ];
                    this.charts.progress.update(); // CHANGED: from 'none'
                }
                return;
            }
        }
        
        // If this.charts.distribution is correctly initialized and distinct:
        if (this.charts.distribution && metrics.detailed) { // Check for metrics.detailed
            this.charts.distribution.data.datasets[0].data = [
                metrics.completed_tasks || 0,
                metrics.detailed.in_progress || 0, // Use detailed metrics
                metrics.detailed.pending || 0,   // Use detailed metrics
                metrics.detailed.blocked || 0    // Add blocked if it's part of this chart
            ];
            this.charts.distribution.update(); // CHANGED: from 'none'
        } else if (this.charts.distribution) { // Fallback if metrics.detailed is not available
             this.charts.distribution.data.datasets[0].data = [
                metrics.completed_tasks || 0,
                0, 
                0,
                0 
            ];
            this.charts.distribution.update(); // CHANGED: from 'none'
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
                progressBar.style.width = `${Math.min(percentage, 100)}%`;
                progressBar.setAttribute('aria-valuenow', percentage);
            }
        }        updateLastRefreshTime() {
            const element = document.getElementById('lastUpdated');
            if (element && this.lastUpdate) {
                element.textContent = `Last updated: ${this.lastUpdate.toLocaleTimeString()}`;
            }
        }
    
        formatRelativeTime(date) {
            const now = new Date();
            const diffMs = now - date;
            const diffMins = Math.floor(diffMs / 60000);
            const diffHours = Math.floor(diffMins / 60);
            const diffDays = Math.floor(diffHours / 24);
    
            if (diffMins < 1) return 'Just now';
            if (diffMins < 60) return `${diffMins}m ago`;
            if (diffHours < 24) return `${diffHours}h ago`;
            return `${diffDays}d ago`;
        }
    
        showRefreshSuccess() {
            this.showNotification('Dashboard updated successfully', 'success');
        }
    
        showRefreshError() {
            this.showNotification('Failed to update dashboard', 'error');
        }
    
        showError(message) {
            this.showNotification(message, 'error');
        }
    
        showNotification(message, type = 'info') {
            const container = document.getElementById('notifications');
            if (!container) return;
    
            const notification = document.createElement('div');
            notification.className = `notification notification-${type}`;
            notification.textContent = message;
    
            container.appendChild(notification);
    
            // Auto-remove after 3 seconds
            setTimeout(() => {
                if (notification.parentNode) {
                    notification.parentNode.removeChild(notification);
                }
            }, 3000);
        }
    }
    
    // Enhanced Timeline Component
    class TimelineManager {
        constructor() {
            this.timelineData = [];
            this.timelineChart = null;
        }
    
        async loadTimelineData() {
            try {
                const response = await fetch('/api/timeline');
                this.timelineData = await response.json();
                this.renderTimeline();
            } catch (error) {
                console.error('Error loading timeline data:', error);
            }
        }
    
        renderTimeline() {
            const canvas = document.getElementById('timeline-chart');
            if (!canvas || !this.timelineData.length) {
                if (!canvas) console.warn('Timeline chart canvas not found.');
                if (!this.timelineData.length) console.info('No timeline data to render.');
                return;
            }
    
            const ctx = canvas.getContext('2d');
    
            if (this.timelineChart) {
                this.timelineChart.destroy();
            }
    
            this.timelineChart = new Chart(ctx, {
                type: 'line',
                data: {
                    labels: this.timelineData.map(d => d.date),
                    datasets: [{
                        label: 'Cumulative Completion',
                        data: this.timelineData.map(d => d.cumulative_completion),
                        borderColor: '#4CAF50',
                        backgroundColor: 'rgba(76, 175, 80, 0.1)',
                        fill: true
                    }, {
                        label: 'Projected Completion',
                        data: this.timelineData.map(d => d.projected_completion),
                        borderColor: '#FF9800',
                        backgroundColor: 'transparent',
                        borderDash: [5, 5]
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    animation: { // Disable animation for timeline chart as well
                        duration: 0
                    },
                    scales: {
                        y: {
                            beginAtZero: true,
                            max: 100,
                            title: {
                                display: true,
                                text: 'Completion %'
                            }
                        }
                    },
                    plugins: {
                        title: {
                            display: true,
                            text: 'Sprint Progress Timeline'
                        },
                        legend: {
                            position: 'top'
                        }
                    }
                }
            });
        }
    }
    
    // Sprint Health Analyzer
    class HealthAnalyzer {
        constructor() {
            this.healthMetrics = {
                velocity: 0,
                blockers: 0,
                riskFactors: [],
                trends: []
            };
        }
    
        analyzeSprintHealth(metrics, trends) {
            const health = {
                score: 0,
                status: 'UNKNOWN',
                recommendations: [],
                alerts: []
            };
    
            // Velocity analysis
            const velocityScore = this.analyzeVelocity(metrics.team_velocity, trends);
            health.score += velocityScore * 0.4;
    
            // Completion rate analysis
            const completionScore = this.analyzeCompletion(metrics.completion_rate);
            health.score += completionScore * 0.3;
    
            // Blocker analysis
            const blockerScore = this.analyzeBlockers(metrics.detailed?.blocked || 0);
            health.score += blockerScore * 0.3;
    
            // Determine overall status
            if (health.score >= 8) health.status = 'HEALTHY';
            else if (health.score >= 6) health.status = 'NEEDS_ATTENTION';
            else if (health.score >= 4) health.status = 'AT_RISK';
            else health.status = 'CRITICAL';
    
            // Generate recommendations
            health.recommendations = this.generateRecommendations(health.score, metrics);
    
            return health;
        }
    
        analyzeVelocity(velocity, trends) {
            // Implement velocity analysis logic
            if (velocity === 'High') return 10;
            if (velocity === 'Medium') return 7;
            if (velocity === 'Low') return 4;
            return 5; // Default
        }
    
        analyzeCompletion(rate) {
            if (rate >= 80) return 10;
            if (rate >= 60) return 8;
            if (rate >= 40) return 6;
            if (rate >= 20) return 4;
            return 2;
        }
    
        analyzeBlockers(blockedCount) {
            if (blockedCount === 0) return 10;
            if (blockedCount <= 2) return 8;
            if (blockedCount <= 5) return 6;
            return 3;
        }
    
        generateRecommendations(score, metrics) {
            const recommendations = [];
    
            if (score < 6) {
                recommendations.push('Consider sprint scope adjustment');
                recommendations.push('Review and address blockers');
            }
    
            if (metrics.completion_rate < 50) {
                recommendations.push('Focus on high-priority tasks');
            }
    
            if (metrics.detailed?.blocked > 0) {
                recommendations.push('Address blocking issues immediately');
            }
    
            return recommendations;
        }
    }
    
    // Initialize dashboard when DOM is loaded
    document.addEventListener('DOMContentLoaded', async () => {
        try {
            const dashboardManager = new DashboardManager();
            const timelineManager = new TimelineManager();
            const healthAnalyzer = new HealthAnalyzer();
    
            // Initialize components
            await dashboardManager.initialize();
            await timelineManager.loadTimelineData();
    
            // Make managers globally available for debugging
            window.dashboardManager = dashboardManager;
            window.timelineManager = timelineManager;
            window.healthAnalyzer = healthAnalyzer;
    
            console.log('Enhanced Dashboard initialized successfully');
    
        } catch (error) {
            console.error('Failed to initialize dashboard:', error);
        }
    });
