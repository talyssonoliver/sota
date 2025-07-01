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
            progressTrend: '/api/progress/trend',
            systemHealth: '/api/system/health',
            timelineData: '/api/timeline/data',
            // New business metrics endpoints
            qaPassRate: '/api/qa_pass_rate',
            codeCoverage: '/api/code_coverage',
            sprintVelocity: '/api/sprint_velocity',
            completionTrend: '/api/completion_trend',
            qaResults: '/api/qa_results',
            coverageTrend: '/api/coverage_trend'
        };
        
        // Enhanced automation monitoring state
        this.automationMonitoring = {
            lastHealthCheck: null,
            systemComponents: {},
            performanceMetrics: {},
            alertsEnabled: true
        };
          // Phase 6 Step 6.5 Enhanced Charts Configuration
        this.enhancedCharts = {
            dailyAutomationChart: null,
            velocityTrackingChart: null,
            interactiveTimelineChart: null,
            sprintHealthChart: null,
            criticalPathChart: null,
            overallStatusDoughnutChart: null,
            tasksByDayStackedChart: null,
            tasksByOwnerStackedChart: null,
            trendAnalysisChart: null
        };
        
        this.initializeCharts();
        this.setupEventHandlers();
        this.initializeAutomationMonitoring();
        this.initializeEnhancedCharts(); // New initialization method
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
      async initialize() {
        console.log('Initializing Dashboard Manager...');
        
        // Wait a bit for global charts to be initialized
        await new Promise(resolve => setTimeout(resolve, 100));
        
        // Initialize chart references from global scope
        this.initializeChartReferences();
        
        await this.loadInitialData();
        this.startAutoUpdate();
    }
    
    initializeChartReferences() {
        // Get chart instances from global scope if they exist
        if (typeof window !== 'undefined') {
            if (window.completionChart) this.charts.completionChart = window.completionChart;
            if (window.progressChart) this.charts.progressChart = window.progressChart;
            if (window.qaChart) this.charts.qaChart = window.qaChart;
            if (window.coverageChart) this.charts.coverageChart = window.coverageChart;
            if (window.timelineChart) this.charts.timelineChart = window.timelineChart;
            
            console.log('Chart references initialized:', Object.keys(this.charts));
        }
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
            
            // Load business metrics in parallel
            const [qaPassRateData, codeCoverageData, sprintVelocityData, completionTrendData, qaResultsData, coverageTrendData] = await Promise.all([
                this.fetchData(this.endpoints.qaPassRate),
                this.fetchData(this.endpoints.codeCoverage),
                this.fetchData(this.endpoints.sprintVelocity),
                this.fetchData(this.endpoints.completionTrend),
                this.fetchData(this.endpoints.qaResults),
                this.fetchData(this.endpoints.coverageTrend)
            ]);
            
            // Update dashboard with loaded data
            this.updateMetricsDisplay(metrics.data);
            this.updateHealthIndicators(health.data);
            this.updateAutomationStatus(automation.data);
            this.updateRecentActivity(activity.data);
            
            // Update business metrics displays
            this.updateBusinessMetrics(qaPassRateData.data, codeCoverageData.data, sprintVelocityData.data);
            
            // Update charts
            const trends = await this.fetchData(this.endpoints.progressTrend);
            this.updateProgressCharts(metrics.data, trends.data);
            this.updateBusinessCharts(qaPassRateData.data, codeCoverageData.data, sprintVelocityData.data, completionTrendData.data, qaResultsData.data, coverageTrendData.data);
            
            this.lastUpdate = new Date();
            this.updateLastRefreshTime();
            
            console.log('Initial data loaded successfully');
            
        } catch (error) {
            console.error('Error loading initial data:', error);
            this.showError('Failed to load dashboard data');
        }
    }
      async fetchData(endpoint, options = {}) {
        try {
            const url = this.apiBaseUrl + endpoint;
            console.log(`Fetching data from: ${url}`);
            
            const response = await fetch(url);
            
            if (!response.ok) {
                throw new Error(`Failed to fetch ${endpoint}: ${response.statusText}`);
            }
            
            const data = await response.json();
            
            if (data.status !== 'success') {
                if (options.allowFailure) {
                    console.warn(`API warning for ${endpoint}: ${data.message || 'Unknown error'}`);
                    return null;
                } else {
                    throw new Error(`API error: ${data.message || 'Unknown error'}`);
                }
            }
            
            return options.dataOnly ? data.data : data;
            
        } catch (error) {
            if (options.allowFailure) {
                console.warn(`Failed to fetch ${endpoint}:`, error);
                return null;
            } else {
                console.error(`Error fetching ${endpoint}:`, error);
                throw error;
            }
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
            console.log('Refreshing dashboard data...');
            
            // Fetch all data in parallel
            const [metrics, sprintHealth, automation, recentActivity, progressTrend, systemHealth, timelineData] = await Promise.all([
                this.fetchData(this.endpoints.metrics),
                this.fetchData(this.endpoints.sprintHealth),
                this.fetchData(this.endpoints.automationStatus),
                this.fetchData(this.endpoints.recentActivity),
                this.fetchData(this.endpoints.progressTrend),
                this.fetchData(this.endpoints.systemHealth),
                this.fetchData(this.endpoints.timelineData)
            ]);

            // Fetch business metrics in parallel
            const [qaPassRateData, codeCoverageData, sprintVelocityData, completionTrendData, qaResultsData, coverageTrendData] = await Promise.all([
                this.fetchData(this.endpoints.qaPassRate),
                this.fetchData(this.endpoints.codeCoverage),
                this.fetchData(this.endpoints.sprintVelocity),
                this.fetchData(this.endpoints.completionTrend),
                this.fetchData(this.endpoints.qaResults),
                this.fetchData(this.endpoints.coverageTrend)
            ]);
            
            // Update dashboard components
            this.updateMetricsDisplay(metrics);
            this.updateHealthIndicators(sprintHealth);
            this.updateAutomationStatus(automation);
            this.updateRecentActivity(recentActivity);
            this.updateProgressCharts(metrics, progressTrend);
            this.updateSystemHealthDisplay(systemHealth);
            this.updateTimelineDisplay(timelineData);

            // Update business metrics
            this.updateBusinessMetrics(qaPassRateData.data, codeCoverageData.data, sprintVelocityData.data);
            this.updateBusinessCharts(qaPassRateData.data, codeCoverageData.data, sprintVelocityData.data, completionTrendData.data, qaResultsData.data, coverageTrendData.data);
            
            this.lastUpdate = new Date();
            console.log('Dashboard data refreshed successfully');
            
        } catch (error) {
            console.error('Error refreshing dashboard data:', error);
        } finally {
            this.isUpdating = false;
        }
    }
      updateMetricsDisplay(metrics) {
        try {
            // Handle different data structures - extract sprint data if nested
            let sprintData = metrics;
            if (metrics.data && metrics.data.sprint) {
                sprintData = metrics.data.sprint;
            } else if (metrics.sprint) {
                sprintData = metrics.sprint;
            }
            
            console.log('Updating metrics display with data:', sprintData);
            
            // Update completion rate
            if (sprintData.completion_rate !== undefined) {
                this.updateElement('completionRate', `${sprintData.completion_rate.toFixed(1)}%`);
                this.updateProgressBar('completionProgress', sprintData.completion_rate);
            }
            
            // Update task counts
            if (sprintData.total_tasks !== undefined) {
                this.updateElement('totalTasks', sprintData.total_tasks);
            }
            if (sprintData.completed_tasks !== undefined) {
                this.updateElement('completedTasks', sprintData.completed_tasks);
            }
            if (sprintData.in_progress_tasks !== undefined) {
                this.updateElement('inProgressTasks', sprintData.in_progress_tasks);
            }
            this.updateElement('pendingTasks', sprintData.pending_tasks || 0);
            
            // Update velocity - handle different possible structures
            if (sprintData.velocity) {
                this.updateElement('dailyVelocity', sprintData.velocity.daily_average || '--');
                this.updateElement('weeklyVelocity', sprintData.velocity.weekly_average || '--');
            } else if (sprintData.daily_velocity !== undefined) {
                this.updateElement('dailyVelocity', sprintData.daily_velocity);
            }
            
            // Update QA pass rate if available in main metrics
            if (sprintData.qa_pass_rate !== undefined) {
                this.updateElement('qaPassRate', `${sprintData.qa_pass_rate.toFixed(1)}%`);
            }
            
            // Update coverage if available in main metrics
            if (sprintData.average_coverage !== undefined) {
                this.updateElement('avgCoverage', `${sprintData.average_coverage.toFixed(1)}%`);
            }
            
        } catch (error) {
            console.error('Error updating metrics display:', error);
            console.error('Metrics data structure:', metrics);
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
            // Update main progress chart
            const progressChart = this.charts.progressChart;
            if (progressChart && metrics) {
                // Extract data from nested structure if needed
                let taskData = metrics;
                if (metrics.data && metrics.data.sprint) {
                    taskData = metrics.data.sprint;
                } else if (metrics.sprint) {
                    taskData = metrics.sprint;
                }
                
                // Update progress chart data
                progressChart.data.datasets[0].data = [
                    taskData.completed_tasks || 0,
                    taskData.in_progress_tasks || 0,
                    taskData.pending_tasks || 0,
                    taskData.failed_tasks || 0
                ];
                progressChart.update('none');
                console.log('Progress chart updated with data:', progressChart.data.datasets[0].data);
            }
            
            // Legacy chart handling for backward compatibility
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
            
        } catch (error) {
            console.error('Error updating charts:', error);
        }
    }
    
    updateSystemHealthDisplay(systemHealth) {
        try {
            if (!systemHealth || !systemHealth.data) return;
            
            const healthData = systemHealth.data;
            
            // Update overall system status
            const overallStatusElement = document.getElementById('overallSystemStatus');
            if (overallStatusElement) {
                overallStatusElement.textContent = healthData.overall_status || 'Unknown';
                overallStatusElement.className = `status-value status-${healthData.overall_status}`;
            }
            
            // Update component health statuses
            if (healthData.components) {
                Object.entries(healthData.components).forEach(([component, status]) => {
                    const componentElement = document.getElementById(`component-${component.replace('_', '-')}`);
                    if (componentElement) {
                        const statusText = status.status || 'unknown';
                        componentElement.textContent = statusText;
                        componentElement.className = `component-status status-${statusText}`;
                    }
                });
            }
            
            // Update performance metrics
            if (healthData.performance) {
                this.updateElement('cpu-usage', healthData.performance.cpu_usage);
                this.updateElement('memory-usage', healthData.performance.memory_usage);
                this.updateElement('api-response-time', healthData.performance.api_response_time);
            }
            
            // Update recommendations
            if (healthData.recommendations && healthData.recommendations.length > 0) {
                const recommendationsElement = document.getElementById('system-recommendations');
                if (recommendationsElement) {
                    recommendationsElement.innerHTML = healthData.recommendations
                        .map(rec => `<li class="recommendation-item">${rec}</li>`)
                        .join('');
                }
            }
            
            // Update automation monitoring state
            this.automationMonitoring.lastHealthCheck = healthData.last_full_check;
            this.automationMonitoring.systemComponents = healthData.components || {};
            
        } catch (error) {
            console.error('Error updating system health display:', error);
        }
    }
    
    updateTimelineDisplay(timelineData) {
        try {
            if (!timelineData || !timelineData.data) return;
            
            const timeline = timelineData.data;
            
            // Update timeline summary
            if (timeline.summary) {
                this.updateElement('timeline-total-days', timeline.summary.total_days);
                this.updateElement('timeline-completion', `${timeline.summary.current_completion}%`);
                this.updateElement('timeline-velocity', timeline.summary.average_velocity?.toFixed(1));
                this.updateElement('timeline-tasks-completed', timeline.summary.total_tasks_completed);
            }
            
            // Update timeline chart if available
            if (this.charts.timelineChart && timeline.timeline_events) {
                this.updateTimelineChart(timeline.timeline_events, timeline.milestones);
            }
            
        } catch (error) {
            console.error('Error updating timeline display:', error);
        }    }
    
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
            
            // Update progress text if it exists
            const progressText = document.getElementById('progressText');
            if (progressText) {
                progressText.textContent = `${percentage.toFixed(1)}%`;
            }
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
      updateBusinessMetrics(qaPassRateData, codeCoverageData, sprintVelocityData) {
        try {
            console.log('updateBusinessMetrics called with:', {
                qaPassRateData,
                codeCoverageData, 
                sprintVelocityData
            });

            // Update QA Pass Rate
            if (qaPassRateData && qaPassRateData.pass_rate !== undefined) {
                console.log('Updating QA Pass Rate:', qaPassRateData.pass_rate);
                this.updateElement('qaPassRate', `${qaPassRateData.pass_rate.toFixed(1)}%`);
                
                // Update change indicator if trend data available
                if (qaPassRateData.daily_trends && qaPassRateData.daily_trends.length >= 2) {
                    const latestTrend = qaPassRateData.daily_trends[qaPassRateData.daily_trends.length - 1];
                    const previousTrend = qaPassRateData.daily_trends[qaPassRateData.daily_trends.length - 2];
                    const change = latestTrend.pass_rate - previousTrend.pass_rate;
                    const changeElement = document.getElementById('qaChange');
                    if (changeElement) {
                        changeElement.textContent = `${change >= 0 ? '+' : ''}${change.toFixed(1)}%`;
                        changeElement.className = `metric-change ${change >= 0 ? 'change-positive' : 'change-negative'}`;
                    }
                }
            } else {
                console.warn('QA Pass Rate data missing or invalid:', qaPassRateData);
            }

            // Update Code Coverage
            if (codeCoverageData && codeCoverageData.overall_coverage !== undefined) {
                console.log('Updating Code Coverage:', codeCoverageData.overall_coverage);
                this.updateElement('avgCoverage', `${codeCoverageData.overall_coverage.toFixed(1)}%`);
                
                // Update change indicator if trend available
                if (codeCoverageData.trend_direction) {
                    const changeElement = document.getElementById('coverageChange');
                    if (changeElement) {
                        const change = codeCoverageData.coverage_change || 0;
                        changeElement.textContent = `${change >= 0 ? '+' : ''}${change.toFixed(1)}%`;
                        changeElement.className = `metric-change ${change >= 0 ? 'change-positive' : 'change-negative'}`;
                    }
                }
            } else {
                console.warn('Code Coverage data missing or invalid:', codeCoverageData);
            }

            // Update Sprint Velocity
            if (sprintVelocityData && sprintVelocityData.current_velocity !== undefined) {
                console.log('Updating Sprint Velocity:', sprintVelocityData.current_velocity);
                this.updateElement('sprintVelocity', sprintVelocityData.current_velocity.toFixed(1));
                
                // Update change indicator based on velocity trend
                if (sprintVelocityData.sprint_history && sprintVelocityData.sprint_history.length >= 2) {
                    const latest = sprintVelocityData.sprint_history[sprintVelocityData.sprint_history.length - 1];
                    const previous = sprintVelocityData.sprint_history[sprintVelocityData.sprint_history.length - 2];
                    const change = latest.completed_points - previous.completed_points;
                    const changeElement = document.getElementById('velocityChange');
                    if (changeElement) {
                        changeElement.textContent = `${change >= 0 ? '+' : ''}${change.toFixed(1)}`;
                        changeElement.className = `metric-change ${change >= 0 ? 'change-positive' : 'change-negative'}`;
                    }
                }
            } else {
                console.warn('Sprint Velocity data missing or invalid:', sprintVelocityData);
            }

            console.log('Business metrics updated successfully');
        } catch (error) {
            console.error('Error updating business metrics:', error);
        }
    }    updateBusinessCharts(qaPassRateData, codeCoverageData, sprintVelocityData, completionTrendData, qaResultsData, coverageTrendData) {
        try {
            // Update QA Results Chart
            this.updateQaChart(qaResultsData);
            
            // Update Code Coverage Trend Chart
            this.updateCoverageChart(coverageTrendData);
            
            // Update Sprint Velocity Chart (Main Dashboard)
            this.updateVelocityChart(sprintVelocityData);
            
            // Update Timeline Chart
            this.updateTimelineChart(sprintVelocityData, completionTrendData);

            console.log('Business charts updated successfully');
        } catch (error) {
            console.error('Error updating business charts:', error);
        }
    }

    updateQaChart(qaResultsData) {
        try {
            const qaChart = this.charts.qaChart || this.getOrCreateChart('qaChart', 'bar');
            
            if (qaResultsData && qaResultsData.test_summary) {
                const summary = qaResultsData.test_summary;
                qaChart.data.datasets[0].data = [
                    summary.passed,
                    summary.failed,
                    summary.skipped || 0
                ];
                qaChart.update('none');
                
                console.log('QA Chart updated with real data');
            }
        } catch (error) {
            console.error('Error updating QA chart:', error);
        }
    }

    updateCoverageChart(coverageTrendData) {
        try {
            const coverageChart = this.charts.coverageChart || this.getOrCreateChart('coverageChart', 'line');
            
            if (coverageTrendData && coverageTrendData.coverage_history) {
                const history = coverageTrendData.coverage_history;
                coverageChart.data.labels = history.map(item => item.date);
                coverageChart.data.datasets[0].data = history.map(item => item.coverage_percentage);
                coverageChart.update('none');
                
                console.log('Coverage Chart updated with real data');
            }
        } catch (error) {
            console.error('Error updating coverage chart:', error);
        }
    }

    updateTimelineChart(sprintVelocityData, completionTrendData) {
        try {
            const timelineChart = this.charts.timelineChart || this.getOrCreateChart('timelineChart', 'line');
            
            if (sprintVelocityData && sprintVelocityData.sprint_history) {
                const history = sprintVelocityData.sprint_history;
                timelineChart.data.labels = history.map(item => `Sprint ${item.sprint_id}`);
                
                // Update velocity data
                if (timelineChart.data.datasets[0]) {
                    timelineChart.data.datasets[0].data = history.map(item => item.completed_points);
                    timelineChart.data.datasets[0].label = 'Completed Points';
                }
                
                // Update completion rate data if second dataset exists
                if (timelineChart.data.datasets[1]) {
                    timelineChart.data.datasets[1].data = history.map(item => item.completion_rate);
                    timelineChart.data.datasets[1].label = 'Completion Rate %';
                }
                
                timelineChart.update('none');
                
                // Update timeline summary metrics
                if (sprintVelocityData.average_velocity !== undefined) {
                    this.updateElement('timeline-avg-velocity', sprintVelocityData.average_velocity.toFixed(1));
                }
                
                console.log('Timeline Chart updated with real data');
            }
        } catch (error) {
            console.error('Error updating timeline chart:', error);
        }
    }    getOrCreateChart(canvasId, chartType) {
        // Try to get existing chart from this.charts
        if (this.charts[canvasId]) {
            return this.charts[canvasId];
        }
        
        // Try to get chart from global scope (unified dashboard)
        if (typeof window !== 'undefined') {
            const globalChart = window[canvasId];
            if (globalChart) {
                this.charts[canvasId] = globalChart;
                return globalChart;
            }
        }
        
        // Try to create chart if canvas exists
        const canvas = document.getElementById(canvasId);
        if (canvas) {
            const ctx = canvas.getContext('2d');
            let chartConfig;
            
            // Create appropriate chart configuration
            switch (chartType) {
                case 'bar':
                    chartConfig = {
                        type: 'bar',
                        data: {
                            labels: [],
                            datasets: [{
                                label: 'Data',
                                data: [],
                                backgroundColor: ['#28a745', '#dc3545', '#6c757d']
                            }]
                        },
                        options: {
                            responsive: true,
                            maintainAspectRatio: false
                        }
                    };
                    break;
                case 'line':
                    chartConfig = {
                        type: 'line',
                        data: {
                            labels: [],
                            datasets: [{
                                label: 'Data',
                                data: [],
                                borderColor: '#2196F3',
                                backgroundColor: 'rgba(33, 150, 243, 0.1)',
                                fill: true
                            }]
                        },
                        options: {
                            responsive: true,
                            maintainAspectRatio: false
                        }
                    };
                    break;
                default:
                    chartConfig = {
                        type: chartType,
                        data: { labels: [], datasets: [{ data: [] }] },
                        options: { responsive: true, maintainAspectRatio: false }
                    };
            }
            
            try {
                const chart = new Chart(ctx, chartConfig);
                this.charts[canvasId] = chart;
                return chart;
            } catch (error) {
                console.error(`Error creating chart ${canvasId}:`, error);
            }
        }
        
        // Return a simple mock object if all else fails
        return {
            data: {
                labels: [],
                datasets: [{ data: [] }, { data: [] }]
            },
            update: (mode) => {
                console.log(`Chart ${canvasId} update called (mode: ${mode})`);
            }
        };
    }

    // Phase 6 Step 6.5 Enhanced Charts Initialization
    initializeEnhancedCharts() {
        console.log('Initializing Phase 6 Step 6.5 Enhanced Visual Progress Charts...');
        
        try {
            // Initialize main dashboard charts first
            this.initializeMainDashboardCharts();
            
            // Initialize Daily Automation Chart
            this.initializeDailyAutomationChart();
            
            // Initialize Velocity Tracking Chart
            this.initializeVelocityTrackingChart();
            
            // Initialize Interactive Timeline Chart
            this.initializeInteractiveTimelineChart();
            
            // Initialize Sprint Health Chart
            this.initializeSprintHealthChart();
              // Initialize Critical Path Chart
            this.initializeCriticalPathChart();
            
            // Initialize Progress Summary Charts
            this.initializeOverallStatusDoughnutChart();
            this.initializeTasksByDayStackedChart();
            this.initializeTasksByOwnerStackedChart();
            this.initializeTrendAnalysisChart();
            
            // Set up enhanced charts update interval
            this.setupEnhancedChartsRefresh();
            
            console.log('Enhanced charts initialization complete');
        } catch (error) {
            console.error('Error initializing enhanced charts:', error);
        }
    }    // Initialize the main dashboard charts that are referenced in HTML
    initializeMainDashboardCharts() {
        console.log('Initializing main dashboard charts...');
        
        // Initialize Progress Chart
        this.initializeProgressChart();
        
        // Initialize QA Chart
        this.initializeQAChart();
        
        // Initialize Velocity Chart
        this.initializeVelocityChart();
        
        // Initialize Timeline Chart
        this.initializeTimelineChart();
        
        console.log('Main dashboard charts initialized');
    }

    initializeProgressChart() {
        const canvas = document.getElementById('progressChart');
        if (!canvas) {
            console.warn('Progress chart canvas not found');
            return;
        }

        const ctx = canvas.getContext('2d');
        this.charts.progressChart = new Chart(ctx, {
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
        });
        
        console.log('Progress Chart initialized');
    }

    initializeQAChart() {
        const canvas = document.getElementById('qaChart');
        if (!canvas) {
            console.warn('QA chart canvas not found');
            return;
        }

        const ctx = canvas.getContext('2d');
        this.charts.qaChart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: ['Passed', 'Failed', 'Skipped'],
                datasets: [{
                    label: 'Test Results',
                    data: [0, 0, 0],
                    backgroundColor: [
                        '#4CAF50',  // Green for passed
                        '#F44336'  // Red for failed
                    ],
                    borderWidth: 1,
                    borderColor: '#ffffff'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    },
                    title: {
                        display: true,
                        text: 'QA Test Results'
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: 'Number of Tests'
                        }
                    }
                }
            }
        });
        
        console.log('QA Chart initialized');
    }

    initializeVelocityChart() {
        const canvas = document.getElementById('velocityChart');
        if (!canvas) {
            console.warn('Velocity chart canvas not found');
            return;
        }

        const ctx = canvas.getContext('2d');
        this.charts.velocityChart = new Chart(ctx, {
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
                    label: 'Weekly Average',
                    data: [],
                    borderColor: '#4CAF50',
                    backgroundColor: 'rgba(76, 175, 80, 0.1)',
                    fill: false,
                    borderDash: [5, 5]
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    title: {
                        display: true,
                        text: 'Team Velocity Trend'
                    },
                    legend: {
                        display: true,
                        position: 'top'
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: 'Points Completed'
                        }
                    },
                    x: {
                        title: {
                            display: true,
                            text: 'Time Period'
                        }
                    }
                }
            }
        });
          console.log('Velocity Chart initialized');
    }

    initializeTimelineChart() {
        const canvas = document.getElementById('timelineChart');
        if (!canvas) {
            console.warn('Timeline chart canvas not found');
            return;
        }

        const ctx = canvas.getContext('2d');
        this.charts.timelineChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: [],
                datasets: [{
                    label: 'Sprint Progress',
                    data: [],
                    borderColor: '#FF9800',
                    backgroundColor: 'rgba(255, 152, 0, 0.1)',
                    fill: true,
                    tension: 0.4
                }, {
                    label: 'Target Progress',
                    data: [],
                    borderColor: '#E0E0E0',
                    backgroundColor: 'rgba(224, 224, 224, 0.1)',
                    fill: false,
                    borderDash: [5, 5]
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    title: {
                        display: true,
                        text: 'Sprint Timeline Progress'
                    },
                    legend: {
                        display: true,
                        position: 'top'
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        max: 100,
                        title: {
                            display: true,
                            text: 'Progress (%)'
                        }
                    },
                    x: {
                        title: {
                            display: true,
                            text: 'Days'
                        }
                    }
                }
            }
        });
        
        console.log('Timeline Chart initialized');
    }
    
    initializeDailyAutomationChart() {
        const canvas = document.getElementById('dailyAutomationChart');
        if (!canvas) return;

        const ctx = canvas.getContext('2d');
        this.enhancedCharts.dailyAutomationChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: [],
                datasets: [{
                    label: 'Daily Cycles',
                    data: [],
                    borderColor: '#667eea',
                    backgroundColor: 'rgba(102, 126, 234, 0.1)',
                    fill: true,
                    tension: 0.4
                }, {
                    label: 'Success Rate %',
                    data: [],
                    borderColor: '#28a745',
                    backgroundColor: 'rgba(40, 167, 69, 0.1)',
                    fill: false,
                    yAxisID: 'y1'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                interaction: {
                    mode: 'index',
                    intersect: false,
                },
                scales: {
                    y: {
                        type: 'linear',
                        display: true,
                        position: 'left',
                        title: {
                            display: true,
                            text: 'Cycles Count'
                        }
                    },
                    y1: {
                        type: 'linear',
                        display: true,
                        position: 'right',
                        title: {
                            display: true,
                            text: 'Success Rate %'
                        },
                        grid: {
                            drawOnChartArea: false,
                        },
                        min: 0,
                        max: 100
                    }
                },
                plugins: {
                    title: {
                        display: true,
                        text: 'Daily Automation Timeline'
                    },
                    legend: {
                        display: true,
                        position: 'top'
                    }
                }
            }
        });
    }

    initializeVelocityTrackingChart() {
        const canvas = document.getElementById('velocityTrackingChart');
        if (!canvas) return;

        const ctx = canvas.getContext('2d');
        this.enhancedCharts.velocityTrackingChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: [],
                datasets: [{
                    label: 'Actual Velocity',
                    data: [],
                    borderColor: '#2196F3',
                    backgroundColor: 'rgba(33, 150, 243, 0.1)',
                    fill: true,
                    tension: 0.4
                }, {
                    label: 'Predicted Velocity',
                    data: [],
                    borderColor: '#ff9800',
                    backgroundColor: 'rgba(255, 152, 0, 0.1)',
                    fill: false,
                    borderDash: [5, 5]
                }, {
                    label: 'Target Velocity',
                    data: [],
                    borderColor: '#4caf50',
                    backgroundColor: 'transparent',
                    fill: false,
                    borderDash: [10, 5]
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                interaction: {
                    mode: 'index',
                    intersect: false,
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: 'Story Points / Tasks'
                        }
                    }
                },
                plugins: {
                    title: {
                        display: true,
                        text: 'Velocity Tracking & Predictions'
                    },
                    tooltip: {
                        callbacks: {
                            afterLabel: function(context) {
                                if (context.datasetIndex === 1) {
                                    return 'Confidence: 85%';
                                }
                                return '';
                            }
                        }
                    }
                }
            }
        });
    }

    initializeInteractiveTimelineChart() {
        const canvas = document.getElementById('interactiveTimelineChart');
        if (!canvas) return;

        const ctx = canvas.getContext('2d');
        this.enhancedCharts.interactiveTimelineChart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: [],
                datasets: [{
                    label: 'Completed Tasks',
                    data: [],
                    backgroundColor: '#28a745',
                    borderColor: '#155724',
                    borderWidth: 1
                }, {
                    label: 'In Progress Tasks',
                    data: [],
                    backgroundColor: '#ffc107',
                    borderColor: '#856404',
                    borderWidth: 1
                }, {
                    label: 'Blocked Tasks',
                    data: [],
                    backgroundColor: '#dc3545',
                    borderColor: '#721c24',
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    title: {
                        display: true,
                        text: 'Interactive Daily Timeline'
                    }
                },
                scales: {
                    x: {
                        stacked: true,
                        title: {
                            display: true,
                            text: 'Date'
                        }
                    },
                    y: {
                        stacked: true,
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: 'Task Count'
                        }
                    }
                },
                onClick: (event, elements) => {
                    if (elements.length > 0) {
                        const element = elements[0];
                        const dataIndex = element.index;
                        const date = this.enhancedCharts.interactiveTimelineChart.data.labels[dataIndex];
                        this.showTimelineDetails(date);
                    }
                }
            }
        });
    }

    initializeSprintHealthChart() {
        const canvas = document.getElementById('sprintHealthChart');
        if (!canvas) return;

        const ctx = canvas.getContext('2d');
        this.enhancedCharts.sprintHealthChart = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: ['Excellent', 'Good', 'Fair', 'Needs Attention'],
                datasets: [{
                    data: [0, 0, 0, 0],
                    backgroundColor: [
                        '#28a745',  // Green - Excellent
                        '#17a2b8',  // Blue - Good  
                        '#ffc107',  // Yellow - Fair
                        '#dc3545'   // Red - Needs Attention
                    ],
                    borderWidth: 2,
                    borderColor: '#ffffff'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    title: {
                        display: true,
                        text: 'Sprint Health Indicators'
                    },
                    legend: {
                        display: true,
                        position: 'bottom'
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                const label = context.label || '';
                                const value = context.parsed || 0;
                                return `${label}: ${value.toFixed(1)}%`;
                            }
                        }
                    }
                },
                cutout: '50%'
            }
        });
    }

    initializeCriticalPathChart() {
        const canvas = document.getElementById('criticalPathChart');
        if (!canvas) return;

        const ctx = canvas.getContext('2d');
        this.enhancedCharts.criticalPathChart = new Chart(ctx, {
            type: 'scatter',
            data: {
                datasets: [{
                    label: 'Critical Tasks',
                    data: [],
                    backgroundColor: '#dc3545',
                    borderColor: '#721c24',
                    pointRadius: 8,
                    pointHoverRadius: 12
                }, {
                    label: 'Normal Tasks',
                    data: [],
                    backgroundColor: '#28a745',
                    borderColor: '#155724',
                    pointRadius: 6,
                    pointHoverRadius: 10
                }, {
                    label: 'Dependencies',
                    data: [],
                    showLine: true,
                    borderColor: '#6c757d',
                    borderDash: [5, 5],
                    pointRadius: 0,
                    fill: false
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    title: {
                        display: true,
                        text: 'Critical Path Visualization'
                    },
                    tooltip: {
                        callbacks: {
                            title: function(tooltipItems) {
                                return `Task: ${tooltipItems[0].raw.taskName || 'Unknown'}`;
                            },
                            label: function(context) {
                                const point = context.raw;
                                return [
                                    `Duration: ${point.x} days`,
                                    `Priority: ${point.y}`,
                                    `Risk Level: ${point.riskLevel || 'Low'}`
                                ];
                            }
                        }
                    }
                },
                scales: {
                    x: {
                        title: {
                            display: true,
                            text: 'Duration (Days)'
                        }
                    },
                    y: {
                        title: {
                            display: true,
                            text: 'Priority Level'
                        }
                    }
                }            }
        });
    }

    initializeOverallStatusDoughnutChart() {
        const canvas = document.getElementById('overallStatusDoughnutChart');
        if (!canvas) return;

        const ctx = canvas.getContext('2d');
        this.enhancedCharts.overallStatusDoughnutChart = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: ['Completed', 'In Progress', 'Blocked', 'To Do'],
                datasets: [{
                    data: [0, 0, 0, 0],
                    backgroundColor: [
                        '#28a745',  // Green - Completed
                        '#ffc107',  // Yellow - In Progress  
                        '#dc3545',  // Red - Blocked
                        '#6c757d'   // Gray - To Do
                    ],
                    borderWidth: 2,
                    borderColor: '#ffffff'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    title: {
                        display: true,
                        text: 'Overall Task Status'
                    },
                    legend: {
                        display: true,
                        position: 'bottom'
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                const label = context.label || '';
                                const value = context.parsed || 0;
                                const total = context.dataset.data.reduce((a, b) => a + b, 0);
                                const percentage = total > 0 ? ((value / total) * 100).toFixed(1) : '0.0';
                                return `${label}: ${value} (${percentage}%)`;
                            }
                        }
                    }
                },
                cutout: '50%'
            }
        });
    }

    initializeTasksByDayStackedChart() {
        const canvas = document.getElementById('tasksByDayStackedChart');
        if (!canvas) return;

        const ctx = canvas.getContext('2d');
        this.enhancedCharts.tasksByDayStackedChart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: [],
                datasets: [{
                    label: 'Completed',
                    data: [],
                    backgroundColor: '#28a745',
                    borderColor: '#155724',
                    borderWidth: 1
                }, {
                    label: 'In Progress',
                    data: [],
                    backgroundColor: '#ffc107',
                    borderColor: '#856404',
                    borderWidth: 1
                }, {
                    label: 'Blocked',
                    data: [],
                    backgroundColor: '#dc3545',
                    borderColor: '#721c24',
                    borderWidth: 1
                }, {
                    label: 'To Do',
                    data: [],
                    backgroundColor: '#6c757d',
                    borderColor: '#495057',
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    title: {
                        display: true,
                        text: 'Tasks by Day'
                    }
                },
                scales: {
                    x: {
                        stacked: true,
                        title: {
                            display: true,
                            text: 'Date'
                        }
                    },
                    y: {
                        stacked: true,
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: 'Task Count'
                        }
                    }
                }
            }
        });
    }

    initializeTasksByOwnerStackedChart() {
        const canvas = document.getElementById('tasksByOwnerStackedChart');
        if (!canvas) return;

        const ctx = canvas.getContext('2d');
        this.enhancedCharts.tasksByOwnerStackedChart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: [],
                datasets: [{
                    label: 'Completed',
                    data: [],
                    backgroundColor: '#28a745',
                    borderColor: '#155724',
                    borderWidth: 1
                }, {
                    label: 'In Progress',
                    data: [],
                    backgroundColor: '#ffc107',
                    borderColor: '#856404',
                    borderWidth: 1
                }, {
                    label: 'Blocked',
                    data: [],
                    backgroundColor: '#dc3545',
                    borderColor: '#721c24',
                    borderWidth: 1
                }, {
                    label: 'To Do',
                    data: [],
                    backgroundColor: '#6c757d',
                    borderColor: '#495057',
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    title: {
                        display: true,
                        text: 'Tasks by Owner'
                    }
                },
                scales: {
                    x: {
                        stacked: true,
                        title: {
                            display: true,
                            text: 'Owner'
                        }
                    },
                    y: {
                        stacked: true,
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: 'Task Count'
                        }
                    }
                }
            }
        });
    }

    initializeTrendAnalysisChart() {
        const canvas = document.getElementById('trendAnalysisChart');
        if (!canvas) return;

        const ctx = canvas.getContext('2d');
        this.enhancedCharts.trendAnalysisChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: [],
                datasets: [{
                    label: 'Completion Rate',
                    data: [],
                    borderColor: '#28a745',
                    backgroundColor: 'rgba(40, 167, 69, 0.1)',
                    fill: true,
                    tension: 0.4
                }, {
                    label: 'Velocity',
                    data: [],
                    borderColor: '#2196F3',
                    backgroundColor: 'rgba(33, 150, 243, 0.1)',
                    fill: false,
                    yAxisID: 'y1'
                }, {
                    label: 'Predicted Trend',
                    data: [],
                    borderColor: '#ff9800',
                    backgroundColor: 'transparent',
                    fill: false,
                    borderDash: [5, 5]
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                interaction: {
                    mode: 'index',
                    intersect: false,
                },
                scales: {
                    y: {
                        type: 'linear',
                        display: true,
                        position: 'left',
                        title: {
                            display: true,
                            text: 'Completion Rate %'
                        },
                        min: 0,
                        max: 100
                    },
                    y1: {
                        type: 'linear',
                        display: true,
                        position: 'right',
                        title: {
                            display: true,
                            text: 'Velocity'
                        },
                        grid: {
                            drawOnChartArea: false,
                        }
                    }
                },
                plugins: {
                    title: {
                        display: true,
                        text: 'Trend Analysis & Predictions'
                    },
                    legend: {
                        display: true,
                        position: 'top'
                    }
                }
            }
        });
    }

    setupEnhancedChartsRefresh() {
        // Update enhanced charts every 2 minutes
        setInterval(() => {
            this.updateEnhancedCharts();
        }, 120000);
        
        // Initial update
        setTimeout(() => {
            this.updateEnhancedCharts();
        }, 2000);
    }    async updateEnhancedCharts() {
        try {
            console.log('Updating enhanced charts...');
            
            // Fetch enhanced chart data
            const [
                dailyAutomationData,
                velocityData,
                timelineData,
                healthData,
                criticalPathData,
                progressSummaryData
            ] = await Promise.all([
                this.fetchEnhancedData('/api/visualization/daily_automation'),
                this.fetchEnhancedData('/api/visualization/velocity_tracking'),
                this.fetchEnhancedData('/api/visualization/interactive_timeline'),
                this.fetchEnhancedData('/api/visualization/sprint_health'),
                this.fetchEnhancedData('/api/visualization/critical_path'),
                this.fetchEnhancedData('/api/visualization/progress_summary')
            ]);

            // Update charts with new data
            this.updateDailyAutomationChart(dailyAutomationData);
            this.updateVelocityTrackingChart(velocityData);
            this.updateInteractiveTimelineChart(timelineData);
            this.updateSprintHealthChart(healthData);
            this.updateCriticalPathChart(criticalPathData);
            
            // Update Phase 6 Step 6.5 Progress Summary Charts
            this.updateOverallStatusDoughnutChart(progressSummaryData);
            this.updateTasksByDayStackedChart(progressSummaryData);
            this.updateTasksByOwnerStackedChart(progressSummaryData);
            this.updateTrendAnalysisChart(progressSummaryData);
            
            // Update enhanced metrics display
            this.updateEnhancedMetrics(dailyAutomationData, velocityData, healthData);
            
            console.log('Enhanced charts updated successfully');
        } catch (error) {
            console.error('Error updating enhanced charts:', error);
            this.showEnhancedChartsError();
        }
    }// Use the consolidated fetchData method instead of duplicate fetchEnhancedData
    async fetchEnhancedData(endpoint) {
        return await this.fetchData(endpoint, { allowFailure: true, dataOnly: true });
    }

    updateDailyAutomationChart(data) {
        if (!data || !this.enhancedCharts.dailyAutomationChart) return;

        const chart = this.enhancedCharts.dailyAutomationChart;
        const cycleData = data.daily_cycles || [];
        
        const labels = cycleData.map(cycle => cycle.date);
        const cyclesCounts = cycleData.map(cycle => cycle.cycles_completed || 0);
        const successRates = cycleData.map(cycle => cycle.success_rate || 0);
        
        chart.data.labels = labels;
        chart.data.datasets[0].data = cyclesCounts;
        chart.data.datasets[1].data = successRates;
        chart.update('none');
        
        // Update daily automation metrics
        if (data.automation_metrics) {
            this.updateElement('daily-cycles-count', data.automation_metrics.total_cycles || 0);
            this.updateElement('daily-success-rate', `${(data.automation_metrics.average_success_rate || 0).toFixed(1)}%`);
            this.updateElement('daily-duration', `${(data.automation_metrics.average_duration || 0).toFixed(1)}m`);
            this.updateElement('daily-next-cycle', data.automation_metrics.next_cycle_time || '--:--');
        }
    }

    updateVelocityTrackingChart(data) {
        if (!data || !this.enhancedCharts.velocityTrackingChart) return;

        const chart = this.enhancedCharts.velocityTrackingChart;
        const velocityHistory = data.velocity_history || [];
        
        const labels = velocityHistory.map(item => item.date);
        const actualVelocity = velocityHistory.map(item => item.actual_velocity || 0);
        const predictedVelocity = data.predictions ? data.predictions.predicted_values || [] : [];
        const targetVelocity = velocityHistory.map(() => data.target_velocity || 0);
        
        chart.data.labels = labels;
        chart.data.datasets[0].data = actualVelocity;
        chart.data.datasets[1].data = predictedVelocity;
        chart.data.datasets[2].data = targetVelocity;
        chart.update('none');
        
        // Update velocity metrics
        if (data.velocity_summary) {
            this.updateElement('velocity-current', `${(data.velocity_summary.current_velocity || 0).toFixed(1)}`);
            this.updateElement('velocity-trend', data.velocity_summary.trend_direction || 'stable');
            this.updateElement('velocity-prediction', `${(data.velocity_summary.next_week_prediction || 0).toFixed(1)}`);
            this.updateElement('velocity-confidence', `${(data.velocity_summary.confidence_level || 0).toFixed(1)}%`);
        }
    }

    updateInteractiveTimelineChart(data) {
        if (!data || !this.enhancedCharts.interactiveTimelineChart) return;

        const chart = this.enhancedCharts.interactiveTimelineChart;
        const timelineEvents = data.timeline_events || [];
        
        const labels = timelineEvents.map(event => event.date);
        const completedTasks = timelineEvents.map(event => event.completed_tasks || 0);
        const inProgressTasks = timelineEvents.map(event => event.in_progress_tasks || 0);
        const blockedTasks = timelineEvents.map(event => event.blocked_tasks || 0);
        
        chart.data.labels = labels;
        chart.data.datasets[0].data = completedTasks;
        chart.data.datasets[1].data = inProgressTasks;
        chart.data.datasets[2].data = blockedTasks;
        chart.update('none');
        
        // Update timeline metrics
        if (data.timeline_summary) {
            this.updateElement('timeline-total-events', data.timeline_summary.total_events || 0);
            this.updateElement('timeline-completion-rate', `${(data.timeline_summary.completion_rate || 0).toFixed(1)}%`);
            this.updateElement('timeline-trend', data.timeline_summary.trend || 'stable');
            this.updateElement('timeline-avg-velocity', `${(data.timeline_summary.average_velocity || 0).toFixed(1)}`);
        }
    }

    updateSprintHealthChart(data) {
        if (!data || !this.enhancedCharts.sprintHealthChart) return;

        const chart = this.enhancedCharts.sprintHealthChart;
        const healthIndicators = data.health_indicators || {};
        
        // Calculate health distribution based on various factors
        const overallHealth = healthIndicators.overall_health || 0;
        const healthDistribution = this.calculateHealthDistribution(overallHealth, healthIndicators);
        
        chart.data.datasets[0].data = [
            healthDistribution.excellent,
            healthDistribution.good,
            healthDistribution.fair,
            healthDistribution.needs_attention
        ];
        chart.update('none');
        
        // Update health gauge display
        this.updateHealthGauge(overallHealth);
        
        // Update component health bars
        this.updateComponentHealthBars(healthIndicators);
    }

    updateCriticalPathChart(data) {
        if (!data || !this.enhancedCharts.criticalPathChart) return;

        const chart = this.enhancedCharts.criticalPathChart;
        const criticalTasks = data.critical_tasks || [];
        const normalTasks = data.normal_tasks || [];
        const dependencies = data.dependencies || [];
        
        chart.data.datasets[0].data = criticalTasks.map(task => ({
            x: task.duration,
            y: task.priority,
            taskName: task.name,
            riskLevel: task.risk_level
        }));
        
        chart.data.datasets[1].data = normalTasks.map(task => ({
            x: task.duration,
            y: task.priority,
            taskName: task.name,
            riskLevel: task.risk_level
        }));
        
        chart.data.datasets[2].data = dependencies.map(dep => ({
            x: dep.x,
            y: dep.y
        }));
        
        chart.update('none');
        
        // Update critical path metrics
        if (data.critical_path_summary) {
            this.updateElement('critical-tasks-count', data.critical_path_summary.critical_tasks_count || 0);
            this.updateElement('critical-path-health', `${(data.critical_path_summary.health_score || 0).toFixed(1)}%`);
            this.updateElement('risk-assessment', data.critical_path_summary.risk_level || 'Low');
        }
    }

    calculateHealthDistribution(overallHealth, indicators) {
        // Simulate health distribution based on overall health score
        if (overallHealth >= 85) {
            return { excellent: 70, good: 25, fair: 5, needs_attention: 0 };
        } else if (overallHealth >= 70) {
            return { excellent: 40, good: 45, fair: 15, needs_attention: 0 };
        } else if (overallHealth >= 55) {
            return { excellent: 20, good: 35, fair: 35, needs_attention: 10 };
        } else {
            return { excellent: 10, good: 20, fair: 30, needs_attention: 40 };
        }
    }

    updateHealthGauge(healthScore) {
        const gaugeElement = document.querySelector('.health-gauge');
        if (!gaugeElement) return;
        
        const percentage = Math.max(0, Math.min(100, healthScore));
        const angle = (percentage / 100) * 360;
        
        gaugeElement.style.background = `conic-gradient(
            #28a745 0deg ${angle * 0.6}deg,
            #ffc107 ${angle * 0.6}deg ${angle * 0.8}deg,
            #dc3545 ${angle * 0.8}deg ${angle}deg,
            #e9ecef ${angle}deg 360deg
        )`;
        
        const scoreElement = gaugeElement.querySelector('.gauge-score');
        if (scoreElement) {
            scoreElement.textContent = `${percentage.toFixed(0)}%`;
        }
        
        const statusElement = gaugeElement.querySelector('.gauge-status');
        if (statusElement) {
            if (percentage >= 85) {
                statusElement.textContent = 'Excellent';
                statusElement.className = 'gauge-status status-excellent';
            } else if (percentage >= 70) {
                statusElement.textContent = 'Good';
                statusElement.className = 'gauge-status status-good';
            } else if (percentage >= 55) {
                statusElement.textContent = 'Fair';
                statusElement.className = 'gauge-status status-fair';
            } else {
                statusElement.textContent = 'Needs Attention';
                statusElement.className = 'gauge-status status-attention';
            }
        }
    }

    updateComponentHealthBars(healthIndicators) {
        const components = ['completion', 'velocity', 'quality', 'automation'];
        
        components.forEach(component => {
            const barElement = document.getElementById(`health-${component}-bar`);
            const valueElement = document.getElementById(`health-${component}-value`);
            
            if (barElement && valueElement) {
                const healthValue = healthIndicators[`${component}_health`] || 0;
                const fillElement = barElement.querySelector('.component-fill');
                
                if (fillElement) {
                    fillElement.style.width = `${healthValue}%`;
                    
                    // Set color based on health value
                    if (healthValue >= 80) {
                        fillElement.style.backgroundColor = '#28a745';
                    } else if (healthValue >= 60) {
                        fillElement.style.backgroundColor = '#ffc107';
                    } else {
                        fillElement.style.backgroundColor = '#dc3545';
                    }
                }
                
                valueElement.textContent = `${healthValue.toFixed(1)}%`;
            }
        });
    }

    updateEnhancedMetrics(automationData, velocityData, healthData) {
        // Update enhanced charts summary
        if (automationData && automationData.automation_metrics) {
            this.updateElement('enhanced-uptime', `${(automationData.automation_metrics.uptime_percentage || 0).toFixed(1)}%`);
        }
        
        if (velocityData && velocityData.velocity_summary) {
            this.updateElement('enhanced-velocity', `${(velocityData.velocity_summary.current_velocity || 0).toFixed(1)}`);
        }
        
        if (healthData && healthData.health_indicators) {
            this.updateElement('enhanced-health', `${(healthData.health_indicators.overall_health || 0).toFixed(1)}%`);
        }
        
        // Update last refresh time for enhanced section
        const enhancedLastUpdate = document.getElementById('enhanced-last-update');
        if (enhancedLastUpdate) {
            enhancedLastUpdate.textContent = `Last updated: ${new Date().toLocaleTimeString()}`;
        }
    }

    showTimelineDetails(date) {
        // Show detailed timeline information for the selected date
        const modal = document.createElement('div');
        modal.className = 'timeline-modal';
        modal.innerHTML = `
            <div class="modal-content">
                <div class="modal-header">
                    <h3>Timeline Details - ${date}</h3>
                    <button class="modal-close">&times;</button>
                </div>
                <div class="modal-body">
                    <p>Detailed timeline information for ${date} would be displayed here.</p>
                    <p>This could include task details, automation events, and performance metrics.</p>
                </div>
            </div>
        `;
        
        modal.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.5);
            display: flex;
            justify-content: center;
            align-items: center;
            z-index: 1000;
        `;
        
        modal.querySelector('.modal-content').style.cssText = `
            background: white;
            padding: 20px;
            border-radius: 8px;
            max-width: 500px;
            width: 90%;
        `;
        
        modal.querySelector('.modal-close').addEventListener('click', () => {
            document.body.removeChild(modal);
        });
        
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                document.body.removeChild(modal);
            }
        });
        
        document.body.appendChild(modal);
    }

    showEnhancedChartsError() {
        const errorElements = document.querySelectorAll('.chart-status');
        errorElements.forEach(element => {
            element.textContent = 'Loading failed';
            element.className = 'chart-status status-error';
        });
    }

    // Update methods for Phase 6 Step 6.5 Progress Summary Charts
    updateOverallStatusDoughnutChart(data) {
        if (!data || !this.enhancedCharts.overallStatusDoughnutChart) return;

        const chart = this.enhancedCharts.overallStatusDoughnutChart;
        const overallStatus = data.overall_status || {};
        
        chart.data.datasets[0].data = [
            overallStatus.completed || 0,
            overallStatus.in_progress || 0,
            overallStatus.blocked || 0,
            overallStatus.todo || 0
        ];
        chart.update('none');
        
        // Update summary cards
        if (data.summary_metrics) {
            this.updateElement('summary-completed', overallStatus.completed || 0);
            this.updateElement('summary-in-progress', overallStatus.in_progress || 0);
            this.updateElement('summary-blocked', overallStatus.blocked || 0);
            this.updateElement('summary-todo', overallStatus.todo || 0);
        }
    }

    updateTasksByDayStackedChart(data) {
        if (!data || !this.enhancedCharts.tasksByDayStackedChart) return;

        const chart = this.enhancedCharts.tasksByDayStackedChart;
        const dailyBreakdown = data.daily_breakdown || [];
        
        const labels = dailyBreakdown.map(day => day.date);
        const completedData = dailyBreakdown.map(day => day.completed || 0);
        const inProgressData = dailyBreakdown.map(day => day.in_progress || 0);
        const blockedData = dailyBreakdown.map(day => day.blocked || 0);
        const todoData = dailyBreakdown.map(day => day.todo || 0);
        
        chart.data.labels = labels;
        chart.data.datasets[0].data = completedData;
        chart.data.datasets[1].data = inProgressData;
        chart.data.datasets[2].data = blockedData;
        chart.data.datasets[3].data = todoData;
        chart.update('none');
    }

    updateTasksByOwnerStackedChart(data) {
        if (!data || !this.enhancedCharts.tasksByOwnerStackedChart) return;

        const chart = this.enhancedCharts.tasksByOwnerStackedChart;
        const ownerBreakdown = data.owner_breakdown || [];
        
        const labels = ownerBreakdown.map(owner => owner.owner);
        const completedData = ownerBreakdown.map(owner => owner.completed || 0);
        const inProgressData = ownerBreakdown.map(owner => owner.in_progress || 0);
        const blockedData = ownerBreakdown.map(owner => owner.blocked || 0);
        const todoData = ownerBreakdown.map(owner => owner.todo || 0);
        
        chart.data.labels = labels;
        chart.data.datasets[0].data = completedData;
        chart.data.datasets[1].data = inProgressData;
        chart.data.datasets[2].data = blockedData;
        chart.data.datasets[3].data = todoData;
        chart.update('none');
    }

    updateTrendAnalysisChart(data) {
        if (!data || !this.enhancedCharts.trendAnalysisChart) return;

        const chart = this.enhancedCharts.trendAnalysisChart;
        const dailyBreakdown = data.daily_breakdown || [];
        
        // Calculate completion trend over time
        const labels = dailyBreakdown.map(day => day.date);
        const completionRates = dailyBreakdown.map(day => {
            const total = (day.completed || 0) + (day.in_progress || 0) + (day.blocked || 0) + (day.todo || 0);
            return total > 0 ? ((day.completed || 0) / total * 100) : 0;
        });
        
        // Calculate velocity trend
        const velocityData = dailyBreakdown.map(day => (day.completed || 0) + (day.in_progress || 0));
        
        // Generate prediction line (simple linear trend)
        const predictionData = this.generateTrendPrediction(completionRates);
        
        chart.data.labels = labels;
        chart.data.datasets[0].data = completionRates;
        chart.data.datasets[1].data = velocityData;
        chart.data.datasets[2].data = predictionData;
        chart.update('none');
        
        // Update trend indicators
        if (data.trend_indicators) {
            this.updateElement('trend-completion', data.trend_indicators.completion_trend || 'stable');
            this.updateElement('trend-velocity', data.trend_indicators.velocity_trend || 'medium');
            this.updateElement('trend-health', data.trend_indicators.health_status || 'good');
        }
    }

    generateTrendPrediction(dataPoints) {
        if (dataPoints.length < 2) return [];
        
        // Simple linear regression for trend prediction
        const n = dataPoints.length;
        const sumX = (n * (n - 1)) / 2;
        const sumY = dataPoints.reduce((a, b) => a + b, 0);
        const sumXY = dataPoints.reduce((sum, y, x) => sum + (x * y), 0);
        const sumXX = (n * (n - 1) * (2 * n - 1)) / 6;
        
        const slope = (n * sumXY - sumX * sumY) / (n * sumXX - sumX * sumX);
        const intercept = (sumY - slope * sumX) / n;
        
        // Generate prediction for next few points
        return dataPoints.map((_, index) => slope * index + intercept);
    }

    // ...existing code...
}

/**
 * Enhanced Timeline Component
 */
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

/**
 * Sprint Health Analyzer
 */
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

    // Toggle chart data display (referenced by HTML buttons)
    toggleChartData(chartType, dataType) {
        console.log(`Toggling chart: ${chartType} to ${dataType}`);
        
        // Update button states
        const buttons = document.querySelectorAll(`[onclick*="toggleChart('${chartType}'"]`);
        buttons.forEach(btn => btn.classList.remove('active'));
        
        const activeButton = document.querySelector(`[onclick*="toggleChart('${chartType}', '${dataType}'"]`);
        if (activeButton) {
            activeButton.classList.add('active');
        }
        
        // Handle chart updates based on type and data
        switch (chartType) {
            case 'progress':
                this.updateProgressChartView(dataType);
                break;
            case 'qa':
                this.updateQAChartView(dataType);
                break;
            case 'velocity':
                this.updateVelocityChartView(dataType);
                break;
        }
    }

    updateProgressChartView(dataType) {
        if (!this.charts.progressChart) return;
        
        // Switch between tasks and completion views
        if (dataType === 'tasks') {
            // Show task breakdown (existing implementation)
            this.updateProgressCharts();
        } else if (dataType === 'completion') {
            // Show completion percentage view
            this.charts.progressChart.data.labels = ['Completed', 'Remaining'];
            const totalTasks = this.cachedData?.metrics?.data?.sprint?.total_tasks || 0;
            const completedTasks = this.cachedData?.metrics?.data?.sprint?.completed_tasks || 0;
            this.charts.progressChart.data.datasets[0].data = [completedTasks, totalTasks - completedTasks];
            this.charts.progressChart.update();
        }
    }

    updateQAChartView(dataType) {
        if (!this.charts.qaChart) return;
        
        // Switch between pass rate and coverage views
        if (dataType === 'pass_rate') {
            // Show pass/fail breakdown (existing implementation)
            this.updateQACharts();
        } else if (dataType === 'coverage') {
            // Show coverage metrics
            const coverage = this.cachedData?.metrics?.data?.sprint?.average_coverage || 0;
            this.charts.qaChart.data.labels = ['Covered', 'Not Covered'];
            this.charts.qaChart.data.datasets[0].data = [coverage, 100 - coverage];
            this.charts.qaChart.update();
        }
    }

    updateVelocityChartView(dataType) {
        if (!this.charts.velocityChart) return;
        
        // Switch between daily and weekly views
        if (dataType === 'daily') {
            // Show daily velocity (existing implementation)
            this.updateVelocityChart(this.cachedData?.sprintVelocity);
        } else if (dataType === 'weekly') {
            // Show weekly averages
            const history = this.cachedData?.sprintVelocity?.sprint_history || [];
            const weeklyData = this.calculateWeeklyAverages(history);
            
            this.charts.velocityChart.data.labels = weeklyData.labels;
            this.charts.velocityChart.data.datasets[0].data = weeklyData.values;
            this.charts.velocityChart.update();
        }
    }

    calculateWeeklyAverages(history) {
        // Group sprints by week and calculate averages
        const weeks = {};
        history.forEach(sprint => {
            const week = Math.floor(sprint.sprint_id / 7) + 1;
            if (!weeks[week]) weeks[week] = [];
            weeks[week].push(sprint.velocity);
        });

        const labels = Object.keys(weeks).map(w => `Week ${w}`);
        const values = Object.values(weeks).map(velocities => 
            velocities.reduce((sum, v) => sum + v, 0) / velocities.length
        );        return { labels, values };
    }

    // Toggle timeline period (referenced by HTML buttons)
    toggleTimelinePeriod(period) {
        console.log(`Toggling timeline period to: ${period}`);
        
        // Update button states
        const buttons = document.querySelectorAll(`[onclick*="toggleTimeline("]`);
        buttons.forEach(btn => btn.classList.remove('active'));
        
        const activeButton = document.querySelector(`[onclick*="toggleTimeline('${period}'"]`);
        if (activeButton) {
            activeButton.classList.add('active');
        }
        
        // Update timeline chart if it exists
        if (this.charts.timelineChart) {
            this.updateTimelineChartPeriod(period);
        }
    }

    updateTimelineChartPeriod(period) {
        // This would update the timeline chart based on the selected period
        // For now, just log the action
        console.log(`Updating timeline chart for period: ${period}`);
        
        // In a full implementation, this would:
        // 1. Filter timeline data based on period
        // 2. Update chart data
        // 3. Refresh the chart display
    }
}

// Global dashboard manager instance
let dashboardManager = null;

// Initialize dashboard when DOM is loaded
document.addEventListener('DOMContentLoaded', async () => {
    try {
        console.log('DOM loaded, initializing dashboard...');
        
        // Create dashboard manager and make it globally accessible
        dashboardManager = new DashboardManager();
        
        // Initialize dashboard
        await dashboardManager.initialize();
        
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
