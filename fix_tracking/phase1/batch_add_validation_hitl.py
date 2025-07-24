#!/usr/bin/env python3
"""Batch add validation to HITL route endpoints."""

import re
from pathlib import Path

def add_validation_to_hitl_routes():
    """Add validation decorators to HITL routes that don't have them."""
    
    file_path = Path("src/interfaces/api/hitl_routes.py")
    content = file_path.read_text()
    
    # Define validation schemas for specific endpoints
    endpoint_validations = {
        'batch_process_checkpoints': {
            'checkpoint_ids': {'type': 'string', 'required': True, 'max_length': 2000},
            'action': {'type': 'enum', 'required': True, 'values': ['approve', 'reject', 'escalate']},
            'reason': {'type': 'string', 'required': False, 'max_length': 500}
        },
        'capture_checkpoint_feedback': {
            'rating': {'type': 'integer', 'required': True, 'min': 1, 'max': 5},
            'comment': {'type': 'string', 'required': False, 'max_length': 1000},
            'category': {'type': 'string', 'required': False, 'max_length': 100}
        },
        'export_feedback_data': {
            'format': {'type': 'enum', 'required': False, 'values': ['json', 'csv', 'xlsx']},
            'date_from': {'type': 'string', 'required': False, 'max_length': 20},
            'date_to': {'type': 'string', 'required': False, 'max_length': 20}
        },
        'batch_approve_checkpoints': {
            'checkpoint_ids': {'type': 'string', 'required': True, 'max_length': 2000},
            'reason': {'type': 'string', 'required': False, 'max_length': 500}
        },
        'batch_reject_checkpoints': {
            'checkpoint_ids': {'type': 'string', 'required': True, 'max_length': 2000},
            'reason': {'type': 'string', 'required': True, 'max_length': 500}
        },
        'register_webhook': {
            'url': {'type': 'string', 'required': True, 'max_length': 500},
            'events': {'type': 'string', 'required': True, 'max_length': 200},
            'secret': {'type': 'string', 'required': False, 'max_length': 100}
        },
        'request_github_pr_review': {
            'reviewer': {'type': 'string', 'required': True, 'max_length': 100},
            'message': {'type': 'string', 'required': False, 'max_length': 1000}
        },
        'send_slack_approval_request': {
            'channel': {'type': 'string', 'required': True, 'max_length': 100},
            'message': {'type': 'string', 'required': True, 'max_length': 1000},
            'approvers': {'type': 'string', 'required': False, 'max_length': 500}
        },
        'create_jira_review_issue': {
            'project': {'type': 'string', 'required': True, 'max_length': 50},
            'summary': {'type': 'string', 'required': True, 'max_length': 200},
            'description': {'type': 'string', 'required': False, 'max_length': 2000}
        },
        'process_widget_action': {
            'action': {'type': 'string', 'required': True, 'max_length': 100},
            'data': {'type': 'string', 'required': False, 'max_length': 2000}
        }
    }
    
    # Add validation to each endpoint
    for endpoint_name, schema in endpoint_validations.items():
        # Find the route definition
        pattern = f"(@hitl_bp\\.route\\([^)]+methods=\\[[^]]*[\"']POST[\"'][^]]*\\]\\))\\s*def {endpoint_name}\\("
        
        match = re.search(pattern, content)
        if match:
            route_decorator = match.group(1)
            
            # Check if already has validation
            context_start = max(0, match.start() - 200)
            context = content[context_start:match.end()]
            
            if '@validate_input' not in context:
                # Generate validation decorator
                schema_str = "{\n"
                for field, field_schema in schema.items():
                    schema_str += f"    '{field}': {field_schema},\n"
                schema_str = schema_str.rstrip(',\n') + '\n}'
                
                # Add auth and validation decorators
                new_decorators = f"{route_decorator}\n@auth.require_auth\n@validate_input({{}}, json_schema={schema_str})"
                
                # Replace in content
                content = content.replace(route_decorator, new_decorators)
                print(f"✅ Added validation to {endpoint_name}")
            else:
                print(f"➡️  {endpoint_name} already has validation")
        else:
            print(f"❌ Could not find {endpoint_name}")
    
    # Write back
    file_path.write_text(content)
    print(f"\n📝 Updated {file_path}")

if __name__ == "__main__":
    add_validation_to_hitl_routes()