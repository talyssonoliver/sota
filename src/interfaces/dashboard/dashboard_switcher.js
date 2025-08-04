/**
 * Dashboard Switcher - Multi-Dashboard Navigation System
 * Allows switching between different dashboard interfaces
 */

class DashboardSwitcher {
    constructor() {
        this.dashboards = {
            'command-center': {
                title: 'Interactive Command Center',
                url: '/dashboard/interactive_command_center.html',
                icon: 'fas fa-rocket',
                description: 'Full system control and monitoring'
            },
            'professional': {
                title: 'Interactive Professional Dashboard',
                url: '/dashboard/interactive_professional_dashboard.html',
                icon: 'fas fa-chart-area',
                description: 'Real-time event-driven monitoring & control'
            },
            'unified': {
                title: 'Unified Basic Dashboard',
                url: '/dashboard/unified_dashboard.html',
                icon: 'fas fa-tachometer-alt',
                description: 'Simple and lightweight monitoring'
            },
            'hitl-kanban': {
                title: 'HITL Kanban Board',
                url: '/api/dashboard/hitl/kanban-data',
                icon: 'fas fa-clipboard-list',
                description: 'Human-in-the-Loop review system',
                isApi: true
            },
            'management': {
                title: 'Quality Management Dashboard',
                url: '/dashboard/interactive_professional_dashboard.html',
                icon: 'fas fa-users-cog',
                description: 'Quality metrics and compliance (redirects to Interactive Dashboard)'
            },
            'api-test': {
                title: 'API Testing Interface',
                url: '/dashboard/test_api.html',
                icon: 'fas fa-code',
                description: 'Development and testing tools'
            }
        };
        
        this.currentDashboard = null;
        this.isFullscreen = false;
        
        // Initialize
        this.init();
    }

    init() {
        console.log('🎛️ Dashboard Switcher initializing...');
        
        // Set default selection
        this.selectDashboard('command-center');
        
        // Check if there's a dashboard preference stored
        const savedDashboard = localStorage.getItem('preferredDashboard');
        if (savedDashboard && this.dashboards[savedDashboard]) {
            this.selectDashboard(savedDashboard);
        }
        
        // Setup keyboard shortcuts
        this.setupKeyboardShortcuts();
        
        // Auto-refresh capability
        this.setupAutoRefresh();
        
        // Add additional event listeners as backup
        this.setupEventListeners();
        
        console.log('✅ Dashboard Switcher initialized successfully');
    }
    
    setupEventListeners() {
        // Add event listeners to all dashboard cards as backup
        document.querySelectorAll('.dashboard-card').forEach(card => {
            const onclickAttr = card.getAttribute('onclick');
            if (onclickAttr) {
                const dashboardId = onclickAttr.match(/loadDashboard\('([^']+)'\)/);
                if (dashboardId && dashboardId[1]) {
                    card.addEventListener('click', (e) => {
                        e.preventDefault();
                        console.log(`🖱️ Card clicked: ${dashboardId[1]}`);
                        this.loadDashboard(dashboardId[1]);
                    });
                }
            }
        });
        
        // Add event listeners to buttons within cards
        document.querySelectorAll('.btn').forEach(btn => {
            const onclickAttr = btn.getAttribute('onclick');
            if (onclickAttr && onclickAttr.includes('loadDashboard')) {
                const dashboardId = onclickAttr.match(/loadDashboard\('([^']+)'\)/);
                if (dashboardId && dashboardId[1]) {
                    btn.addEventListener('click', (e) => {
                        e.preventDefault();
                        e.stopPropagation();
                        console.log(`🔘 Button clicked: ${dashboardId[1]}`);
                        this.loadDashboard(dashboardId[1]);
                    });
                }
            } else if (onclickAttr && onclickAttr.includes('previewDashboard')) {
                const dashboardId = onclickAttr.match(/previewDashboard\('([^']+)'\)/);
                if (dashboardId && dashboardId[1]) {
                    btn.addEventListener('click', (e) => {
                        e.preventDefault();
                        e.stopPropagation();
                        console.log(`👁️ Preview clicked: ${dashboardId[1]}`);
                        this.previewDashboard(dashboardId[1]);
                    });
                }
            }
        });
        
        // Add event listeners to toggle buttons
        document.querySelectorAll('.toggle-btn').forEach(btn => {
            const onclickAttr = btn.getAttribute('onclick');
            if (onclickAttr && onclickAttr.includes('filterDashboards')) {
                const category = onclickAttr.match(/filterDashboards\('([^']+)'/);
                if (category && category[1]) {
                    btn.addEventListener('click', (e) => {
                        e.preventDefault();
                        console.log(`🔍 Filter clicked: ${category[1]}`);
                        this.filterDashboards(category[1], btn);
                    });
                }
            }
        });
        
        console.log('📝 Event listeners setup complete');
    }

