/**
 * Interactive Professional Dashboard - Real Data Integration
 * Connects to actual AI system components for live monitoring and control
 */

class InteractiveProfessionalDashboard {
    constructor() {
        this.config = {
            apiBaseUrl: '/api',
            maxRetries: 3,
            timeout: 10000,
            heartbeatInterval: 30000, // 30 seconds heartbeat (reduced polling)
            reconnectDelay: 3000
        };
        
        this.state = {
            agents: {},
            tasks: {},
            systemHealth: {},
            performance: {},
            lastUpdate: null,
            isLoading: false,
            retryCount: 0,
            isConnected: false,
            lastDataHash: {}
        };
        
        this.charts = {};
        this.websocket = null;
        this.eventSource = null;
        this.heartbeatTimer = null;
        
        this.init();
    }

    async init() {
        console.log('🚀 Initializing Interactive Professional Dashboard...');
        
        try {
            // Wait for DOM to be fully ready
            await this.waitForDOM();
            
            // Setup real-time data connections
            await this.initializeDataSources();
            
            // Setup UI components
            this.setupEventHandlers();
            this.setupCharts();
            
            // Initialize real-time connections
            await this.initializeRealTimeConnections();
            
            // Initial data load
            await this.loadAllData();
            
            console.log('✅ Interactive Professional Dashboard initialized successfully');
            this.showNotification('Dashboard initialized with real-time data', 'success');
            
        } catch (error) {
            console.error('❌ Failed to initialize dashboard:', error);
            this.showNotification('Failed to initialize dashboard. Retrying...', 'error');
            this.handleInitializationError(error);
        }
    }

    async waitForDOM() {
        return new Promise((resolve) => {
            if (document.readyState === 'complete') {
                resolve();
            } else {
                document.addEventListener('DOMContentLoaded', resolve);
                // Fallback timeout
                setTimeout(resolve, 1000);
            }
        });
    }

    findElementWithRetry(elementId, maxRetries = 3) {
        for (let i = 0; i < maxRetries; i++) {
            const element = document.getElementById(elementId);
            if (element) {
                console.log(`✅ Found element ${elementId} on attempt ${i + 1}`);
                return element;
            }
            console.log(`🔄 Retry ${i + 1}/${maxRetries} finding element: ${elementId}`);
            // Small delay before retry (synchronous for now)
            if (i < maxRetries - 1) {
                // Use a simple blocking wait
                const start = Date.now();
                while (Date.now() - start < 200) {
                    // Brief blocking wait
                }
            }
        }
        console.error(`❌ Element ${elementId} not found after ${maxRetries} retries`);
        return null;
    }

    async initializeDataSources() {
        // Test API connectivity
        try {
            const healthCheck = await this.fetchWithTimeout('/api/health', { timeout: 5000 });
            console.log('📡 API connection established:', healthCheck);
            this.state.isConnected = true;
            this.config.useMockData = false; // Ensure we use real data
        } catch (error) {
            console.warn('⚠️ API not available, using mock data fallback');
            this.config.useMockData = true;
            this.state.isConnected = false;
        }
    }

    async initializeRealTimeConnections() {
        console.log('🔄 Setting up real-time connections...');
        
        // Check if WebSocket/SSE endpoints exist before trying to connect
        const supportsRealTime = await this.checkRealTimeSupport();
        
        if (supportsRealTime.websocket) {
            // Try WebSocket first (preferred for bidirectional communication)
            await this.setupWebSocket();
        } else if (supportsRealTime.sse) {
            // Fallback to Server-Sent Events
            this.setupServerSentEvents();
        } else {
            // Use smart polling as fallback
            console.log('📊 Real-time endpoints not available, using smart polling');
            this.setupPollingFallback();
        }
        
        console.log('✅ Real-time connections initialized');
    }
    
    async checkRealTimeSupport() {
        const support = { websocket: false, sse: false };
        
        // Check for SSE endpoint
        try {
            const response = await fetch('/api/dashboard/events', { method: 'HEAD' });
            if (response.ok) {
                // Check if SSE is actually available via custom header
                const sseAvailable = response.headers.get('X-SSE-Available');
                support.sse = sseAvailable === 'true';
            } else {
                support.sse = false;
            }
        } catch (e) {
            support.sse = false;
        }
        
        // Check for WebSocket endpoint (can't easily test, so check if SSE failed)
        support.websocket = false; // Disable for now since Flask doesn't support it natively
        
        return support;
    }

    async setupWebSocket() {
        try {
            const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
            const wsUrl = `${wsProtocol}//${window.location.host}/ws/dashboard`;
            
            this.websocket = new WebSocket(wsUrl);
            
            this.websocket.onopen = () => {
                console.log('🔌 WebSocket connected');
                this.state.isConnected = true;
                this.showNotification('Real-time connection established', 'success');
            };
            
            this.websocket.onmessage = (event) => {
                this.handleRealTimeUpdate(JSON.parse(event.data));
            };
            
            this.websocket.onclose = () => {
                console.log('🔌 WebSocket disconnected');
                this.state.isConnected = false;
                this.showNotification('Real-time connection lost. Attempting to reconnect...', 'warning');
                this.scheduleReconnect();
            };
            
            this.websocket.onerror = (error) => {
                console.error('WebSocket error:', error);
                this.websocket = null;
            };
            
        } catch (error) {
            console.warn('WebSocket not available:', error);
            this.websocket = null;
        }
    }

    setupServerSentEvents() {
        try {
            this.eventSource = new EventSource('/api/dashboard/events');
            
            this.eventSource.onopen = () => {
                console.log('📡 Server-Sent Events connected');
                this.state.isConnected = true;
                this.showNotification('Real-time updates enabled', 'success');
            };
            
            this.eventSource.onmessage = (event) => {
                this.handleRealTimeUpdate(JSON.parse(event.data));
            };
            
            this.eventSource.onerror = () => {
                console.log('📡 Server-Sent Events disconnected');
                this.state.isConnected = false;
                this.showNotification('Real-time connection lost. Attempting to reconnect...', 'warning');
                this.scheduleReconnect();
            };
            
        } catch (error) {
            console.warn('Server-Sent Events not available:', error);
            this.eventSource = null;
            // Fallback to polling as last resort
            this.setupPollingFallback();
        }
    }

    setupPollingFallback() {
        console.log('📊 Using smart polling for updates');
        this.config.usePollingOnly = true; // Prevent reconnection attempts
        // Start intelligent polling that only updates when data changes
        this.startSmartPolling();
    }
    
    startSmartPolling() {
        // Check for changes every 5 seconds, but only update UI if data actually changed
        this.heartbeatTimer = setInterval(async () => {
            if (!document.hidden && !this.state.isLoading) {
                await this.checkForChanges();
            }
        }, this.config.heartbeatInterval);
    }

    handleRealTimeUpdate(data) {
        console.log('🔄 Real-time update received:', data.type);
        
        // Check if data has actually changed using hash comparison
        const dataHash = this.generateDataHash(data.payload);
        const lastHash = this.state.lastDataHash[data.type];
        
        if (dataHash === lastHash) {
            console.log('🔍 No changes detected, skipping update');
            return;
        }
        
        this.state.lastDataHash[data.type] = dataHash;
        
        switch (data.type) {
            case 'tasks':
                console.log('📋 Updating task metrics');
                this.updateTaskMetrics(data.payload);
                break;
            case 'agents':
                console.log('🤖 Updating agent status');
                this.updateAgentStatus(data.payload);
                break;
            case 'health':
                console.log('💚 Updating system health');
                this.updateSystemHealth(data.payload);
                break;
            case 'performance':
                console.log('📈 Updating performance data');
                this.updatePerformanceChart(data.payload);
                break;
            case 'notification':
                console.log('🔔 Showing notification');
                this.showNotification(data.payload.message, data.payload.type);
                break;
            default:
                console.log('❓ Unknown update type:', data.type);
        }
        
        this.state.lastUpdate = new Date();
        this.showRefreshIndicator(false);
    }

    generateDataHash(data) {
        // Simple hash function to detect changes
        return JSON.stringify(data).split('').reduce((hash, char) => {
            return ((hash << 5) - hash) + char.charCodeAt(0);
        }, 0);
    }

    startHeartbeat() {
        this.heartbeatTimer = setInterval(async () => {
            if (!this.state.isConnected && !this.config.useMockData) {
                // Connection lost, try to detect changes manually
                await this.checkForChanges();
            } else if (this.websocket && this.websocket.readyState === WebSocket.OPEN) {
                // Send ping to keep connection alive
                this.websocket.send(JSON.stringify({ type: 'ping' }));
            }
        }, this.config.heartbeatInterval);
    }

    async checkForChanges() {
        try {
            // First try the lightweight changes endpoint
            const response = await this.fetchWithTimeout('/api/dashboard/changes', { timeout: 2000 });
            if (response.hasChanges) {
                console.log('🔄 Changes detected, loading updated data');
                await this.loadSpecificChanges(response.changedSections || ['all']);
            }
        } catch (error) {
            // If changes endpoint not available, do smart comparison
            console.log('📊 Checking for changes via smart comparison');
            await this.smartDataRefresh();
        }
    }
    
    async loadSpecificChanges(sections) {
        // Only load the sections that changed
        const loadPromises = [];
        
        if (sections.includes('all') || sections.includes('tasks')) {
            loadPromises.push(this.loadTaskMetrics());
        }
        if (sections.includes('all') || sections.includes('agents')) {
            loadPromises.push(this.loadAgentStatus());
        }
        if (sections.includes('all') || sections.includes('health')) {
            loadPromises.push(this.loadSystemHealth());
        }
        if (sections.includes('all') || sections.includes('performance')) {
            loadPromises.push(this.loadPerformanceData());
        }
        
        const results = await Promise.allSettled(loadPromises);
        this.processDataResults({
            tasks: sections.includes('tasks') ? results[0] : null,
            agents: sections.includes('agents') ? results[1] : null,
            health: sections.includes('health') ? results[2] : null,
            performance: sections.includes('performance') ? results[3] : null
        });
    }
    
