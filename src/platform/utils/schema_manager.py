#!/usr/bin/env python3
"""
Consolidated Schema Management Utility

Replaces the duplicate utils/fix_yaml_schemas.py and utils/add_schemas_to_tasks.py
scripts with a unified, configurable schema management system.

This utility can:
- Add schema directives to YAML files
- Update existing schema directives
- Validate schema file compatibility
- Manage multiple schema configurations
- Provide comprehensive reporting
"""

import argparse
import json
import logging
import os
import re
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
import yaml

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


class SchemaManagerError(Exception):
    """Custom exception for schema management errors."""
    pass


class SchemaConfiguration:
    """Configuration for schema management operations."""
    
    def __init__(self, 
                 schema_path: str,
                 schema_type: str = "task",
                 relative_from: str = "tasks"):
        """
        Initialize schema configuration.
        
        Args:
            schema_path: Path to the schema file
            schema_type: Type of schema (task, workflow, etc.)
            relative_from: Directory from which schema path should be relative
        """
        self.schema_path = schema_path
        self.schema_type = schema_type
        self.relative_from = relative_from
        
        # Validate schema file exists
        if not Path(schema_path).exists():
            raise SchemaManagerError(f"Schema file not found: {schema_path}")
    
    def get_directive(self) -> str:
        """Get the yaml-language-server directive for this schema."""
        # Calculate relative path from the reference directory
        schema_file = Path(self.schema_path)
        relative_from_path = Path(self.relative_from)
        
        try:
            # Calculate relative path
            rel_path = os.path.relpath(schema_file, relative_from_path)
            return f"# yaml-language-server: $schema={rel_path}"
        except ValueError:
            # If relative path calculation fails, use absolute path
            return f"# yaml-language-server: $schema={schema_file.absolute()}"