    selectDashboard(dashboardId) {
        // Visual selection update
        document.querySelectorAll('.dashboard-card').forEach(card => {
            card.classList.remove('selected');
        });
        
        const selectedCard = document.querySelector(`[onclick*="${dashboardId}"]`);
        if (selectedCard) {
            selectedCard.classList.add('selected');
        }
        
        this.currentDashboard = dashboardId;
    }

    loadDashboard(dashboardId) {
        console.log(`🚀 Loading dashboard: ${dashboardId}`);
        
        if (!this.dashboards[dashboardId]) {
            console.error(`Dashboard '${dashboardId}' not found`);
            console.log('Available dashboards:', Object.keys(this.dashboards));
            this.showNotification('Dashboard not found', 'error');
            return;
        }

        const dashboard = this.dashboards[dashboardId];
        console.log(`📋 Dashboard config:`, dashboard);
        
        // Save preference
        localStorage.setItem('preferredDashboard', dashboardId);
        
        // Update UI
        this.selectDashboard(dashboardId);
        
        // Show frame container
        const selectorEl = document.getElementById('dashboardSelector');
        const frameEl = document.getElementById('dashboardFrame');
        const backBtn = document.querySelector('.back-to-selector');
        
        if (selectorEl) selectorEl.style.display = 'none';
        if (frameEl) frameEl.style.display = 'block';
        if (backBtn) backBtn.classList.add('show');
        
        // Update frame title
        const frameTitle = document.getElementById('frameTitle');
        if (frameTitle) {
            frameTitle.innerHTML = `<i class="${dashboard.icon}"></i> <span>${dashboard.title}</span>`;
        }
        
        // Load dashboard
        const iframe = document.getElementById('dashboardIframe');
        if (!iframe) {
            console.error('Dashboard iframe not found');
            this.showNotification('Dashboard container not found', 'error');
            return;
        }
        
        if (dashboard.isApi) {
            // For API endpoints, create a simple wrapper
            console.log(`🔗 Loading API dashboard: ${dashboard.url}`);
            this.loadApiDashboard(dashboard, iframe);
        } else {
            // For HTML files
            console.log(`📄 Loading HTML dashboard: ${dashboard.url}`);
            iframe.src = dashboard.url;
        }
        
        console.log(`📊 Successfully loaded dashboard: ${dashboard.title}`);
        this.showNotification(`Loaded ${dashboard.title}`, 'success');
    }

    loadApiDashboard(dashboard, iframe) {
        // Create a wrapper HTML for API data
        const wrapperHtml = `
        <!DOCTYPE html>
        <html>
        <head>
            <title>${dashboard.title}</title>
            <style>
                body { 
                    font-family: 'Segoe UI', sans-serif; 
                    margin: 20px; 
                    background: #1a1a2e;
                    color: white;
                }
                .container { max-width: 1200px; margin: 0 auto; }
                .api-data { 
                    background: #16213e; 
                    padding: 20px; 
                    border-radius: 10px; 
                    margin: 20px 0;
                    border: 1px solid #0f3460;
                }
                .loading { text-align: center; padding: 40px; }
                .error { color: #ff6b6b; }
                .success { color: #00ff88; }
                pre { 
                    background: #0d1929; 
                    padding: 15px; 
                    border-radius: 8px; 
                    overflow-x: auto;
                    border: 1px solid #0f3460;
                }
            </style>
        </head>
        <body>
            <div class="container">
                <h1><i class="${dashboard.icon}"></i> ${dashboard.title}</h1>
                <p>${dashboard.description}</p>
                <div id="apiData" class="loading">
                    <p>Loading API data...</p>
                </div>
            </div>
            <script>
                fetch('${dashboard.url}')
                    .then(response => response.json())
                    .then(data => {
                        document.getElementById('apiData').innerHTML = 
                            '<div class="api-data success"><h3>API Response:</h3><pre>' + 
                            JSON.stringify(data, null, 2) + '</pre></div>';
                    })
                    .catch(error => {
                        document.getElementById('apiData').innerHTML = 
                            '<div class="api-data error"><h3>Error:</h3><p>' + error.message + '</p></div>';
                    });
            </script>
        </body>
        </html>
        `;
        
        iframe.src = 'data:text/html;charset=utf-8,' + encodeURIComponent(wrapperHtml);
    }

