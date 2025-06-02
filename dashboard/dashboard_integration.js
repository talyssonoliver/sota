/**
 * Dashboard Integration Script - Phase 6 Step 6.4
 * 
 * This script bridges the basic completion charts dashboard with the enhanced
 * dashboard functionality, providing real-time updates, system health monitoring,
 * and interactive timeline features.
 */

// Enhanced dashboard integration
let enhancedDashboard = null;
let basicDashboardMode = true;

// Initialize enhanced dashboard integration
function initializeEnhancedDashboardIntegration() {
    console.log('Initializing enhanced dashboard integration...');
    
    // Check if enhanced dashboard is available
    if (typeof DashboardManager !== 'undefined') {
        try {
            enhancedDashboard = new DashboardManager();
            
            // Initialize enhanced dashboard
            enhancedDashboard.initialize().then(() => {
                console.log('Enhanced dashboard initialized successfully');
                basicDashboardMode = false;
                
                // Update UI to show enhanced features are active
                updateEnhancedStatusIndicator(true);
                
            }).catch(error => {
                console.warn('Enhanced dashboard initialization failed:', error);
                fallbackToBasicMode();
            });
            
        } catch (error) {
            console.warn('Enhanced dashboard class not available:', error);
            fallbackToBasicMode();
        }
    } else {
        console.log('Enhanced dashboard not available, using basic mode');
        fallbackToBasicMode();
    }
}

// Fallback to basic dashboard mode
function fallbackToBasicMode() {
    basicDashboardMode = true;
    updateEnhancedStatusIndicator(false);
    
    // Initialize basic system health display
    initializeBasicSystemHealth();
    
    // Initialize basic timeline functionality
    initializeBasicTimeline();
}

// Update status indicator for enhanced features
function updateEnhancedStatusIndicator(enhanced) {
    // Add status indicator to header if it doesn't exist
    let statusIndicator = document.getElementById('dashboard-status');
    if (!statusIndicator) {
        statusIndicator = document.createElement('div');
        statusIndicator.id = 'dashboard-status';
        statusIndicator.style.cssText = `
            position: absolute;
            top: 10px;
            right: 20px;
            padding: 5px 10px;
            border-radius: 15px;
            font-size: 0.8em;
            font-weight: bold;
        `;
        
        const header = document.querySelector('.header');
        if (header) {
            header.style.position = 'relative';
            header.appendChild(statusIndicator);
        }
    }
    
    if (enhanced) {
        statusIndicator.textContent = '🚀 Enhanced Mode';
        statusIndicator.style.backgroundColor = '#28a745';
        statusIndicator.style.color = 'white';
    } else {
        statusIndicator.textContent = '📊 Basic Mode';
        statusIndicator.style.backgroundColor = '#ffc107';
        statusIndicator.style.color = '#212529';
    }
}

// Basic system health implementation
function initializeBasicSystemHealth() {
    console.log('Initializing basic system health monitoring...');
    
    // Fetch system health data from API
    setInterval(updateBasicSystemHealth, 30000);
    updateBasicSystemHealth(); // Initial update
}

// Update basic system health display
async function updateBasicSystemHealth() {
    try {
        const response = await fetch('http://localhost:5000/api/system/health');
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }
        
        const healthData = await response.json();
        if (healthData.status === 'success' && healthData.data) {
            updateSystemHealthElements(healthData.data);
        }
    } catch (error) {
        console.warn('Failed to fetch system health:', error);
        showSystemHealthError();
    }
}

// Update system health UI elements
function updateSystemHealthElements(health) {
    // Update overall status
    const statusElement = document.getElementById('overall-health-status');
    if (statusElement) {
        statusElement.textContent = health.overall_status.toUpperCase();
        statusElement.className = `health-status ${health.overall_status}`;
    }
    
    // Update component statuses
    if (health.components) {
        Object.entries(health.components).forEach(([component, data]) => {
            const elementId = `component-${component.replace('_', '-')}`;
            const element = document.getElementById(elementId);
            if (element) {
                element.textContent = data.status || 'unknown';
                element.className = `component-status ${data.status}`;
            }
        });
    }
    
    // Update performance metrics
    if (health.performance) {
        const cpuElement = document.getElementById('cpu-usage');
        if (cpuElement) cpuElement.textContent = health.performance.cpu_usage;
        
        const memoryElement = document.getElementById('memory-usage');
        if (memoryElement) memoryElement.textContent = health.performance.memory_usage;
        
        const apiElement = document.getElementById('api-response-time');
        if (apiElement) apiElement.textContent = health.performance.api_response_time;
    }
    
    // Update recommendations
    const recommendationsElement = document.getElementById('system-recommendations');
    if (recommendationsElement && health.recommendations) {
        if (health.recommendations.length > 0) {
            recommendationsElement.innerHTML = health.recommendations
                .map(rec => `<li>${rec}</li>`)
                .join('');
        } else {
            recommendationsElement.innerHTML = '<li>System running optimally</li>';
        }
    }
}