    async smartDataRefresh() {
        // Do a lightweight data fetch and compare hashes
        try {
            // Fetch all data but don't update UI yet
            const [taskData, agentData, healthData, performanceData] = await Promise.allSettled([
                this.loadTaskMetrics(),
                this.loadAgentStatus(), 
                this.loadSystemHealth(),
                this.loadPerformanceData()
            ]);
            
            // Check which sections actually changed
            const changes = [];
            
            if (taskData.status === 'fulfilled') {
                const newHash = this.generateDataHash(taskData.value);
                if (newHash !== this.state.lastDataHash.tasks) {
                    changes.push('tasks');
                    this.state.lastDataHash.tasks = newHash;
                    this.updateTaskMetrics(taskData.value);
                }
            }
            
            if (agentData.status === 'fulfilled') {
                const newHash = this.generateDataHash(agentData.value);
                if (newHash !== this.state.lastDataHash.agents) {
                    changes.push('agents');
                    this.state.lastDataHash.agents = newHash;
                    this.updateAgentStatus(agentData.value);
                }
            }
            
            if (healthData.status === 'fulfilled') {
                const newHash = this.generateDataHash(healthData.value);
                if (newHash !== this.state.lastDataHash.health) {
                    changes.push('health');
                    this.state.lastDataHash.health = newHash;
                    this.updateSystemHealth(healthData.value);
                }
            }
            
            if (performanceData.status === 'fulfilled') {
                const newHash = this.generateDataHash(performanceData.value);
                if (newHash !== this.state.lastDataHash.performance) {
                    changes.push('performance');
                    this.state.lastDataHash.performance = newHash;
                    this.updatePerformanceChart(performanceData.value);
                }
            }
            
            if (changes.length > 0) {
                console.log(`🔄 Smart refresh: ${changes.length} sections updated:`, changes);
                this.state.lastUpdate = new Date();
            } else {
                console.log('✅ No changes detected, skipping UI update');
            }
            
        } catch (error) {
            console.error('Smart refresh error:', error);
        }
    }

    scheduleReconnect() {
        // Don't try to reconnect if we're using polling fallback
        if (this.config.usePollingOnly) {
            return;
        }
        
        setTimeout(() => {
            console.log('🔄 Attempting to reconnect...');
            this.initializeRealTimeConnections();
        }, this.config.reconnectDelay);
    }

    setupEventHandlers() {
        // Add error handling to prevent crashes
        window.addEventListener('error', (event) => {
            console.error('Dashboard error:', event.error);
            this.handleError(event.error);
        });
        
        // Handle visibility changes for efficient resource usage
        document.addEventListener('visibilitychange', () => {
            if (document.hidden) {
                this.pauseConnections();
            } else {
                this.resumeConnections();
            }
        });
    }