    previewDashboard(dashboardId) {
        if (!this.dashboards[dashboardId]) {
            console.error(`Dashboard '${dashboardId}' not found`);
            return;
        }

        const dashboard = this.dashboards[dashboardId];
        
        // Create preview window
        const previewWindow = window.open(
            dashboard.url,
            'preview',
            'width=1200,height=800,scrollbars=yes,resizable=yes'
        );
        
        if (previewWindow) {
            previewWindow.focus();
            this.showNotification(`Previewing ${dashboard.title}`, 'success');
        } else {
            this.showNotification('Please allow pop-ups to preview dashboards', 'warning');
        }
    }

    filterDashboards(category, clickedButton = null) {
        // Update toggle buttons
        document.querySelectorAll('.toggle-btn').forEach(btn => {
            btn.classList.remove('active');
        });
        
        // If no button passed, find the button by category
        if (!clickedButton) {
            const buttons = document.querySelectorAll('.toggle-btn');
            buttons.forEach(btn => {
                if (btn.textContent.toLowerCase().includes(category.toLowerCase()) || 
                    (category === 'all' && btn.textContent.includes('All'))) {
                    btn.classList.add('active');
                }
            });
        } else {
            clickedButton.classList.add('active');
        }

        // Filter dashboard cards
        const cards = document.querySelectorAll('.dashboard-card');
        
        cards.forEach(card => {
            if (category === 'all') {
                card.style.display = 'block';
            } else {
                const cardCategory = card.getAttribute('data-category');
                card.style.display = cardCategory === category ? 'block' : 'none';
            }
        });

        console.log(`🔍 Filtered dashboards by category: ${category}`);
    }

    showSelector() {
        document.getElementById('dashboardSelector').style.display = 'block';
        document.getElementById('dashboardFrame').style.display = 'none';
        document.querySelector('.back-to-selector').classList.remove('show');
    }

    refreshDashboard() {
        const iframe = document.getElementById('dashboardIframe');
        iframe.src = iframe.src; // Force reload
        this.showNotification('Dashboard refreshed', 'success');
    }

    toggleFullscreen() {
        const frameContainer = document.getElementById('dashboardFrame');
        
        if (!this.isFullscreen) {
            // Enter fullscreen
            if (frameContainer.requestFullscreen) {
                frameContainer.requestFullscreen();
            } else if (frameContainer.webkitRequestFullscreen) {
                frameContainer.webkitRequestFullscreen();
            } else if (frameContainer.msRequestFullscreen) {
                frameContainer.msRequestFullscreen();
            }
            this.isFullscreen = true;
            document.querySelector('[onclick="toggleFullscreen()"] i').className = 'fas fa-compress';
        } else {
            // Exit fullscreen
            if (document.exitFullscreen) {
                document.exitFullscreen();
            } else if (document.webkitExitFullscreen) {
                document.webkitExitFullscreen();
            } else if (document.msExitFullscreen) {
                document.msExitFullscreen();
            }
            this.isFullscreen = false;
            document.querySelector('[onclick="toggleFullscreen()"] i').className = 'fas fa-expand';
        }
    }

    setupKeyboardShortcuts() {
        document.addEventListener('keydown', (e) => {
            // Alt + number keys for quick dashboard switching
            if (e.altKey && e.key >= '1' && e.key <= '6') {
                e.preventDefault();
                const dashboardKeys = Object.keys(this.dashboards);
                const index = parseInt(e.key) - 1;
                if (dashboardKeys[index]) {
                    this.loadDashboard(dashboardKeys[index]);
                }
            }
            
            // Escape to return to selector
            if (e.key === 'Escape') {
                this.showSelector();
            }
            
            // F5 to refresh current dashboard
            if (e.key === 'F5' && document.getElementById('dashboardFrame').style.display !== 'none') {
                e.preventDefault();
                this.refreshDashboard();
            }
            
            // F11 for fullscreen toggle
            if (e.key === 'F11' && document.getElementById('dashboardFrame').style.display !== 'none') {
                e.preventDefault();
                this.toggleFullscreen();
            }
        });
    }