class SchemaManager:
    """Unified schema management for YAML files."""
    
    def __init__(self):
        """Initialize the schema manager."""
        self.stats = {
            'updated': 0,
            'skipped': 0,
            'errors': 0,
            'validated': 0
        }
        
        # Predefined schema configurations
        self.schema_configs = {
            'ai_agent_task': SchemaConfiguration(
                schema_path="tasks/task-schema.json",
                schema_type="task",
                relative_from="tasks"
            ),
            'generic_task': SchemaConfiguration(
                schema_path="config/schemas/task.schema.json", 
                schema_type="task",
                relative_from="tasks"
            )
        }
    
    def add_schema_config(self, name: str, config: SchemaConfiguration):
        """Add a new schema configuration."""
        self.schema_configs[name] = config
    
    def process_yaml_files(self, 
                          directory: str = "tasks",
                          schema_config: str = "ai_agent_task",
                          pattern: str = "*.yaml",
                          force_update: bool = False,
                          validate_content: bool = False) -> Dict[str, int]:
        """
        Process YAML files to add or update schema directives.
        
        Args:
            directory: Directory containing YAML files
            schema_config: Name of schema configuration to use
            pattern: File pattern to match
            force_update: Whether to update existing directives
            validate_content: Whether to validate file content against schema
            
        Returns:
            Dictionary with processing statistics
        """
        if schema_config not in self.schema_configs:
            raise SchemaManagerError(f"Unknown schema configuration: {schema_config}")
        
        config = self.schema_configs[schema_config]
        yaml_files = list(Path(directory).glob(pattern))
        
        logger.info(f"Found {len(yaml_files)} YAML files in {directory}/")
        logger.info(f"Using schema configuration: {schema_config}")
        logger.info(f"Schema directive: {config.get_directive()}")
        
        # Reset stats
        self.stats = {'updated': 0, 'skipped': 0, 'errors': 0, 'validated': 0}
        
        for file_path in yaml_files:
            try:
                self._process_single_file(file_path, config, force_update, validate_content)
            except Exception as e:
                logger.error(f"Error processing {file_path.name}: {e}")
                self.stats['errors'] += 1
        
        # Print summary
        self._print_summary()
        return self.stats.copy()
    
    def _process_single_file(self, 
                           file_path: Path, 
                           config: SchemaConfiguration,
                           force_update: bool,
                           validate_content: bool):
        """Process a single YAML file."""
        # Read file content
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        target_directive = config.get_directive()
        
        # Check if file already has correct directive
        if target_directive in content:
            logger.debug(f"Skipping {file_path.name} (already has correct schema directive)")
            self.stats['skipped'] += 1
            return
        
        # Check for existing schema directive
        existing_directive_pattern = r"# yaml-language-server: \$schema=[^\n]*"
        has_existing_directive = re.search(existing_directive_pattern, content)
        
        if has_existing_directive and not force_update:
            logger.debug(f"Skipping {file_path.name} (has different schema directive, use --force to update)")
            self.stats['skipped'] += 1
            return
        
        # Update content
        if has_existing_directive and force_update:
            # Replace existing directive
            new_content = re.sub(
                existing_directive_pattern,
                target_directive,
                content
            )
            logger.info(f"Updated existing directive in {file_path.name}")
        else:
            # Add new directive at the beginning
            new_content = f"{target_directive}\n{content}"
            logger.info(f"Added new directive to {file_path.name}")
        
        # Validate content if requested
        if validate_content:
            try:
                self._validate_yaml_content(new_content, config)
                self.stats['validated'] += 1
            except Exception as e:
                logger.warning(f"Validation failed for {file_path.name}: {e}")
        
        # Write updated content
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(new_content)
        
        self.stats['updated'] += 1
    
    def _validate_yaml_content(self, content: str, config: SchemaConfiguration):
        """Validate YAML content against schema."""
        try:
            # Parse YAML content
            yaml_data = yaml.safe_load(content)
            
            # Load schema
            with open(config.schema_path, 'r') as f:
                schema = json.load(f)
            
            # Basic validation - check required fields if specified
            if 'required' in schema and yaml_data:
                for required_field in schema['required']:
                    if required_field not in yaml_data:
                        raise SchemaManagerError(f"Missing required field: {required_field}")
            
            logger.debug("YAML content validation passed")
            
        except yaml.YAMLError as e:
            raise SchemaManagerError(f"Invalid YAML syntax: {e}")
        except json.JSONDecodeError as e:
            raise SchemaManagerError(f"Invalid schema JSON: {e}")
    
    def _print_summary(self):
        """Print processing summary."""
        total = sum(self.stats.values())
        logger.info("\n" + "="*50)
        logger.info("SCHEMA MANAGEMENT SUMMARY")
        logger.info("="*50)
        logger.info(f"Files Updated:    {self.stats['updated']}")
        logger.info(f"Files Skipped:    {self.stats['skipped']}")
        logger.info(f"Files Validated:  {self.stats['validated']}")
        logger.info(f"Errors:          {self.stats['errors']}")
        logger.info(f"Total Processed: {total}")
        logger.info("="*50)
    
    def list_configurations(self):
        """List available schema configurations."""
        print("\nAvailable Schema Configurations:")
        print("="*50)
        for name, config in self.schema_configs.items():
            print(f"Name: {name}")
            print(f"  Schema Path: {config.schema_path}")
            print(f"  Schema Type: {config.schema_type}")
            print(f"  Relative From: {config.relative_from}")
            print(f"  Directive: {config.get_directive()}")
            print()
    
    def analyze_schema_conflicts(self) -> Dict[str, Any]:
        """Analyze conflicts between different schema files."""
        conflicts = {
            'duplicate_schemas': [],
            'incompatible_fields': {},
            'missing_schemas': []
        }
        
        # Check for schema file conflicts
        schema_paths = [config.schema_path for config in self.schema_configs.values()]
        schema_contents = {}
        
        for path in set(schema_paths):
            try:
                with open(path, 'r') as f:
                    schema_contents[path] = json.load(f)
            except FileNotFoundError:
                conflicts['missing_schemas'].append(path)
            except Exception as e:
                logger.error(f"Error reading schema {path}: {e}")
        
        # Analyze field compatibility between schemas
        if len(schema_contents) > 1:
            schema_items = list(schema_contents.items())
            for i, (path1, schema1) in enumerate(schema_items):
                for path2, schema2 in schema_items[i+1:]:
                    field_conflicts = self._compare_schemas(schema1, schema2)
                    if field_conflicts:
                        conflicts['incompatible_fields'][f"{path1} vs {path2}"] = field_conflicts
        
        return conflicts
    
    def _compare_schemas(self, schema1: Dict, schema2: Dict) -> List[str]:
        """Compare two schemas and find conflicts."""
        conflicts = []
        
        # Compare required fields
        req1 = set(schema1.get('required', []))
        req2 = set(schema2.get('required', []))
        
        if req1 != req2:
            conflicts.append(f"Different required fields: {req1} vs {req2}")
        
        # Compare properties
        props1 = schema1.get('properties', {})
        props2 = schema2.get('properties', {})
        
        common_fields = set(props1.keys()) & set(props2.keys())
        for field in common_fields:
            prop1 = props1[field]
            prop2 = props2[field]
            
            # Check type compatibility
            type1 = prop1.get('type')
            type2 = prop2.get('type')
            
            if type1 != type2:
                conflicts.append(f"Field '{field}' has different types: {type1} vs {type2}")
            
            # Check enum compatibility
            enum1 = prop1.get('enum')
            enum2 = prop2.get('enum')
            
            if enum1 and enum2 and set(enum1) != set(enum2):
                conflicts.append(f"Field '{field}' has different enum values: {enum1} vs {enum2}")
        
        return conflicts


