/**
 * Gantt Chart Component - Phase 6 Step 6.7
 * 
 * Professional Gantt chart visualization with critical path analysis,
 * interactive timeline adjustment, and resource optimization.
 */

class GanttChartComponent {
    constructor(containerId) {
        this.containerId = containerId;
        this.container = document.getElementById(containerId);
        this.ganttData = null;
        this.chart = null;
        this.apiBaseUrl = 'http://localhost:5000';
        this.selectedLibrary = 'mermaid'; // default to mermaid, can switch to frappe-gantt
        
        this.initializeComponent();
    }

    async initializeComponent() {
        try {
            console.log('Initializing Gantt Chart Component...');
            
            // Create component structure
            this.createComponentHTML();
            
            // Load necessary libraries
            await this.loadGanttLibraries();
            
            // Set up event handlers
            this.setupEventHandlers();
            
            // Load initial data
            await this.loadGanttData();
            
            console.log('Gantt Chart Component initialized successfully');
        } catch (error) {
            console.error('Failed to initialize Gantt Chart Component:', error);
            this.showError('Failed to initialize Gantt chart');
        }
    }

    createComponentHTML() {
        this.container.innerHTML = `
            <div class="gantt-component">
                <div class="gantt-header">
                    <div class="gantt-title">
                        <h3>Gantt Chart & Critical Path View</h3>
                        <div class="gantt-status" id="gantt-status">
                            <span class="status-indicator" id="gantt-status-indicator">●</span>
                            <span id="gantt-status-text">Loading...</span>
                        </div>
                    </div>
                    
                    <div class="gantt-controls">
                        <div class="gantt-toolbar">
                            <button class="btn btn-primary" onclick="ganttChart.refreshData()">
                                <i class="icon-refresh"></i> Refresh
                            </button>
                            
                            <div class="btn-group">
                                <button class="btn btn-secondary active" data-view="gantt" onclick="ganttChart.switchView('gantt')">
                                    Gantt View
                                </button>
                                <button class="btn btn-secondary" data-view="critical" onclick="ganttChart.switchView('critical')">
                                    Critical Path
                                </button>
                                <button class="btn btn-secondary" data-view="resources" onclick="ganttChart.switchView('resources')">
                                    Resources
                                </button>
                            </div>
                            
                            <div class="time-range-selector">
                                <select id="time-range" onchange="ganttChart.changeTimeRange(this.value)">
                                    <option value="week">This Week</option>
                                    <option value="month" selected>This Month</option>
                                    <option value="quarter">This Quarter</option>
                                    <option value="all">All Time</option>
                                </select>
                            </div>
                            
                            <button class="btn btn-info" onclick="ganttChart.showOptimizationPanel()">
                                <i class="icon-optimize"></i> Optimize
                            </button>
                        </div>
                    </div>
                </div>

                <!-- Metrics Summary Row -->
                <div class="gantt-metrics-row">
                    <div class="gantt-metric">
                        <span class="metric-label">Project Duration</span>
                        <span class="metric-value" id="project-duration">-- days</span>
                    </div>
                    <div class="gantt-metric">
                        <span class="metric-label">Critical Path</span>
                        <span class="metric-value" id="critical-path-duration">-- days</span>
                    </div>
                    <div class="gantt-metric">
                        <span class="metric-label">Total Tasks</span>
                        <span class="metric-value" id="total-tasks">--</span>
                    </div>
                    <div class="gantt-metric">
                        <span class="metric-label">Progress</span>
                        <span class="metric-value" id="project-progress">--%</span>
                    </div>
                    <div class="gantt-metric">
                        <span class="metric-label">Resource Utilization</span>
                        <span class="metric-value" id="resource-utilization">--%</span>
                    </div>
                </div>

                <!-- Main Gantt Chart Container -->
                <div class="gantt-main-container">
                    <div class="gantt-chart-container" id="gantt-chart-view">
                        <!-- Mermaid Gantt Chart -->
                        <div class="mermaid-gantt" id="mermaid-gantt-container">
                            <div class="mermaid" id="mermaid-gantt-diagram">
                                <!-- Mermaid diagram will be rendered here -->
                            </div>
                        </div>
                        
                        <!-- Alternative: Frappe Gantt Chart -->
                        <div class="frappe-gantt" id="frappe-gantt-container" style="display: none;">
                            <svg id="frappe-gantt-svg"></svg>
                        </div>
                    </div>

                    <!-- Critical Path Visualization -->
                    <div class="critical-path-container" id="critical-path-view" style="display: none;">
                        <div class="critical-path-summary">
                            <h4>Critical Path Analysis</h4>
                            <div class="critical-path-metrics">
                                <div class="cp-metric">
                                    <span class="cp-label">Critical Tasks</span>
                                    <span class="cp-value" id="critical-tasks-count">--</span>
                                </div>
                                <div class="cp-metric">
                                    <span class="cp-label">Path Duration</span>
                                    <span class="cp-value" id="critical-path-days">-- days</span>
                                </div>
                                <div class="cp-metric">
                                    <span class="cp-label">Risk Level</span>
                                    <span class="cp-value risk-level" id="critical-path-risk">--</span>
                                </div>
                            </div>
                        </div>
                        
                        <div class="critical-tasks-list">
                            <h5>Critical Tasks</h5>
                            <div class="tasks-table-container">
                                <table class="critical-tasks-table">
                                    <thead>
                                        <tr>
                                            <th>Task</th>
                                            <th>Duration</th>
                                            <th>Start Date</th>
                                            <th>End Date</th>
                                            <th>Dependencies</th>
                                            <th>Risk</th>
                                        </tr>
                                    </thead>
                                    <tbody id="critical-tasks-tbody">
                                        <!-- Critical tasks will be populated here -->
                                    </tbody>
                                </table>
                            </div>
                        </div>
                        
                        <div class="dependency-graph">
                            <h5>Dependency Network</h5>
                            <div class="mermaid" id="dependency-diagram">
                                <!-- Dependency diagram will be rendered here -->
                            </div>
                        </div>
                    </div>

                    <!-- Resource Optimization View -->
                    <div class="resource-optimization-container" id="resource-optimization-view" style="display: none;">
                        <div class="resource-summary">
                            <h4>Resource Optimization</h4>
                            <div class="resource-metrics">
                                <div class="resource-metric">
                                    <span class="resource-label">Team Members</span>
                                    <span class="resource-value" id="team-members-count">--</span>
                                </div>
                                <div class="resource-metric">
                                    <span class="resource-label">Avg Utilization</span>
                                    <span class="resource-value" id="avg-utilization">--%</span>
                                </div>
                                <div class="resource-metric">
                                    <span class="resource-label">Bottlenecks</span>
                                    <span class="resource-value" id="bottlenecks-count">--</span>
                                </div>
                            </div>
                        </div>
                        
                        <div class="resource-allocation-chart">
                            <canvas id="resource-allocation-canvas"></canvas>
                        </div>
                        
                        <div class="optimization-recommendations">
                            <h5>Optimization Recommendations</h5>
                            <div class="recommendations-list" id="optimization-recommendations-list">
                                <!-- Recommendations will be populated here -->
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Optimization Panel (Modal) -->
                <div class="optimization-panel" id="optimization-panel" style="display: none;">
                    <div class="panel-content">
                        <div class="panel-header">
                            <h4>Timeline Optimization</h4>
                            <button class="close-btn" onclick="ganttChart.closeOptimizationPanel()">×</button>
                        </div>
                        
                        <div class="panel-body">
                            <div class="optimization-options">
                                <div class="option-group">
                                    <label>Optimization Goal:</label>
                                    <select id="optimization-goal">
                                        <option value="minimize_duration">Minimize Duration</option>
                                        <option value="balance_resources">Balance Resources</option>
                                        <option value="reduce_risk">Reduce Risk</option>
                                        <option value="maximize_quality">Maximize Quality</option>
                                    </select>
                                </div>
                                
                                <div class="option-group">
                                    <label>Resource Constraints:</label>
                                    <input type="range" id="resource-constraint" min="50" max="150" value="100">
                                    <span id="resource-constraint-value">100%</span>
                                </div>
                                
                                <div class="option-group">
                                    <label>Time Constraints:</label>
                                    <input type="range" id="time-constraint" min="80" max="120" value="100">
                                    <span id="time-constraint-value">100%</span>
                                </div>
                            </div>
                            
                            <div class="optimization-results" id="optimization-results" style="display: none;">
                                <h5>Optimization Results</h5>
                                <div class="results-content">
                                    <!-- Results will be populated here -->
                                </div>
                            </div>
                        </div>
                        
                        <div class="panel-footer">
                            <button class="btn btn-primary" onclick="ganttChart.runOptimization()">
                                Run Optimization
                            </button>
                            <button class="btn btn-secondary" onclick="ganttChart.applyOptimization()">
                                Apply Changes
                            </button>
                            <button class="btn btn-outline" onclick="ganttChart.closeOptimizationPanel()">
                                Cancel
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }

    async loadGanttLibraries() {
        try {
            // Load Mermaid if not already loaded
            if (!window.mermaid) {
                await this.loadScript('https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js');
                window.mermaid.initialize({ 
                    startOnLoad: false,
                    theme: 'default',
                    gantt: {
                        titleTopMargin: 25,
                        barHeight: 20,
                        fontFamily: '"Inter", -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
                        fontSize: 11,
                        gridLineStartPadding: 35,
                        bottomPadding: 50,
                        leftPadding: 75
                    }
                });
            }

            // Optionally load Frappe Gantt for fallback
            if (!window.Gantt && this.selectedLibrary === 'frappe') {
                await this.loadScript('https://cdn.jsdelivr.net/npm/frappe-gantt@0.6.1/dist/frappe-gantt.min.js');
                await this.loadStylesheet('https://cdn.jsdelivr.net/npm/frappe-gantt@0.6.1/dist/frappe-gantt.css');
            }

            console.log('Gantt libraries loaded successfully');
        } catch (error) {
            console.error('Failed to load Gantt libraries:', error);
            throw error;
        }
    }

    loadScript(src) {
        return new Promise((resolve, reject) => {
            const script = document.createElement('script');
            script.src = src;
            script.onload = resolve;
            script.onerror = reject;
            document.head.appendChild(script);
        });
    }

    loadStylesheet(href) {
        return new Promise((resolve, reject) => {
            const link = document.createElement('link');
            link.rel = 'stylesheet';
            link.href = href;
            link.onload = resolve;
            link.onerror = reject;
            document.head.appendChild(link);
        });
    }

    setupEventHandlers() {
        // Set up resource constraint slider
        const resourceSlider = document.getElementById('resource-constraint');
        const resourceValue = document.getElementById('resource-constraint-value');
        
        if (resourceSlider && resourceValue) {
            resourceSlider.addEventListener('input', (e) => {
                resourceValue.textContent = `${e.target.value}%`;
            });
        }

        // Set up time constraint slider
        const timeSlider = document.getElementById('time-constraint');
        const timeValue = document.getElementById('time-constraint-value');
        
        if (timeSlider && timeValue) {
            timeSlider.addEventListener('input', (e) => {
                timeValue.textContent = `${e.target.value}%`;
            });
        }
    }

    async loadGanttData() {
        try {
            this.updateStatus('loading', 'Loading Gantt data...');
            
            // Fetch Gantt data from the backend
            const response = await fetch(`${this.apiBaseUrl}/api/gantt/data`);
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            this.ganttData = await response.json();
            
            // Update metrics
            this.updateMetrics();
            
            // Render the chart
            await this.renderGanttChart();
            
            this.updateStatus('ready', 'Gantt chart loaded');
            
        } catch (error) {
            console.error('Failed to load Gantt data:', error);
            this.updateStatus('error', 'Failed to load data');
            
            // Load sample data for demo
            this.loadSampleData();
        }
    }

    updateMetrics() {
        if (!this.ganttData) return;

        const { project_timeline, critical_path } = this.ganttData;
        
        if (project_timeline) {
            this.updateElement('project-duration', `${project_timeline.total_duration} days`);
            this.updateElement('critical-path-duration', `${project_timeline.critical_path_duration} days`);
            this.updateElement('total-tasks', project_timeline.total_tasks);
            this.updateElement('project-progress', `${project_timeline.progress.toFixed(1)}%`);
            
            // Calculate average resource utilization
            const avgUtilization = Object.values(project_timeline.resource_utilization || {})
                .reduce((acc, val) => acc + val, 0) / 
                Object.keys(project_timeline.resource_utilization || {}).length || 0;
            this.updateElement('resource-utilization', `${(avgUtilization * 100).toFixed(1)}%`);
        }

        if (critical_path) {
            this.updateElement('critical-tasks-count', critical_path.length);
            this.updateElement('critical-path-days', `${project_timeline?.critical_path_duration || 0} days`);
            
            // Determine risk level based on critical path length and slack
            const riskLevel = this.calculateRiskLevel();
            const riskElement = document.getElementById('critical-path-risk');
            if (riskElement) {
                riskElement.textContent = riskLevel;
                riskElement.className = `cp-value risk-level risk-${riskLevel.toLowerCase()}`;
            }
        }
    }

    calculateRiskLevel() {
        if (!this.ganttData) return 'Unknown';
        
        const { tasks } = this.ganttData;
        const criticalTasks = tasks.filter(task => task.critical_path);
        const avgSlack = tasks.reduce((acc, task) => acc + task.slack_time, 0) / tasks.length;
        
        if (criticalTasks.length > tasks.length * 0.5 || avgSlack < 1) {
            return 'High';
        } else if (criticalTasks.length > tasks.length * 0.3 || avgSlack < 3) {
            return 'Medium';
        } else {
            return 'Low';
        }
    }

    async renderGanttChart() {
        if (!this.ganttData) return;

        if (this.selectedLibrary === 'mermaid') {
            await this.renderMermaidGantt();
        } else if (this.selectedLibrary === 'frappe') {
            this.renderFrappeGantt();
        }
    }

    async renderMermaidGantt() {
        try {
            const mermaidCode = this.generateMermaidGanttCode();
            const element = document.getElementById('mermaid-gantt-diagram');
            
            if (element) {
                element.innerHTML = mermaidCode;
                await window.mermaid.run();
                console.log('Mermaid Gantt chart rendered successfully');
            }
        } catch (error) {
            console.error('Failed to render Mermaid Gantt:', error);
            this.showError('Failed to render Gantt chart');
        }
    }

    generateMermaidGanttCode() {
        if (!this.ganttData || !this.ganttData.tasks) {
            return 'gantt\n    title Project Timeline\n    dateFormat YYYY-MM-DD\n    No tasks available :2024-01-01, 1d';
        }

        const { tasks } = this.ganttData;
        let mermaidCode = `gantt
    title Project Timeline
    dateFormat YYYY-MM-DD
    axisFormat %m/%d
    
`;

        // Group tasks by assigned person or category
        const taskGroups = this.groupTasksForMermaid(tasks);
        
        for (const [section, sectionTasks] of Object.entries(taskGroups)) {
            mermaidCode += `    section ${section}\n`;
            
            for (const task of sectionTasks) {
                const status = this.getMermaidTaskStatus(task);
                const startDate = this.formatDateForMermaid(task.start_date);
                const endDate = this.formatDateForMermaid(task.end_date);
                
                mermaidCode += `    ${task.name} :${status}${task.id}, ${startDate}, ${endDate}\n`;
            }
            mermaidCode += '\n';
        }

        return mermaidCode;
    }

    groupTasksForMermaid(tasks) {
        const groups = {};
        
        for (const task of tasks) {
            const section = task.assigned_to || 'Unassigned';
            if (!groups[section]) {
                groups[section] = [];
            }
            groups[section].push(task);
        }
        
        return groups;
    }

    getMermaidTaskStatus(task) {
        if (task.critical_path) {
            return 'crit, ';
        } else if (task.status === 'completed') {
            return 'done, ';
        } else if (task.status === 'in_progress') {
            return 'active, ';
        } else {
            return '';
        }
    }

    formatDateForMermaid(dateStr) {
        const date = new Date(dateStr);
        return date.toISOString().split('T')[0];
    }

    renderFrappeGantt() {
        try {
            const tasks = this.convertToFrappeFormat();
            const ganttContainer = document.getElementById('frappe-gantt-svg');
            
            if (ganttContainer && window.Gantt) {
                this.chart = new window.Gantt(ganttContainer, tasks, {
                    header_height: 50,
                    column_width: 30,
                    step: 24,
                    view_modes: ['Quarter Day', 'Half Day', 'Day', 'Week', 'Month'],
                    bar_height: 20,
                    bar_corner_radius: 3,
                    arrow_curve: 5,
                    padding: 18,
                    view_mode: 'Day',
                    date_format: 'YYYY-MM-DD',
                    on_click: (task) => this.onTaskClick(task),
                    on_date_change: (task, start, end) => this.onTaskDateChange(task, start, end),
                    on_progress_change: (task, progress) => this.onTaskProgressChange(task, progress),
                    on_view_change: (mode) => this.onViewChange(mode)
                });
                
                console.log('Frappe Gantt chart rendered successfully');
            }
        } catch (error) {
            console.error('Failed to render Frappe Gantt:', error);
            this.showError('Failed to render Gantt chart');
        }
    }

    convertToFrappeFormat() {
        if (!this.ganttData || !this.ganttData.tasks) return [];
        
        return this.ganttData.tasks.map(task => ({
            id: task.id,
            name: task.name,
            start: task.start_date,
            end: task.end_date,
            progress: task.progress,
            dependencies: task.dependencies.join(','),
            custom_class: task.critical_path ? 'critical-task' : ''
        }));
    }

    // Event handlers for interactive features
    onTaskClick(task) {
        console.log('Task clicked:', task);
        this.showTaskDetails(task);
    }

    onTaskDateChange(task, start, end) {
        console.log('Task date changed:', task, start, end);
        // This would trigger an API call to update the task dates
        this.updateTaskDates(task.id, start, end);
    }

    onTaskProgressChange(task, progress) {
        console.log('Task progress changed:', task, progress);
        // This would trigger an API call to update the task progress
        this.updateTaskProgress(task.id, progress);
    }

    onViewChange(mode) {
        console.log('View mode changed:', mode);
    }

    // View switching methods
    switchView(viewType) {
        // Update button states
        document.querySelectorAll('[data-view]').forEach(btn => {
            btn.classList.remove('active');
        });
        document.querySelector(`[data-view="${viewType}"]`).classList.add('active');

        // Show/hide appropriate containers
        document.getElementById('gantt-chart-view').style.display = 
            viewType === 'gantt' ? 'block' : 'none';
        document.getElementById('critical-path-view').style.display = 
            viewType === 'critical' ? 'block' : 'none';
        document.getElementById('resource-optimization-view').style.display = 
            viewType === 'resources' ? 'block' : 'none';

        // Load view-specific data
        if (viewType === 'critical') {
            this.loadCriticalPathView();
        } else if (viewType === 'resources') {
            this.loadResourceOptimizationView();
        }
    }

    loadCriticalPathView() {
        if (!this.ganttData) return;

        const { tasks, critical_path } = this.ganttData;
        const criticalTasks = tasks.filter(task => task.critical_path);
        
        // Populate critical tasks table
        const tbody = document.getElementById('critical-tasks-tbody');
        if (tbody) {
            tbody.innerHTML = criticalTasks.map(task => `
                <tr class="critical-task-row">
                    <td class="task-name">${task.name}</td>
                    <td class="task-duration">${task.duration} days</td>
                    <td class="task-start">${this.formatDisplayDate(task.start_date)}</td>
                    <td class="task-end">${this.formatDisplayDate(task.end_date)}</td>
                    <td class="task-dependencies">${task.dependencies.join(', ') || 'None'}</td>
                    <td class="task-risk">
                        <span class="risk-badge risk-${this.getTaskRiskLevel(task).toLowerCase()}">
                            ${this.getTaskRiskLevel(task)}
                        </span>
                    </td>
                </tr>
            `).join('');
        }

        // Render dependency diagram
        this.renderDependencyDiagram();
    }

    renderDependencyDiagram() {
        if (!this.ganttData) return;

        const dependencyCode = this.generateDependencyMermaidCode();
        const element = document.getElementById('dependency-diagram');
        
        if (element) {
            element.innerHTML = dependencyCode;
            window.mermaid.run();
        }
    }

    generateDependencyMermaidCode() {
        const { tasks } = this.ganttData;
        const criticalTasks = tasks.filter(task => task.critical_path);
        
        let mermaidCode = `graph TD\n`;
        
        for (const task of criticalTasks) {
            const nodeId = task.id.replace(/[^a-zA-Z0-9]/g, '');
            mermaidCode += `    ${nodeId}[${task.name}]\n`;
            
            for (const depId of task.dependencies) {
                const depNodeId = depId.replace(/[^a-zA-Z0-9]/g, '');
                mermaidCode += `    ${depNodeId} --> ${nodeId}\n`;
            }
        }
        
        // Add styling for critical path
        mermaidCode += `    classDef critical fill:#ff6b6b,stroke:#d63447,stroke-width:2px,color:#fff\n`;
        const criticalNodeIds = criticalTasks.map(t => t.id.replace(/[^a-zA-Z0-9]/g, ''));
        mermaidCode += `    class ${criticalNodeIds.join(',')} critical\n`;
        
        return mermaidCode;
    }