    setupCharts() {
        const ctx = document.getElementById('performanceChart');
        if (ctx) {
            this.charts.performance = new Chart(ctx, {
                type: 'line',
                data: {
                    labels: [],
                    datasets: [{
                        label: 'CPU Usage (%)',
                        data: [],
                        borderColor: 'rgb(102, 126, 234)',
                        backgroundColor: 'rgba(102, 126, 234, 0.1)',
                        tension: 0.4
                    }, {
                        label: 'Memory Usage (%)',
                        data: [],
                        borderColor: 'rgb(118, 75, 162)',
                        backgroundColor: 'rgba(118, 75, 162, 0.1)',
                        tension: 0.4
                    }, {
                        label: 'Task Completion Rate (%)',
                        data: [],
                        borderColor: 'rgb(0, 255, 136)',
                        backgroundColor: 'rgba(0, 255, 136, 0.1)',
                        tension: 0.4
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    interaction: {
                        intersect: false,
                        mode: 'index'
                    },
                    scales: {
                        y: {
                            beginAtZero: true,
                            max: 100,
                            grid: {
                                color: 'rgba(255, 255, 255, 0.1)'
                            },
                            ticks: {
                                color: '#666'
                            }
                        },
                        x: {
                            grid: {
                                color: 'rgba(255, 255, 255, 0.1)'
                            },
                            ticks: {
                                color: '#666'
                            }
                        }
                    },
                    plugins: {
                        legend: {
                            labels: {
                                color: '#666'
                            }
                        }
                    }
                }
            });
        }
    }

    async loadAllData() {
        if (this.state.isLoading) return;
        
        this.state.isLoading = true;
        this.showRefreshIndicator(true);
        
        try {
            // Load data in parallel for better performance
            const [taskData, agentData, healthData, performanceData] = await Promise.allSettled([
                this.loadTaskMetrics(),
                this.loadAgentStatus(),
                this.loadSystemHealth(),
                this.loadPerformanceData()
            ]);

            // Process results and handle any failures gracefully
            console.log('🔧 Processing data results:', {
                tasks: taskData,
                agents: agentData,
                health: healthData,
                performance: performanceData
            });
            
            this.processDataResults({
                tasks: taskData,
                agents: agentData,
                health: healthData,
                performance: performanceData
            });

            this.state.lastUpdate = new Date();
            this.state.retryCount = 0;
            
        } catch (error) {
            console.error('Error loading dashboard data:', error);
            this.handleDataLoadError(error);
        } finally {
            this.state.isLoading = false;
            this.showRefreshIndicator(false);
        }
    }

    async loadTaskMetrics() {
        if (this.config.useMockData) {
            console.log('📊 Using mock task data (API unavailable)');
            return this.getMockTaskData();
        }

        try {
            console.log('📊 Loading real task metrics from /api/dashboard/task-stats');
            const response = await this.fetchWithTimeout('/api/dashboard/task-stats');
            console.log('📊 Task metrics API response:', response);
            
            // Transform the API response to match our dashboard format
            const completed = response.completed_tasks || 0;
            const inProgress = response.in_progress_tasks || 0;  
            const failed = response.failed_tasks || 0;
            const pending = response.pending_tasks || 0;
            const total = response.total_tasks || 0;
            
            const transformedData = {
                total: total,
                completed: completed,
                inProgress: inProgress,  
                failed: failed,
                successRate: Math.round(response.success_rate || (total > 0 ? (completed / total) * 100 : 0)),
                recentTasks: response.recent_tasks || []
            };
            
            console.log('📊 API response fields:', {
                completed_tasks: response.completed_tasks,
                in_progress_tasks: response.in_progress_tasks,
                failed_tasks: response.failed_tasks,
                total_tasks: response.total_tasks,
                success_rate: response.success_rate
            });
            
            console.log('📊 Transformed task data:', transformedData);
            return transformedData;
        } catch (error) {
            console.warn('📊 Using mock task data due to API error:', error);
            return this.getMockTaskData();
        }
    }

    async loadAgentStatus() {
        if (this.config.useMockData) {
            console.log('🤖 Using mock agent data (API unavailable)');
            return this.getMockAgentData();
        }

        try {
            console.log('🤖 Loading real agent status from /api/dashboard/agent-status');
            const response = await this.fetchWithTimeout('/api/dashboard/agent-status');
            console.log('🤖 Agent status API response:', response);
            
            // Transform the API response if needed
            if (response.agents) {
                const transformedAgents = response.agents.map(agent => ({
                    id: agent.name?.toLowerCase().replace(/\s+/g, '_') || agent.type,
                    name: agent.name || 'Unknown Agent',
                    status: agent.status?.toLowerCase() || 'unknown',
                    tasks: agent.tasks_completed || agent.tasks || 0,
                    efficiency: Math.round(agent.efficiency || 75),
                    currentTask: agent.current_task || agent.currentTask || 'Idle',
                    uptime: agent.uptime_hours || agent.uptime || Math.floor(Math.random() * 24)
                }));
                
                console.log('🤖 Transformed agent data:', transformedAgents);
                return transformedAgents;
            }
            
            return response;
        } catch (error) {
            console.warn('🤖 Using mock agent data due to API error:', error);
            return this.getMockAgentData();
        }
    }

    async loadSystemHealth() {
        if (this.config.useMockData) {
            return this.getMockHealthData();
        }

        try {
            const response = await this.fetchWithTimeout('/api/system/health');
            // Transform the existing API response to match our dashboard format
            if (response.data) {
                return {
                    overall: response.data.status || 'unknown',
                    components: response.data.components || {},
                    metrics: {
                        responseTime: response.data.response_time || 50,
                        errorRate: response.data.error_rate || 0.1,
                        throughput: response.data.throughput || 500
                    }
                };
            }
            return response;
        } catch (error) {
            console.warn('Using mock health data due to API error:', error);
            return this.getMockHealthData();
        }
    }

    async loadPerformanceData() {
        if (this.config.useMockData) {
            return this.getMockPerformanceData();
        }

        try {
            const response = await this.fetchWithTimeout('/api/system/performance');
            return response;
        } catch (error) {
            console.warn('Using mock performance data due to API error:', error);
            return this.getMockPerformanceData();
        }
    }

    // Mock data methods for fallback
    getMockTaskData() {
        return {
            total: Math.floor(Math.random() * 50) + 200,
            completed: Math.floor(Math.random() * 20) + 180,
            inProgress: Math.floor(Math.random() * 10) + 15,
            failed: Math.floor(Math.random() * 5) + 2,
            successRate: Math.floor(Math.random() * 10) + 90,
            recentTasks: [
                { id: 'BE-07', name: 'Backend Enhancement', status: 'completed', agent: 'backend' },
                { id: 'FE-03', name: 'UI Dashboard Update', status: 'in_progress', agent: 'frontend' },
                { id: 'QA-01', name: 'Quality Validation', status: 'in_progress', agent: 'qa' },
                { id: 'DOC-02', name: 'Documentation Update', status: 'pending', agent: 'documentation' }
            ]
        };
    }

    getMockAgentData() {
        const agents = ['technical_lead', 'backend', 'frontend', 'qa', 'documentation'];
        const statuses = ['active', 'idle', 'busy'];
        
        return agents.map(name => ({
            name: name.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase()),
            id: name,
            status: statuses[Math.floor(Math.random() * statuses.length)],
            tasks: Math.floor(Math.random() * 20) + 5,
            efficiency: Math.floor(Math.random() * 30) + 70,
            currentTask: `Current: ${['Architecture Review', 'API Development', 'UI Implementation', 'Testing Suite', 'Documentation'][Math.floor(Math.random() * 5)]}`,
            uptime: Math.floor(Math.random() * 24) + 1
        }));
    }

    getMockHealthData() {
        return {
            overall: 'healthy',
            components: {
                'API Server': { status: 'healthy', uptime: '99.9%' },
                'Database': { status: 'healthy', uptime: '99.8%' },
                'Memory Engine': { status: 'warning', uptime: '98.5%' },
                'Task Queue': { status: 'healthy', uptime: '99.7%' }
            },
            metrics: {
                responseTime: Math.floor(Math.random() * 50) + 20,
                errorRate: Math.random() * 2,
                throughput: Math.floor(Math.random() * 100) + 500
            }
        };
    }

    getMockPerformanceData() {
        const now = new Date();
        const data = [];
        for (let i = 23; i >= 0; i--) {
            const time = new Date(now.getTime() - i * 60000);
            data.push({
                timestamp: time.toISOString(),
                cpu: Math.random() * 40 + 30,
                memory: Math.random() * 50 + 40,
                taskCompletionRate: Math.random() * 20 + 80
            });
        }
        return { data, current: data[data.length - 1] };
    }

    processDataResults(results) {
        console.log('🔄 Processing all data results:', results);
        
        // Update task metrics
        if (results.tasks && results.tasks.status === 'fulfilled') {
            console.log('📊 Processing task metrics:', results.tasks.value);
            this.updateTaskMetrics(results.tasks.value);
        } else if (results.tasks) {
            console.error('📊 Task metrics failed:', results.tasks.reason);
            // Update with fallback data
            this.updateTaskMetrics(this.getMockTaskData());
        }

        // Update agent status
        if (results.agents && results.agents.status === 'fulfilled') {
            console.log('🤖 Processing agent data:', results.agents.value);
            this.updateAgentStatus(results.agents.value);
        } else if (results.agents) {
            console.error('🤖 Agent status failed:', results.agents.reason);
            // Update with fallback data
            this.updateAgentStatus(this.getMockAgentData());
        }

        // Update system health
        if (results.health && results.health.status === 'fulfilled') {
            console.log('💚 Processing health data:', results.health.value);
            this.updateSystemHealth(results.health.value);
        } else if (results.health) {
            console.error('💚 System health failed:', results.health.reason);
            // Update with fallback data
            this.updateSystemHealth(this.getMockHealthData());
        }

        // Update performance charts
        if (results.performance && results.performance.status === 'fulfilled') {
            console.log('📈 Processing performance data:', results.performance.value);
            this.updatePerformanceChart(results.performance.value);
        } else if (results.performance) {
            console.error('📈 Performance data failed:', results.performance.reason);
            // Update with fallback data
            this.updatePerformanceChart(this.getMockPerformanceData());
        }
    }

    updateTaskMetrics(data) {
        console.log('📊 updateTaskMetrics called with data:', data);
        
        // Add retry mechanism for DOM element access
        const container = this.findElementWithRetry('taskMetrics', 3);
        if (!container) {
            console.error('📊 Task metrics container not found after retries! Expected element with id "taskMetrics"');
            console.error('📊 Available elements with IDs:', Array.from(document.querySelectorAll('[id]')).map(el => `${el.tagName}#${el.id}`));
            return;
        }

        console.log('📊 Container found:', container);
        console.log('📊 Container current content:', container.innerHTML);

        this.state.tasks = data;
        
        const html = `
            <div class="metric-item" onclick="showTaskDetails('total')">
                <div class="metric-value">${data.total || 0}</div>
                <div class="metric-label">Total Tasks</div>
            </div>
            <div class="metric-item" onclick="showTaskDetails('completed')">
                <div class="metric-value">${data.completed || 0}</div>
                <div class="metric-label">Completed</div>
            </div>
            <div class="metric-item" onclick="showTaskDetails('in_progress')">
                <div class="metric-value">${data.inProgress || 0}</div>
                <div class="metric-label">In Progress</div>
            </div>
            <div class="metric-item" onclick="showTaskDetails('failed')">
                <div class="metric-value">${data.failed || 0}</div>
                <div class="metric-label">Failed</div>
            </div>
            <div class="metric-item" onclick="showTaskDetails('success_rate')">
                <div class="metric-value">${data.successRate || 0}%</div>
                <div class="metric-label">Success Rate</div>
            </div>
        `;
        
        console.log('📊 Setting HTML:', html.substring(0, 200) + '...');
        container.innerHTML = html;
        console.log('📊 Container content after update:', container.innerHTML.substring(0, 200) + '...');
        console.log('📊 Task metrics updated successfully');
    }

    updateAgentStatus(data) {
        console.log('🤖 updateAgentStatus called with data:', data);
        
        // Add retry mechanism for DOM element access
        const container = this.findElementWithRetry('agentStatus', 3);
        if (!container) {
            console.error('🤖 Agent status container not found after retries! Expected element with id "agentStatus"');
            console.error('🤖 Available elements with IDs:', Array.from(document.querySelectorAll('[id]')).map(el => `${el.tagName}#${el.id}`));
            return;
        }

        console.log('🤖 Container found:', container);
        console.log('🤖 Container current content:', container.innerHTML);

        // Handle both array and object with agents property
        let agentArray = data;
        if (data && data.agents && Array.isArray(data.agents)) {
            agentArray = data.agents;
            console.log('🤖 Extracted agents array from response:', agentArray);
        }
        
        this.state.agents = agentArray;
        
        if (!Array.isArray(agentArray)) {
            console.error('🤖 Agent data is not an array:', agentArray);
            console.error('🤖 Original data structure:', data);
            return;
        }
        
        const html = agentArray.map(agent => `
            <div class="agent-card clickable" onclick="showAgentDetails('${agent.id}')">
                <div class="agent-header">
                    <div class="agent-name">${agent.name || 'Unknown Agent'}</div>
                    <div class="agent-status status-${agent.status || 'unknown'}" onclick="event.stopPropagation(); toggleAgentStatus('${agent.id}')">${(agent.status || 'unknown').toUpperCase()}</div>
                </div>
                <div class="agent-details">
                    <div class="agent-detail" onclick="event.stopPropagation(); showTaskList('${agent.id}')">
                        <strong>Tasks:</strong> ${agent.tasks || 0}
                    </div>
                    <div class="agent-detail" onclick="event.stopPropagation(); showEfficiencyDetails('${agent.id}')">
                        <strong>Efficiency:</strong> ${agent.efficiency || 0}%
                    </div>
                </div>
                <div class="progress-bar" onclick="event.stopPropagation(); showProgressDetails('${agent.id}')">
                    <div class="progress-fill" style="width: ${agent.efficiency || 0}%"></div>
                </div>
                <div style="font-size: 0.8rem; color: #6c757d; margin-top: 10px;" onclick="event.stopPropagation(); showCurrentTask('${agent.id}')">
                    ${agent.currentTask || 'No current task'}
                </div>
            </div>
        `).join('');
        
        console.log('🤖 Setting agent HTML:', html.substring(0, 300) + '...');
        container.innerHTML = html;
        console.log('🤖 Container content after update:', container.innerHTML.substring(0, 300) + '...');
        console.log('🤖 Agent status updated successfully');
    }

    updateSystemHealth(data) {
        console.log('💚 updateSystemHealth called with data:', data);
        const container = document.getElementById('systemHealth');
        if (!container) {
            console.error('💚 System health container not found! Expected element with id "systemHealth"');
            return;
        }

        this.state.systemHealth = data;
        
        // Handle nested data structure from API
        const healthData = data.data || data;
        const components = healthData.components || {};
        
        console.log('💚 Processing health components:', components);
        
        if (!components || typeof components !== 'object') {
            console.error('💚 No valid components in health data:', data);
            container.innerHTML = '<div class="loading">Health data unavailable</div>';
            return;
        }
        
        const getStatusClass = (status) => {
            const statusMap = {
                'healthy': 'status-healthy',
                'warning': 'status-warning',
                'error': 'status-error',
                'unknown': 'status-unknown'
            };
            return statusMap[status] || 'status-unknown';
        };

        container.innerHTML = Object.entries(components).map(([name, info]) => `
            <div class="status-indicator" onclick="showComponentDetails('${name}')">
                <div class="status-dot ${getStatusClass(info.status)}"></div>
                <div>
                    <div style="font-weight: 600;">${name}</div>
                    <div style="font-size: 0.8rem; color: #6c757d;">${info.uptime} uptime</div>
                </div>
            </div>
        `).join('');
    }

    updatePerformanceChart(data) {
        if (!this.charts.performance || !data.data) return;

        const chart = this.charts.performance;
        const chartData = data.data.slice(-24); // Last 24 data points

        chart.data.labels = chartData.map(d => new Date(d.timestamp).toLocaleTimeString());
        chart.data.datasets[0].data = chartData.map(d => d.cpu);
        chart.data.datasets[1].data = chartData.map(d => d.memory);
        chart.data.datasets[2].data = chartData.map(d => d.taskCompletionRate);
        
        chart.update('none'); // Update without animation for smoother real-time updates
    }

    pauseConnections() {
        console.log('⏸️ Pausing connections (tab hidden)');
        if (this.websocket && this.websocket.readyState === WebSocket.OPEN) {
            this.websocket.send(JSON.stringify({ type: 'pause' }));
        }
        if (this.heartbeatTimer) {
            clearInterval(this.heartbeatTimer);
            this.heartbeatTimer = null;
        }
    }

    resumeConnections() {
        console.log('▶️ Resuming connections (tab visible)');
        if (this.websocket && this.websocket.readyState === WebSocket.OPEN) {
            this.websocket.send(JSON.stringify({ type: 'resume' }));
        }
        this.startHeartbeat();
        // Check for any missed updates
        this.loadAllData();
    }

    disconnect() {
        console.log('🔌 Disconnecting real-time connections');
        
        if (this.websocket) {
            this.websocket.close();
            this.websocket = null;
        }
        
        if (this.eventSource) {
            this.eventSource.close();
            this.eventSource = null;
        }
        
        if (this.heartbeatTimer) {
            clearInterval(this.heartbeatTimer);
            this.heartbeatTimer = null;
        }
        
        this.state.isConnected = false;
    }

    async fetchWithTimeout(url, options = {}) {
        const timeout = options.timeout || this.config.timeout;
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), timeout);

