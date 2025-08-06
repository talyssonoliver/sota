
from src.infrastructure.utils.common_imports import (
    Enum,
    Path,
    dataclass,
    json,
    subprocess,
    tempfile,
    time
)
"""
Incremental Analysis for Pull Requests
Provides incremental analysis focusing on changed files and new code,
optimizing validation for pull request workflows.
"""

# import json  # Consolidated to common_imports
# import subprocess  # Consolidated to common_imports
# import tempfile  # Consolidated to common_imports
# import time  # Consolidated to common_imports
# from dataclasses import dataclass  # Consolidated to common_imports
# from enum import Enum  # Consolidated to common_imports
# from pathlib import Path  # Consolidated to common_imports
from typing import Any, Dict, List, Optional, Tuple

from .base_validator import BaseValidator
from .validator import Validator


class ChangeType(Enum):
    """Type of change in a file."""

    ADDED = "added"
    MODIFIED = "modified"
    DELETED = "deleted"
    RENAMED = "renamed"


@dataclass
class FileChange:
    """Represents a file change in a pull request."""

    file_path: str
    change_type: ChangeType
    lines_added: int
    lines_deleted: int
    old_file_path: Optional[str] = None  # For renamed files
    is_new_file: bool = False


@dataclass
class IncrementalResult:
    """Result of incremental analysis."""

    changed_files_count: int
    new_issues_count: int
    fixed_issues_count: int
    net_quality_impact: float  # -1 to 1, where 1 is improvement
    focus_areas: List[str]
    recommendations: List[str]


