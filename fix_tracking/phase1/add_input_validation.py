#!/usr/bin/env python3
"""Add input validation to all POST/PUT/PATCH endpoints."""

import re
from pathlib import Path
from typing import Dict

def analyze_endpoint(method: str, route: str, func_content: str) -> Dict[str, str]:
    """Analyze endpoint to determine appropriate validation schema."""
    
    # Common patterns for different types of endpoints
    validation_schemas = {
        'id_param': {
            'type': 'string',
            'required': True,
            'max_length': 100
        },
        'description': {
            'type': 'string', 
            'required': True,
            'max_length': 1000
        },
        'reason': {
            'type': 'string',
            'required': False,
            'max_length': 500
        },
        'notes': {
            'type': 'string',
            'required': False,
            'max_length': 1000
        },
        'priority': {
            'type': 'enum',
            'required': False,
            'values': ['low', 'medium', 'high']
        },
        'status': {
            'type': 'enum',
            'required': False,
            'values': ['pending', 'approved', 'rejected']
        }
    }
    
    # Determine validation based on route patterns
    if 'approve' in route or 'approve' in func_content.lower():
        return {
            'reason': validation_schemas['reason'],
            'notes': validation_schemas['notes']
        }
    elif 'reject' in route or 'reject' in func_content.lower():
        return {
            'reason': {'type': 'string', 'required': True, 'max_length': 500},
            'notes': validation_schemas['notes']
        }
    elif 'checkpoint' in route or 'task' in route:
        return {
            'task_id': validation_schemas['id_param'],
            'description': validation_schemas['description'],
            'priority': validation_schemas['priority']
        }
    elif 'feedback' in route:
        return {
            'rating': {'type': 'integer', 'required': True, 'min': 1, 'max': 5},
            'comment': validation_schemas['description'],
            'category': validation_schemas['id_param']
        }
    elif 'webhook' in route:
        return {
            'url': {'type': 'string', 'required': True, 'max_length': 500},
            'secret': {'type': 'string', 'required': False, 'max_length': 100},
            'events': {'type': 'string', 'required': True, 'max_length': 200}
        }
    else:
        # Generic validation for unknown endpoints
        return {
            'data': {'type': 'string', 'required': False, 'max_length': 2000}
        }

def add_validation_to_endpoint(content: str, file_path: Path) -> str:
    """Add input validation decorators to POST/PUT/PATCH endpoints."""
    
    # Pattern to match route decorators with POST/PUT/PATCH methods
    route_pattern = r'(@\w+\.route\([^)]+methods=\[[^]]*["\'](?:POST|PUT|PATCH)["\'][^]]*\]\))\s*(@[^\\n]*\\n)*\s*(def\s+\w+\([^)]*\):)'
    
    def replace_route(match):
        route_decorator = match.group(1)
        existing_decorators = match.group(2) or ""
        function_def = match.group(3)
        
        # Extract route info
        route_match = re.search(r'["\']([^"\']+)["\'].*methods=\[[^]]*["\'](\w+)["\']', route_decorator)
        if not route_match:
            return match.group(0)  # No change if we can't parse
        
        route_path = route_match.group(1)
        method = route_match.group(2)
        
        # Check if validation already exists
        if '@validate_input' in existing_decorators:
            return match.group(0)  # Already has validation
        
        # Generate validation schema
        func_content = content[match.end():match.end()+500]  # Look ahead for context
        schema = analyze_endpoint(method, route_path, func_content)
        
        # Format schema as string
        schema_str = "{\n"
        for field, field_schema in schema.items():
            schema_str += f"            '{field}': {field_schema},\n"
        schema_str = schema_str.rstrip(',\n') + '\n        }'
        
        # Add validation decorator
        validation_decorator = f"        @validate_input({{}}, json_schema={schema_str})\n"
        
        return f"{route_decorator}\n{existing_decorators.rstrip()}\n{validation_decorator}        {function_def}"
    
    # Apply the pattern replacement
    result = re.sub(route_pattern, replace_route, content, flags=re.MULTILINE)
    
    # Add import if validation was added and import doesn't exist
    if '@validate_input' in result and 'from src.infrastructure.security.input_validator import validate_input' not in result:
        # Find a good place to add the import
        import_pattern = r'(from src\.infrastructure\.security\.auth_middleware import[^\\n]+)'
        if re.search(import_pattern, result):
            result = re.sub(
                import_pattern, 
                r'\1\nfrom src.infrastructure.security.input_validator import validate_input',
                result
            )
        else:
            # Add at the end of imports
            result = re.sub(
                r'(import [^\\n]+\n\n)',
                r'\1from src.infrastructure.security.input_validator import validate_input\n\n',
                result,
                count=1
            )
    
    return result

def process_file(file_path: Path) -> bool:
    """Process a single file to add input validation."""
    print(f"Processing {file_path}")
    
    try:
        content = file_path.read_text()
        original_content = content
        
        # Add validation to endpoints
        content = add_validation_to_endpoint(content, file_path)
        
        if content != original_content:
            file_path.write_text(content)
            print(f"  ✅ Updated {file_path}")
            return True
        else:
            print(f"  ➡️  No changes needed for {file_path}")
            return False
            
    except Exception as e:
        print(f"  ❌ Error processing {file_path}: {e}")
        return False

def main():
    """Main function."""
    # Find API files with POST/PUT endpoints
    api_files = [
        Path("src/interfaces/dashboard/api/unified_api_server.py"),
        Path("src/interfaces/dashboard/api/routes.py"),
        Path("src/interfaces/dashboard/api/gantt_api.py"),
        Path("src/interfaces/api/webhook_manager.py"),
        Path("src/interfaces/api/external_integrations.py"),
    ]
    
    updated_files = []
    for api_file in api_files:
        if api_file.exists():
            if process_file(api_file):
                updated_files.append(api_file)
        else:
            print(f"Warning: {api_file} not found")
    
    print("\n📊 Summary:")
    print(f"Files updated: {len(updated_files)}")
    if updated_files:
        print("Updated files:")
        for file_path in updated_files:
            print(f"  - {file_path}")

if __name__ == "__main__":
    main()