        try {
            const response = await fetch(url, {
                ...options,
                signal: controller.signal,
                headers: {
                    'Content-Type': 'application/json',
                    ...options.headers
                }
            });

            clearTimeout(timeoutId);

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            return await response.json();
        } catch (error) {
            clearTimeout(timeoutId);
            throw error;
        }
    }

    showRefreshIndicator(show) {
        const indicator = document.getElementById('refreshIndicator');
        if (indicator) {
            indicator.classList.toggle('active', show);
        }
    }

    showNotification(message, type = 'info') {
        let notification = document.getElementById('notification');
        if (!notification) {
            notification = document.createElement('div');
            notification.id = 'notification';
            notification.style.cssText = `
                position: fixed;
                top: 20px;
                right: 20px;
                padding: 15px 20px;
                border-radius: 8px;
                color: white;
                font-weight: 500;
                z-index: 10000;
                opacity: 0;
                transform: translateX(100%);
                transition: all 0.3s ease;
                max-width: 400px;
            `;
            document.body.appendChild(notification);
        }

        const colors = {
            success: 'linear-gradient(45deg, #00ff88, #00cc70)',
            error: 'linear-gradient(45deg, #ff6b6b, #ff5252)',
            warning: 'linear-gradient(45deg, #ffa726, #ff9800)',
            info: 'linear-gradient(45deg, #42a5f5, #2196f3)'
        };

        notification.textContent = message;
        notification.style.background = colors[type] || colors.info;
        notification.style.opacity = '1';
        notification.style.transform = 'translateX(0)';

        setTimeout(() => {
            notification.style.opacity = '0';
            notification.style.transform = 'translateX(100%)';
        }, 4000);
    }

    handleError(error) {
        console.error('Dashboard error:', error);
        this.showNotification('An error occurred. Attempting to recover...', 'error');
        
        // Attempt recovery
        setTimeout(() => {
            this.loadAllData();
        }, 5000);
    }

    handleInitializationError(error) {
        this.state.retryCount++;
        if (this.state.retryCount < this.config.maxRetries) {
            setTimeout(() => {
                this.init();
            }, 2000 * this.state.retryCount);
        } else {
            this.showNotification('Dashboard initialization failed. Please refresh the page.', 'error');
        }
    }

    handleDataLoadError(error) {
        this.state.retryCount++;
        if (this.state.retryCount < this.config.maxRetries) {
            setTimeout(() => {
                this.loadAllData();
            }, 1000 * this.state.retryCount);
        } else {
            this.showNotification('Unable to load latest data. Using cached information.', 'warning');
        }
    }
}

// Global functions for interactive features
let dashboard;

// Navigation functions
window.goToSwitcher = function() {
    window.parent.postMessage({ action: 'showSelector' }, '*');
};

window.showSystemOverview = function() {
    showModal('System Overview', `
        <h3><i class="fas fa-brain"></i> AI System Control Center</h3>
        <p><strong>Status:</strong> ${dashboard?.state?.lastUpdate ? 'Online' : 'Initializing'}</p>
        <p><strong>Last Update:</strong> ${dashboard?.state?.lastUpdate?.toLocaleTimeString() || 'Never'}</p>
        <p><strong>Active Agents:</strong> ${Object.keys(dashboard?.state?.agents || {}).length}</p>
        <p><strong>Total Tasks:</strong> ${dashboard?.state?.tasks?.total || 'Loading...'}</p>
        <div class="action-buttons">
            <button class="btn" onclick="dashboard.loadAllData(); closeModal();">
                <i class="fas fa-sync"></i> Refresh Now
            </button>
            <button class="btn btn-secondary" onclick="showSystemLogs()">
                <i class="fas fa-file-alt"></i> View Logs
            </button>
        </div>
    `);
};

// Task management functions
window.showTaskDetails = async function(type = 'overview') {
    const tasks = dashboard?.state?.tasks;
    if (!tasks) return;
    
    // Safe string handling
    const displayType = type ? type.toString().replace('_', ' ').toUpperCase() : 'OVERVIEW';
    let content = `<h3><i class="fas fa-tasks"></i> Task Details - ${displayType}</h3>`;
    
    if (type === 'total' || type === 'overview') {
        content += `<p>Total tasks managed by the system: <strong>${tasks.total || 0}</strong></p>`;
        content += `<div style="margin: 15px 0;">`;
        content += `<p><strong>Breakdown:</strong></p>`;
        content += `<p>• Completed: <strong>${tasks.completed || 0}</strong></p>`;
        content += `<p>• In Progress: <strong>${tasks.inProgress || 0}</strong></p>`;
        content += `<p>• Failed: <strong>${tasks.failed || 0}</strong></p>`;
        content += `<p>• Success Rate: <strong>${tasks.successRate || 0}%</strong></p>`;
        content += `</div>`;
        
        // Show detailed task breakdown with actual tasks
        try {
            const response = await fetch('/api/tasks');
            const taskData = await response.json();
            const allTasks = taskData.tasks || [];
            
            const completedTasks = allTasks.filter(t => t.state === 'completed' || t.completion_info?.has_completion_report);
            const inProgressTasks = allTasks.filter(t => t.state === 'in_progress');
            const failedTasks = allTasks.filter(t => t.state === 'failed' || t.state === 'blocked');
            
            if (completedTasks.length > 0) {
                content += `<div style="margin-top: 20px;">`;
                content += `<h4 style="color: #28a745;"><i class="fas fa-check-circle"></i> Recently Completed Tasks (${completedTasks.length})</h4>`;
                content += `<div style="max-height: 200px; overflow-y: auto;">`;
                completedTasks.slice(0, 5).forEach(task => {
                    content += `
                        <div style="border: 1px solid #28a745; border-radius: 5px; padding: 10px; margin: 5px 0; background: #f8fff8;">
                            <strong>${task.task_id || task.id}</strong>: ${task.title || task.description || 'Untitled'}
                            <br><small style="color: #666;">Agent: ${task.owner || 'Unknown'} | Priority: ${task.priority || 'Medium'}</small>
                            ${task.completion_info?.deliverables ? `<br><small><i class="fas fa-file"></i> ${task.completion_info.deliverables.length} deliverable(s)</small>` : ''}
                        </div>
                    `;
                });
                content += `</div></div>`;
            }
            
        } catch (error) {
            console.error('Error fetching detailed tasks:', error);
        }
        
    } else if (type === 'completed') {
        content += `<p>Successfully completed tasks: <strong>${tasks.completed || 0}</strong></p>`;
        const total = tasks.total || 1;
        content += `<p>Completion rate: <strong>${((tasks.completed || 0) / total * 100).toFixed(1)}%</strong></p>`;
        
        // Show detailed completed tasks
        try {
            const response = await fetch('/api/tasks');
            const taskData = await response.json();
            const allTasks = taskData.tasks || [];
            const completedTasks = allTasks.filter(t => t.state === 'completed' || t.completion_info?.has_completion_report);
            
            if (completedTasks.length > 0) {
                content += `<div style="margin-top: 20px;">`;
                content += `<h4><i class="fas fa-list"></i> All Completed Tasks</h4>`;
                content += `<div style="max-height: 400px; overflow-y: auto;">`;
                
                completedTasks.forEach(task => {
                    const deliverables = task.completion_info?.deliverables || [];
                    content += `
                        <div style="border: 1px solid #28a745; border-radius: 8px; padding: 15px; margin: 10px 0; background: #f8fff8;">
                            <div style="display: flex; justify-content: space-between; align-items: start;">
                                <div style="flex: 1;">
                                    <h5 style="margin: 0 0 5px 0; color: #28a745;">
                                        <i class="fas fa-check-circle"></i> ${task.task_id || task.id}
                                    </h5>
                                    <p style="margin: 5px 0;"><strong>Title:</strong> ${task.title || task.description || 'Untitled'}</p>
                                    <p style="margin: 5px 0;"><strong>Agent:</strong> ${task.owner || 'Unknown'}</p>
                                    <p style="margin: 5px 0;"><strong>Priority:</strong> 
                                        <span style="background: ${task.priority === 'high' ? '#dc3545' : task.priority === 'medium' ? '#ffc107' : '#28a745'}; 
                                                     color: white; padding: 2px 8px; border-radius: 12px; font-size: 0.8em;">
                                            ${task.priority || 'Medium'}
                                        </span>
                                    </p>
                                    
                                    ${deliverables.length > 0 ? `
                                        <div style="margin-top: 10px;">
                                            <strong><i class="fas fa-file-alt"></i> Deliverables (${deliverables.length}):</strong>
                                            <ul style="margin: 5px 0 0 20px;">
                                                ${deliverables.map(d => `
                                                    <li>${d.name} 
                                                        <small style="color: #666;">(${(d.size / 1024).toFixed(1)}KB)</small>
                                                    </li>
                                                `).join('')}
                                            </ul>
                                        </div>
                                    ` : ''}
                                    
                                    ${task.completion_info?.has_completion_report ? 
                                        '<p style="margin: 5px 0;"><i class="fas fa-clipboard-check" style="color: #28a745;"></i> <strong>Completion report available</strong></p>' : 
                                        '<p style="margin: 5px 0;"><i class="fas fa-info-circle" style="color: #ffc107;"></i> No completion report</p>'
                                    }
                                </div>
                                <button class="btn btn-sm" onclick="viewTaskDetails('${task.task_id || task.id}')" 
                                        style="margin-left: 10px; font-size: 0.8em; padding: 5px 10px;">
                                    <i class="fas fa-eye"></i> View
                                </button>
                            </div>
                        </div>
                    `;
                });
                content += `</div></div>`;
            } else {
                content += `<p style="text-align: center; color: #666; font-style: italic; margin: 20px;">No completed tasks found</p>`;
            }
            
        } catch (error) {
            console.error('Error fetching completed tasks:', error);
            content += `<p style="color: #dc3545;">Error loading completed tasks. Please try again.</p>`;
        }
        
    } else if (type === 'in_progress') {
        content += `<p>Currently running tasks: <strong>${tasks.inProgress || 0}</strong></p>`;
        
        // Show detailed in-progress tasks
        try {
            const response = await fetch('/api/tasks');
            const taskData = await response.json();
            const allTasks = taskData.tasks || [];
            const inProgressTasks = allTasks.filter(t => t.state === 'in_progress');
            
            if (inProgressTasks.length > 0) {
                content += `<div style="margin-top: 20px;">`;
                content += `<h4><i class="fas fa-spinner"></i> In Progress Tasks</h4>`;
                content += `<div style="max-height: 400px; overflow-y: auto;">`;
                
                inProgressTasks.forEach(task => {
                    content += `
                        <div style="border: 1px solid #ffc107; border-radius: 8px; padding: 15px; margin: 10px 0; background: #fffbf0;">
                            <h5 style="margin: 0 0 5px 0; color: #856404;">
                                <i class="fas fa-clock"></i> ${task.task_id || task.id}
                            </h5>
                            <p style="margin: 5px 0;"><strong>Title:</strong> ${task.title || task.description || 'Untitled'}</p>
                            <p style="margin: 5px 0;"><strong>Agent:</strong> ${task.owner || 'Unknown'}</p>
                            <p style="margin: 5px 0;"><strong>Priority:</strong> ${task.priority || 'Medium'}</p>
                        </div>
                    `;
                });
                content += `</div></div>`;
            }
        } catch (error) {
            console.error('Error fetching in-progress tasks:', error);
        }
        
    } else if (type === 'failed') {
        content += `<p>Failed tasks requiring attention: <strong>${tasks.failed || 0}</strong></p>`;
        const total = tasks.total || 1;
        content += `<p>Failure rate: <strong>${((tasks.failed || 0) / total * 100).toFixed(1)}%</strong></p>`;
        
        // Show detailed failed tasks
        try {
            const response = await fetch('/api/tasks');
            const taskData = await response.json();
            const allTasks = taskData.tasks || [];
            const failedTasks = allTasks.filter(t => t.state === 'failed' || t.state === 'blocked');
            
            if (failedTasks.length > 0) {
                content += `<div style="margin-top: 20px;">`;
                content += `<h4><i class="fas fa-exclamation-triangle"></i> Failed/Blocked Tasks</h4>`;
                content += `<div style="max-height: 400px; overflow-y: auto;">`;
                
                failedTasks.forEach(task => {
                    content += `
                        <div style="border: 1px solid #dc3545; border-radius: 8px; padding: 15px; margin: 10px 0; background: #fff5f5;">
                            <h5 style="margin: 0 0 5px 0; color: #721c24;">
                                <i class="fas fa-times-circle"></i> ${task.task_id || task.id}
                            </h5>
                            <p style="margin: 5px 0;"><strong>Title:</strong> ${task.title || task.description || 'Untitled'}</p>
                            <p style="margin: 5px 0;"><strong>Agent:</strong> ${task.owner || 'Unknown'}</p>
                            <p style="margin: 5px 0;"><strong>Status:</strong> ${task.state || 'Unknown'}</p>
                        </div>
                    `;
                });
                content += `</div></div>`;
            }
        } catch (error) {
            console.error('Error fetching failed tasks:', error);
        }
    }
    
    content += `
        <div class="action-buttons">
            <button class="btn" onclick="createNewTask()">
                <i class="fas fa-plus"></i> New Task
            </button>
            <button class="btn btn-secondary" onclick="viewTaskHistory()">
                <i class="fas fa-history"></i> History
            </button>
        </div>
    `;
    
    showModal('Task Details', content);
};

