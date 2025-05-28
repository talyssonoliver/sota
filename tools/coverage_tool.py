"""
Coverage Tool - Helps agents analyze test coverage metrics
"""

import json
import os
import subprocess
from typing import Any, Dict, List, Optional

from .base_tool import ArtesanatoBaseTool


class CoverageTool(ArtesanatoBaseTool):
    """Tool for analyzing and reporting on test coverage for the project."""

    name: str = "coverage_tool"
    description: str = "Tool for analyzing and reporting on test coverage metrics for JavaScript, TypeScript, and Python code."
    project_root: str = ""
    thresholds: Dict[str, int] = {
        "lines": 70,
        "statements": 70,
        "functions": 70,
        "branches": 60
    }

    def _run(self, query: str) -> str:
        """Execute a coverage operation based on the query."""
        try:
            query_lower = query.lower()

            if "get report" in query_lower:
                format_type = self._extract_param(query, "format") or "summary"
                path = self._extract_param(query, "path") or ""
                return self._get_coverage_report(path, format_type)

            elif "check thresholds" in query_lower:
                return self._check_coverage_thresholds()

            elif "set thresholds" in query_lower:
                lines = self._extract_param(query, "lines")
                statements = self._extract_param(query, "statements")
                functions = self._extract_param(query, "functions")
                branches = self._extract_param(query, "branches")
                return self._set_coverage_thresholds(
                    lines, statements, functions, branches)

            elif "identify gaps" in query_lower:
                path = self._extract_param(query, "path") or ""
                return self._identify_coverage_gaps(path)

            else:
                return json.dumps(
                    self.format_response(
                        data=None,
                        error="Unsupported coverage operation. Supported operations: get report, check thresholds, set thresholds, identify gaps"))

        except Exception as e:
            return json.dumps(self.handle_error(e, "CoverageTool._run"))

    def _extract_param(self, query: str, param_name: str) -> str:
        """Extract a parameter value from the query string."""
        param_start = query.find(f"{param_name}:") + len(param_name) + 1
        if param_start < len(param_name) + 1:
            return ""

        # Find the end of the parameter value
        next_param_pos = query[param_start:].find(":")
        param_end = param_start + \
            next_param_pos if next_param_pos != -1 else len(query)

        # If there's a comma before the next param, use that as the end
        comma_pos = query[param_start:].find(",")
        if comma_pos != - \
                1 and (comma_pos < next_param_pos or next_param_pos == -1):
            param_end = param_start + comma_pos

        return query[param_start:param_end].strip()

    def _get_coverage_report(self, path: str, format_type: str) -> str:
        """Get a coverage report for the specified path in the requested format."""
        try:
            # In a real implementation, we would run the coverage tool and parse the results
            # For this mock, we'll return simulated coverage data

            coverage_data = self._get_mock_coverage_data()

            # Filter by path if specified
            if path:
                if format_type == "summary":
                    # Filter files but keep the overall structure
                    filtered_files = [
                        file for file in coverage_data["files"] if path in file["path"]]
                    if not filtered_files:
                        return json.dumps(
                            self.format_response(
                                data={
                                    "message": f"No coverage data found for path: {path}",
                                    "coverage": None}))
                    coverage_data["files"] = filtered_files

                    # Recalculate totals based on filtered files
                    if filtered_files:
                        coverage_data["total"] = {
                            "lines": sum(
                                f["lines"] for f in filtered_files) /
                            len(filtered_files),
                            "statements": sum(
                                f["statements"] for f in filtered_files) /
                            len(filtered_files),
                            "functions": sum(
                                f["functions"] for f in filtered_files) /
                            len(filtered_files),
                            "branches": sum(
                                f["branches"] for f in filtered_files) /
                            len(filtered_files)}

            # Format based on the requested type
            if format_type == "detailed":
                return json.dumps(self.format_response(
                    data={
                        "format": "detailed",
                        "path": path or "entire project",
                        "coverage": coverage_data,
                        "uncovered_lines": self._get_mock_uncovered_lines(path)
                    }
                ))
            else:  # summary is the default
                return json.dumps(self.format_response(
                    data={
                        "format": "summary",
                        "path": path or "entire project",
                        "coverage": {
                            "total": coverage_data["total"],
                            "file_count": len(coverage_data["files"])
                        }
                    }
                ))

        except Exception as e:
            return json.dumps(
                self.handle_error(
                    e, "CoverageTool._get_coverage_report"))

    def _check_coverage_thresholds(self) -> str:
        """Check if current coverage meets the defined thresholds."""
        try:
            coverage_data = self._get_mock_coverage_data()
            total = coverage_data["total"]

            # Compare against thresholds
            results = {
                "lines": {
                    "actual": total["lines"],
                    "threshold": self.thresholds["lines"],
                    "passing": total["lines"] >= self.thresholds["lines"]
                },
                "statements": {
                    "actual": total["statements"],
                    "threshold": self.thresholds["statements"],
                    "passing": total["statements"] >= self.thresholds["statements"]
                },
                "functions": {
                    "actual": total["functions"],
                    "threshold": self.thresholds["functions"],
                    "passing": total["functions"] >= self.thresholds["functions"]
                },
                "branches": {
                    "actual": total["branches"],
                    "threshold": self.thresholds["branches"],
                    "passing": total["branches"] >= self.thresholds["branches"]
                }
            }

            # Overall pass/fail
            all_passing = all(metric["passing"] for metric in results.values())

            return json.dumps(
                self.format_response(
                    data={
                        "thresholds": self.thresholds,
                        "results": results,
                        "passing": all_passing,
                        "message": "All coverage thresholds met." if all_passing else "Some coverage thresholds not met."}))

        except Exception as e:
            return json.dumps(
                self.handle_error(
                    e, "CoverageTool._check_coverage_thresholds"))

    def _set_coverage_thresholds(
            self,
            lines: str,
            statements: str,
            functions: str,
            branches: str) -> str:
        """Set new coverage thresholds."""
        try:
            # Update thresholds if provided
            if lines:
                self.thresholds["lines"] = float(lines)
            if statements:
                self.thresholds["statements"] = float(statements)
            if functions:
                self.thresholds["functions"] = float(functions)
            if branches:
                self.thresholds["branches"] = float(branches)

            return json.dumps(self.format_response(
                data={
                    "message": "Coverage thresholds updated successfully.",
                    "thresholds": self.thresholds
                }
            ))

        except ValueError as e:
            return json.dumps(
                self.handle_error(
                    e, "CoverageTool._set_coverage_thresholds, invalid numeric value"))
        except Exception as e:
            return json.dumps(
                self.handle_error(
                    e, "CoverageTool._set_coverage_thresholds"))

    def _identify_coverage_gaps(self, path: str) -> str:
        """Identify areas with poor test coverage."""
        try:
            coverage_data = self._get_mock_coverage_data()

            # Filter files by path if specified
            if path:
                files = [file for file in coverage_data["files"]
                         if path in file["path"]]
            else:
                files = coverage_data["files"]

            if not files:
                return json.dumps(self.format_response(
                    data={
                        "message": f"No files found matching path: {path}",
                        "gaps": []
                    }
                ))

            # Identify files with coverage below thresholds
            gaps = []

            for file in files:
                file_gaps = {
                    "metric": [],
                    "path": file["path"]
                }

                # Check each metric
                if file["lines"] < self.thresholds["lines"]:
                    file_gaps["metric"].append("lines")
                if file["statements"] < self.thresholds["statements"]:
                    file_gaps["metric"].append("statements")
                if file["functions"] < self.thresholds["functions"]:
                    file_gaps["metric"].append("functions")
                if file["branches"] < self.thresholds["branches"]:
                    file_gaps["metric"].append("branches")

                # If any metrics are below threshold, add to gaps
                if file_gaps["metric"]:
                    file_gaps["coverage"] = {
                        "lines": file["lines"],
                        "statements": file["statements"],
                        "functions": file["functions"],
                        "branches": file["branches"]
                    }

                    # Add uncovered lines and functions
                    file_gaps["details"] = self._get_mock_file_gap_details(
                        file["path"])

                    gaps.append(file_gaps)

            # Sort gaps by severity (number of failing metrics)
            gaps.sort(key=lambda x: len(x["metric"]), reverse=True)

            return json.dumps(self.format_response(
                data={
                    "message": f"Found {len(gaps)} files with coverage gaps.",
                    "gaps": gaps
                }
            ))

        except Exception as e:
            return json.dumps(
                self.handle_error(
                    e, "CoverageTool._identify_coverage_gaps"))

    def _get_mock_coverage_data(self) -> Dict[str, Any]:
        """Return mock coverage data for demonstration."""
        return {
            "total": {
                "lines": 78.5,
                "statements": 77.8,
                "functions": 68.2,
                "branches": 65.0
            },
            "files": [
                {
                    "path": "src/components/Button.tsx",
                    "lines": 95.2,
                    "statements": 94.1,
                    "functions": 90.0,
                    "branches": 85.7
                },
                {
                    "path": "src/components/Card.tsx",
                    "lines": 87.3,
                    "statements": 86.5,
                    "functions": 80.0,
                    "branches": 75.0
                },
                {
                    "path": "src/hooks/useCart.ts",
                    "lines": 68.4,
                    "statements": 67.9,
                    "functions": 60.0,
                    "branches": 55.2
                },
                {
                    "path": "src/utils/formatters.ts",
                    "lines": 92.1,
                    "statements": 91.5,
                    "functions": 100.0,
                    "branches": 88.9
                },
                {
                    "path": "src/hooks/useAuth.ts",
                    "lines": 62.8,
                    "statements": 61.5,
                    "functions": 55.0,
                    "branches": 48.3
                },
                {
                    "path": "src/services/api.ts",
                    "lines": 72.4,
                    "statements": 71.9,
                    "functions": 65.0,
                    "branches": 60.5
                }
            ]
        }

    def _get_mock_uncovered_lines(self, path: str) -> List[Dict[str, Any]]:
        """Return mock uncovered lines for demonstration."""
        # Return a different set of mock uncovered lines based on the path
        if "useCart" in path:
            return [
                {
                    "path": "src/hooks/useCart.ts",
                    "lines": [45, 46, 47, 72, 73, 95, 96, 97, 98],
                    "functions": ["handleCheckoutError", "calculateTaxes"]
                }
            ]
        elif "useAuth" in path:
            return [{"path": "src/hooks/useAuth.ts",
                     "lines": [33,
                               34,
                               35,
                               50,
                               51,
                               82,
                               83,
                               84,
                               85,
                               86,
                               120,
                               121],
                     "functions": ["validateToken",
                                   "refreshToken",
                                   "handleAuthError"]}]
        else:
            return [
                {
                    "path": "src/components/Button.tsx",
                    "lines": [42],
                    "functions": []
                },
                {
                    "path": "src/components/Card.tsx",
                    "lines": [27, 28, 55],
                    "functions": ["handleImageError"]
                },
                {
                    "path": "src/hooks/useCart.ts",
                    "lines": [45, 46, 47, 72, 73, 95, 96, 97, 98],
                    "functions": ["handleCheckoutError", "calculateTaxes"]
                }
            ]

    def _get_mock_file_gap_details(self, file_path: str) -> Dict[str, Any]:
        """Return mock gap details for a specific file."""
        if "useCart" in file_path:
            return {
                "uncovered_lines": [
                    45,
                    46,
                    47,
                    72,
                    73,
                    95,
                    96,
                    97,
                    98],
                "uncovered_functions": [
                    "handleCheckoutError",
                    "calculateTaxes"],
                "uncovered_branches": [
                    "if (cart.items.length === 0)",
                    "if (user.address === null)"],
                "total_lines": 150,
                "total_functions": 10,
                "total_branches": 15}
        elif "useAuth" in file_path:
            return {
                "uncovered_lines": [
                    33,
                    34,
                    35,
                    50,
                    51,
                    82,
                    83,
                    84,
                    85,
                    86,
                    120,
                    121],
                "uncovered_functions": [
                    "validateToken",
                    "refreshToken",
                    "handleAuthError"],
                "uncovered_branches": [
                    "if (token === null)",
                    "if (error.code === 'AUTH_EXPIRED')",
                    "if (!localStorage.getItem('refresh_token'))"],
                "total_lines": 140,
                "total_functions": 8,
                "total_branches": 12}
        elif "Button" in file_path:
            return {
                "uncovered_lines": [42],
                "uncovered_functions": [],
                "uncovered_branches": ["if (isDisabled && !showDisabledStyle)"],
                "total_lines": 80,
                "total_functions": 5,
                "total_branches": 7}
        elif "Card" in file_path:
            return {
                "uncovered_lines": [
                    27,
                    28,
                    55],
                "uncovered_functions": ["handleImageError"],
                "uncovered_branches": [
                    "if (error && onError)",
                    "if (!imageUrl)"],
                "total_lines": 95,
                "total_functions": 5,
                "total_branches": 8}
        elif "formatters" in file_path:
            return {
                "uncovered_lines": [105],
                "uncovered_functions": [],
                "uncovered_branches": ["if (locale !== 'pt-BR' && locale !== 'en-US')"],
                "total_lines": 70,
                "total_functions": 6,
                "total_branches": 9}
        else:
            return {
                "uncovered_lines": [120, 121, 122],
                "uncovered_functions": ["handleEdgeCase"],
                "uncovered_branches": ["if (condition && anotherCondition)"],
                "total_lines": 100,
                "total_functions": 10,
                "total_branches": 15
            }
