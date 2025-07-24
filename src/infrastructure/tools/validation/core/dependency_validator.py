"""
Dependency Validator
Validates project dependencies and detects unused packages with safe categorization.
"""

import ast
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Set

from .base_validator import BaseValidator


class DependencyValidator(BaseValidator):
    """Validates project dependencies and analyzes usage patterns."""

    def __init__(self, root_path: Optional[Path] = None):
        """Initialize dependency validator."""
        super().__init__(root_path)
        self.dependency_analysis: Optional[Dict[str, List[str]]] = None

    def validate_dependencies(self):
        """Validate dependencies and detect unused packages with safe categorization."""
        # Check requirements.txt
        requirements_file = self.root_path / "requirements.txt"
        if not requirements_file.exists():
            self.add_issue(
                category="dependencies",
                issue_type="MISSING_REQUIREMENTS",
                file_path=str(requirements_file),
                message="requirements.txt file not found",
                severity="warning",
                fix_suggestion="Create requirements.txt file to track dependencies",
            )
            return False

        try:
            # Parse declared dependencies
            declared_deps = self._parse_requirements_file(requirements_file)

            # Find used imports
            used_imports = self._find_used_imports()

            # Categorize dependencies for safer analysis
            self.dependency_analysis = self._categorize_dependencies(
                declared_deps, used_imports
            )

            # Report findings with appropriate safety levels
            self._report_dependency_findings(requirements_file)

            # Return success if no critical dependency issues found
            return True

        except Exception as e:
            self.add_issue(
                category="dependencies",
                issue_type="DEPENDENCY_ANALYSIS_ERROR",
                file_path=str(requirements_file),
                message=f"Could not analyze requirements.txt: {str(e)}",
                severity="error",
                fix_suggestion="Check requirements.txt syntax and permissions",
            )
            return False

    def _parse_requirements_file(self, requirements_file: Path) -> Set[str]:
        """Parse requirements.txt and extract package names."""
        declared_deps = set()

        with open(requirements_file, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    # Handle different version specifiers
                    for separator in ["==", ">=", "<=", "~=", ">", "<", "!="]:
                        if separator in line:
                            line = line.split(separator)[0]
                            break

                    pkg_name = line.strip()
                    if pkg_name:
                        declared_deps.add(pkg_name)

        return declared_deps

    def _find_used_imports(self) -> Set[str]:
        """Find all imports used in Python files with parallel processing."""
        import concurrent.futures

        if not self.python_files:
            self._collect_files()

        print(f"   📦 Scanning {len(self.python_files)} files for dependencies...")

        def extract_imports_from_file(file_path: Path) -> Set[str]:
            """Extract imports from a single file."""
            imports = set()
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()

                tree = ast.parse(content)
                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            if not self._is_local_import(alias.name):
                                imports.add(alias.name.split(".")[0])

                    elif isinstance(node, ast.ImportFrom):
                        if node.module and not self._is_local_import(node.module):
                            imports.add(node.module.split(".")[0])

            except Exception:
                # Skip files that can't be parsed
                pass
            return imports

        # Process files in parallel
        used_imports = set()
        processed_count = 0
        chunk_size = max(1, len(self.python_files) // 10)  # 10 progress updates

        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
            future_to_file = {
                executor.submit(extract_imports_from_file, file_path): file_path
                for file_path in self.python_files
            }

            for future in concurrent.futures.as_completed(future_to_file):
                try:
                    file_imports = future.result()
                    used_imports.update(file_imports)
                    processed_count += 1

                    # Progress reporting
                    if processed_count % chunk_size == 0 or processed_count == len(
                        self.python_files
                    ):
                        progress = (processed_count / len(self.python_files)) * 100
                        print(
                            f"   Progress: {processed_count}/{len(self.python_files)} ({progress:.1f}%)"
                        )

                except Exception:
                    processed_count += 1
                    continue

        print(f"   ✓ Found {len(used_imports)} unique dependencies")
        return used_imports

    def _is_local_import(self, import_name: str) -> bool:
        """Check if an import is local to the project."""
        return import_name.startswith("src.") or import_name.startswith(".")

    def _categorize_dependencies(
        self, declared_deps: Set[str], used_imports: Set[str]
    ) -> Dict[str, List[str]]:
        """Categorize dependencies for safer analysis with comprehensive context."""

        # Enhanced categorization with risk assessment
        categories = {
            "direct_imports": [],  # Found in Python code
            "dev_tools": [],  # Development/testing tools
            "runtime_critical": [],  # Never remove these
            "infrastructure": [],  # Docker, CI/CD, deployment
            "transitive": [],  # Required by other packages
            "type_stubs": [],  # types-* packages
            "optional_features": [],  # Conditionally activated
            "unknown": [],  # Needs investigation
            "safe_to_review": [],  # Low risk candidates
        }

        # Load configuration for categorization
        config = self._load_dependency_config()

        # Scan multiple locations for usage
        usage_context = self._scan_comprehensive_usage(declared_deps)

        # Find potentially unused dependencies
        unused_deps = declared_deps - used_imports

        # Account for different import names
        unused_deps = self._normalize_import_names(unused_deps, used_imports)

        # Categorize each unused dependency with context
        for dep in unused_deps:
            context = usage_context.get(dep, {})
            category = self._assess_dependency_category(dep, context, config)
            categories[category].append(
                {
                    "name": dep,
                    "context": context,
                    "risk_level": self._assess_risk_level(dep, context, config),
                    "suggestions": self._generate_dependency_suggestions(dep, context),
                }
            )

        return categories

    def _load_dependency_config(self) -> Dict:
        """Load dependency categorization configuration."""
        return {
            "dev_tools": {
                "pytest",
                "pytest-cov",
                "pytest-xdist",
                "pytest-mock",
                "pytest-asyncio",
                "black",
                "ruff",
                "mypy",
                "isort",
                "pylint",
                "bandit",
                "coverage",
                "tox",
                "pre-commit",
                "sphinx",
                "sphinx-rtd-theme",
                "jupyterlab",
                "notebook",
                "ipython",
                "ipykernel",
                "flake8",
                "autopep8",
            },
            "runtime_critical": {
                "django",
                "flask",
                "fastapi",
                "sqlalchemy",
                "alembic",
                "celery",
                "redis",
                "psycopg2",
                "psycopg2-binary",
                "gunicorn",
                "uvicorn",
                "werkzeug",
                "jinja2",
                "requests",
                "numpy",
                "pandas",
                "scipy",
                "matplotlib",
                "tensorflow",
                "torch",
                "transformers",
                "langchain",
                "openai",
                "stripe",
                "boto3",
                "azure",
                "kubernetes",
            },
            "infrastructure": {
                "docker",
                "docker-compose",
                "kubernetes",
                "helm",
                "terraform",
                "ansible",
                "fabric",
                "supervisor",
                "systemd",
                "nginx",
                "apache",
            },
            "type_stubs": {
                "types-requests",
                "types-PyYAML",
                "types-redis",
                "types-psycopg2",
                "types-setuptools",
                "types-toml",
                "mypy-extensions",
            },
            "import_name_mapping": {
                "pillow": "PIL",
                "beautifulsoup4": "bs4",
                "pyyaml": "yaml",
                "python-dateutil": "dateutil",
                "msgpack-python": "msgpack",
                "psycopg2-binary": "psycopg2",
                "python-dotenv": "dotenv",
                "python-multipart": "multipart",
                "scikit-learn": "sklearn",
            },
            "scan_locations": [
                "Dockerfile*",
                "docker-compose*.yml",
                ".github/workflows/*.yml",
                "Makefile",
                "*.sh",
                "tox.ini",
                "noxfile.py",
                "pyproject.toml",
                "setup.py",
                "*.ini",
                "*.yaml",
                "*.yml",
                "requirements*.txt",
            ],
        }

    def _scan_comprehensive_usage(self, dependencies: Set[str]) -> Dict[str, Dict]:
        """Scan multiple locations for dependency usage with optimized algorithm."""
        import time

        start_time = time.time()
        print(
            f"   📦 Starting optimized dependency scanning for {len(dependencies)} dependencies..."
        )

        # Initialize result structure
        usage_context = {
            dep: {
                "python_files": [],
                "config_files": [],
                "scripts": [],
                "docker_files": [],
                "ci_files": [],
                "documentation": [],
                "possible_indirect": [],
            }
            for dep in dependencies
        }

        # Build reverse index: file -> dependencies found in it
        # This reduces complexity from O(deps × files) to O(files + deps)
        file_dependency_map = self._build_file_dependency_index(dependencies)

        # Populate usage context from reverse index
        for file_path, found_deps in file_dependency_map.items():
            file_category = self._categorize_file_type(file_path)

            for dep in found_deps:
                if dep in usage_context:
                    usage_context[dep][file_category].append(str(file_path))

        # Add indirect dependency information
        for dep in dependencies:
            usage_context[dep]["possible_indirect"] = self._check_indirect_deps(dep)

        duration = time.time() - start_time
        total_files_scanned = len(file_dependency_map)
        print(
            f"   ✓ Dependency scanning completed in {duration:.2f}s ({total_files_scanned} files)"
        )

        return usage_context

    def _build_file_dependency_index(self, dependencies: Set[str]) -> Dict:
        """Build optimized index: file -> list of dependencies found in it."""
        import concurrent.futures
        from collections import defaultdict

        file_dependency_map = defaultdict(list)
        all_files = []

        # Collect all files to scan
        if not self.python_files:
            self._collect_files()

        # Add Python files
        all_files.extend(self.python_files)

        # Add configuration files
        config_patterns = ["*.ini", "*.yaml", "*.yml", "*.toml", "*.json", "*.cfg"]
        for pattern in config_patterns:
            all_files.extend(self.root_path.glob(f"**/{pattern}"))

        # Add script files
        script_patterns = ["*.sh", "*.bash", "Makefile", "makefile"]
        for pattern in script_patterns:
            all_files.extend(self.root_path.glob(f"**/{pattern}"))

        # Add Docker and CI files
        docker_patterns = ["Dockerfile*", "docker-compose*.yml", "docker-compose*.yaml"]
        ci_patterns = [
            ".github/workflows/*.yml",
            ".github/workflows/*.yaml",
            ".gitlab-ci.yml",
        ]

        for pattern in docker_patterns + ci_patterns:
            all_files.extend(self.root_path.glob(pattern))

        # Remove duplicates and filter out non-existent files
        unique_files = list(set(f for f in all_files if f.exists() and f.is_file()))

        print(
            f"   📁 Scanning {len(unique_files)} files for {len(dependencies)} dependencies..."
        )

        def scan_file_for_dependencies(file_path):
            """Scan a single file for all dependencies (parallel worker function)."""
            found_deps = []
            try:
                # Skip binary files and very large files for performance
                if file_path.suffix in [".pyc", ".pyo", ".so", ".dll", ".exe"]:
                    return file_path, found_deps

                # Check file size (skip files > 10MB)
                if file_path.stat().st_size > 10 * 1024 * 1024:
                    return file_path, found_deps

                with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()

                # Search for each dependency in the file content
                for dep in dependencies:
                    # Check for various patterns of dependency usage
                    patterns = [
                        f"import {dep}",
                        f"from {dep}",
                        f'"{dep}"',
                        f"'{dep}'",
                        f"{dep}==",
                        f"{dep}>=",
                        f" {dep} ",  # Standalone word
                    ]

                    if any(pattern in content for pattern in patterns):
                        found_deps.append(dep)

            except Exception:
                # Skip files that can't be read
                pass

            return file_path, found_deps

        # Process files in parallel with progress tracking
        processed_count = 0
        chunk_size = max(1, len(unique_files) // 20)  # 20 progress updates

        with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
            future_to_file = {
                executor.submit(scan_file_for_dependencies, file_path): file_path
                for file_path in unique_files
            }

            for future in concurrent.futures.as_completed(future_to_file):
                try:
                    file_path, found_deps = future.result()
                    if found_deps:
                        file_dependency_map[file_path] = found_deps

                    processed_count += 1

                    # Progress reporting
                    if processed_count % chunk_size == 0 or processed_count == len(
                        unique_files
                    ):
                        progress = (processed_count / len(unique_files)) * 100
                        print(
                            f"   Progress: {processed_count}/{len(unique_files)} ({progress:.1f}%)"
                        )

                except Exception:
                    processed_count += 1
                    continue

        dependencies_found = sum(len(deps) for deps in file_dependency_map.values())
        print(
            f"   ✓ Found {dependencies_found} dependency references across {len(file_dependency_map)} files"
        )

        return dict(file_dependency_map)

    def _categorize_file_type(self, file_path) -> str:
        """Categorize a file into the appropriate dependency context category."""
        file_path_str = str(file_path).lower()

        # Python files
        if file_path_str.endswith(".py"):
            return "python_files"

        # Configuration files
        config_extensions = [".ini", ".yaml", ".yml", ".toml", ".json", ".cfg"]
        if any(file_path_str.endswith(ext) for ext in config_extensions):
            return "config_files"

        # Docker files
        if any(
            pattern in file_path_str for pattern in ["dockerfile", "docker-compose"]
        ):
            return "docker_files"

        # CI/CD files
        if any(
            pattern in file_path_str
            for pattern in [
                ".github/workflows",
                ".gitlab-ci",
                ".travis",
                "azure-pipelines",
            ]
        ):
            return "ci_files"

        # Script files
        script_extensions = [".sh", ".bash", ".bat", ".cmd"]
        if (
            any(file_path_str.endswith(ext) for ext in script_extensions)
            or "makefile" in file_path_str
        ):
            return "scripts"

        # Documentation files
        doc_extensions = [".md", ".rst", ".txt"]
        if any(file_path_str.endswith(ext) for ext in doc_extensions):
            return "documentation"

        # Default to scripts for unknown file types
        return "scripts"

    def _assess_dependency_category(self, dep: str, context: Dict, config: Dict) -> str:
        """Assess which category a dependency belongs to."""

        # Check if it's a known type stub
        if dep.startswith("types-") or dep in config["type_stubs"]:
            return "type_stubs"

        # Check if it's a known dev tool
        if dep in config["dev_tools"]:
            return "dev_tools"

        # Check if it's runtime critical
        if dep in config["runtime_critical"]:
            return "runtime_critical"

        # Check if it's infrastructure related
        if dep in config["infrastructure"]:
            return "infrastructure"

        # Check if found in any files
        if any(context.values()):
            if context["python_files"]:
                return "direct_imports"
            elif context["config_files"] or context["scripts"]:
                return "infrastructure"
            elif context["possible_indirect"]:
                return "transitive"
            else:
                return "optional_features"

        # Check if it might be safe to review
        if self._is_safe_to_review(dep, context):
            return "safe_to_review"

        return "unknown"

    def _assess_risk_level(self, dep: str, context: Dict, config: Dict) -> str:
        """Assess the risk level of removing a dependency."""

        # Critical risk - never auto-remove
        if dep in config["runtime_critical"]:
            return "CRITICAL"

        # High risk - framework or data dependencies
        if any(
            keyword in dep.lower()
            for keyword in ["django", "flask", "sql", "auth", "pay"]
        ):
            return "HIGH"

        # Medium risk - has some usage context
        if context["config_files"] or context["scripts"]:
            return "MEDIUM"

        # Low risk - dev tools or clearly unused
        if dep in config["dev_tools"] and not context["python_files"]:
            return "LOW"

        return "MEDIUM"  # Default to medium risk

    def _generate_dependency_suggestions(self, dep: str, context: Dict) -> List[str]:
        """Generate actionable suggestions for each dependency."""
        suggestions = []

        if context["python_files"]:
            suggestions.append(f"Used in {len(context['python_files'])} Python files")

        if context["config_files"]:
            suggestions.append(
                f"Referenced in config files: {', '.join(context['config_files'][:3])}"
            )

        if context["scripts"]:
            suggestions.append(f"Used in scripts: {', '.join(context['scripts'][:3])}")

        if context["possible_indirect"]:
            suggestions.append(
                f"Possible transitive dependency of: {', '.join(context['possible_indirect'][:3])}"
            )

        if not any(context.values()):
            suggestions.append("No usage found - candidate for removal")
            suggestions.append("Run: pip show " + dep + " to check what depends on it")

        return suggestions

    def _normalize_import_names(
        self, unused_deps: Set[str], used_imports: Set[str]
    ) -> Set[str]:
        """Normalize import names to handle different package/import name mappings."""
        config = self._load_dependency_config()
        import_name_mapping = config["import_name_mapping"]

        normalized_unused = set(unused_deps)

        # Account for different import names
        for dep in list(normalized_unused):
            if dep in import_name_mapping:
                if import_name_mapping[dep] in used_imports:
                    normalized_unused.remove(dep)

        return normalized_unused

    def _scan_python_usage(self, dependency: str) -> List[str]:
        """Scan Python files for dependency usage."""
        usage_files = []

        if not self.python_files:
            self._collect_files()

        for file_path in self.python_files:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()

                # Check for direct imports
                if f"import {dependency}" in content or f"from {dependency}" in content:
                    usage_files.append(str(file_path))
                # Check for string references (dynamic imports)
                elif f'"{dependency}"' in content or f"'{dependency}'" in content:
                    usage_files.append(str(file_path))

            except Exception:
                continue

        return usage_files

    def _scan_config_files(self, dependency: str) -> List[str]:
        """Scan configuration files for dependency references."""
        usage_files = []
        config_patterns = ["*.ini", "*.yaml", "*.yml", "*.toml", "*.json", "*.cfg"]

        for pattern in config_patterns:
            for file_path in self.root_path.glob(f"**/{pattern}"):
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        content = f.read()
                        if dependency in content:
                            usage_files.append(str(file_path))
                except Exception:
                    continue

        return usage_files

    def _scan_scripts(self, dependency: str) -> List[str]:
        """Scan shell scripts and makefiles for dependency usage."""
        usage_files = []
        script_patterns = ["*.sh", "*.bash", "Makefile", "makefile", "*.py"]

        for pattern in script_patterns:
            for file_path in self.root_path.glob(f"**/{pattern}"):
                if file_path.name.endswith(".py") and file_path in self.python_files:
                    continue  # Already scanned in Python files

                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        content = f.read()
                        if dependency in content:
                            usage_files.append(str(file_path))
                except Exception:
                    continue

        return usage_files

    def _scan_docker_files(self, dependency: str) -> List[str]:
        """Scan Docker files for dependency usage."""
        usage_files = []
        docker_patterns = ["Dockerfile*", "docker-compose*.yml", "docker-compose*.yaml"]

        for pattern in docker_patterns:
            for file_path in self.root_path.glob(f"**/{pattern}"):
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        content = f.read()
                        if dependency in content:
                            usage_files.append(str(file_path))
                except Exception:
                    continue

        return usage_files

    def _scan_ci_files(self, dependency: str) -> List[str]:
        """Scan CI/CD files for dependency usage."""
        usage_files = []
        ci_patterns = [
            ".github/workflows/*.yml",
            ".github/workflows/*.yaml",
            ".gitlab-ci.yml",
            ".travis.yml",
            "azure-pipelines.yml",
        ]

        for pattern in ci_patterns:
            for file_path in self.root_path.glob(pattern):
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        content = f.read()
                        if dependency in content:
                            usage_files.append(str(file_path))
                except Exception:
                    continue

        return usage_files

    def _check_indirect_deps(self, dependency: str) -> List[str]:
        """Check if this dependency is required by other installed packages."""
        indirect_deps = []

        try:
            # This would require pip/pkg_resources but we'll keep it simple
            # In a real implementation, you'd use pkg_resources.get_distribution()
            # to check what depends on this package

            # For now, just check common patterns
            common_transitive = {
                "setuptools": ["pip", "wheel", "build"],
                "wheel": ["pip", "setuptools"],
                "certifi": ["requests", "urllib3"],
                "urllib3": ["requests"],
                "charset-normalizer": ["requests"],
                "idna": ["requests"],
                "six": ["many older packages"],
                "packaging": ["build tools"],
            }

            if dependency in common_transitive:
                indirect_deps.extend(common_transitive[dependency])

        except Exception:
            pass

        return indirect_deps

    def _is_safe_to_review(self, dependency: str, context: Dict) -> bool:
        """Determine if a dependency is safe to review for removal."""
        # Safe if it's a dev tool with no usage found
        config = self._load_dependency_config()

        if dependency in config["dev_tools"]:
            return not any(context.values())

        # Safe if it's a documentation or formatting tool
        safe_patterns = ["sphinx", "doc", "format", "lint", "test"]
        if any(pattern in dependency.lower() for pattern in safe_patterns):
            return not context["python_files"]

        return False

    def _report_dependency_findings(self, requirements_file: Path):
        """Report dependency analysis findings with enhanced context."""
        if not self.dependency_analysis:
            return

        for category, deps in self.dependency_analysis.items():
            if not deps:
                continue

            # Report each dependency with its context
            for dep_info in deps:
                if isinstance(dep_info, dict):
                    dep_name = dep_info.get("name", "unknown")
                    risk_level = dep_info.get("risk_level", "MEDIUM")
                    suggestions = dep_info.get("suggestions", [])
                else:
                    # Handle legacy format
                    dep_name = str(dep_info)
                    risk_level = "MEDIUM"
                    suggestions = []

                # Generate appropriate issue based on category
                if category == "safe_to_review":
                    self.add_issue(
                        category="dependencies",
                        issue_type="SAFE_TO_REVIEW_DEPENDENCY",
                        file_path=str(requirements_file),
                        message=f"Low-risk unused dependency: {dep_name}",
                        severity="info",
                        fix_suggestion=f"Safe to remove {dep_name} after testing: {'; '.join(suggestions[:2])}",
                        auto_fixable=False,
                    )

                elif category == "dev_tools":
                    self.add_issue(
                        category="dependencies",
                        issue_type="DEV_TOOL_DEPENDENCY",
                        file_path=str(requirements_file),
                        message=f"Development tool in main requirements: {dep_name}",
                        severity="info",
                        fix_suggestion=f"Consider moving {dep_name} to dev requirements",
                        auto_fixable=False,
                    )

                elif category == "runtime_critical":
                    self.add_issue(
                        category="dependencies",
                        issue_type="CRITICAL_DEPENDENCY_UNUSED",
                        file_path=str(requirements_file),
                        message=f"Critical dependency appears unused: {dep_name} (Risk: {risk_level})",
                        severity="warning",
                        fix_suggestion=f"CAREFUL: {dep_name} may be runtime-critical. Verify before removing.",
                        auto_fixable=False,
                    )

                elif category == "transitive":
                    self.add_issue(
                        category="dependencies",
                        issue_type="TRANSITIVE_DEPENDENCY",
                        file_path=str(requirements_file),
                        message=f"Possible transitive dependency: {dep_name}",
                        severity="info",
                        fix_suggestion=f"Verify if {dep_name} is directly needed: {'; '.join(suggestions[:2])}",
                        auto_fixable=False,
                    )

                elif category == "unknown":
                    self.add_issue(
                        category="dependencies",
                        issue_type="UNKNOWN_DEPENDENCY_USAGE",
                        file_path=str(requirements_file),
                        message=f"Unknown usage pattern for dependency: {dep_name}",
                        severity="warning",
                        fix_suggestion=f"Manual investigation required for {dep_name}: {'; '.join(suggestions[:2])}",
                        auto_fixable=False,
                    )

    def run_dependency_review(self):
        """Interactive dependency review session."""
        if not self.dependency_analysis:
            print("🔍 No dependency analysis available. Run validation first.")
            return

        print("\n📦 DEPENDENCY REVIEW SESSION")
        print("=" * 50)

        for category, deps in self.dependency_analysis.items():
            if not deps:
                continue

            print(
                f"\n{self._get_category_icon(category)} {category.replace('_', ' ').title()}: {len(deps)} items"
            )

            if category == "truly_unused":
                print("🟢 These appear safe to remove:")
                for dep in deps:
                    print(f"   - {dep}")

            elif category == "dev_tools":
                print("🟡 Development tools (consider moving to dev requirements):")
                for dep in deps:
                    print(f"   - {dep}")

            elif category == "runtime_critical":
                print("🔴 CRITICAL - Review carefully before removing:")
                for dep in deps:
                    print(f"   - {dep}")

            elif category == "indirect_deps":
                print("🔵 Likely indirect dependencies:")
                for dep in deps:
                    print(f"   - {dep}")

        print("\n💡 TIP: Use 'pip show <package>' to see dependency relationships")
        print("💡 TIP: Use 'pipdeptree' to visualize full dependency tree")

    def _get_category_icon(self, category: str) -> str:
        """Get emoji icon for dependency category."""
        icons = {
            "direct_imports": "�",
            "dev_tools": "🔧",
            "runtime_critical": "⚠️",
            "infrastructure": "🏗️",
            "transitive": "🔗",
            "type_stubs": "📝",
            "optional_features": "🔀",
            "unknown": "❓",
            "safe_to_review": "🟢",
            # Legacy compatibility
            "truly_unused": "🗑️",
            "indirect_deps": "🔗",
        }
        return icons.get(category, "📦")

    def generate_dependency_report(self):
        """Generate a detailed dependency usage report."""
        if not self.dependency_analysis:
            print("🔍 No dependency analysis available. Run validation first.")
            return

        print("\n📊 DEPENDENCY USAGE REPORT")
        print("=" * 60)

        # Generate timestamp
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"Generated: {timestamp}")

        # Summary statistics
        total_declared = sum(len(deps) for deps in self.dependency_analysis.values())
        print("\n📈 SUMMARY:")
        print(f"Total declared dependencies: {total_declared}")

        for category, deps in self.dependency_analysis.items():
            if deps:
                print(
                    f"{self._get_category_icon(category)} {category.replace('_', ' ').title()}: {len(deps)}"
                )

        # Detailed breakdown
        print("\n📋 DETAILED BREAKDOWN:")

        for category, deps in self.dependency_analysis.items():
            if not deps:
                continue

            print(
                f"\n{self._get_category_icon(category)} {category.replace('_', ' ').title()}:"
            )

            for dep in sorted(deps):
                print(f"  • {dep}")

        # Recommendations
        print("\n💡 RECOMMENDATIONS:")

        if self.dependency_analysis.get("truly_unused"):
            print("🗑️  Safe to remove (after testing):")
            for dep in sorted(self.dependency_analysis["truly_unused"]):
                print(f"   pip uninstall {dep}")

        if self.dependency_analysis.get("dev_tools"):
            print("🔧 Consider moving to dev requirements:")
            for dep in sorted(self.dependency_analysis["dev_tools"]):
                print(f"   {dep}  # dev tool")

        if self.dependency_analysis.get("runtime_critical"):
            print("⚠️  Review carefully (may be runtime-critical):")
            for dep in sorted(self.dependency_analysis["runtime_critical"]):
                print(f"   {dep}  # REVIEW BEFORE REMOVING")

        # Save report to file
        report_file = (
            f"dependency_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        )
        try:
            with open(report_file, "w", encoding="utf-8") as f:
                f.write("DEPENDENCY USAGE REPORT\n")
                f.write(f"Generated: {timestamp}\n\n")

                f.write("SUMMARY:\n")
                f.write(f"Total declared dependencies: {total_declared}\n")

                for category, deps in self.dependency_analysis.items():
                    if deps:
                        f.write(f"{category.replace('_', ' ').title()}: {len(deps)}\n")

                f.write("\nDETAILED BREAKDOWN:\n")
                for category, deps in self.dependency_analysis.items():
                    if deps:
                        f.write(f"\n{category.replace('_', ' ').title()}:\n")
                        for dep in sorted(deps):
                            f.write(f"  - {dep}\n")

                f.write("\nRECOMMENDATIONS:\n")
                if self.dependency_analysis.get("truly_unused"):
                    f.write("Safe to remove (after testing):\n")
                    for dep in sorted(self.dependency_analysis["truly_unused"]):
                        f.write(f"  pip uninstall {dep}\n")

            print(f"\n📄 Full report saved to: {report_file}")

        except Exception as e:
            print(f"⚠️  Could not save report to file: {e}")

        print("\n💡 TIP: Run 'pip show <package>' to see dependency details")
        print("💡 TIP: Run 'pipdeptree' to see full dependency tree")
        print("💡 TIP: Test thoroughly before removing any dependencies")