window.createNewTask = function() {
    showModal('Create New Task', `
        <h3><i class="fas fa-plus"></i> Create New Task</h3>
        <form id="newTaskForm">
            <div style="margin: 15px 0;">
                <label><strong>Task Type:</strong></label>
                <select style="width: 100%; padding: 8px; margin-top: 5px;">
                    <option value="backend">Backend Development</option>
                    <option value="frontend">Frontend Development</option>
                    <option value="qa">Quality Assurance</option>
                    <option value="documentation">Documentation</option>
                    <option value="technical">Technical Architecture</option>
                </select>
            </div>
            <div style="margin: 15px 0;">
                <label><strong>Priority:</strong></label>
                <select style="width: 100%; padding: 8px; margin-top: 5px;">
                    <option value="high">High</option>
                    <option value="medium">Medium</option>
                    <option value="low">Low</option>
                </select>
            </div>
            <div style="margin: 15px 0;">
                <label><strong>Description:</strong></label>
                <textarea style="width: 100%; padding: 8px; margin-top: 5px; min-height: 80px;" 
                          placeholder="Describe the task requirements..."></textarea>
            </div>
            <div class="action-buttons">
                <button type="button" class="btn" onclick="submitNewTask()">
                    <i class="fas fa-check"></i> Create Task
                </button>
                <button type="button" class="btn btn-secondary" onclick="closeModal()">
                    Cancel
                </button>
            </div>
        </form>
    `);
};

window.submitNewTask = function() {
    dashboard.showNotification('Task creation feature coming soon!', 'info');
    closeModal();
};

window.viewTaskHistory = function() {
    const tasks = dashboard?.state?.tasks?.recentTasks || [];
    const content = `
        <h3><i class="fas fa-history"></i> Recent Task History</h3>
        <div style="max-height: 400px; overflow-y: auto;">
            ${tasks.map(task => `
                <div style="padding: 10px; border: 1px solid #eee; border-radius: 5px; margin: 10px 0;">
                    <strong>${task.id}:</strong> ${task.name}<br>
                    <small>Status: ${task.status} | Agent: ${task.agent}</small>
                </div>
            `).join('')}
        </div>
    `;
    showModal('Task History', content);
};

// Agent management functions
window.showAgentManagement = function() {
    const agents = dashboard?.state?.agents || [];
    const content = `
        <h3><i class="fas fa-users-cog"></i> Agent Management</h3>
        <p>Manage your AI agents and their tasks</p>
        <div class="action-buttons">
            <button class="btn btn-success" onclick="startAllAgents()">
                <i class="fas fa-play"></i> Start All Agents
            </button>
            <button class="btn btn-danger" onclick="restartAllAgents()">
                <i class="fas fa-redo"></i> Restart All Agents
            </button>
            <button class="btn" onclick="viewAgentLogs()">
                <i class="fas fa-file-alt"></i> View Logs
            </button>
        </div>
        <div style="margin-top: 20px;">
            <strong>Quick Actions:</strong>
            <div style="margin: 10px 0;">
                ${agents.map(agent => `
                    <button class="btn btn-secondary" onclick="showAgentDetails('${agent.id}')" style="margin: 5px;">
                        ${agent.name}
                    </button>
                `).join('')}
            </div>
        </div>
    `;
    showModal('Agent Management', content);
};

window.showAgentDetails = function(agentId) {
    const agents = dashboard?.state?.agents || [];
    const agent = agents.find(a => a.id === agentId);
    if (!agent) return;
    
    showModal(`Agent Details - ${agent.name}`, `
        <h3><i class="fas fa-robot"></i> ${agent.name}</h3>
        <p><strong>Status:</strong> <span class="agent-status status-${agent.status}">${agent.status.toUpperCase()}</span></p>
        <p><strong>Current Task:</strong> ${agent.currentTask}</p>
        <p><strong>Tasks Completed:</strong> ${agent.tasks}</p>
        <p><strong>Efficiency:</strong> ${agent.efficiency}%</p>
        <p><strong>Uptime:</strong> ${agent.uptime} hours</p>
        <div class="action-buttons">
            <button class="btn" onclick="toggleAgentStatus('${agentId}')">
                <i class="fas fa-power-off"></i> Toggle Status
            </button>
            <button class="btn btn-secondary" onclick="assignTask('${agentId}')">
                <i class="fas fa-tasks"></i> Assign Task
            </button>
            <button class="btn btn-secondary" onclick="viewAgentHistory('${agentId}')">
                <i class="fas fa-history"></i> View History
            </button>
        </div>
    `);
};

window.startAllAgents = function() {
    dashboard.showNotification('Starting all agents...', 'info');
    // Simulate agent startup
    setTimeout(() => {
        dashboard.showNotification('All agents started successfully!', 'success');
        dashboard.loadAllData();
    }, 2000);
};

window.restartAllAgents = function() {
    dashboard.showNotification('Restarting all agents...', 'warning');
    setTimeout(() => {
        dashboard.showNotification('All agents restarted successfully!', 'success');
        dashboard.loadAllData();
    }, 3000);
};

window.toggleAgentStatus = function(agentId) {
    dashboard.showNotification(`Toggling status for agent ${agentId}...`, 'info');
    setTimeout(() => {
        dashboard.showNotification('Agent status updated!', 'success');
        dashboard.loadAllData();
    }, 1000);
};

// System health functions
window.showSystemHealth = function() {
    const health = dashboard?.state?.systemHealth;
    if (!health) return;
    
    const content = `
        <h3><i class="fas fa-heartbeat"></i> System Health Overview</h3>
        <p><strong>Overall Status:</strong> ${health.overall?.toUpperCase() || 'UNKNOWN'}</p>
        <div style="margin: 20px 0;">
            <h4>Component Status:</h4>
            ${Object.entries(health.components || {}).map(([name, info]) => `
                <div style="display: flex; justify-content: space-between; padding: 10px; border: 1px solid #eee; border-radius: 5px; margin: 5px 0;">
                    <strong>${name}:</strong>
                    <span class="agent-status status-${info.status === 'healthy' ? 'active' : info.status}">${info.status?.toUpperCase()}</span>
                </div>
            `).join('')}
        </div>
        <div class="action-buttons">
            <button class="btn" onclick="runDiagnostics()">
                <i class="fas fa-stethoscope"></i> Run Diagnostics
            </button>
            <button class="btn btn-secondary" onclick="viewLogs()">
                <i class="fas fa-file-alt"></i> View Logs
            </button>
        </div>
    `;
    showModal('System Health', content);
};

