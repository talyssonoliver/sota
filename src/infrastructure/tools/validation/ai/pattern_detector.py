
from src.infrastructure.utils.common_imports import (
    Path,
    hashlib,
    json,
    os,
    re,
    time
)
"""
AI Pattern Detector
Advanced pattern detection using AI-assisted analysis for code quality and consistency.
"""

import ast
import difflib
from collections import defaultdict
from typing import Any, Dict, List, Optional, Set, Tuple

from ..core.base_validator import BaseValidator

# Security pattern constants to avoid duplication
EVAL_PATTERN = r"eval\s*\("
EVAL_MESSAGE = "Use of eval() is dangerous"
EXEC_PATTERN = r"exec\s*\("
EXEC_MESSAGE = "Use of exec() is dangerous"
OS_SYSTEM_PATTERN = r"os\.system\s*\("
OS_SYSTEM_MESSAGE = "Use of os.system() is dangerous"


class AIPatternDetector(BaseValidator):
    """AI-assisted pattern detection for advanced code analysis."""

    def __init__(self, root_path: Optional[Path] = None):
        """Initialize AI pattern detector."""
        super().__init__(root_path)
        self._load_ai_config()
        self.code_patterns: Dict[str, List[str]] = defaultdict(list)
        self.duplicate_blocks: List[Tuple[str, str, float]] = []
        self.naming_inconsistencies: List[Dict] = []
        self.architectural_violations: List[Dict] = []

        # Add caching for performance
        self._ast_cache: Dict[str, ast.AST] = {}
        self._hash_cache: Dict[str, str] = {}
        self._file_mtime_cache: Dict[str, float] = {}
        self._cache_file = self.root_path / ".validation_cache" / "ai_patterns.json"

    def _load_ai_config(self) -> None:
        """Load AI-specific configuration and merge with base config."""
        config_path = (
            self.root_path
            / "src"
            / "infrastructure"
            / "tools"
            / "validation"
            / "config"
            / "ai_validation_config.json"
        )

        if config_path.exists():
            try:
                with open(config_path, "r") as f:
                    ai_config = json.load(f)
                    # Merge AI-specific config with base config
                    self.config.update(ai_config)
            except Exception:
                pass

        # Set AI-specific defaults if not loaded from config
        ai_defaults = {
            "duplicate_code_threshold": 0.8,
            "hallucinated_import_check": True,
            "circular_dependency_detection": True,
            "naming_consistency_check": True,
            "unused_code_detection": True,
            "security_pattern_scanning": True,
            "ai_pattern_detection": {
                "min_duplicate_lines": 5,
                "similarity_threshold": 0.85,
                "naming_pattern_threshold": 0.7,
            },
        }

        # Add AI defaults if not already present
        for key, value in ai_defaults.items():
            if key not in self.config:
                self.config[key] = value

    def analyze_patterns(self) -> bool:
        """Run AI-assisted pattern analysis with caching."""
        if not self.python_files:
            self._collect_files()

        print("🤖 AI Pattern Detection Analysis...")

        # Load cache for faster analysis
        self._load_cache()

        # Only analyze changed files
        changed_files = self._get_changed_files()
        if changed_files:
            print(
                f"   📝 Analyzing {len(changed_files)} changed files (cached: {len(self.python_files) - len(changed_files)})"
            )
        else:
            print("   ✓ All files cached, using previous analysis")
            # Still run lightweight checks even for cached files
            return self._run_lightweight_analysis()

        # Optimize analysis based on number of files
        total_files = len(self.python_files)
        analysis_mode = "full"

        if total_files > 500:
            analysis_mode = "sample"
            print(
                f"   ⚡ Large codebase detected ({total_files} files), using sampled analysis"
            )
        elif total_files > 200:
            analysis_mode = "optimized"
            print(
                f"   ⚡ Medium codebase detected ({total_files} files), using optimized analysis"
            )

        # Only analyze changed files for performance
        files_to_analyze = (
            changed_files if changed_files else self.python_files[:50]
        )  # Limit to 50 files max

        # Detect duplicate code patterns (optimized)
        self._detect_duplicate_code_optimized(files_to_analyze, analysis_mode)

        # Analyze naming consistency (lightweight)
        self._analyze_naming_consistency_optimized(files_to_analyze)

        # Check for hallucinated imports (lightweight)
        self._check_hallucinated_imports_optimized(files_to_analyze)

        # Skip heavy analysis for large codebases or if disabled
        if analysis_mode == "sample" or self.config.get("quick_mode", False):
            print("   ⚡ Skipping heavy analysis (performance mode)")
        else:
            # Security pattern analysis (optimized)
            self._analyze_security_patterns_optimized(files_to_analyze)

            # Code smell detection (optimized)
            self._detect_code_smells_optimized(files_to_analyze)

        # Save cache for next run
        self._save_cache()

        return not self.has_errors()

    def _run_lightweight_analysis(self) -> bool:
        """Run only lightweight analysis when all files are cached."""
        # Quick check for critical issues only
        critical_patterns = [
            (EVAL_PATTERN, EVAL_MESSAGE),
            (EXEC_PATTERN, EXEC_MESSAGE),
            (OS_SYSTEM_PATTERN, OS_SYSTEM_MESSAGE),
        ]

        # Sample only a few files for quick check
        sample_files = (
            self.python_files[:10] if len(self.python_files) > 10 else self.python_files
        )

        for file_path in sample_files:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()

                for pattern, message in critical_patterns:
                    if re.search(pattern, content):
                        self.add_issue(
                            category="ai_analysis",
                            issue_type="SECURITY_ISSUE",
                            file_path=str(file_path),
                            message=f"Critical security issue: {message}",
                            severity="error",
                            fix_suggestion=message,
                            auto_fixable=False,
                        )
            except Exception:
                continue

        return not self.has_errors()

    def _detect_duplicate_code(self):
        """Detect duplicate code blocks using similarity analysis with parallel processing."""
        import concurrent.futures

        threshold = self.config.get("duplicate_code_threshold", 0.8)
        min_lines = self.config.get("ai_pattern_detection", {}).get(
            "min_duplicate_lines", 5
        )

        print(
            f"   🔍 Analyzing {len(self.python_files)} files for duplicate code patterns..."
        )

        def process_file_for_blocks(file_path):
            """Process a single file to extract code blocks."""
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    lines = f.readlines()

                blocks = self._extract_code_blocks(lines)
                return [(file_path, block) for block in blocks]
            except Exception:
                return []

        # Collect all code blocks in parallel
        all_blocks = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
            future_to_file = {
                executor.submit(process_file_for_blocks, file_path): file_path
                for file_path in self.python_files
            }

            for future in concurrent.futures.as_completed(future_to_file):
                try:
                    blocks = future.result()
                    all_blocks.extend(blocks)
                except Exception:
                    continue

        print(f"   📊 Found {len(all_blocks)} code blocks to analyze")

        # Build hash map for duplicate detection
        code_blocks = {}
        duplicate_count = 0

        for file_path, block_info in all_blocks:
            block_hash = self._calculate_block_hash(block_info["content"])

            if block_hash in code_blocks:
                # Found potential duplicate
                original = code_blocks[block_hash]
                similarity = self._calculate_similarity(
                    original["content"], block_info["content"]
                )

                if similarity >= threshold and len(block_info["content"]) >= min_lines:
                    self.add_issue(
                        category="ai_analysis",
                        issue_type="CODE_SMELL",
                        file_path=str(file_path),
                        message=f"Duplicate code block detected (similarity: {similarity:.2%})",
                        line=block_info["line"],
                        severity="warning",
                        fix_suggestion=f"Consider extracting duplicate code into a shared function. Similar code found in {original['file']}:{original['line']}",
                        auto_fixable=False,
                    )

                    self.duplicate_blocks.append(
                        (
                            str(file_path),
                            str(original["file"]),
                            similarity,
                        )
                    )
                    duplicate_count += 1
            else:
                code_blocks[block_hash] = {
                    "file": file_path,
                    "line": block_info["line"],
                    "content": block_info["content"],
                }

        if duplicate_count > 0:
            print(f"   ⚠️  Found {duplicate_count} duplicate code blocks")

    def _extract_code_blocks(self, lines: List[str]) -> List[Dict]:
        """Extract meaningful code blocks from file."""
        blocks = []

        try:
            content = "".join(lines)
            tree = ast.parse(content)

            for node in ast.walk(tree):
                if isinstance(
                    node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)
                ):
                    start_line = node.lineno - 1
                    end_line = getattr(node, "end_lineno", start_line + 10) - 1

                    if end_line < len(lines):
                        block_content = lines[start_line:end_line]
                        blocks.append(
                            {
                                "type": type(node).__name__,
                                "name": node.name,
                                "line": node.lineno,
                                "content": block_content,
                            }
                        )
        except Exception:
            pass

        return blocks

    def _calculate_block_hash(self, content: List[str]) -> str:
        """Calculate hash for code block (ignoring whitespace and comments)."""
        # Normalize content by removing comments and extra whitespace
        normalized = []
        for line in content:
            line = line.strip()
            if line and not line.startswith("#"):
                # Remove inline comments
                if "#" in line:
                    line = line.split("#")[0].strip()
                normalized.append(line)

        # Create hash of normalized content
        content_str = "\n".join(normalized)
        return hashlib.sha256(content_str.encode()).hexdigest()

    def _calculate_similarity(self, content1: List[str], content2: List[str]) -> float:
        """Calculate similarity between two code blocks."""
        # Convert to strings and normalize
        str1 = "\n".join(line.strip() for line in content1 if line.strip())
        str2 = "\n".join(line.strip() for line in content2 if line.strip())

        # Use sequence matcher for similarity
        matcher = difflib.SequenceMatcher(None, str1, str2)
        return matcher.ratio()

    def _analyze_naming_consistency(self):
        """Analyze naming consistency across the codebase."""
        if not self.config.get("naming_consistency_check", True):
            return

        naming_patterns = defaultdict(set)

        for file_path in self.python_files:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()

                tree = ast.parse(content)

                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef):
                        naming_patterns["functions"].add(node.name)
                    elif isinstance(node, ast.ClassDef):
                        naming_patterns["classes"].add(node.name)
                    elif isinstance(node, ast.Name):
                        if isinstance(node.ctx, ast.Store):
                            naming_patterns["variables"].add(node.id)

            except Exception:
                continue

        # Analyze patterns for inconsistencies
        self._check_naming_patterns(naming_patterns)

    def _check_naming_patterns(self, patterns: Dict[str, Set[str]]):
        """Check for naming pattern inconsistencies."""
        for category, names in patterns.items():
            if len(names) < 2:
                continue

            # Group similar names
            similar_groups = self._group_similar_names(list(names))

            for group in similar_groups:
                if len(group) > 1:
                    # Found inconsistent naming
                    base_name = max(group, key=len)  # Use longest as base

                    for name in group:
                        if name != base_name:
                            self.add_issue(
                                category="ai_analysis",
                                issue_type="NAMING_CONVENTION",
                                file_path="multiple_files",
                                message=f"Inconsistent {category} naming: '{name}' vs '{base_name}'",
                                severity="info",
                                fix_suggestion=f"Consider using consistent naming pattern: '{base_name}'",
                                auto_fixable=False,
                            )

    def _group_similar_names(self, names: List[str]) -> List[List[str]]:
        """Group similar names together."""
        threshold = self.config.get("ai_pattern_detection", {}).get(
            "naming_pattern_threshold", 0.7
        )
        groups = []

        for name in names:
            added_to_group = False

            for group in groups:
                for group_name in group:
                    similarity = difflib.SequenceMatcher(None, name, group_name).ratio()
                    if similarity >= threshold:
                        group.append(name)
                        added_to_group = True
                        break

                if added_to_group:
                    break

            if not added_to_group:
                groups.append([name])

        return [group for group in groups if len(group) > 1]

    def _check_hallucinated_imports(self):
        """Check for potentially hallucinated or non-existent imports."""
        if not self.config.get("hallucinated_import_check", True):
            return

        # Common hallucinated imports in AI-generated code
        suspicious_imports = {
            "ai_utils",
            "ml_helpers",
            "data_processor",
            "model_utils",
            "config_manager",
            "base_handler",
            "utils_helper",
            "common_utils",
            "ai_processor",
            "smart_handler",
            "auto_handler",
            "intelligent_processor",
        }

        for file_path in self.python_files:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()

                tree = ast.parse(content)

                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            if alias.name in suspicious_imports:
                                self.add_issue(
                                    category="ai_analysis",
                                    issue_type="IMPORT_ERROR",
                                    file_path=str(file_path),
                                    message=f"Potentially hallucinated import: {alias.name}",
                                    line=node.lineno,
                                    severity="warning",
                                    fix_suggestion=f"Verify that '{alias.name}' is a real module or implement it",
                                    auto_fixable=False,
                                )

                    elif isinstance(node, ast.ImportFrom):
                        if node.module in suspicious_imports:
                            self.add_issue(
                                category="ai_analysis",
                                issue_type="IMPORT_ERROR",
                                file_path=str(file_path),
                                message=f"Potentially hallucinated import: from {node.module}",
                                line=node.lineno,
                                severity="warning",
                                fix_suggestion=f"Verify that '{node.module}' is a real module or implement it",
                                auto_fixable=False,
                            )

            except Exception:
                continue

    def _detect_architectural_violations(self):
        """Detect architectural pattern violations."""
        if not self.config.get("circular_dependency_detection", True):
            return

        # Build dependency graph
        dependency_graph = self._build_dependency_graph()

        # Check for circular dependencies
        cycles = self._find_cycles(dependency_graph)

        for cycle in cycles:
            cycle_str = " -> ".join(cycle)
            self.add_issue(
                category="ai_analysis",
                issue_type="CIRCULAR_IMPORT",
                file_path=cycle[0],
                message=f"Circular dependency detected: {cycle_str}",
                severity="error",
                fix_suggestion="Refactor to remove circular dependencies",
                auto_fixable=False,
            )

    def _build_dependency_graph(self) -> Dict[str, Set[str]]:
        """Build dependency graph for circular dependency detection."""
        graph = defaultdict(set)

        for file_path in self.python_files:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()

                tree = ast.parse(content)
                file_key = str(file_path.relative_to(self.root_path))

                for node in ast.walk(tree):
                    if isinstance(node, ast.ImportFrom):
                        if node.module and node.module.startswith("src."):
                            # Convert module to file path
                            module_path = node.module.replace(".", "/") + ".py"
                            graph[file_key].add(module_path)

            except Exception:
                continue

        return graph

    def _find_cycles(self, graph: Dict[str, Set[str]]) -> List[List[str]]:
        """Find cycles in dependency graph using DFS."""
        visited = set()
        rec_stack = set()
        cycles = []

        def dfs(node: str, path: List[str]) -> bool:
            if node in rec_stack:
                # Found cycle
                cycle_start = path.index(node)
                cycle = path[cycle_start:] + [node]
                cycles.append(cycle)
                return True

            if node in visited:
                return False

            visited.add(node)
            rec_stack.add(node)

            for neighbor in graph.get(node, set()):
                if dfs(neighbor, path + [node]):
                    rec_stack.remove(node)
                    return True

            rec_stack.remove(node)
            return False

        for node in graph:
            if node not in visited:
                dfs(node, [])

        return cycles

    def _analyze_unused_code(self):
        """Analyze for unused code patterns."""
        if not self.config.get("unused_code_detection", True):
            return

        # Enhanced unused code detection could include:
        # - Unused imports analysis
        # - Unused variable detection
        # - Dead code identification
        # For now, this is handled by other validators

    def _analyze_security_patterns(self):
        """Analyze security patterns and vulnerabilities."""
        if not self.config.get("security_pattern_scanning", True):
            return

        security_patterns = [
            (EVAL_PATTERN, EVAL_MESSAGE),
            (EXEC_PATTERN, EXEC_MESSAGE),
            (OS_SYSTEM_PATTERN, OS_SYSTEM_MESSAGE),
            (
                r"subprocess\.shell\s*=\s*True",
                "Shell=True in subprocess is dangerous",
            ),
            (
                r"pickle\.loads?\s*\(",
                "Use of pickle with untrusted data is dangerous",
            ),
            (
                r"yaml\.load\s*\(",
                "Use yaml.safe_load() instead of yaml.load()",
            ),
        ]

        for file_path in self.python_files:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()

                lines = content.split("\n")

                for i, line in enumerate(lines, 1):
                    for pattern, message in security_patterns:
                        if re.search(pattern, line):
                            self.add_issue(
                                category="ai_analysis",
                                issue_type="SECURITY_ISSUE",
                                file_path=str(file_path),
                                message=f"Security issue: {message}",
                                line=i,
                                severity="error",
                                fix_suggestion=message,
                                auto_fixable=False,
                            )

            except Exception:
                continue

    def _detect_code_smells(self):
        """Detect common code smells."""
        code_smells = [
            (r"#\s*TODO.*", "TODO comment found"),
            (r"#\s*FIXME.*", "FIXME comment found"),
            (r"#\s*HACK.*", "HACK comment found"),
            (r"print\s*\(", "Print statement (consider using logging)"),
            (r"except\s*:", "Bare except clause"),
            (r"pass\s*$", "Empty pass statement"),
        ]

        for file_path in self.python_files:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()

                lines = content.split("\n")

                for i, line in enumerate(lines, 1):
                    for pattern, message in code_smells:
                        if re.search(pattern, line.strip()):
                            self.add_issue(
                                category="ai_analysis",
                                issue_type="CODE_SMELL",
                                file_path=str(file_path),
                                message=f"Code smell: {message}",
                                line=i,
                                severity="info",
                                fix_suggestion=f"Consider addressing: {message}",
                                auto_fixable=False,
                            )

            except Exception:
                continue

    def generate_ai_report(self) -> Dict[str, Any]:
        """Generate comprehensive AI analysis report."""
        return {
            "duplicate_code_blocks": len(self.duplicate_blocks),
            "naming_inconsistencies": len(self.naming_inconsistencies),
            "architectural_violations": len(self.architectural_violations),
            "total_ai_issues": len(
                [i for i in self.issues if i.category == "ai_analysis"]
            ),
            "pattern_analysis": {
                "code_patterns": dict(self.code_patterns),
                "duplicate_blocks": self.duplicate_blocks,
                "naming_issues": self.naming_inconsistencies,
            },
            "recommendations": self._generate_ai_recommendations(),
        }

    def _generate_ai_recommendations(self) -> List[str]:
        """Generate AI-specific recommendations."""
        recommendations = []

        if self.duplicate_blocks:
            recommendations.append(
                "Consider refactoring duplicate code blocks into reusable functions"
            )

        if self.naming_inconsistencies:
            recommendations.append("Establish and follow consistent naming conventions")

        if self.architectural_violations:
            recommendations.append("Review and resolve architectural violations")

        return recommendations

    def _load_cache(self):
        """Load cached analysis results."""

        try:
            if self._cache_file.exists():
                with open(self._cache_file, "r") as f:
                    cache_data = json.load(f)
                    self._file_mtime_cache = cache_data.get("file_mtimes", {})
                    self._hash_cache = cache_data.get("file_hashes", {})
                    print(f"   📋 Loaded cache for {len(self._file_mtime_cache)} files")
        except Exception:
            # Cache loading failed, continue without cache
            pass

    def _save_cache(self):
        """Save analysis results to cache."""

        try:
            self._cache_file.parent.mkdir(parents=True, exist_ok=True)
            cache_data = {
                "file_mtimes": self._file_mtime_cache,
                "file_hashes": self._hash_cache,
                "last_updated": time.time(),
            }
            with open(self._cache_file, "w") as f:
                json.dump(cache_data, f, indent=2)
        except Exception:
            # Cache saving failed, continue without cache
            pass

    def _get_changed_files(self) -> List[Path]:
        """Get list of files that have changed since last analysis."""
        changed_files = []

        for file_path in self.python_files:
            file_str = str(file_path)
            try:
                current_mtime = os.path.getmtime(file_path)
                cached_mtime = self._file_mtime_cache.get(file_str, 0)

                if current_mtime > cached_mtime:
                    changed_files.append(file_path)
                    self._file_mtime_cache[file_str] = current_mtime
            except Exception:
                # If we can't get mtime, assume file changed
                changed_files.append(file_path)

        return changed_files

    def _detect_duplicate_code_optimized(
        self, files_to_analyze: List[Path], analysis_mode: str
    ):
        """Optimized duplicate code detection with sampling."""
        if analysis_mode == "sample":
            # Sample-based analysis for large codebases
            sample_size = min(50, len(files_to_analyze))
            files_to_analyze = files_to_analyze[:sample_size]
            print(f"   🔍 Sampling {sample_size} files for duplicate detection")

        threshold = self.config.get("duplicate_code_threshold", 0.8)
        min_lines = self.config.get("ai_pattern_detection", {}).get(
            "min_duplicate_lines", 5
        )
        
        print(f"   🎯 Using similarity threshold: {threshold}, min lines: {min_lines}")

        # Use hash-based quick filtering before expensive similarity calculation
        code_hashes = {}
        duplicate_count = 0

        for file_path in files_to_analyze:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    lines = f.readlines()

                blocks = self._extract_code_blocks(lines)

                for block_info in blocks:
                    block_hash = self._calculate_block_hash(block_info["content"])

                    if block_hash in code_hashes:
                        # Quick duplicate found
                        original = code_hashes[block_hash]
                        if len(block_info["content"]) >= min_lines:
                            self.add_issue(
                                category="ai_analysis",
                                issue_type="CODE_SMELL",
                                file_path=str(file_path),
                                message="Duplicate code block detected (hash match)",
                                line=block_info["line"],
                                severity="warning",
                                fix_suggestion=f"Consider extracting duplicate code into a shared function. Similar code found in {original['file']}:{original['line']}",
                                auto_fixable=False,
                            )
                            duplicate_count += 1
                    else:
                        code_hashes[block_hash] = {
                            "file": file_path,
                            "line": block_info["line"],
                            "content": block_info["content"],
                        }
            except Exception:
                continue

        if duplicate_count > 0:
            print(f"   ⚠️  Found {duplicate_count} duplicate code blocks")

    def _analyze_naming_consistency_optimized(self, files_to_analyze: List[Path]):
        """Optimized naming consistency analysis."""
        if not self.config.get("naming_consistency_check", True):
            return

        # Limit analysis to prevent performance issues
        sample_files = (
            files_to_analyze[:30] if len(files_to_analyze) > 30 else files_to_analyze
        )
        naming_patterns = defaultdict(set)

        for file_path in sample_files:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()

                # Quick check - only parse if file size is reasonable
                if len(content) > 50000:  # Skip very large files
                    continue

                tree = ast.parse(content)

                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef):
                        naming_patterns["functions"].add(node.name)
                    elif isinstance(node, ast.ClassDef):
                        naming_patterns["classes"].add(node.name)

            except Exception:
                continue

        # Only check for major inconsistencies
        self._check_naming_patterns_optimized(naming_patterns)

    def _check_naming_patterns_optimized(self, patterns: Dict[str, Set[str]]):
        """Optimized naming pattern checking."""
        for category, names in patterns.items():
            if len(names) < 5:  # Only check if we have enough samples
                continue

            # Simple heuristic: check for mixed snake_case/camelCase
            snake_case_count = sum(1 for name in names if "_" in name)
            camel_case_count = sum(
                1 for name in names if any(c.isupper() for c in name[1:])
            )

            if snake_case_count > 0 and camel_case_count > 0:
                self.add_issue(
                    category="ai_analysis",
                    issue_type="NAMING_CONVENTION",
                    file_path="multiple_files",
                    message=f"Mixed naming conventions in {category}: {snake_case_count} snake_case, {camel_case_count} camelCase",
                    severity="info",
                    fix_suggestion=f"Consider using consistent naming convention for {category}",
                    auto_fixable=False,
                )

    def _check_hallucinated_imports_optimized(self, files_to_analyze: List[Path]):
        """Optimized hallucinated import checking."""
        if not self.config.get("hallucinated_import_check", True):
            return

        suspicious_imports = {
            "ai_utils",
            "ml_helpers",
            "data_processor",
            "model_utils",
            "config_manager",
            "base_handler",
            "utils_helper",
            "common_utils",
        }

        # Sample files for quick check
        sample_files = (
            files_to_analyze[:20] if len(files_to_analyze) > 20 else files_to_analyze
        )

        for file_path in sample_files:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()

                # Quick regex check instead of AST parsing
                for suspicious in suspicious_imports:
                    if re.search(
                        rf"\bimport\s+{suspicious}\b|\bfrom\s+{suspicious}\s+import",
                        content,
                    ):
                        self.add_issue(
                            category="ai_analysis",
                            issue_type="IMPORT_ERROR",
                            file_path=str(file_path),
                            message=f"Potentially hallucinated import: {suspicious}",
                            severity="warning",
                            fix_suggestion=f"Verify that '{suspicious}' is a real module",
                            auto_fixable=False,
                        )

            except Exception:
                continue

    def _analyze_security_patterns_optimized(self, files_to_analyze: List[Path]):
        """Optimized security pattern analysis."""
        if not self.config.get("security_pattern_scanning", True):
            return

        # Focus on most critical security patterns only
        critical_patterns = [
            (EVAL_PATTERN, EVAL_MESSAGE),
            (EXEC_PATTERN, EXEC_MESSAGE),
            (OS_SYSTEM_PATTERN, OS_SYSTEM_MESSAGE),
            (r"subprocess.*shell\s*=\s*True", "Shell=True in subprocess is dangerous"),
        ]

        # Sample files for performance
        sample_files = (
            files_to_analyze[:25] if len(files_to_analyze) > 25 else files_to_analyze
        )

        for file_path in sample_files:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()

                # Check all patterns at once with single pass
                for pattern, message in critical_patterns:
                    matches = list(re.finditer(pattern, content))
                    for match in matches:
                        line_num = content[: match.start()].count("\n") + 1
                        self.add_issue(
                            category="ai_analysis",
                            issue_type="SECURITY_ISSUE",
                            file_path=str(file_path),
                            message=f"Security issue: {message}",
                            line=line_num,
                            severity="error",
                            fix_suggestion=message,
                            auto_fixable=False,
                        )

            except Exception:
                continue

    def _detect_code_smells_optimized(self, files_to_analyze: List[Path]):
        """Optimized code smell detection."""
        # Focus on most important code smells only
        important_smells = [
            (r"#\s*TODO.*", "TODO comment found"),
            (r"#\s*FIXME.*", "FIXME comment found"),
            (r"except\s*:", "Bare except clause"),
        ]

        # Sample files for performance
        sample_files = (
            files_to_analyze[:20] if len(files_to_analyze) > 20 else files_to_analyze
        )

        for file_path in sample_files:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()

                # Check all patterns at once with single pass
                for pattern, message in important_smells:
                    matches = list(re.finditer(pattern, content))
                    for match in matches:
                        line_num = content[: match.start()].count("\n") + 1
                        self.add_issue(
                            category="ai_analysis",
                            issue_type="CODE_SMELL",
                            file_path=str(file_path),
                            message=f"Code smell: {message}",
                            line=line_num,
                            severity="info",
                            fix_suggestion=f"Consider addressing: {message}",
                            auto_fixable=False,
                        )

            except Exception:
                continue
