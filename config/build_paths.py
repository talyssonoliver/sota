"""
Centralized build path configuration for AI Agent System.
All runtime-generated files should use these paths instead of hardcoded directories.
"""

from pathlib import Path

# Base build directory
BUILD_DIR = Path("build")

# Dashboard paths
DASHBOARD_DIR = BUILD_DIR / "dashboard"
DASHBOARD_NOTIFICATIONS_DIR = DASHBOARD_DIR / "notifications"
DASHBOARD_VISUALIZATIONS_DIR = DASHBOARD_DIR / "visualizations"

# Storage paths
STORAGE_DIR = BUILD_DIR / "storage"
HITL_STORAGE_DIR = STORAGE_DIR / "hitl"
HOT_STORAGE_DIR = STORAGE_DIR / "hot"
WARM_STORAGE_DIR = STORAGE_DIR / "warm"
COLD_STORAGE_DIR = STORAGE_DIR / "cold"
DATA_STORAGE_DIR = BUILD_DIR / "data" / "storage"

# Runtime paths
RUNTIME_DIR = BUILD_DIR / "runtime"
LOGS_DIR = RUNTIME_DIR / "logs"
OUTPUTS_DIR = RUNTIME_DIR / "outputs"
CACHE_DIR = RUNTIME_DIR / "cache"
TEMP_DIR = RUNTIME_DIR / "temp"

# Test paths
TEST_OUTPUTS_DIR = BUILD_DIR / "test_outputs"

# Reports and templates
REPORTS_DIR = BUILD_DIR / "reports"
TEMPLATES_DIR = BUILD_DIR / "templates"
EMAIL_TEMPLATES_DIR = TEMPLATES_DIR / "email"

# Ensure all directories exist
def ensure_build_directories():
    """Create all build directories if they don't exist."""
    directories = [
        BUILD_DIR,
        DASHBOARD_DIR,
        DASHBOARD_NOTIFICATIONS_DIR,
        DASHBOARD_VISUALIZATIONS_DIR,
        STORAGE_DIR,
        HITL_STORAGE_DIR,
        HOT_STORAGE_DIR,
        WARM_STORAGE_DIR,
        COLD_STORAGE_DIR,
        DATA_STORAGE_DIR,
        RUNTIME_DIR,
        LOGS_DIR,
        OUTPUTS_DIR,
        CACHE_DIR,
        TEMP_DIR,
        TEST_OUTPUTS_DIR,
        REPORTS_DIR,
        TEMPLATES_DIR,
        EMAIL_TEMPLATES_DIR,
    ]
    
    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)

# Legacy path mapping for migration
LEGACY_PATH_MAPPING = {
    "dashboard": DASHBOARD_DIR,
    "dashboard/notifications": DASHBOARD_NOTIFICATIONS_DIR,
    "dashboard/visualizations": DASHBOARD_VISUALIZATIONS_DIR,
    "storage/hitl": HITL_STORAGE_DIR,
    "storage/hot": HOT_STORAGE_DIR,
    "storage/warm": WARM_STORAGE_DIR,
    "storage/cold": COLD_STORAGE_DIR,
    "data/storage": DATA_STORAGE_DIR,
    "logs": LOGS_DIR,
    "outputs": OUTPUTS_DIR,
    "test_outputs": TEST_OUTPUTS_DIR,
    "reports": REPORTS_DIR,
    "templates/email": EMAIL_TEMPLATES_DIR,
}