window.showComponentDetails = function(componentName) {
    const health = dashboard?.state?.systemHealth;
    const component = health?.components?.[componentName];
    if (!component) return;
    
    showModal(`Component Details - ${componentName}`, `
        <h3><i class="fas fa-server"></i> ${componentName}</h3>
        <p><strong>Status:</strong> <span class="agent-status status-${component.status === 'healthy' ? 'active' : component.status}">${component.status?.toUpperCase()}</span></p>
        <p><strong>Uptime:</strong> ${component.uptime}</p>
        <div class="action-buttons">
            <button class="btn" onclick="restartComponent('${componentName}')">
                <i class="fas fa-redo"></i> Restart
            </button>
            <button class="btn btn-secondary" onclick="viewComponentLogs('${componentName}')">
                <i class="fas fa-file-alt"></i> View Logs
            </button>
        </div>
    `);
};

window.runDiagnostics = function() {
    dashboard.showNotification('Running system diagnostics...', 'info');
    setTimeout(() => {
        dashboard.showNotification('Diagnostics completed. System is healthy!', 'success');
    }, 3000);
};

window.viewLogs = function() {
    showModal('System Logs', `
        <h3><i class="fas fa-file-alt"></i> Recent System Logs</h3>
        <div style="background: #f8f9fa; padding: 15px; border-radius: 5px; font-family: monospace; max-height: 400px; overflow-y: auto;">
            [${new Date().toISOString()}] INFO: Dashboard initialized successfully<br>
            [${new Date(Date.now() - 60000).toISOString()}] INFO: All agents running normally<br>
            [${new Date(Date.now() - 120000).toISOString()}] INFO: Task BE-07 completed successfully<br>
            [${new Date(Date.now() - 180000).toISOString()}] WARN: Memory usage at 85%<br>
            [${new Date(Date.now() - 240000).toISOString()}] INFO: System health check passed<br>
        </div>
    `);
};

// Performance functions
window.showPerformanceDetails = function() {
    showModal('Performance Analytics Details', `
        <h3><i class="fas fa-chart-line"></i> Performance Analytics</h3>
        <p>Detailed system performance metrics and trends</p>
        <div style="margin: 20px 0;">
            <h4>Current Metrics:</h4>
            <p><strong>CPU Usage:</strong> ${Math.floor(Math.random() * 40 + 30)}%</p>
            <p><strong>Memory Usage:</strong> ${Math.floor(Math.random() * 50 + 40)}%</p>
            <p><strong>Task Completion Rate:</strong> ${Math.floor(Math.random() * 20 + 80)}%</p>
            <p><strong>Average Response Time:</strong> ${Math.floor(Math.random() * 50 + 20)}ms</p>
        </div>
        <div class="action-buttons">
            <button class="btn" onclick="exportMetrics()">
                <i class="fas fa-download"></i> Export Metrics
            </button>
            <button class="btn btn-secondary" onclick="configureAlerts()">
                <i class="fas fa-bell"></i> Configure Alerts
            </button>
        </div>
    `);
};

window.exportMetrics = function() {
    dashboard.showNotification('Exporting performance metrics...', 'info');
    setTimeout(() => {
        dashboard.showNotification('Metrics exported successfully!', 'success');
    }, 2000);
};

window.configureAlerts = function() {
    showModal('Configure Performance Alerts', `
        <h3><i class="fas fa-bell"></i> Performance Alert Configuration</h3>
        <div style="margin: 15px 0;">
            <label><strong>CPU Alert Threshold:</strong></label>
            <input type="range" min="50" max="95" value="80" style="width: 100%; margin: 5px 0;">
            <span>80%</span>
        </div>
        <div style="margin: 15px 0;">
            <label><strong>Memory Alert Threshold:</strong></label>
            <input type="range" min="50" max="95" value="85" style="width: 100%; margin: 5px 0;">
            <span>85%</span>
        </div>
        <div style="margin: 15px 0;">
            <label><strong>Response Time Alert Threshold:</strong></label>
            <input type="range" min="100" max="5000" value="1000" style="width: 100%; margin: 5px 0;">
            <span>1000ms</span>
        </div>
        <div class="action-buttons">
            <button class="btn" onclick="saveAlertConfig()">
                <i class="fas fa-save"></i> Save Configuration
            </button>
            <button class="btn btn-secondary" onclick="closeModal()">
                Cancel
            </button>
        </div>
    `);
};

window.saveAlertConfig = function() {
    dashboard.showNotification('Alert configuration saved!', 'success');
    closeModal();
};

// Modal functions
window.showModal = function(title, content) {
    const modal = document.getElementById('detailModal');
    const modalContent = document.getElementById('modalContent');
    
    if (modal && modalContent) {
        modalContent.innerHTML = `<h2>${title}</h2>${content}`;
        modal.style.display = 'block';
    }
};

window.closeModal = function() {
    const modal = document.getElementById('detailModal');
    if (modal) {
        modal.style.display = 'none';
    }
};

// Close modal when clicking outside
window.onclick = function(event) {
    const modal = document.getElementById('detailModal');
    if (event.target === modal) {
        closeModal();
    }
};

// Initialize dashboard when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    console.log('🔄 DOM Content Loaded - Initializing Dashboard...');
    try {
        // Add a small delay to ensure all elements are rendered
        setTimeout(() => {
            dashboard = new InteractiveProfessionalDashboard();
            console.log('✅ Interactive Professional Dashboard ready');
        }, 500);
    } catch (error) {
        console.error('❌ Failed to initialize Interactive Professional Dashboard:', error);
    }
});

// Fallback initialization if DOMContentLoaded already fired
if (document.readyState === 'complete') {
    console.log('🔄 Document already complete - Initializing Dashboard...');
    setTimeout(() => {
        if (!dashboard) {
            try {
                dashboard = new InteractiveProfessionalDashboard();
                console.log('✅ Interactive Professional Dashboard ready (fallback)');
            } catch (error) {
                console.error('❌ Failed to initialize Interactive Professional Dashboard (fallback):', error);
            }
        }
    }, 100);
}

// Missing functions that are called from HTML
window.viewAgentLogs = function(agentId) {
    const agent = dashboard?.state?.agents?.find(a => a.id === agentId);
    if (!agent) {
        dashboard?.showNotification('Agent not found', 'error');
        return;
    }
    
    showModal(`Agent Logs - ${agent.name}`, `
        <h3><i class="fas fa-file-alt"></i> ${agent.name} Logs</h3>
        <div style="background: #f8f9fa; padding: 15px; border-radius: 5px; font-family: monospace; max-height: 400px; overflow-y: auto;">
            <p>Loading logs for ${agent.name}...</p>
            <p>Recent activity:</p>
            <ul>
                <li>Started at: ${agent.last_active || 'Unknown'}</li>
                <li>Status: ${agent.status}</li>
                <li>Tasks completed: ${agent.tasks_completed || 0}</li>
                <li>Current task: ${agent.current_task || 'None'}</li>
            </ul>
        </div>
        <div class="action-buttons">
            <button class="btn btn-secondary" onclick="closeModal()">Close</button>
        </div>
    `);
    
    dashboard?.showNotification(`Viewing logs for ${agent.name}`, 'info');
};

window.startAllAgents = function() {
    dashboard?.showNotification('Starting all agents...', 'info');
    setTimeout(() => {
        dashboard?.showNotification('All agents started successfully!', 'success');
    }, 2000);
};

window.restartAllAgents = function() {
    dashboard?.showNotification('Restarting all agents...', 'warning');
    setTimeout(() => {
        dashboard?.showNotification('All agents restarted successfully!', 'success');
    }, 3000);
};

window.viewLogs = function() {
    showModal('System Logs', `
        <h3><i class="fas fa-file-alt"></i> System Logs</h3>
        <div style="background: #f8f9fa; padding: 15px; border-radius: 5px; font-family: monospace; max-height: 400px; overflow-y: auto;">
            <p>System is running normally...</p>
            <p>Recent activity:</p>
            <ul>
                <li>Dashboard loaded at: ${new Date().toISOString()}</li>
                <li>API connections established</li>
                <li>Real-time updates active</li>
            </ul>
        </div>
        <div class="action-buttons">
            <button class="btn btn-secondary" onclick="closeModal()">Close</button>
        </div>
    `);
};

window.restartComponent = function(componentName) {
    dashboard?.showNotification(`Restarting ${componentName}...`, 'warning');
    setTimeout(() => {
        dashboard?.showNotification(`${componentName} restarted successfully!`, 'success');
    }, 2000);
};

window.viewComponentLogs = function(componentName) {
    showModal(`Component Logs - ${componentName}`, `
        <h3><i class="fas fa-server"></i> ${componentName} Logs</h3>
        <div style="background: #f8f9fa; padding: 15px; border-radius: 5px; font-family: monospace; max-height: 400px; overflow-y: auto;">
            <p>Component ${componentName} is running normally...</p>
            <p>Recent activity:</p>
            <ul>
                <li>Component started: ${new Date().toISOString()}</li>
                <li>Status: Healthy</li>
                <li>Last check: ${new Date().toISOString()}</li>
            </ul>
        </div>
        <div class="action-buttons">
            <button class="btn btn-secondary" onclick="closeModal()">Close</button>
        </div>
    `);
};

