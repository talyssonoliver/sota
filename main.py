#!/usr/bin/env python3
"""
SOTA AI System -Coding Application
==================================================

A local development environment with multi-agent architecture, modern web GUI,
and seamless integration with Claude AI for coding, project management, and collaboration.

Key Features:
- Multi-Agent Architecture: Specialized agents that collaborate on coding tasks
- Modern Web GUI: Browser-based interface for managing Claude sessions
- MCP Integration: Model Context Protocol for seamless tool connections  
- Local Development: Runs entirely on your machine with Node.js/Python hybrid
- Project Management: Workspace and file management like a professional IDE
- Real-time Collaboration: Agents work together on complex development tasks

Usage:
    python main.py                    # Launch with web GUI
    python main.py --headless         # Run without GUI (API only)
    python main.py --port 8080        # Specify custom port
    python main.py --validate         # Run system validation
    python main.py --agents-only      # Start agents without web interface
"""

import argparse
import asyncio
import logging
import sys
import webbrowser
from pathlib import Path
from typing import Dict, List, Optional

# Configure logging with proper Unicode handling
import platform
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Create logs directory if it doesn't exist
log_dir = Path('logs')
log_dir.mkdir(parents=True, exist_ok=True)

# Configure handlers with proper encoding
handlers: List[logging.Handler] = [
    logging.FileHandler('logs/main.log', mode='a', encoding='utf-8')
]

# Add console handler with Windows-compatible encoding
if platform.system() == "Windows":
    console_handler = logging.StreamHandler(sys.stdout)
    console_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(console_formatter)
    handlers.append(console_handler)
else:
    handlers.append(logging.StreamHandler(sys.stdout))

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=handlers
)
logger = logging.getLogger(__name__)

# Apply system patches
try:
    from patches import apply_all_patches
    apply_all_patches()
    logger.info("Applied system patches successfully")
except ImportError:
    logger.warning("Could not load patches. Some features may not work correctly.")

# Import core components
import_errors = []
components_loaded = True

try:
    from src.interfaces.dashboard.api.unified_api_server import UnifiedDashboardAPI as RealUnifiedDashboardAPI
except ImportError as e:
    import_errors.append(f"UnifiedDashboardAPI: {e}")
    components_loaded = False
    RealUnifiedDashboardAPI = None
    
try:
    from src.core.agents.factory import AgentFactory as RealAgentFactory
except ImportError as e:
    import_errors.append(f"AgentFactory: {e}")
    components_loaded = False
    RealAgentFactory = None
    
try:
    from src.infrastructure.memory.engines.memory_engine import MemoryEngine as RealMemoryEngine
except ImportError as e:
    import_errors.append(f"MemoryEngine: {e}")
    components_loaded = False
    RealMemoryEngine = None
    
try:
    from src.core.workflows.registry import WorkflowRegistry as RealWorkflowRegistry
except ImportError as e:
    import_errors.append(f"WorkflowRegistry: {e}")
    RealWorkflowRegistry = None

if import_errors:
    logger.warning(f"Some components not available: {'; '.join(import_errors)}")
    
# Import assignments - use real classes if available
UnifiedDashboardAPI = RealUnifiedDashboardAPI
AgentFactory = RealAgentFactory  
MemoryEngine = RealMemoryEngine
WorkflowRegistry = RealWorkflowRegistry