    setupAutoRefresh() {
        // Auto-refresh every 5 minutes for data freshness
        setInterval(() => {
            if (document.getElementById('dashboardFrame').style.display !== 'none') {
                console.log('🔄 Auto-refreshing dashboard data...');
                // Only refresh if user hasn't interacted recently
                if (Date.now() - this.lastInteraction > 300000) { // 5 minutes
                    this.refreshDashboard();
                }
            }
        }, 300000); // 5 minutes
        
        // Track user interactions
        this.lastInteraction = Date.now();
        document.addEventListener('click', () => {
            this.lastInteraction = Date.now();
        });
        document.addEventListener('keydown', () => {
            this.lastInteraction = Date.now();
        });
    }

    showNotification(message, type = 'success') {
        // Create notification element if it doesn't exist
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
            `;
            document.body.appendChild(notification);
        }

        // Set notification content and style
        notification.textContent = message;
        notification.className = `notification ${type}`;
        
        // Color coding
        const colors = {
            success: 'linear-gradient(45deg, #00ff88, #00cc70)',
            error: 'linear-gradient(45deg, #ff6b6b, #ff5252)',
            warning: 'linear-gradient(45deg, #ffa726, #ff9800)',
            info: 'linear-gradient(45deg, #42a5f5, #2196f3)'
        };
        
        notification.style.background = colors[type] || colors.info;

        // Show notification
        notification.style.opacity = '1';
        notification.style.transform = 'translateX(0)';

        // Auto-hide after 3 seconds
        setTimeout(() => {
            notification.style.opacity = '0';
            notification.style.transform = 'translateX(100%)';
        }, 3000);
    }

    getDashboardStats() {
        return {
            totalDashboards: Object.keys(this.dashboards).length,
            currentDashboard: this.currentDashboard,
            preferredDashboard: localStorage.getItem('preferredDashboard'),
            isFullscreen: this.isFullscreen
        };
    }
}

// Global functions for HTML onclick handlers
let dashboardSwitcher;

window.loadDashboard = function(dashboardId) {
    console.log(`🎯 Global loadDashboard called with: ${dashboardId}`);
    if (dashboardSwitcher) {
        dashboardSwitcher.loadDashboard(dashboardId);
    } else {
        console.error('Dashboard switcher not initialized');
        alert('Dashboard switcher not initialized. Please refresh the page.');
    }
};

window.previewDashboard = function(dashboardId) {
    if (dashboardSwitcher) {
        dashboardSwitcher.previewDashboard(dashboardId);
    } else {
        console.error('Dashboard switcher not initialized');
    }
};

window.filterDashboards = function(category, event = null) {
    if (dashboardSwitcher) {
        const clickedButton = event ? event.target : null;
        dashboardSwitcher.filterDashboards(category, clickedButton);
    } else {
        console.error('Dashboard switcher not initialized');
    }
};

window.showSelector = function() {
    if (dashboardSwitcher) {
        dashboardSwitcher.showSelector();
    } else {
        console.error('Dashboard switcher not initialized');
    }
};

window.refreshDashboard = function() {
    if (dashboardSwitcher) {
        dashboardSwitcher.refreshDashboard();
    } else {
        console.error('Dashboard switcher not initialized');
    }
};

window.toggleFullscreen = function() {
    if (dashboardSwitcher) {
        dashboardSwitcher.toggleFullscreen();
    } else {
        console.error('Dashboard switcher not initialized');
    }
};

// Initialize when page loads
document.addEventListener('DOMContentLoaded', () => {
    try {
        dashboardSwitcher = new DashboardSwitcher();
        
        console.log('🎛️ Dashboard Switcher loaded successfully');
        console.log('📊 Available dashboards:', Object.keys(dashboardSwitcher.dashboards));
        console.log('⌨️ Keyboard shortcuts:');
        console.log('   Alt + 1-6: Quick dashboard switching');
        console.log('   Escape: Return to selector');
        console.log('   F5: Refresh current dashboard');
        console.log('   F11: Toggle fullscreen');

        // Test that all global functions are available
        console.log('🔧 Testing global functions...');
        console.log('✅ loadDashboard:', typeof window.loadDashboard);
        console.log('✅ previewDashboard:', typeof window.previewDashboard);
        console.log('✅ filterDashboards:', typeof window.filterDashboards);
        console.log('✅ showSelector:', typeof window.showSelector);
        console.log('✅ refreshDashboard:', typeof window.refreshDashboard);
        console.log('✅ toggleFullscreen:', typeof window.toggleFullscreen);
        
    } catch (error) {
        console.error('❌ Failed to initialize Dashboard Switcher:', error);
    }
});

// Export for external access
window.DashboardSwitcher = DashboardSwitcher;