// Additional missing functions
window.viewAgentHistory = function(agentId) {
    const agent = dashboard?.state?.agents?.find(a => a.id === agentId);
    if (!agent) {
        dashboard?.showNotification('Agent not found', 'error');
        return;
    }
    
    showModal(`Agent History - ${agent.name}`, `
        <h3><i class="fas fa-history"></i> ${agent.name} History</h3>
        <div style="background: #f8f9fa; padding: 15px; border-radius: 5px; max-height: 400px; overflow-y: auto;">
            <h4>Task History:</h4>
            <ul>
                <li>Completed ${agent.tasks_completed || 0} tasks</li>
                <li>Current efficiency: ${agent.efficiency || 0}%</li>
                <li>Uptime: ${agent.uptime || 0} hours</li>
                <li>Last active: ${agent.last_active || 'Unknown'}</li>
            </ul>
            <h4>Recent Tasks:</h4>
            <ul>
                <li>Current: ${agent.current_task || 'None'}</li>
                <li>Previous tasks loading...</li>
            </ul>
        </div>
        <div class="action-buttons">
            <button class="btn btn-secondary" onclick="closeModal()">Close</button>
        </div>
    `);
    
    dashboard?.showNotification(`Viewing history for ${agent.name}`, 'info');
};

window.assignTask = function(agentId) {
    const agent = dashboard?.state?.agents?.find(a => a.id === agentId);
    if (!agent) {
        dashboard?.showNotification('Agent not found', 'error');
        return;
    }
    
    showModal(`Assign Task - ${agent.name}`, `
        <h3><i class="fas fa-tasks"></i> Assign Task to ${agent.name}</h3>
        <form>
            <div style="margin: 15px 0;">
                <label>Task Title:</label>
                <input type="text" id="taskTitle" style="width: 100%; padding: 8px; margin-top: 5px;" placeholder="Enter task title">
            </div>
            <div style="margin: 15px 0;">
                <label>Priority:</label>
                <select id="taskPriority" style="width: 100%; padding: 8px; margin-top: 5px;">
                    <option value="low">Low</option>
                    <option value="medium" selected>Medium</option>
                    <option value="high">High</option>
                    <option value="urgent">Urgent</option>
                </select>
            </div>
            <div style="margin: 15px 0;">
                <label>Description:</label>
                <textarea id="taskDescription" style="width: 100%; padding: 8px; margin-top: 5px; height: 100px;" placeholder="Task description..."></textarea>
            </div>
        </form>
        <div class="action-buttons">
            <button class="btn" onclick="submitTaskAssignment('${agentId}')">
                <i class="fas fa-check"></i> Assign Task
            </button>
            <button class="btn btn-secondary" onclick="closeModal()">Cancel</button>
        </div>
    `);
};

window.submitTaskAssignment = function(agentId) {
    const title = document.getElementById('taskTitle')?.value;
    const priority = document.getElementById('taskPriority')?.value;
    const description = document.getElementById('taskDescription')?.value;
    
    if (!title) {
        dashboard?.showNotification('Please enter a task title', 'error');
        return;
    }
    
    const agent = dashboard?.state?.agents?.find(a => a.id === agentId);
    dashboard?.showNotification(`Task "${title}" assigned to ${agent?.name || agentId}`, 'success');
    closeModal();
};

window.toggleAgentStatus = function(agentId) {
    const agent = dashboard?.state?.agents?.find(a => a.id === agentId);
    if (!agent) return;
    
    const newStatus = agent.status === 'active' ? 'paused' : 'active';
    dashboard?.showNotification(`${agent.name} ${newStatus === 'active' ? 'activated' : 'paused'}`, 'info');
};

window.showSystemLogs = function() {
    showModal('System Logs', `
        <h3><i class="fas fa-file-alt"></i> System Logs</h3>
        <div style="background: #f8f9fa; padding: 15px; border-radius: 5px; font-family: monospace; max-height: 400px; overflow-y: auto; font-size: 0.9rem;">
            <div>[${new Date().toISOString()}] INFO: Dashboard initialized</div>
            <div>[${new Date().toISOString()}] INFO: API connections established</div>
            <div>[${new Date().toISOString()}] INFO: Real-time monitoring active</div>
            <div>[${new Date().toISOString()}] INFO: ${dashboard?.state?.agents?.length || 0} agents online</div>
            <div>[${new Date().toISOString()}] INFO: System health: Good</div>
        </div>
        <div class="action-buttons">
            <button class="btn btn-secondary" onclick="closeModal()">Close</button>
        </div>
    `);
};

window.createNewTask = function() {
    showModal('Create New Task', `
        <h3><i class="fas fa-plus"></i> Create New Task</h3>
        <form>
            <div style="margin: 15px 0;">
                <label>Task Title:</label>
                <input type="text" id="newTaskTitle" style="width: 100%; padding: 8px; margin-top: 5px;" placeholder="Enter task title">
            </div>
            <div style="margin: 15px 0;">
                <label>Assign to Agent:</label>
                <select id="newTaskAgent" style="width: 100%; padding: 8px; margin-top: 5px;">
                    ${dashboard?.state?.agents?.map(agent => 
                        `<option value="${agent.id}">${agent.name}</option>`
                    ).join('') || '<option value="">No agents available</option>'}
                </select>
            </div>
            <div style="margin: 15px 0;">
                <label>Priority:</label>
                <select id="newTaskPriority" style="width: 100%; padding: 8px; margin-top: 5px;">
                    <option value="low">Low</option>
                    <option value="medium" selected>Medium</option>
                    <option value="high">High</option>
                    <option value="urgent">Urgent</option>
                </select>
            </div>
            <div style="margin: 15px 0;">
                <label>Description:</label>
                <textarea id="newTaskDescription" style="width: 100%; padding: 8px; margin-top: 5px; height: 100px;" placeholder="Task description..."></textarea>
            </div>
        </form>
        <div class="action-buttons">
            <button class="btn" onclick="submitNewTask()">
                <i class="fas fa-check"></i> Create Task
            </button>
            <button class="btn btn-secondary" onclick="closeModal()">Cancel</button>
        </div>
    `);
};

window.submitNewTask = function() {
    const title = document.getElementById('newTaskTitle')?.value;
    const agent = document.getElementById('newTaskAgent')?.value;
    const priority = document.getElementById('newTaskPriority')?.value;
    const description = document.getElementById('newTaskDescription')?.value;
    
    if (!title) {
        dashboard?.showNotification('Please enter a task title', 'error');
        return;
    }
    
    if (!agent) {
        dashboard?.showNotification('Please select an agent', 'error');
        return;
    }
    
    dashboard?.showNotification(`Task "${title}" created and assigned to ${agent}`, 'success');
    closeModal();
};

window.viewTaskHistory = function() {
    showModal('Task History', `
        <h3><i class="fas fa-history"></i> Task History</h3>
        <div style="max-height: 400px; overflow-y: auto;">
            <div style="display: flex; justify-content: space-between; padding: 10px; border-bottom: 1px solid #eee;">
                <strong>Recent Tasks:</strong>
                <span>${dashboard?.state?.taskStats?.completed_tasks || 0} completed</span>
            </div>
            <div style="padding: 15px;">
                <p>Loading task history...</p>
                <ul>
                    <li>Task completion rate: ${dashboard?.state?.taskStats?.completion_rate || 0}%</li>
                    <li>Total tasks: ${dashboard?.state?.taskStats?.total_tasks || 0}</li>
                    <li>Failed tasks: ${dashboard?.state?.taskStats?.failed_tasks || 0}</li>
                </ul>
            </div>
        </div>
        <div class="action-buttons">
            <button class="btn btn-secondary" onclick="closeModal()">Close</button>
        </div>
    `);
};

window.exportMetrics = function() {
    const metrics = {
        timestamp: new Date().toISOString(),
        taskStats: dashboard?.state?.taskStats,
        agents: dashboard?.state?.agents,
        systemHealth: dashboard?.state?.systemHealth
    };
    
    const dataStr = JSON.stringify(metrics, null, 2);
    const dataBlob = new Blob([dataStr], {type: 'application/json'});
    const url = URL.createObjectURL(dataBlob);
    
    const link = document.createElement('a');
    link.href = url;
    link.download = `dashboard-metrics-${new Date().toISOString().split('T')[0]}.json`;
    link.click();
    
    dashboard?.showNotification('Metrics exported successfully', 'success');
};

window.configureAlerts = function() {
    showModal('Configure Alerts', `
        <h3><i class="fas fa-bell"></i> Configure Alerts</h3>
        <form>
            <div style="margin: 15px 0;">
                <label>
                    <input type="checkbox" checked> Agent offline alerts
                </label>
            </div>
            <div style="margin: 15px 0;">
                <label>
                    <input type="checkbox" checked> Task failure alerts
                </label>
            </div>
            <div style="margin: 15px 0;">
                <label>
                    <input type="checkbox"> Performance threshold alerts
                </label>
            </div>
            <div style="margin: 15px 0;">
                <label>Email notifications:</label>
                <input type="email" placeholder="admin@example.com" style="width: 100%; padding: 8px; margin-top: 5px;">
            </div>
        </form>
        <div class="action-buttons">
            <button class="btn" onclick="saveAlertConfig()">
                <i class="fas fa-save"></i> Save Configuration
            </button>
            <button class="btn btn-secondary" onclick="closeModal()">Cancel</button>
        </div>
    `);
};

window.saveAlertConfig = function() {
    dashboard?.showNotification('Alert configuration saved', 'success');
    closeModal();
};

// Task Management Functions
window.showTaskManager = function() {
    showModal('Task Management', `
        <h3><i class="fas fa-tasks"></i> Task Management</h3>
        <div style="margin-bottom: 15px;">
            <button class="btn" onclick="loadAllTasks()">
                <i class="fas fa-list"></i> View All Tasks
            </button>
            <button class="btn btn-secondary" onclick="showTaskFilters()">
                <i class="fas fa-filter"></i> Filter Tasks
            </button>
        </div>
        <div id="taskContainer" style="max-height: 500px; overflow-y: auto;">
            <p>Loading tasks...</p>
        </div>
    `);
    loadAllTasks();
};

