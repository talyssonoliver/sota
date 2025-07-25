/**
 * Enhanced Dashboard JavaScript
 * Provides real-time updates and interactive functionality
 */

class DashboardManager {
    constructor() {
        this.initialized = false;
        this.updateInterval = 30000; // 30 seconds
        this.refreshTimer = null;
    }

    init() {
        if (this.initialized) return;
        
        console.log('Initializing Enhanced Dashboard...');
        this.initialized = true;
        
        // Initialize dashboard components
        this.setupEventListeners();
        this.loadInitialData();
        this.startAutoRefresh();
        
        console.log('Dashboard initialized successfully');
    }

    setupEventListeners() {
        // Add event listeners for dashboard interactions
        document.addEventListener('DOMContentLoaded', () => {
            this.init();
        });
    }

    loadInitialData() {
        // Load initial dashboard data
        const contentDiv = document.getElementById('dashboard-content');
        if (contentDiv) {
            contentDiv.innerHTML = `
                <div class="dashboard-section">
                    <h2>System Status</h2>
                    <p>All systems operational</p>
                </div>
                <div class="dashboard-section">
                    <h2>Recent Activity</h2>
                    <p>No recent activity</p>
                </div>
            `;
        }
    }

    startAutoRefresh() {
        this.refreshTimer = setInterval(() => {
            this.refreshData();
        }, this.updateInterval);
    }

    refreshData() {
        console.log('Refreshing dashboard data...');
        // Implementation would fetch real data from API
    }

    stopAutoRefresh() {
        if (this.refreshTimer) {
            clearInterval(this.refreshTimer);
            this.refreshTimer = null;
        }
    }
}

// Initialize dashboard when script loads
const dashboard = new DashboardManager();

// Initialize immediately if DOM is already loaded
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => dashboard.init());
} else {
    dashboard.init();
}

// Export for use in tests
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { DashboardManager };
}