#!/usr/bin/env python3
"""
Dependency Analysis Script
Analyzes import dependencies between duplicated modules to determine safe migration order.
"""

import ast
import json
from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Set

class DependencyAnalyzer:
    def __init__(self, root_dir: str):
        self.root_dir = Path(root_dir)
        self.file_imports = defaultdict(set)  # file -> set of imports
        self.import_to_files = defaultdict(set)  # import -> set of files using it
        self.file_dependencies = defaultdict(set)  # file -> set of files it depends on
        self.reverse_dependencies = defaultdict(set)  # file -> set of files that depend on it
        
        # Critical entry points and their importance
        self.critical_files = {
            'main.py': 100,
            'orchestration/__init__.py': 90,
            'tools/__init__.py': 85,
            'src/core/__init__.py': 80,
            'src/infrastructure/__init__.py': 80,
            'tests/run_tests.py': 75,
        }
        
        # Duplicated module mappings
        self.duplicate_mappings = {
            # Orchestration workflows
            'orchestration/': 'src/core/workflows/',
            
            # Memory engine
            'tools/memory/': 'src/infrastructure/memory/',
            'engines/': 'src/infrastructure/memory/engines/',
            
            # Tools
            'tools/': 'src/infrastructure/tools/',
            
            # Agents
            'agents/': 'src/core/agents/',
            
            # Handlers
            'handlers/': 'src/infrastructure/tools/handlers/',
            
            # Graph tools
            'graph/': 'src/infrastructure/tools/',
            
            # Security patches
            'patches/': 'src/infrastructure/security/',
            'security/': 'src/infrastructure/security/',
            
            # Analytics
            'analytics/': 'src/integrations/analytics/',
            
            # CLI tools
            'cli/': 'src/interfaces/cli/',
            
            # API interfaces
            'api/': 'src/interfaces/api/',
            
            # Dashboard
            'dashboard/': 'src/interfaces/dashboard/',
        }
    
    def analyze_file(self, file_path: Path) -> Set[str]:
        """Analyze a Python file and extract its imports."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Parse the AST to extract imports
            tree = ast.parse(content)
            imports = set()
            
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.add(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        imports.add(node.module)
                        # Also add specific imports
                        for alias in node.names:
                            imports.add(f"{node.module}.{alias.name}")
            
            return imports
            
        except (SyntaxError, UnicodeDecodeError, FileNotFoundError) as e:
            print(f"Warning: Could not analyze {file_path}: {e}")
            return set()
    
    def build_dependency_graph(self):
        """Build the complete dependency graph."""
        print("Building dependency graph...")
        
        # Find all Python files
        python_files = list(self.root_dir.rglob("*.py"))
        python_files = [f for f in python_files if ".venv" not in str(f) and "htmlcov" not in str(f)]
        
        # Analyze each file
        for file_path in python_files:
            relative_path = str(file_path.relative_to(self.root_dir))
            imports = self.analyze_file(file_path)
            self.file_imports[relative_path] = imports
            
            # Build reverse mapping
            for imp in imports:
                self.import_to_files[imp].add(relative_path)
        
        # Build file-to-file dependencies
        for file_path, imports in self.file_imports.items():
            for imp in imports:
                # Try to map import to actual files
                potential_files = self._map_import_to_files(imp)
                for dep_file in potential_files:
                    if dep_file != file_path and dep_file in self.file_imports:
                        self.file_dependencies[file_path].add(dep_file)
                        self.reverse_dependencies[dep_file].add(file_path)
    
    def _map_import_to_files(self, import_name: str) -> List[str]:
        """Map an import statement to potential file paths."""
        potential_files = []
        
        # Handle local imports
        parts = import_name.split('.')
        
        # Try different combinations
        for i in range(len(parts)):
            # Try as module path
            module_path = '/'.join(parts[:i+1])
            potential_files.extend([
                f"{module_path}.py",
                f"{module_path}/__init__.py",
            ])
            
            # Try with src/ prefix
            potential_files.extend([
                f"src/{module_path}.py",
                f"src/{module_path}/__init__.py",
            ])
        
        # Filter to existing files
        existing_files = []
        for pf in potential_files:
            if pf in self.file_imports:
                existing_files.append(pf)
        
        return existing_files
    
    def find_leaf_nodes(self) -> List[str]:
        """Find files that are imported by many but import few (leaf nodes)."""
        leaf_scores = {}
        
        for file_path in self.file_imports:
            import_count = len(self.file_dependencies.get(file_path, set()))
            imported_by_count = len(self.reverse_dependencies.get(file_path, set()))
            
            # Leaf score: high if imported by many, low if imports many
            if import_count == 0:
                leaf_score = imported_by_count + 10  # Bonus for no dependencies
            else:
                leaf_score = imported_by_count / (import_count + 1)
            
            leaf_scores[file_path] = leaf_score
        
        # Sort by score (highest first)
        return sorted(leaf_scores.keys(), key=lambda x: leaf_scores[x], reverse=True)
    
    def find_root_nodes(self) -> List[str]:
        """Find files that import many but are imported by few (root nodes)."""
        root_scores = {}
        
        for file_path in self.file_imports:
            import_count = len(self.file_dependencies.get(file_path, set()))
            imported_by_count = len(self.reverse_dependencies.get(file_path, set()))
            
            # Root score: high if imports many, low if imported by many
            if imported_by_count == 0:
                root_score = import_count + 10  # Bonus for not being imported
            else:
                root_score = import_count / (imported_by_count + 1)
            
            root_scores[file_path] = root_score
        
        # Sort by score (highest first)
        return sorted(root_scores.keys(), key=lambda x: root_scores[x], reverse=True)
    
    def find_circular_dependencies(self) -> List[List[str]]:
        """Find circular dependencies using DFS."""
        visited = set()
        rec_stack = set()
        cycles = []
        
        def dfs(file_path: str, path: List[str]) -> bool:
            if file_path in rec_stack:
                # Found a cycle
                cycle_start = path.index(file_path)
                cycle = path[cycle_start:] + [file_path]
                cycles.append(cycle)
                return True
            
            if file_path in visited:
                return False
            
            visited.add(file_path)
            rec_stack.add(file_path)
            
            for dep_file in self.file_dependencies.get(file_path, set()):
                if dfs(dep_file, path + [file_path]):
                    pass  # Continue to find all cycles
            
            rec_stack.remove(file_path)
            return False
        
        for file_path in self.file_imports:
            if file_path not in visited:
                dfs(file_path, [])
        
        return cycles
    
    def analyze_duplicates(self) -> Dict[str, Dict[str, any]]:
        """Analyze duplicated files and their migration complexity."""
        duplicate_analysis = {}
        
        for old_path, new_path in self.duplicate_mappings.items():
            old_files = list(self.root_dir.glob(f"{old_path}**/*.py"))
            new_files = list(self.root_dir.glob(f"{new_path}**/*.py"))
            
            analysis = {
                'old_files': [str(f.relative_to(self.root_dir)) for f in old_files],
                'new_files': [str(f.relative_to(self.root_dir)) for f in new_files],
                'migration_complexity': 0,
                'dependencies': set(),
                'dependents': set(),
                'leaf_candidates': [],
                'root_candidates': []
            }
            
            # Analyze each old file
            for old_file in old_files:
                old_rel_path = str(old_file.relative_to(self.root_dir))
                
                # Get dependencies and dependents
                deps = self.file_dependencies.get(old_rel_path, set())
                dependents = self.reverse_dependencies.get(old_rel_path, set())
                
                analysis['dependencies'].update(deps)
                analysis['dependents'].update(dependents)
                
                # Calculate complexity score
                complexity = len(deps) + len(dependents) * 2  # Dependents are more complex
                analysis['migration_complexity'] += complexity
                
                # Check if it's a leaf or root candidate
                if len(deps) <= 2:
                    analysis['leaf_candidates'].append(old_rel_path)
                if len(dependents) <= 1:
                    analysis['root_candidates'].append(old_rel_path)
            
            # Convert sets to lists for JSON serialization
            analysis['dependencies'] = list(analysis['dependencies'])
            analysis['dependents'] = list(analysis['dependents'])
            
            duplicate_analysis[old_path] = analysis
        
        return duplicate_analysis
    
    def generate_migration_order(self) -> List[Dict[str, any]]:
        """Generate optimal migration order."""
        duplicate_analysis = self.analyze_duplicates()
        
        # Sort by migration complexity (lowest first)
        sorted_duplicates = sorted(
            duplicate_analysis.items(),
            key=lambda x: x[1]['migration_complexity']
        )
        
        migration_order = []
        for old_path, analysis in sorted_duplicates:
            
            # Determine migration strategy
            strategy = "simple"
            if analysis['migration_complexity'] > 20:
                strategy = "complex"
            elif analysis['migration_complexity'] > 10:
                strategy = "moderate"
            
            # Determine risk level
            risk = "low"
            if len(analysis['dependents']) > 10:
                risk = "high"
            elif len(analysis['dependents']) > 5:
                risk = "medium"
            
            migration_order.append({
                'old_path': old_path,
                'new_path': self.duplicate_mappings[old_path],
                'strategy': strategy,
                'risk': risk,
                'complexity_score': analysis['migration_complexity'],
                'dependent_count': len(analysis['dependents']),
                'dependency_count': len(analysis['dependencies']),
                'leaf_files': analysis['leaf_candidates'],
                'root_files': analysis['root_candidates']
            })
        
        return migration_order
    
    def generate_report(self) -> Dict[str, any]:
        """Generate comprehensive dependency analysis report."""
        leaf_nodes = self.find_leaf_nodes()[:20]  # Top 20
        root_nodes = self.find_root_nodes()[:20]  # Top 20
        circular_deps = self.find_circular_dependencies()
        migration_order = self.generate_migration_order()
        
        # Test file analysis
        test_files = [f for f in self.file_imports if f.startswith('tests/')]
        test_dependencies = {}
        for test_file in test_files:
            deps = self.file_dependencies.get(test_file, set())
            test_dependencies[test_file] = list(deps)
        
        # Critical path analysis
        critical_analysis = {}
        for critical_file, importance in self.critical_files.items():
            if critical_file in self.file_imports:
                deps = self.file_dependencies.get(critical_file, set())
                dependents = self.reverse_dependencies.get(critical_file, set())
                critical_analysis[critical_file] = {
                    'importance': importance,
                    'dependencies': list(deps),
                    'dependents': list(dependents),
                    'risk_score': len(dependents) * importance / 100
                }
        
        return {
            'summary': {
                'total_files': len(self.file_imports),
                'total_imports': sum(len(imports) for imports in self.file_imports.values()),
                'circular_dependencies': len(circular_deps),
                'duplicate_paths': len(self.duplicate_mappings)
            },
            'leaf_nodes': leaf_nodes,
            'root_nodes': root_nodes,
            'circular_dependencies': circular_deps,
            'migration_order': migration_order,
            'test_dependencies': test_dependencies,
            'critical_path_analysis': critical_analysis,
            'duplicate_mappings': self.duplicate_mappings
        }

def main():
    """Main function to run dependency analysis."""
    # Auto-detect the project root directory (go up from scripts/validation/ to project root)
    script_dir = Path(__file__).parent.parent.parent.absolute()
    analyzer = DependencyAnalyzer(str(script_dir))
    
    print("Starting comprehensive dependency analysis...")
    analyzer.build_dependency_graph()
    
    print("Generating analysis report...")
    report = analyzer.generate_report()
    
    # Ensure reports directory exists
    reports_dir = script_dir / "reports"
    reports_dir.mkdir(exist_ok=True)
    
    # Save detailed report to reports directory
    report_file = reports_dir / 'dependency_analysis_report.json'
    with open(report_file, 'w') as f:
        json.dump(report, f, indent=2)
    
    # Print summary
    print("\n" + "="*80)
    print("DEPENDENCY ANALYSIS SUMMARY")
    print("="*80)
    
    print(f"\nTotal Files Analyzed: {report['summary']['total_files']}")
    print(f"Total Import Statements: {report['summary']['total_imports']}")
    print(f"Circular Dependencies Found: {report['summary']['circular_dependencies']}")
    print(f"Duplicate Path Mappings: {report['summary']['duplicate_paths']}")
    
    print("\n" + "-"*60)
    print("MIGRATION ORDER (Lowest Risk First)")
    print("-"*60)
    
    for i, migration in enumerate(report['migration_order'], 1):
        print(f"{i}. {migration['old_path']} -> {migration['new_path']}")
        print(f"   Strategy: {migration['strategy']}, Risk: {migration['risk']}")
        print(f"   Complexity: {migration['complexity_score']}, Dependents: {migration['dependent_count']}")
        if migration['leaf_files']:
            print(f"   Leaf files: {', '.join(migration['leaf_files'][:3])}{'...' if len(migration['leaf_files']) > 3 else ''}")
        print()
    
    print("\n" + "-"*60)
    print("TOP LEAF NODES (Safe to migrate first)")
    print("-"*60)
    for leaf in report['leaf_nodes'][:10]:
        deps = len(analyzer.file_dependencies.get(leaf, set()))
        dependents = len(analyzer.reverse_dependencies.get(leaf, set()))
        print(f"• {leaf} (imports: {deps}, imported by: {dependents})")
    print("\n" + "-"*60)
    print("CIRCULAR DEPENDENCIES (Need careful handling)")
    print("-"*60)
    for i, cycle in enumerate(report['circular_dependencies'][:5], 1):
        print(f"{i}. {' -> '.join(cycle)}")
    
    print("\n" + "-"*60)
    print("CRITICAL PATH ANALYSIS")
    print("-"*60)
    critical_sorted = sorted(
        report['critical_path_analysis'].items(), 
        key=lambda x: x[1]['risk_score'], 
        reverse=True
    )
    for file_path, analysis in critical_sorted[:5]:
        print(f"• {file_path} (Risk Score: {analysis['risk_score']:.1f})")
        print(f"  Dependencies: {len(analysis['dependencies'])}, Dependents: {len(analysis['dependents'])}")
    
    print(f"\nDetailed report saved to: {report_file}")
    print("="*80)

if __name__ == "__main__":
    main()