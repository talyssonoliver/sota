"""
Schema Registry and Validation
Centralized schema definitions and validation service
"""

import json
import yaml
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
from dataclasses import dataclass, field

from .validation_errors import SchemaValidationError, MultipleValidationError


@dataclass
class SchemaDefinition:
    """Schema definition with metadata"""
    name: str
    schema: Dict[str, Any]
    version: str = "1.0"
    description: str = ""
    tags: List[str] = field(default_factory=list)
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


class SchemaRegistry:
    """Centralized registry for schema definitions"""
    
    def __init__(self, schema_dir: Optional[Path] = None):
        self.schemas: Dict[str, SchemaDefinition] = {}
        self.schema_dir = schema_dir or Path("schemas")
        self.cache_enabled = True
        
        # Load schemas from directory if it exists
        if self.schema_dir.exists():
            self.load_all_schemas()
    
    def register_schema(
        self,
        name: str,
        schema: Dict[str, Any],
        version: str = "1.0",
        description: str = "",
        tags: List[str] = None,
        save_to_file: bool = True
    ) -> None:
        """Register a new schema"""
        schema_def = SchemaDefinition(
            name=name,
            schema=schema,
            version=version,
            description=description,
            tags=tags or []
        )
        
        self.schemas[name] = schema_def
        
        if save_to_file:
            self._save_schema_to_file(schema_def)
    
    def get_schema(self, name: str) -> Optional[SchemaDefinition]:
        """Get schema by name"""
        return self.schemas.get(name)
    
    def validate_against_schema(
        self,
        data: Dict[str, Any],
        schema_name: str
    ) -> None:
        """Validate data against registered schema"""
        schema_def = self.get_schema(schema_name)
        if not schema_def:
            raise SchemaValidationError(
                f"Schema '{schema_name}' not found in registry",
                schema_path=schema_name
            )
        
        errors = self._validate_data(data, schema_def.schema, schema_name)
        
        if errors:
            if len(errors) == 1:
                raise errors[0]
            else:
                raise MultipleValidationError(errors)
    
    def _validate_data(
        self,
        data: Dict[str, Any],
        schema: Dict[str, Any],
        schema_path: str
    ) -> List[SchemaValidationError]:
        """Internal validation logic"""
        errors = []
        
        # Check required fields
        required_fields = schema.get('required', [])
        for field in required_fields:
            if field not in data:
                errors.append(
                    SchemaValidationError(
                        f"Required field '{field}' is missing",
                        field=field,
                        schema_path=f"{schema_path}.{field}"
                    )
                )
        
        # Check field properties
        properties = schema.get('properties', {})
        for field, value in data.items():
            if field in properties:
                field_schema = properties[field]
                field_errors = self._validate_field(
                    value, field_schema, f"{schema_path}.{field}", field
                )
                errors.extend(field_errors)
        
        # Check additional properties
        if not schema.get('additionalProperties', True):
            allowed_fields = set(properties.keys())
            for field in data.keys():
                if field not in allowed_fields:
                    errors.append(
                        SchemaValidationError(
                            f"Additional property '{field}' is not allowed",
                            field=field,
                            schema_path=schema_path
                        )
                    )
        
        return errors
    
    def _validate_field(
        self,
        value: Any,
        field_schema: Dict[str, Any],
        schema_path: str,
        field_name: str
    ) -> List[SchemaValidationError]:
        """Validate individual field"""
        errors = []
        
        # Type validation
        expected_type = field_schema.get('type')
        if expected_type:
            type_map = {
                'string': str,
                'integer': int,
                'number': (int, float),
                'boolean': bool,
                'array': list,
                'object': dict,
                'null': type(None)
            }
            
            if expected_type in type_map:
                if not isinstance(value, type_map[expected_type]):
                    errors.append(
                        SchemaValidationError(
                            f"Expected {expected_type}, got {type(value).__name__}",
                            field=field_name,
                            value=value,
                            schema_path=schema_path
                        )
                    )
                    return errors  # Skip further validation if type is wrong
        
        # String validations
        if isinstance(value, str):
            if 'minLength' in field_schema and len(value) < field_schema['minLength']:
                errors.append(
                    SchemaValidationError(
                        f"String length {len(value)} is below minimum {field_schema['minLength']}",
                        field=field_name,
                        value=value,
                        schema_path=schema_path
                    )
                )
            
            if 'maxLength' in field_schema and len(value) > field_schema['maxLength']:
                errors.append(
                    SchemaValidationError(
                        f"String length {len(value)} exceeds maximum {field_schema['maxLength']}",
                        field=field_name,
                        value=value,
                        schema_path=schema_path
                    )
                )
            
            if 'pattern' in field_schema:
                import re
                if not re.match(field_schema['pattern'], value):
                    errors.append(
                        SchemaValidationError(
                            f"String does not match pattern '{field_schema['pattern']}'",
                            field=field_name,
                            value=value,
                            schema_path=schema_path
                        )
                    )
        
        # Number validations
        if isinstance(value, (int, float)):
            if 'minimum' in field_schema and value < field_schema['minimum']:
                errors.append(
                    SchemaValidationError(
                        f"Value {value} is below minimum {field_schema['minimum']}",
                        field=field_name,
                        value=value,
                        schema_path=schema_path
                    )
                )
            
            if 'maximum' in field_schema and value > field_schema['maximum']:
                errors.append(
                    SchemaValidationError(
                        f"Value {value} exceeds maximum {field_schema['maximum']}",
                        field=field_name,
                        value=value,
                        schema_path=schema_path
                    )
                )
        
        # Array validations
        if isinstance(value, list):
            if 'minItems' in field_schema and len(value) < field_schema['minItems']:
                errors.append(
                    SchemaValidationError(
                        f"Array length {len(value)} is below minimum {field_schema['minItems']}",
                        field=field_name,
                        value=value,
                        schema_path=schema_path
                    )
                )
            
            if 'maxItems' in field_schema and len(value) > field_schema['maxItems']:
                errors.append(
                    SchemaValidationError(
                        f"Array length {len(value)} exceeds maximum {field_schema['maxItems']}",
                        field=field_name,
                        value=value,
                        schema_path=schema_path
                    )
                )
            
            # Validate array items
            if 'items' in field_schema:
                item_schema = field_schema['items']
                for i, item in enumerate(value):
                    item_errors = self._validate_field(
                        item, item_schema, f"{schema_path}[{i}]", f"{field_name}[{i}]"
                    )
                    errors.extend(item_errors)
        
        return errors
    
    def load_schema_definitions(self, schema_file: Path) -> None:
        """Load schema definitions from file"""
        if not schema_file.exists():
            return
        
        try:
            with open(schema_file, 'r', encoding='utf-8') as f:
                if schema_file.suffix.lower() == '.json':
                    data = json.load(f)
                elif schema_file.suffix.lower() in ['.yaml', '.yml']:
                    data = yaml.safe_load(f)
                else:
                    return
            
            if isinstance(data, dict):
                for name, schema_data in data.items():
                    if isinstance(schema_data, dict) and 'schema' in schema_data:
                        self.register_schema(
                            name=name,
                            schema=schema_data['schema'],
                            version=schema_data.get('version', '1.0'),
                            description=schema_data.get('description', ''),
                            tags=schema_data.get('tags', []),
                            save_to_file=False
                        )
        except Exception as e:
            print(f"Error loading schema file {schema_file}: {e}")
    
    def load_all_schemas(self) -> None:
        """Load all schema files from schema directory"""
        if not self.schema_dir.exists():
            return
        
        for schema_file in self.schema_dir.glob("*.json"):
            self.load_schema_definitions(schema_file)
        
        for schema_file in self.schema_dir.glob("*.yaml"):
            self.load_schema_definitions(schema_file)
        
        for schema_file in self.schema_dir.glob("*.yml"):
            self.load_schema_definitions(schema_file)
    
    def _save_schema_to_file(self, schema_def: SchemaDefinition) -> None:
        """Save schema definition to file"""
        if not self.schema_dir.exists():
            self.schema_dir.mkdir(parents=True)
        
        schema_file = self.schema_dir / f"{schema_def.name}.json"
        
        schema_data = {
            'schema': schema_def.schema,
            'version': schema_def.version,
            'description': schema_def.description,
            'tags': schema_def.tags
        }
        
        with open(schema_file, 'w', encoding='utf-8') as f:
            json.dump(schema_data, f, indent=2)
    
    def list_schemas(self) -> List[str]:
        """List all registered schema names"""
        return list(self.schemas.keys())
    
    def get_schema_info(self, name: str) -> Optional[Dict[str, Any]]:
        """Get schema information"""
        schema_def = self.get_schema(name)
        if not schema_def:
            return None
        
        return {
            'name': schema_def.name,
            'version': schema_def.version,
            'description': schema_def.description,
            'tags': schema_def.tags,
            'fields': list(schema_def.schema.get('properties', {}).keys())
        }


# Global schema registry instance
_global_registry = None


def get_schema_registry() -> SchemaRegistry:
    """Get global schema registry instance"""
    global _global_registry
    if _global_registry is None:
        _global_registry = SchemaRegistry()
    return _global_registry


def register_schema(name: str, schema: Dict[str, Any], **kwargs) -> None:
    """Register schema in global registry"""
    registry = get_schema_registry()
    registry.register_schema(name, schema, **kwargs)


def validate_against_schema(data: Dict[str, Any], schema_name: str) -> None:
    """Validate data against global schema registry"""
    registry = get_schema_registry()
    registry.validate_against_schema(data, schema_name)


def schema_cache(func):
    """Decorator to cache schema validation results"""
    cache = {}
    
    @functools.wraps(func)
    def wrapper(data, schema_name):
        # Simple cache key based on data structure
        cache_key = (str(sorted(data.keys())), schema_name)
        
        if cache_key in cache:
            return cache[cache_key]
        
        try:
            result = func(data, schema_name)
            cache[cache_key] = result
            return result
        except Exception as e:
            # Don't cache errors
            raise
    
    return wrapper