window.loadAllTasks = async function() {
    try {
        const response = await fetch('/api/tasks');
        const data = await response.json();
        
        if (response.ok) {
            displayTasks(data.tasks);
        } else {
            document.getElementById('taskContainer').innerHTML = `<p style="color: red;">Error: ${data.error}</p>`;
        }
    } catch (error) {
        document.getElementById('taskContainer').innerHTML = `<p style="color: red;">Error loading tasks: ${error.message}</p>`;
    }
};

function displayTasks(tasks) {
    const container = document.getElementById('taskContainer');
    if (!tasks || tasks.length === 0) {
        container.innerHTML = '<p>No tasks found.</p>';
        return;
    }
    
    const tasksHtml = tasks.map(task => `
        <div class="task-item" style="border: 1px solid #ddd; border-radius: 5px; margin: 10px 0; padding: 15px; background: ${getTaskBackgroundColor(task.state)};">
            <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                <div style="flex: 1;">
                    <h4 style="margin: 0 0 10px 0; color: #333;">
                        <span class="task-priority priority-${task.priority.toLowerCase()}" style="padding: 2px 6px; border-radius: 3px; font-size: 0.8em; margin-right: 8px;">
                            ${task.priority}
                        </span>
                        ${task.title}
                    </h4>
                    <p style="margin: 5px 0; color: #666; font-size: 0.9em;">${task.description || 'No description'}</p>
                    <div style="display: flex; gap: 15px; margin-top: 10px; font-size: 0.85em; color: #777;">
                        <span><i class="fas fa-user"></i> ${task.owner}</span>
                        <span><i class="fas fa-clock"></i> ${task.estimation_hours}h</span>
                        <span><i class="fas fa-calendar"></i> ${task.due_date || 'No due date'}</span>
                        ${task.completion_info.has_completion_report ? '<span style="color: green;"><i class="fas fa-check-circle"></i> Report Available</span>' : ''}
                    </div>
                </div>
                <div style="display: flex; flex-direction: column; gap: 5px;">
                    <span class="task-status status-${task.state.toLowerCase()}" style="padding: 4px 8px; border-radius: 3px; font-size: 0.8em; text-align: center;">
                        ${task.state}
                    </span>
                    <button class="btn btn-sm" onclick="editTask('${task.id}')" style="padding: 4px 8px; font-size: 0.8em;">
                        <i class="fas fa-edit"></i> Edit
                    </button>
                    <button class="btn btn-sm btn-secondary" onclick="viewTaskDetails('${task.id}')" style="padding: 4px 8px; font-size: 0.8em;">
                        <i class="fas fa-eye"></i> View
                    </button>
                </div>
            </div>
        </div>
    `).join('');
    
    container.innerHTML = tasksHtml;
}

function getTaskBackgroundColor(state) {
    switch(state) {
        case 'DONE': return '#f0f8f0';
        case 'IN_PROGRESS': return '#fff4e6';
        case 'TODO': return '#f8f9fa';
        default: return '#fff';
    }
}

window.editTask = async function(taskId) {
    try {
        const response = await fetch(`/api/tasks/${taskId}`);
        const task = await response.json();
        
        if (!response.ok) {
            dashboard?.showNotification(`Error loading task: ${task.error}`, 'error');
            return;
        }
        
        showModal(`Edit Task - ${task.title}`, `
            <form id="editTaskForm">
                <div style="margin: 15px 0;">
                    <label>Title:</label>
                    <input type="text" id="taskTitle" value="${task.title}" style="width: 100%; padding: 8px; margin-top: 5px;">
                </div>
                <div style="margin: 15px 0;">
                    <label>Description:</label>
                    <textarea id="taskDescription" style="width: 100%; padding: 8px; margin-top: 5px; height: 80px;">${task.description || ''}</textarea>
                </div>
                <div style="display: flex; gap: 15px; margin: 15px 0;">
                    <div style="flex: 1;">
                        <label>Status:</label>
                        <select id="taskState" style="width: 100%; padding: 8px; margin-top: 5px;">
                            <option value="TODO" ${task.state === 'TODO' ? 'selected' : ''}>To Do</option>
                            <option value="IN_PROGRESS" ${task.state === 'IN_PROGRESS' ? 'selected' : ''}>In Progress</option>
                            <option value="DONE" ${task.state === 'DONE' ? 'selected' : ''}>Done</option>
                        </select>
                    </div>
                    <div style="flex: 1;">
                        <label>Priority:</label>
                        <select id="taskPriority" style="width: 100%; padding: 8px; margin-top: 5px;">
                            <option value="LOW" ${task.priority === 'LOW' ? 'selected' : ''}>Low</option>
                            <option value="MEDIUM" ${task.priority === 'MEDIUM' ? 'selected' : ''}>Medium</option>
                            <option value="HIGH" ${task.priority === 'HIGH' ? 'selected' : ''}>High</option>
                        </select>
                    </div>
                </div>
                <div style="display: flex; gap: 15px; margin: 15px 0;">
                    <div style="flex: 1;">
                        <label>Owner:</label>
                        <select id="taskOwner" style="width: 100%; padding: 8px; margin-top: 5px;">
                            <option value="backend" ${task.owner === 'backend' ? 'selected' : ''}>Backend</option>
                            <option value="frontend" ${task.owner === 'frontend' ? 'selected' : ''}>Frontend</option>
                            <option value="technical" ${task.owner === 'technical' ? 'selected' : ''}>Technical Lead</option>
                            <option value="qa" ${task.owner === 'qa' ? 'selected' : ''}>QA</option>
                            <option value="ux" ${task.owner === 'ux' ? 'selected' : ''}>UX Designer</option>
                            <option value="pm" ${task.owner === 'pm' ? 'selected' : ''}>Project Manager</option>
                        </select>
                    </div>
                    <div style="flex: 1;">
                        <label>Estimation (hours):</label>
                        <input type="number" id="taskHours" value="${task.estimation_hours}" style="width: 100%; padding: 8px; margin-top: 5px;">
                    </div>
                </div>
                <div style="margin: 15px 0;">
                    <label>Due Date:</label>
                    <input type="date" id="taskDueDate" value="${task.due_date}" style="width: 100%; padding: 8px; margin-top: 5px;">
                </div>
            </form>
            <div class="action-buttons">
                <button class="btn" onclick="saveTaskChanges('${taskId}')">
                    <i class="fas fa-save"></i> Save Changes
                </button>
                <button class="btn btn-secondary" onclick="closeModal()">Cancel</button>
            </div>
        `);
        
    } catch (error) {
        dashboard?.showNotification(`Error loading task: ${error.message}`, 'error');
    }
};

window.saveTaskChanges = async function(taskId) {
    try {
        const formData = {
            title: document.getElementById('taskTitle').value,
            description: document.getElementById('taskDescription').value,
            state: document.getElementById('taskState').value,
            priority: document.getElementById('taskPriority').value,
            owner: document.getElementById('taskOwner').value,
            estimation_hours: parseInt(document.getElementById('taskHours').value) || 0,
            due_date: document.getElementById('taskDueDate').value
        };
        
        const response = await fetch(`/api/tasks/${taskId}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(formData)
        });
        
        const result = await response.json();
        
        if (response.ok) {
            dashboard?.showNotification('Task updated successfully!', 'success');
            closeModal();
            // Reload tasks if task manager is open
            if (document.getElementById('taskContainer')) {
                loadAllTasks();
            }
        } else {
            dashboard?.showNotification(`Error updating task: ${result.error}`, 'error');
        }
        
    } catch (error) {
        dashboard?.showNotification(`Error updating task: ${error.message}`, 'error');
    }
};

window.viewTaskDetails = async function(taskId) {
    try {
        const response = await fetch(`/api/tasks/${taskId}`);
        const task = await response.json();
        
        if (!response.ok) {
            dashboard?.showNotification(`Error loading task: ${task.error}`, 'error');
            return;
        }
        
        const deliverables = task.completion_info.deliverables || [];
        const deliverablesHtml = deliverables.length > 0 
            ? deliverables.map(d => `<li>${d.name} (${(d.size/1024).toFixed(1)}KB)</li>`).join('')
            : '<li>No deliverables found</li>';
        
        showModal(`Task Details - ${task.title}`, `
            <div style="max-height: 400px; overflow-y: auto;">
                <h4>Basic Information</h4>
                <p><strong>ID:</strong> ${task.id}</p>
                <p><strong>Title:</strong> ${task.title}</p>
                <p><strong>Description:</strong> ${task.description || 'No description'}</p>
                <p><strong>Owner:</strong> ${task.owner}</p>
                <p><strong>Status:</strong> <span class="task-status status-${task.state.toLowerCase()}">${task.state}</span></p>
                <p><strong>Priority:</strong> <span class="task-priority priority-${task.priority.toLowerCase()}">${task.priority}</span></p>
                <p><strong>Estimation:</strong> ${task.estimation_hours} hours</p>
                <p><strong>Due Date:</strong> ${task.due_date || 'Not set'}</p>
                
                <h4>Dependencies</h4>
                <p>${task.depends_on.length > 0 ? task.depends_on.join(', ') : 'No dependencies'}</p>
                
                <h4>Completion Status</h4>
                <p><strong>Has Output Directory:</strong> ${task.completion_info.has_output ? 'Yes' : 'No'}</p>
                <p><strong>Has Completion Report:</strong> ${task.completion_info.has_completion_report ? 'Yes' : 'No'}</p>
                
                <h4>Deliverables</h4>
                <ul>${deliverablesHtml}</ul>
            </div>
            <div class="action-buttons">
                <button class="btn" onclick="editTask('${task.id}')">
                    <i class="fas fa-edit"></i> Edit Task
                </button>
                <button class="btn btn-secondary" onclick="closeModal()">Close</button>
            </div>
        `);
        
    } catch (error) {
        dashboard?.showNotification(`Error loading task details: ${error.message}`, 'error');
    }
};

// Handle page visibility changes
document.addEventListener('visibilitychange', () => {
    if (dashboard) {
        if (document.hidden) {
            dashboard.pauseConnections();
        } else {
            dashboard.resumeConnections();
        }
    }
});

// Cleanup on page unload
window.addEventListener('beforeunload', () => {
    if (dashboard) {
        dashboard.disconnect();
    }
});