class SOTAAISystem:
    """
    Main application class for the Sota coding environment.
    
    Coordinates multi-agent workflows, web interface, and development tools.
    """
    
    def __init__(self, config: Optional[Dict] = None):
        """Initialize the Claude Code AI application."""
        self.config = config or {}
        self.port = self.config.get('port', 8080)
        self.host = self.config.get('host', 'localhost')
        self.headless = self.config.get('headless', False)
        
        # Core components
        self.memory_engine: Optional[MemoryEngine] = None
        self.agent_factory: Optional[AgentFactory] = None
        self.workflow_registry: Optional[WorkflowRegistry] = None
        self.api_server: Optional[UnifiedDashboardAPI] = None
        
        # Application state
        self.active_sessions: Dict[str, Dict] = {}
        self.running_agents: Dict[str, object] = {}
        self.projects: Dict[str, Dict] = {}
        self.server_thread = None
        
        logger.info(f"SOTA AI System initialized - Port: {self.port}, Headless: {self.headless}")
    
    async def initialize_core_systems(self):
        """Initialize core AI and infrastructure systems."""
        try:
            logger.info("Initializing core AI systems...")
            
            # Initialize memory engine if available
            if MemoryEngine is not None:
                self.memory_engine = MemoryEngine()
                logger.info("Memory engine initialized")
            else:
                logger.warning("Memory engine not available - continuing without it")
            
            # Initialize agent factory if available
            if AgentFactory is not None:
                self.agent_factory = AgentFactory(memory_engine=self.memory_engine)
                logger.info("Agent factory initialized")
            else:
                logger.warning("Agent factory not available - continuing without it")
            
            # Initialize workflow registry if available
            if WorkflowRegistry is not None:
                self.workflow_registry = WorkflowRegistry()
                await self.workflow_registry.initialize()
                logger.info("Workflow registry initialized")
            else:
                logger.warning("Workflow registry not available - continuing without it")
            
            # Load available projects
            await self.discover_projects()
            
            logger.info("Core systems initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize core systems: {e}")
            return False
    
    async def start_web_server(self):
        """Start the web-based GUI server."""
        try:
            if self.headless:
                logger.info("Running in headless mode - skipping web server")
                return True
            
            logger.info(f"Starting web server on {self.host}:{self.port}")
            
            # Initialize unified API server if available
            if UnifiedDashboardAPI is not None:
                from src.interfaces.dashboard.config import DashboardConfig
                config = DashboardConfig()
                config.host = self.host
                config.port = self.port
                config.debug = False
                
                self.api_server = UnifiedDashboardAPI(config)
            else:
                logger.error("UnifiedDashboardAPI not available - cannot start web server")
                return False
            
            # Start the server in a separate thread since Flask's app.run() is blocking
            import threading
            server_exception = None
            
            def run_server():
                nonlocal server_exception
                try:
                    if self.api_server:
                        self.api_server.start_server()
                except Exception as e:
                    server_exception = e
                    logger.error(f"Server thread error: {e}")
            
            self.server_thread = threading.Thread(target=run_server, daemon=True)
            self.server_thread.start()
            
            # Give server time to start and check for errors
            await asyncio.sleep(4)
            
            # Check if server had an exception during startup
            if server_exception:
                logger.error(f"Server failed with exception: {server_exception}")
                return False
            
            # Verify server is running by checking thread status
            if not self.server_thread.is_alive():
                logger.error("Server thread failed to start or died immediately")
                return False
            
            # Open browser if not headless  
            if not self.headless:
                # Use the actual port the server is running on
                actual_port = getattr(self.api_server.config, 'port', self.port)
                url = f"http://{self.host}:{actual_port}"
                logger.info(f"Opening browser to {url}")
                webbrowser.open(url)
                
                # Update our port reference
                self.port = actual_port
            
            logger.info("Web server started successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to start web server: {e}")
            return False
    
    async def discover_projects(self):
        """Discover and load available projects."""
        try:
            logger.info("Discovering projects...")
            
            # Check common project locations
            project_paths = [
                Path.home() / ".claude" / "projects",
                Path.cwd() / "projects",
                Path.cwd() / "workspaces"
            ]
            
            project_count = 0
            for path in project_paths:
                if path.exists():
                    for project_dir in path.iterdir():
                        if project_dir.is_dir():
                            project_info = self.load_project_info(project_dir)
                            if project_info:
                                self.projects[project_dir.name] = project_info
                                project_count += 1
            
            logger.info(f"Discovered {project_count} projects")
            
        except Exception as e:
            logger.error(f"Error discovering projects: {e}")
    
    def load_project_info(self, project_path: Path) -> Optional[Dict]:
        """Load project information and configuration."""
        try:
            project_info = {
                'name': project_path.name,
                'path': str(project_path),
                'type': 'unknown',
                'files': [],
                'config': {}
            }
            
            # Detect project type
            if (project_path / "package.json").exists():
                project_info['type'] = 'nodejs'
            elif (project_path / "requirements.txt").exists() or (project_path / "pyproject.toml").exists():
                project_info['type'] = 'python'
            elif (project_path / "Cargo.toml").exists():
                project_info['type'] = 'rust'
            elif (project_path / "go.mod").exists():
                project_info['type'] = 'go'
            
            # Load project files (limit for performance)
            file_count = 0
            for file_path in project_path.rglob("*"):
                if file_path.is_file() and file_count < 100:  # Limit for performance
                    if not any(ignore in str(file_path) for ignore in ['.git', 'node_modules', '__pycache__', '.venv']):
                        project_info['files'].append({
                            'name': file_path.name,
                            'path': str(file_path.relative_to(project_path)),
                            'size': file_path.stat().st_size
                        })
                        file_count += 1
            
            return project_info
            
        except Exception as e:
            logger.error(f"Error loading project info for {project_path}: {e}")
            return None
    
    def start_agents(self):
        """Start the multi-agent system."""
        try:
            logger.info("Starting multi-agent system...")
            
            if self.agent_factory is None:
                logger.warning("Agent factory not available - skipping agent startup")
                return True
            
            # Start core agents - fix agent names to match factory
            core_agents = [
                'technical_lead',
                'backend', 
                'frontend',
                'qa',
                'documentation'
            ]
            
            for agent_type in core_agents:
                try:
                    # Remove await since create_agent is synchronous
                    agent = self.agent_factory.create_agent(agent_type)
                    if agent:
                        self.running_agents[agent_type] = agent
                        logger.info(f"Started {agent_type} agent")
                    else:
                        logger.warning(f"Could not create {agent_type} agent")
                except Exception as e:
                    logger.error(f"Error starting {agent_type} agent: {e}")
            
            logger.info(f"Started {len(self.running_agents)} agents")
            return True
            
        except Exception as e:
            logger.error(f"Failed to start agents: {e}")
            return False
    
    def run_validation(self):
        """Run system validation tests."""
        logger.info("Running system validation...")
        
        try:
            # Import and run validation from backup
            import subprocess
            result = subprocess.run([
                sys.executable, "main_validation_backup.py"
            ], capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                logger.info("System validation passed")
                print("✅ System validation: PASSED")
                return True
            else:
                logger.error(f"System validation failed: {result.stderr}")
                print("❌ System validation: FAILED")
                return False
                
        except Exception as e:
            logger.error(f"Validation error: {e}")
            return False
    
    async def shutdown(self):
        """Gracefully shutdown the application."""
        logger.info("Shutting down SOTA AI System...")
        
        try:
            # Stop web server
            if self.api_server:
                logger.info("Stopping web server...")
                # The Flask server will be stopped when the process ends
            
            # Stop agents
            for agent_name, agent in self.running_agents.items():
                if hasattr(agent, 'shutdown'):
                    if asyncio.iscoroutinefunction(agent.shutdown):
                        await agent.shutdown()
                    else:
                        agent.shutdown()
                logger.info(f"Stopped {agent_name} agent")
            
            # Clean up memory engine
            if self.memory_engine and hasattr(self.memory_engine, 'cleanup'):
                if asyncio.iscoroutinefunction(self.memory_engine.cleanup):
                    await self.memory_engine.cleanup()
                else:
                    self.memory_engine.cleanup()
            
            logger.info("Shutdown completed successfully")
            
        except Exception as e:
            logger.error(f"Error during shutdown: {e}")
    
    async def run(self):
        """Main application run loop."""
        try:
            # Initialize core systems
            if not await self.initialize_core_systems():
                logger.error("Failed to initialize core systems")
                return False
            
            # Start agents
            if not self.start_agents():
                logger.error("Failed to start agents")
                return False
            
            # Start web server (unless headless or agents-only)
            if not self.config.get('agents_only', False):
                if not await self.start_web_server():
                    logger.error("Failed to start web server")
                    return False
            
            logger.info("🚀 SOTA AI System is running!")
            logger.info(f"📊 Active agents: {len(self.running_agents)}")
            logger.info(f"📁 Available projects: {len(self.projects)}")
            
            if not self.headless:
                # Get actual port the server is running on
                actual_port = getattr(self.api_server.config, 'port', self.port) if self.api_server else self.port
                logger.info(f"🌐 Web interface: http://{self.host}:{actual_port}")
                print("\n🎉 SOTA AI System is ready!")
                print(f"🌐 Open your browser to: http://{self.host}:{actual_port}")
                print(f"📊 {len(self.running_agents)} agents running")
                print(f"📁 {len(self.projects)} projects available")
                print("\n💡 Press Ctrl+C to stop")
            
            # Keep running until interrupted
            try:
                while True:
                    await asyncio.sleep(1)
            except KeyboardInterrupt:
                logger.info("Received shutdown signal")
            
            return True
            
        except Exception as e:
            logger.error(f"Application error: {e}")
            return False
        finally:
            await self.shutdown()


def main():
    """Main entry point with command line argument support."""
    parser = argparse.ArgumentParser(
        description="SOTA AI System - Local development environment with multi-agent architecture",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py                    # Launch with web GUI
  python main.py --headless         # Run without GUI (API only)
  python main.py --port 8080        # Specify custom port
  python main.py --validate         # Run system validation
  python main.py --agents-only      # Start agents without web interface

Features:
  • Multi-Agent Architecture: Collaborative AI agents for development
  • Modern Web GUI: Browser-based interface for managing sessions
  • MCP Integration: Model Context Protocol for tool connections
  • Project Management: Workspace and file management
  • Real-time Collaboration: Agents working together on tasks
        """
    )
    
    parser.add_argument(
        '--port', 
        type=int,
        default=8080,
        help='Port for web server (default: 8080)'
    )
    
    parser.add_argument(
        '--host',
        default='localhost',
        help='Host for web server (default: localhost)'
    )
    
    parser.add_argument(
        '--headless', 
        action='store_true',
        help='Run without web GUI (API only)'
    )
    
    parser.add_argument(
        '--agents-only',
        action='store_true', 
        help='Start agents without web interface'
    )
    
    parser.add_argument(
        '--validate',
        action='store_true',
        help='Run system validation tests'
    )
    
    parser.add_argument(
        '--quiet', 
        action='store_true',
        help='Run with minimal output'
    )
    
    args = parser.parse_args()
    
    if args.quiet:
        logging.getLogger().setLevel(logging.WARNING)
    
    # Handle validation mode
    if args.validate:
        app = SOTAAISystem()
        result = app.run_validation()
        sys.exit(0 if result else 1)
    
    # Run main application
    config = {
        'port': args.port,
        'host': args.host,
        'headless': args.headless,
        'agents_only': args.agents_only
    }
    
    try:
        app = SOTAAISystem(config)
        success = asyncio.run(app.run())
        sys.exit(0 if success else 1)
        
    except KeyboardInterrupt:
        logger.info("Application interrupted by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Application failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()