def main():
    """Main entry point for the schema manager CLI."""
    parser = argparse.ArgumentParser(
        description="Unified Schema Management Utility for YAML files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python utils/schema_manager.py                          # Use default AI agent task schema
  python utils/schema_manager.py --config generic_task   # Use generic task schema
  python utils/schema_manager.py --force                 # Force update existing directives
  python utils/schema_manager.py --validate              # Validate content against schema
  python utils/schema_manager.py --list-configs          # List available configurations
  python utils/schema_manager.py --analyze-conflicts     # Analyze schema conflicts
        """
    )
    
    parser.add_argument(
        'directory',
        nargs='?',
        default='tasks',
        help='Directory containing YAML files (default: tasks)'
    )
    
    parser.add_argument(
        '--config',
        default='ai_agent_task',
        help='Schema configuration to use (default: ai_agent_task)'
    )
    
    parser.add_argument(
        '--pattern',
        default='*.yaml',
        help='File pattern to match (default: *.yaml)'
    )
    
    parser.add_argument(
        '--force',
        action='store_true',
        help='Force update of existing schema directives'
    )
    
    parser.add_argument(
        '--validate',
        action='store_true',
        help='Validate YAML content against schema'
    )
    
    parser.add_argument(
        '--list-configs',
        action='store_true',
        help='List available schema configurations'
    )
    
    parser.add_argument(
        '--analyze-conflicts',
        action='store_true',
        help='Analyze conflicts between schema files'
    )
    
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose logging'
    )
    
    args = parser.parse_args()
    
    # Set logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Initialize schema manager
    try:
        manager = SchemaManager()
        
        # Handle special commands
        if args.list_configs:
            manager.list_configurations()
            return
        
        if args.analyze_conflicts:
            conflicts = manager.analyze_schema_conflicts()
            print("\nSchema Conflict Analysis:")
            print("="*50)
            
            if conflicts['missing_schemas']:
                print(f"Missing Schemas: {conflicts['missing_schemas']}")
            
            if conflicts['incompatible_fields']:
                print("Field Conflicts:")
                for comparison, conflicts_list in conflicts['incompatible_fields'].items():
                    print(f"  {comparison}:")
                    for conflict in conflicts_list:
                        print(f"    - {conflict}")
            
            if not any(conflicts.values()):
                print("No conflicts detected.")
            
            return
        
        # Process YAML files
        stats = manager.process_yaml_files(
            directory=args.directory,
            schema_config=args.config,
            pattern=args.pattern,
            force_update=args.force,
            validate_content=args.validate
        )
        
        # Exit with error code if there were errors
        if stats['errors'] > 0:
            sys.exit(1)
        
    except SchemaManagerError as e:
        logger.error(f"Schema management error: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        logger.info("Operation cancelled by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()