    loadResourceOptimizationView() {
        if (!this.ganttData) return;

        // Update resource metrics
        this.updateResourceMetrics();
        
        // Render resource allocation chart
        this.renderResourceAllocationChart();
        
        // Load optimization recommendations
        this.loadOptimizationRecommendations();
    }

    updateResourceMetrics() {
        const { tasks, project_timeline } = this.ganttData;
        const resources = [...new Set(tasks.map(task => task.assigned_to).filter(Boolean))];
        
        document.getElementById('team-members-count').textContent = resources.length;
        
        const avgUtilization = Object.values(project_timeline.resource_utilization || {})
            .reduce((acc, val) => acc + val, 0) / resources.length || 0;
        document.getElementById('avg-utilization').textContent = `${(avgUtilization * 100).toFixed(1)}%`;
        
        // Count bottlenecks (resources over 90% utilization)
        const bottlenecks = Object.values(project_timeline.resource_utilization || {})
            .filter(utilization => utilization > 0.9).length;
        document.getElementById('bottlenecks-count').textContent = bottlenecks;
    }

    renderResourceAllocationChart() {
        const canvas = document.getElementById('resource-allocation-canvas');
        if (!canvas || !this.ganttData) return;

        const ctx = canvas.getContext('2d');
        const { project_timeline } = this.ganttData;
        const resourceData = project_timeline.resource_utilization || {};
        
        new Chart(ctx, {
            type: 'bar',
            data: {
                labels: Object.keys(resourceData),
                datasets: [{
                    label: 'Resource Utilization',
                    data: Object.values(resourceData).map(val => val * 100),
                    backgroundColor: Object.values(resourceData).map(val => 
                        val > 0.9 ? '#ff6b6b' : val > 0.7 ? '#feca57' : '#48dbfb'
                    ),
                    borderColor: '#2f3542',
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                scales: {
                    y: {
                        beginAtZero: true,
                        max: 100,
                        title: {
                            display: true,
                            text: 'Utilization %'
                        }
                    }
                },
                plugins: {
                    title: {
                        display: true,
                        text: 'Resource Utilization'
                    }
                }
            }
        });
    }

    async loadOptimizationRecommendations() {
        try {
            const response = await fetch(`${this.apiBaseUrl}/api/gantt/recommendations`);
            if (response.ok) {
                const recommendations = await response.json();
                this.displayRecommendations(recommendations);
            }
        } catch (error) {
            console.error('Failed to load recommendations:', error);
            // Show sample recommendations
            this.displaySampleRecommendations();
        }
    }

    displayRecommendations(recommendations) {
        const container = document.getElementById('optimization-recommendations-list');
        if (!container) return;

        container.innerHTML = recommendations.map(rec => `
            <div class="recommendation-item priority-${rec.priority}">
                <div class="recommendation-header">
                    <span class="recommendation-title">${rec.title}</span>
                    <span class="recommendation-impact">Impact: ${rec.impact}</span>
                </div>
                <div class="recommendation-description">${rec.description}</div>
                <div class="recommendation-actions">
                    <button class="btn btn-sm btn-primary" onclick="ganttChart.applyRecommendation('${rec.id}')">
                        Apply
                    </button>
                    <button class="btn btn-sm btn-outline" onclick="ganttChart.dismissRecommendation('${rec.id}')">
                        Dismiss
                    </button>
                </div>
            </div>
        `).join('');
    }

    displaySampleRecommendations() {
        const sampleRecs = [
            {
                id: 'parallel-tasks',
                title: 'Parallelize Independent Tasks',
                description: 'Tasks "Setup Environment" and "Design Database" can run in parallel, reducing timeline by 3 days.',
                priority: 'high',
                impact: 'High'
            },
            {
                id: 'resource-reallocation',
                title: 'Reallocate Overutilized Resources',
                description: 'Developer A is overallocated. Consider redistributing tasks to balance workload.',
                priority: 'medium',
                impact: 'Medium'
            },
            {
                id: 'critical-path-optimization',
                title: 'Optimize Critical Path',
                description: 'Breaking down "Integration Testing" task could reduce critical path duration.',
                priority: 'high',
                impact: 'High'
            }
        ];
        
        this.displayRecommendations(sampleRecs);
    }

    // Optimization panel methods
    showOptimizationPanel() {
        document.getElementById('optimization-panel').style.display = 'flex';
    }

    closeOptimizationPanel() {
        document.getElementById('optimization-panel').style.display = 'none';
        document.getElementById('optimization-results').style.display = 'none';
    }

    async runOptimization() {
        try {
            const goal = document.getElementById('optimization-goal').value;
            const resourceConstraint = document.getElementById('resource-constraint').value;
            const timeConstraint = document.getElementById('time-constraint').value;
            
            const response = await fetch(`${this.apiBaseUrl}/api/gantt/optimize`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    goal,
                    resource_constraint: resourceConstraint / 100,
                    time_constraint: timeConstraint / 100
                })
            });
            
            if (response.ok) {
                const results = await response.json();
                this.displayOptimizationResults(results);
            } else {
                throw new Error('Optimization failed');
            }
        } catch (error) {
            console.error('Optimization error:', error);
            this.showError('Optimization failed');
        }
    }

    displayOptimizationResults(results) {
        const container = document.getElementById('optimization-results');
        container.style.display = 'block';
        
        container.querySelector('.results-content').innerHTML = `
            <div class="optimization-summary">
                <h6>Optimization Summary</h6>
                <div class="result-metrics">
                    <div class="result-metric">
                        <span class="metric-label">Duration Reduction:</span>
                        <span class="metric-value">${results.duration_reduction || 0} days</span>
                    </div>
                    <div class="result-metric">
                        <span class="metric-label">Resource Efficiency:</span>
                        <span class="metric-value">${results.resource_efficiency || 0}%</span>
                    </div>
                    <div class="result-metric">
                        <span class="metric-label">Risk Reduction:</span>
                        <span class="metric-value">${results.risk_reduction || 0}%</span>
                    </div>
                </div>
            </div>
            
            <div class="optimization-changes">
                <h6>Proposed Changes</h6>
                <ul class="changes-list">
                    ${(results.changes || []).map(change => `
                        <li class="change-item">${change}</li>
                    `).join('')}
                </ul>
            </div>
        `;
    }

    // Utility methods
    updateElement(id, value) {
        const element = document.getElementById(id);
        if (element) {
            element.textContent = value;
        }
    }

    updateStatus(status, message) {
        const indicator = document.getElementById('gantt-status-indicator');
        const text = document.getElementById('gantt-status-text');
        
        if (indicator && text) {
            indicator.className = `status-indicator status-${status}`;
            text.textContent = message;
        }
    }

    formatDisplayDate(dateStr) {
        const date = new Date(dateStr);
        return date.toLocaleDateString();
    }

    getTaskRiskLevel(task) {
        if (task.critical_path && task.slack_time === 0) {
            return 'High';
        } else if (task.critical_path || task.slack_time < 2) {
            return 'Medium';
        } else {
            return 'Low';
        }
    }

    showError(message) {
        console.error('Gantt Chart Error:', message);
        this.updateStatus('error', message);
    }

    showTaskDetails(task) {
        // Implementation for showing task details modal
        console.log('Show task details for:', task);
    }

    async updateTaskDates(taskId, start, end) {
        // Implementation for updating task dates via API
        console.log('Update task dates:', taskId, start, end);
    }

    async updateTaskProgress(taskId, progress) {
        // Implementation for updating task progress via API
        console.log('Update task progress:', taskId, progress);
    }

    async refreshData() {
        await this.loadGanttData();
    }

    changeTimeRange(range) {
        console.log('Change time range:', range);
        // Implementation for filtering data by time range
    }

    applyRecommendation(recId) {
        console.log('Apply recommendation:', recId);
        // Implementation for applying optimization recommendation
    }

    dismissRecommendation(recId) {
        console.log('Dismiss recommendation:', recId);
        // Implementation for dismissing recommendation
    }

    applyOptimization() {
        console.log('Apply optimization');
        this.closeOptimizationPanel();
        // Implementation for applying optimization changes
    }

    loadSampleData() {
        // Load sample data for demonstration
        this.ganttData = {
            project_timeline: {
                start_date: "2024-01-01T00:00:00",
                end_date: "2024-02-15T00:00:00",
                total_duration: 45,
                critical_path_duration: 30,
                total_tasks: 12,
                completed_tasks: 4,
                progress: 33.3,
                resource_utilization: {
                    "Developer A": 0.95,
                    "Developer B": 0.75,
                    "Designer": 0.60,
                    "QA Engineer": 0.85
                }
            },
            tasks: [
                {
                    id: "task-1",
                    name: "Project Setup",
                    start_date: "2024-01-01T00:00:00",
                    end_date: "2024-01-03T00:00:00",
                    duration: 3,
                    progress: 100,
                    dependencies: [],
                    assigned_to: "Developer A",
                    status: "completed",
                    critical_path: true,
                    slack_time: 0
                },
                {
                    id: "task-2", 
                    name: "Database Design",
                    start_date: "2024-01-04T00:00:00",
                    end_date: "2024-01-08T00:00:00",
                    duration: 5,
                    progress: 80,
                    dependencies: ["task-1"],
                    assigned_to: "Developer B",
                    status: "in_progress",
                    critical_path: true,
                    slack_time: 0
                },
                {
                    id: "task-3",
                    name: "UI Mockups",
                    start_date: "2024-01-04T00:00:00", 
                    end_date: "2024-01-10T00:00:00",
                    duration: 7,
                    progress: 50,
                    dependencies: ["task-1"],
                    assigned_to: "Designer",
                    status: "in_progress",
                    critical_path: false,
                    slack_time: 3
                }
            ],
            critical_path: ["task-1", "task-2", "task-4", "task-6"]
        };
        
        this.updateMetrics();
        this.renderGanttChart();
        this.updateStatus('ready', 'Sample data loaded');
    }
}

// Global instance
window.ganttChart = null;

// Initialize Gantt chart when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    const ganttContainer = document.getElementById('gantt-chart-component');
    if (ganttContainer) {
        window.ganttChart = new GanttChartComponent('gantt-chart-component');
    }
});