// Show system health error state
function showSystemHealthError() {
    const statusElement = document.getElementById('overall-health-status');
    if (statusElement) {
        statusElement.textContent = 'ERROR';
        statusElement.className = 'health-status error';
    }
    
    // Reset component statuses
    ['dashboard-api', 'metrics-engine', 'automation-system', 'reporting-system'].forEach(component => {
        const element = document.getElementById(`component-${component}`);
        if (element) {
            element.textContent = 'unavailable';
            element.className = 'component-status error';
        }
    });
}

// Basic timeline implementation
function initializeBasicTimeline() {
    console.log('Initializing basic timeline functionality...');
    
    // Fetch timeline data from API
    setInterval(updateBasicTimeline, 60000); // Update every minute
    updateBasicTimeline(); // Initial update
}

// Update basic timeline display
async function updateBasicTimeline() {
    try {
        const response = await fetch('http://localhost:5000/api/timeline/data');
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }
        
        const timelineData = await response.json();
        if (timelineData.status === 'success' && timelineData.data) {
            updateTimelineElements(timelineData.data);
        }
    } catch (error) {
        console.warn('Failed to fetch timeline data:', error);
        showTimelineError();
    }
}

// Update timeline UI elements
function updateTimelineElements(timeline) {
    // Update timeline summary
    if (timeline.summary) {
        const totalDaysElement = document.getElementById('timeline-total-days');
        if (totalDaysElement) totalDaysElement.textContent = timeline.summary.total_days;
        
        const activeSprintsElement = document.getElementById('timeline-active-sprints');
        if (activeSprintsElement) activeSprintsElement.textContent = Math.ceil(timeline.summary.total_days / 7);
        
        const avgVelocityElement = document.getElementById('timeline-avg-velocity');
        if (avgVelocityElement) avgVelocityElement.textContent = timeline.summary.average_velocity.toFixed(1);
        
        const completionTrendElement = document.getElementById('timeline-completion-trend');
        if (completionTrendElement) completionTrendElement.textContent = timeline.summary.current_completion.toFixed(1) + '%';
    }
    
    // Update timeline chart if available
    if (typeof timelineChart !== 'undefined' && timelineChart && timeline.timeline_events) {
        updateTimelineChartData(timeline.timeline_events);
    }
}

// Update timeline chart with real data
function updateTimelineChartData(events) {
    const labels = events.slice(-30).map(event => event.date);
    const velocityData = events.slice(-30).map(event => event.velocity);
    const completionData = events.slice(-30).map(event => event.completion_percentage);
    
    if (timelineChart && timelineChart.data) {
        timelineChart.data.labels = labels;
        timelineChart.data.datasets[0].data = velocityData;
        timelineChart.data.datasets[1].data = completionData;
        timelineChart.update('none');
    }
}

// Show timeline error state
function showTimelineError() {
    const elements = ['timeline-total-days', 'timeline-active-sprints', 'timeline-avg-velocity', 'timeline-completion-trend'];
    elements.forEach(id => {
        const element = document.getElementById(id);
        if (element) element.textContent = '--';
    });
}

// Enhanced timeline controls
function initializeTimelineControlsIntegration() {
    const timelineButtons = document.querySelectorAll('.timeline-btn');
    timelineButtons.forEach(button => {
        button.addEventListener('click', function() {
            // Remove active class from all buttons
            timelineButtons.forEach(btn => btn.classList.remove('active'));
            // Add active class to clicked button
            this.classList.add('active');
            
            // Update timeline data based on selection
            const days = parseInt(this.id.split('-')[1]);
            if (!basicDashboardMode && enhancedDashboard) {
                // Use enhanced dashboard functionality
                console.log('Using enhanced timeline range update');
            } else {
                // Use basic timeline range update
                updateBasicTimelineRange(days);
            }
        });
    });
}

// Basic timeline range update
function updateBasicTimelineRange(days) {
    console.log(`Updating timeline range to ${days} days`);
    
    // Fetch fresh timeline data for the specified range
    fetch(`http://localhost:5000/api/timeline/data?days=${days}`)
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success' && data.data) {
                updateTimelineElements(data.data);
            }
        })
        .catch(error => {
            console.warn('Failed to update timeline range:', error);
        });
}

// Export functions for global access
window.initializeEnhancedDashboardIntegration = initializeEnhancedDashboardIntegration;
window.initializeTimelineControlsIntegration = initializeTimelineControlsIntegration;
window.enhancedDashboard = enhancedDashboard;
window.basicDashboardMode = basicDashboardMode;
