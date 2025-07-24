#!/usr/bin/env python3
"""Add authentication to all API endpoints."""

import re
from pathlib import Path

def add_auth_to_route(content: str) -> str:
    """Add @requires_auth decorator to API routes that don't have it."""
    
    # Pattern to match API routes (exclude health check and static files)
    api_route_pattern = r'(@self\.app\.route\("/api/[^"]+",.*?\))\s*(@with_error_handling)?\s*(def\s+\w+\(.*?\):)'
    
    def replace_route(match):
        route_decorator = match.group(1)
        error_handling = match.group(2) or ""
        function_def = match.group(3)
        
        # Check if this already has auth
        context_before = content[:match.start()]
        last_lines = context_before.split('\n')[-5:]
        if any('@requires_auth' in line or '@public_endpoint' in line for line in last_lines):
            return match.group(0)  # Already has auth
        
        # Add auth decorator
        if error_handling:
            return f"{route_decorator}\n        @requires_auth\n        {error_handling}\n        {function_def}"
        else:
            return f"{route_decorator}\n        @requires_auth\n        {function_def}"
    
    return re.sub(api_route_pattern, replace_route, content, flags=re.MULTILINE | re.DOTALL)

def mark_public_routes(content: str) -> str:
    """Mark specific routes as public."""
    public_patterns = [
        (r'(@self\.app\.route\("/health".*?\))', '@public_endpoint'),
        (r'(@self\.app\.route\("/"\))', '@public_endpoint'),
        (r'(@self\.app\.route\("/dashboard/"\))', '@public_endpoint'),
        (r'(@self\.app\.route\("/dashboard/<.*?>"\))', '@public_endpoint'),
    ]
    
    for pattern, decorator in public_patterns:
        def add_public(match):
            route = match.group(1)
            # Check if already has decorator
            context_before = content[:match.start()]
            last_lines = context_before.split('\n')[-3:]
            if any('@public_endpoint' in line for line in last_lines):
                return match.group(0)
            return f"{route}\n        {decorator}"
        
        content = re.sub(pattern, add_public, content)
    
    return content

def process_file(file_path: Path):
    """Process a single file to add authentication."""
    print(f"Processing {file_path}")
    
    content = file_path.read_text()
    
    # Add auth to API routes
    content = add_auth_to_route(content)
    
    # Mark public routes
    content = mark_public_routes(content)
    
    # Write back
    file_path.write_text(content)
    print(f"Updated {file_path}")

def main():
    """Main function."""
    # Find API files
    api_files = [
        Path("src/interfaces/dashboard/api/unified_api_server.py"),
        Path("src/interfaces/api/webhook_manager.py"),
        Path("src/interfaces/api/external_integrations.py"),
    ]
    
    for api_file in api_files:
        if api_file.exists():
            process_file(api_file)
        else:
            print(f"Warning: {api_file} not found")

if __name__ == "__main__":
    main()