class IncrementalAnalyzer(BaseValidator):
    """Incremental analyzer for pull request validation."""

    def __init__(self, root_path: Optional[Path] = None, base_branch: str = "main"):
        super().__init__(root_path)
        self.base_branch = base_branch
        self.changes: List[FileChange] = []
        self.baseline_report: Optional[Dict[str, Any]] = None
        self.current_report: Optional[Dict[str, Any]] = None
        self.validator = Validator(root_path)
        self.unified_validator = self.validator  # Alias for backward compatibility

    def analyze_pull_request(self, target_branch: str = None) -> IncrementalResult:
        """Analyze changes in a pull request."""
        if target_branch is None:
            target_branch = self.base_branch

        print(f"🔍 Analyzing pull request changes (base: {target_branch})")

        # 1. Get file changes
        self.changes = self._get_file_changes(target_branch)

        if not self.changes:
            print("  ℹ️ No changes detected")
            return IncrementalResult(
                changed_files_count=0,
                new_issues_count=0,
                fixed_issues_count=0,
                net_quality_impact=0.0,
                focus_areas=[],
                recommendations=["No changes to analyze"],
            )

        print(f"  📁 Analyzing {len(self.changes)} changed files")

        # 2. Run validation on current branch
        print("  🔍 Running validation on current branch...")
        self.current_report = self.unified_validator.run_validation()

        # 3. Get baseline from target branch (if possible)
        print(f"  📊 Getting baseline from {target_branch}...")
        self.baseline_report = self._get_baseline_report(target_branch)

        # 4. Focus validation on changed files
        print("  🎯 Focusing on changed files...")
        focused_results = self._analyze_changed_files()

        # 5. Calculate incremental metrics
        print("  📈 Calculating incremental metrics...")
        result = self._calculate_incremental_metrics(focused_results)

        # 6. Generate incremental report
        self._generate_incremental_report(result)

        return result

    def _get_file_changes(self, target_branch: str) -> List[FileChange]:
        """Get list of changed files using git diff."""
        changes = []

        try:
            # Get diff with file statistics
            result = subprocess.run(
                [
                    "git",
                    "diff",
                    "--name-status",
                    "--find-renames",
                    f"{target_branch}...HEAD",
                ],
                cwd=self.root_path,
                capture_output=True,
                text=True,
                timeout=30,
            )

            if result.returncode != 0:
                print(f"  ⚠️ Git diff failed: {result.stderr}")
                return changes

            # Parse git diff output
            for line in result.stdout.strip().split("\n"):
                if not line:
                    continue

                parts = line.split("\t")
                if len(parts) < 2:
                    continue

                status = parts[0]
                file_path = parts[1]

                # Determine change type
                if status.startswith("A"):
                    change_type = ChangeType.ADDED
                    is_new_file = True
                elif status.startswith("M"):
                    change_type = ChangeType.MODIFIED
                    is_new_file = False
                elif status.startswith("D"):
                    change_type = ChangeType.DELETED
                    is_new_file = False
                elif status.startswith("R"):
                    change_type = ChangeType.RENAMED
                    is_new_file = False
                else:
                    continue

                # Get line changes
                lines_added, lines_deleted = self._get_line_changes(
                    file_path, target_branch
                )

                changes.append(
                    FileChange(
                        file_path=file_path,
                        change_type=change_type,
                        lines_added=lines_added,
                        lines_deleted=lines_deleted,
                        is_new_file=is_new_file,
                    )
                )

        except Exception as e:
            print(f"  ⚠️ Error getting file changes: {e}")

        return changes

    def _get_line_changes(self, file_path: str, target_branch: str) -> Tuple[int, int]:
        """Get line addition/deletion count for a file."""
        try:
            result = subprocess.run(
                [
                    "git",
                    "diff",
                    "--numstat",
                    f"{target_branch}...HEAD",
                    "--",
                    file_path,
                ],
                cwd=self.root_path,
                capture_output=True,
                text=True,
                timeout=10,
            )

            if result.returncode == 0 and result.stdout.strip():
                parts = result.stdout.strip().split("\t")
                if len(parts) >= 2:
                    lines_added = int(parts[0]) if parts[0].isdigit() else 0
                    lines_deleted = int(parts[1]) if parts[1].isdigit() else 0
                    return lines_added, lines_deleted

        except Exception:
            pass

        return 0, 0

    def _get_baseline_report(self, target_branch: str) -> Optional[Dict[str, Any]]:
        """Get baseline validation report from target branch."""
        try:
            # Create temporary worktree for baseline analysis
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_path = Path(temp_dir)

                # Create worktree
                subprocess.run(
                    ["git", "worktree", "add", str(temp_path), target_branch],
                    cwd=self.root_path,
                    capture_output=True,
                    timeout=30,
                )

                try:
                    # Run validation on baseline
                    baseline_validator = Validator(temp_path)
                    baseline_report = baseline_validator.run_validation()

                    return baseline_report

                finally:
                    # Clean up worktree
                    subprocess.run(
                        ["git", "worktree", "remove", str(temp_path)],
                        cwd=self.root_path,
                        capture_output=True,
                        timeout=10,
                    )

        except Exception as e:
            print(f"  ⚠️ Could not get baseline report: {e}")

        return None

    def _analyze_changed_files(self) -> Dict[str, Any]:
        """Analyze only the changed files."""
        changed_python_files = []

        for change in self.changes:
            # Skip deleted files early
            if change.change_type == ChangeType.DELETED:
                continue
                
            # Resolve all paths to avoid false positives with relative paths
            file_path = (Path(self.root_path) / change.file_path).resolve()

            # Only analyze existing Python files
            if file_path.exists() and file_path.suffix == ".py":
                changed_python_files.append(file_path)

        if not changed_python_files:
            return {"issues": [], "files_analyzed": 0}

        # Run focused validation on changed files
        print(f"    🔍 Analyzing {len(changed_python_files)} changed Python files")

        # Create a focused validator for changed files
        focused_validator = Validator(self.root_path)
        focused_validator.python_files = changed_python_files

        # Run validation
        focused_report = focused_validator.run_validation()

        return {
            "issues": focused_report.get("detailed_issues", []),
            "files_analyzed": len(changed_python_files),
            "summary": focused_report.get("summary", {}),
            "focused_report": focused_report,
        }

    def _calculate_incremental_metrics(
        self, focused_results: Dict[str, Any]
    ) -> IncrementalResult:
        """Calculate incremental metrics comparing current to baseline."""
        current_issues = len(focused_results.get("issues", []))
        baseline_issues = 0

        if self.baseline_report:
            baseline_issues = self.baseline_report.get("summary", {}).get(
                "total_issues", 0
            )

        # Calculate net impact
        net_issues = current_issues - baseline_issues

        # Calculate quality impact (-1 to 1)
        if baseline_issues == 0:
            net_quality_impact = -0.5 if current_issues > 0 else 0.5
        else:
            net_quality_impact = -min(net_issues / baseline_issues, 1.0)

        # Determine focus areas
        focus_areas = self._determine_focus_areas(focused_results)

        # Generate recommendations
        recommendations = self._generate_incremental_recommendations(
            focused_results, net_quality_impact, current_issues
        )

        return IncrementalResult(
            changed_files_count=len(self.changes),
            new_issues_count=max(0, net_issues),
            fixed_issues_count=max(0, -net_issues),
            net_quality_impact=net_quality_impact,
            focus_areas=focus_areas,
            recommendations=recommendations,
        )

    def _determine_focus_areas(self, focused_results: Dict[str, Any]) -> List[str]:
        """Determine focus areas based on issues found."""
        focus_areas = []
        issues = focused_results.get("issues", [])

        if not issues:
            return ["No issues found in changed files"]

        # Group issues by category
        issue_categories = {}
        for issue in issues:
            category = issue.get("category", "unknown")
            if category not in issue_categories:
                issue_categories[category] = 0
            issue_categories[category] += 1

        # Sort by frequency
        sorted_categories = sorted(
            issue_categories.items(), key=lambda x: x[1], reverse=True
        )

        for category, count in sorted_categories[:5]:  # Top 5 categories
            focus_areas.append(f"{category}: {count} issues")

        return focus_areas

    def _generate_incremental_recommendations(
        self,
        focused_results: Dict[str, Any],
        net_quality_impact: float,
        current_issues: int,
    ) -> List[str]:
        """Generate recommendations for incremental changes."""
        recommendations = []

        # Impact-based recommendations
        if net_quality_impact < -0.3:
            recommendations.append(
                "❌ Quality regression detected - review changes carefully"
            )
        elif net_quality_impact > 0.3:
            recommendations.append("✅ Quality improvement detected - good work!")
        else:
            recommendations.append("➡️ Quality impact is neutral")

        # Issue-based recommendations
        if current_issues == 0:
            recommendations.append("🎉 No issues found in changed files")
        elif current_issues < 5:
            recommendations.append(
                f"🔍 {current_issues} issues found - consider addressing before merge"
            )
        else:
            recommendations.append(
                f"⚠️ {current_issues} issues found - review and fix critical issues"
            )

        # File-specific recommendations
        new_files = [c for c in self.changes if c.is_new_file]
        if new_files:
            recommendations.append(
                f"📄 {len(new_files)} new files added - ensure proper testing"
            )

        large_changes = [c for c in self.changes if c.lines_added > 100]
        if large_changes:
            recommendations.append(
                f"📊 {len(large_changes)} files with large changes - consider breaking into smaller PRs"
            )

        # Quick fixes
        quick_fixes = self._identify_quick_fixes(focused_results)
        if quick_fixes:
            recommendations.extend(quick_fixes)

        return recommendations

    def _identify_quick_fixes(self, focused_results: Dict[str, Any]) -> List[str]:
        """Identify quick fixes for common issues."""
        quick_fixes = []
        issues = focused_results.get("issues", [])

        # Count auto-fixable issues
        auto_fixable = [i for i in issues if i.get("auto_fixable", False)]
        if auto_fixable:
            quick_fixes.append(f"🔧 {len(auto_fixable)} issues can be auto-fixed")

        # Count formatting issues
        formatting_issues = [i for i in issues if i.get("category") == "formatting"]
        if formatting_issues:
            quick_fixes.append(
                f"🎨 Run 'black .' to fix {len(formatting_issues)} formatting issues"
            )

        # Count import issues
        import_issues = [i for i in issues if i.get("category") == "imports"]
        if import_issues:
            quick_fixes.append(
                f"📦 Run 'isort .' to fix {len(import_issues)} import issues"
            )

        return quick_fixes

    def _generate_incremental_report(self, result: IncrementalResult):
        """Generate incremental analysis report."""
        report = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "analysis_type": "incremental",
            "base_branch": self.base_branch,
            "changes_summary": {
                "total_files_changed": result.changed_files_count,
                "files_by_type": self._summarize_changes_by_type(),
                "total_lines_added": sum(c.lines_added for c in self.changes),
                "total_lines_deleted": sum(c.lines_deleted for c in self.changes),
            },
            "quality_impact": {
                "net_quality_impact": result.net_quality_impact,
                "new_issues": result.new_issues_count,
                "fixed_issues": result.fixed_issues_count,
                "impact_assessment": self._assess_impact(result.net_quality_impact),
            },
            "focus_areas": result.focus_areas,
            "recommendations": result.recommendations,
            "file_changes": [
                {
                    "file_path": change.file_path,
                    "change_type": change.change_type.value,
                    "lines_added": change.lines_added,
                    "lines_deleted": change.lines_deleted,
                    "is_new_file": change.is_new_file,
                }
                for change in self.changes
            ],
        }

        # Save report
        report_path = self.root_path / "reports" / "incremental_analysis.json"
        report_path.parent.mkdir(parents=True, exist_ok=True)

        with open(report_path, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, default=str)

        print(f"📊 Incremental analysis report saved: {report_path}")

    def _summarize_changes_by_type(self) -> Dict[str, int]:
        """Summarize changes by type."""
        summary = {}
        for change in self.changes:
            change_type = change.change_type.value
            if change_type not in summary:
                summary[change_type] = 0
            summary[change_type] += 1
        return summary

    def _assess_impact(self, net_quality_impact: float) -> str:
        """Assess the impact of changes."""
        if net_quality_impact > 0.3:
            return "Significant quality improvement"
        elif net_quality_impact > 0.1:
            return "Minor quality improvement"
        elif net_quality_impact > -0.1:
            return "Neutral impact"
        elif net_quality_impact > -0.3:
            return "Minor quality regression"
        else:
            return "Significant quality regression"

    def generate_pr_comment(self, result: IncrementalResult) -> str:
        """Generate a comment for pull request."""
        impact_emoji = (
            "✅"
            if result.net_quality_impact > 0
            else "❌" if result.net_quality_impact < -0.1 else "➡️"
        )

        comment = f"""## {impact_emoji} Code Quality Analysis

### 📊 Summary
- **Files Changed**: {result.changed_files_count}
- **New Issues**: {result.new_issues_count}
- **Fixed Issues**: {result.fixed_issues_count}
- **Quality Impact**: {self._assess_impact(result.net_quality_impact)}

### 🎯 Focus Areas
{chr(10).join(f"- {area}" for area in result.focus_areas)}

### 💡 Recommendations
{chr(10).join(f"- {rec}" for rec in result.recommendations)}

### 📋 File Changes
{chr(10).join(f"- `{change.file_path}` ({change.change_type.value}): +{change.lines_added}/-{change.lines_deleted}" for change in self.changes[:10])}
{f"... and {len(self.changes) - 10} more files" if len(self.changes) > 10 else ""}

---
*Analysis performed by Unified Validation Pipeline*
"""

        return comment

    def should_request_review(self, result: IncrementalResult) -> bool:
        """Determine if manual review should be requested."""
        # Request review if:
        # 1. Quality regression detected
        # 2. High number of new issues
        # 3. Large changes
        # 4. New files added

        conditions = [
            result.net_quality_impact < -0.2,  # Quality regression
            result.new_issues_count > 5,  # Many new issues
            result.changed_files_count > 20,  # Many files changed
            sum(c.lines_added for c in self.changes) > 500,  # Large changes
            len([c for c in self.changes if c.is_new_file]) > 5,  # Many new files
        ]

        return any(conditions)

    def get_merge_recommendation(self, result: IncrementalResult) -> Dict[str, Any]:
        """Get merge recommendation based on analysis."""
        should_block = False
        should_review = self.should_request_review(result)

        # Block merge if significant quality regression
        if result.net_quality_impact < -0.5:
            should_block = True

        # Block merge if too many critical issues
        if result.new_issues_count > 10:
            should_block = True

        return {
            "can_merge": not should_block,
            "requires_review": should_review,
            "recommendation": self._get_merge_recommendation_text(
                should_block, should_review
            ),
            "quality_score": max(0, min(100, 50 + result.net_quality_impact * 50)),
        }

    def _get_merge_recommendation_text(
        self, should_block: bool, should_review: bool
    ) -> str:
        """Generate recommendation text for merge decision."""
        if should_block:
            return "❌ Merge blocked due to quality issues. Please address critical issues before merging."
        elif should_review:
            return "⚠️ Manual review recommended before merge. Consider having a team member review the changes."
        else:
            return "✅ Changes look good! Safe to merge."
