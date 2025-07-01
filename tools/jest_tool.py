"""
Jest Tool - Helps agents generate and run Jest tests
"""

import json
import os
import re
import subprocess
from typing import Any, Dict, List, Optional

from tools.base_tool import ArtesanatoBaseTool


class JestTool(ArtesanatoBaseTool):
    """Tool for generating and running Jest tests for JavaScript/TypeScript code."""

    name: str = "jest_tool"
    description: str = "Tool for generating and running Jest tests for JavaScript and TypeScript components."
    project_root: str

    def __init__(self, project_root: str, **kwargs):
        """Initialize the Jest tool."""
        super().__init__(**kwargs)
        self.project_root = project_root
        self.jest_config = self._read_jest_config()

    def _run(self, query: str) -> str:
        """Execute a Jest operation based on the query."""
        try:
            query_lower = query.lower()

            if "generate test" in query_lower:
                component_path = self._extract_param(query, "path")
                component_code = self._extract_param(query, "code")
                test_type = self._extract_param(query, "type") or "component"
                return self._generate_test(
                    component_path, component_code, test_type)

            elif "run test" in query_lower:
                test_path = self._extract_param(query, "path")
                return self._run_test(test_path)

            elif "list tests" in query_lower:
                component_path = self._extract_param(query, "path")
                return self._list_tests(component_path)

            elif "get coverage" in query_lower:
                path = self._extract_param(query, "path")
                return self._get_coverage(path)

            else:
                return json.dumps(
                    self.format_response(
                        data=None,
                        error="Unsupported Jest operation. Supported operations: generate test, run test, list tests, get coverage"))

        except Exception as e:
            return json.dumps(self.handle_error(e, "JestTool._run"))

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

    def _read_jest_config(self) -> Dict[str, Any]:
        """Read Jest configuration from jest.config.js/ts files."""
        config = {
            "testMatch": ["**/__tests__/**/*.[jt]s?(x)", "**/?(*.)+(spec|test).[jt]s?(x)"],
            "setupFilesAfterEnv": [],
            "testEnvironment": "jsdom",
            "transform": {
                "^.+\\.(js|jsx|ts|tsx)$": ["babel-jest", {"presets": ["next/babel"]}]
            },
            "moduleNameMapper": {
                "^@/(.*)$": "<rootDir>/src/$1"
            }
        }

        try:
            # Check for jest.config.js or jest.config.ts
            config_files = ["jest.config.js", "jest.config.ts"]

            for config_file in config_files:
                config_path = os.path.join(self.project_root, config_file)
                if os.path.exists(config_path):
                    self.log(
                        f"Found Jest config at {config_path}, but automated parsing not implemented.")
                    # In a real implementation, we would parse the Jest config file here
                    # For this demo, we use a default config
                    break
        except Exception as e:
            self.log(f"Error reading Jest config: {str(e)}")

        return config

    def _generate_test(
            self,
            component_path: str,
            component_code: str,
            test_type: str) -> str:
        """Generate Jest test code for the given component."""
        try:
            # Determine if it's a React component
            is_react = "react" in component_code.lower() and (
                "import" in component_code and "from 'react'" in component_code)

            # Extract component name from path or code
            component_name = os.path.basename(component_path).split(
                '.')[0] if component_path else "Component"

            # Try to extract component name from code if we couldn't get it
            # from path
            if component_name == "Component" and component_code:
                # Look for export patterns like "export default function
                # ComponentName" or "export const ComponentName ="
                export_match = re.search(
                    r'export\s+(?:default\s+)?(?:function|const)\s+([A-Za-z0-9_]+)',
                    component_code)
                if export_match:
                    component_name = export_match.group(1)

            test_code = ""

            if test_type == "hook" or "use" in component_name.lower():
                # Generate test for a React hook
                test_code = self._generate_hook_test(
                    component_name, component_code)
            elif test_type == "util" or "util" in component_path.lower():
                # Generate test for a utility function
                test_code = self._generate_util_test(
                    component_name, component_code)
            else:
                # Default to component test
                test_code = self._generate_component_test(
                    component_name, component_code, is_react)

            # Create suggested test path
            if component_path:
                base_dir = os.path.dirname(component_path)
                base_name = os.path.basename(component_path).split('.')[0]

                # Handle different test file location patterns
                if "/__tests__/" in component_path:
                    test_path = component_path.replace(
                        ".tsx",
                        ".test.tsx").replace(
                        ".ts",
                        ".test.ts").replace(
                        ".jsx",
                        ".test.jsx").replace(
                        ".js",
                        ".test.js")
                else:
                    # Check if there's a __tests__ directory
                    tests_dir = os.path.join(base_dir, "__tests__")
                    if os.path.exists(tests_dir):
                        test_path = os.path.join(
                            tests_dir, f"{base_name}.test.{component_path.split('.')[-1]}")
                    else:
                        test_path = component_path.replace(
                            ".tsx",
                            ".test.tsx").replace(
                            ".ts",
                            ".test.ts").replace(
                            ".jsx",
                            ".test.jsx").replace(
                            ".js",
                            ".test.js")
            else:
                test_path = f"{component_name}.test.tsx" if is_react else f"{component_name}.test.ts"

            return json.dumps(self.format_response(
                data={
                    "component_name": component_name,
                    "test_code": test_code,
                    "suggested_test_path": test_path,
                    "test_type": test_type
                }
            ))

        except Exception as e:
            return json.dumps(self.handle_error(e, "JestTool._generate_test"))

    def _generate_component_test(
            self,
            component_name: str,
            component_code: str,
            is_react: bool) -> str:
        """Generate test code for a React component."""
        # Default React component test
        component_import = f"import {component_name} from './{component_name}';" if is_react else f"import {{ {component_name} }} from './{component_name}';"

        # Check if component takes props by looking for a Props type/interface
        has_props = "Props" in component_code or "props" in component_code

        additional_test = (
            "test('renders with different props', () => {\n"
            "    // Test component with various prop combinations\n"
            f"    render(<{component_name} {{ /* different props */ }} />);\n"
            "    // Add assertions for prop-specific behavior\n"
            "  });" if has_props else ""
        )

        test_code = f"""import React from 'react';
import {{ render, screen }} from '@testing-library/react';
import userEvent from '@testing-library/user-event';
{component_import}

describe('{component_name}', () => {{
  test('renders correctly', () => {{
    render(<{component_name} {"{ /* props here */ }" if has_props else ""} />);
    // Add assertions here
    expect(screen.getByText(/some content/i)).toBeInTheDocument();
  }});

  test('handles user interactions', async () => {{
    render(<{component_name} {"{ /* props here */ }" if has_props else ""} />);
    const user = userEvent.setup();

    // Example: click a button
    // await user.click(screen.getByRole('button', {{ name: /click me/i }}));

    // Add assertions for the expected behavior after interaction
    // expect(screen.getByText(/new content/i)).toBeInTheDocument();
  }});

  {additional_test}
}});
"""
        return test_code

    def _generate_hook_test(self, hook_name: str, hook_code: str) -> str:
        """Generate test code for a React hook."""
        test_code = f"""import {{ renderHook, act }} from '@testing-library/react-hooks';
import {{ {hook_name} }} from './{hook_name}';

describe('{hook_name}', () => {{
  test('should initialize with default values', () => {{
    const {{ result }} = renderHook(() => {hook_name}());

    // Add assertions for initial state
    // expect(result.current.someValue).toBe(initialValue);
  }});

  test('should handle state updates', () => {{
    const {{ result }} = renderHook(() => {hook_name}());

    act(() => {{
      // Call a function from the hook that updates state
      // result.current.someFunction();
    }});

    // Add assertions for updated state
    // expect(result.current.someValue).toBe(newValue);
  }});

  test('should handle errors correctly', () => {{
    // Test error cases if applicable
    // const {{ result }} = renderHook(() => {hook_name}({{ errorFlag: true }}));
    // expect(result.current.error).toBeTruthy();
  }});
}});
"""
        return test_code

    def _generate_util_test(self, util_name: str, util_code: str) -> str:
        """Generate test code for a utility function."""
        test_code = f"""import {util_name} from './{util_name}';

describe('{util_name}', () => {{
  test('should work with valid inputs', () => {{
    // Example: test with valid inputs
    // const result = {util_name}(validInput);
    // expect(result).toBe(expectedOutput);
  }});

  test('should handle edge cases', () => {{
    // Example: test with edge cases
    // expect({util_name}(edgeCase)).toBe(expectedOutput);
  }});

  test('should throw errors for invalid inputs', () => {{
    // Example: test with invalid inputs
    // expect(() => {util_name}(invalidInput)).toThrow();
  }});
}});
"""
        return test_code

    def _run_test(self, test_path: str) -> str:
        """Run Jest test(s) for the given path."""
        try:
            if not os.path.exists(
                os.path.join(
                    self.project_root,
                    test_path)) and not os.path.exists(test_path):
                return json.dumps(self.format_response(
                    data={
                        "message": f"Test file not found: {test_path}",
                        "success": False
                    },
                    error="Test file not found"
                ))

            # In a real implementation, we would actually run the tests
            # For this mock, we'll return a simulated test result

            return json.dumps(self.format_response(
                data={
                    "message": f"Tests run successfully for {test_path}",
                    "success": True,
                    "results": {
                        "numFailedTestSuites": 0,
                        "numPassedTestSuites": 1,
                        "numFailedTests": 0,
                        "numPassedTests": 3,
                        "numTotalTests": 3
                    },
                    "test_path": test_path
                }
            ))
        except Exception as e:
            return json.dumps(self.handle_error(e, "JestTool._run_test"))

    def _list_tests(self, component_path: str) -> str:
        """List tests for a specific component or directory."""
        try:
            # Extract the component name or directory
            if component_path:
                component_name = os.path.basename(component_path).split('.')[0]
                component_dir = os.path.dirname(component_path)
            else:
                component_name = ""
                component_dir = ""

            # In a real implementation, we would find all test files for this component
            # For this mock, we'll return simulated test files

            test_files = []

            if component_name:
                # Add potential test files based on common patterns
                test_files.append({
                    "path": os.path.join(component_dir, f"{component_name}.test.ts"),
                    "type": "Unit test",
                    "exists": False
                })
                test_files.append({
                    "path": os.path.join(component_dir, f"{component_name}.test.tsx"),
                    "type": "Component test",
                    "exists": False
                })
                test_files.append({
                    "path": os.path.join(component_dir, "__tests__", f"{component_name}.test.ts"),
                    "type": "Unit test",
                    "exists": False
                })
                test_files.append({
                    "path": os.path.join(component_dir, "__tests__", f"{component_name}.test.tsx"),
                    "type": "Component test",
                    "exists": False
                })
            else:
                # List some common test directories
                test_files.append({
                    "path": "src/__tests__",
                    "type": "Test directory",
                    "exists": False
                })
                test_files.append({
                    "path": "tests/unit",
                    "type": "Unit test directory",
                    "exists": False
                })
                test_files.append({
                    "path": "tests/integration",
                    "type": "Integration test directory",
                    "exists": False
                })

            # In a real implementation, we would check if these files actually exist
            # For this mock, we'll just assume none exist

            return json.dumps(
                self.format_response(
                    data={
                        "component": component_name,
                        "test_files": test_files,
                        "message": (
                            f"Found {len(test_files)} potential test locations for "
                            f"{component_name or 'the project'}."
                        )
                    }))
        except Exception as e:
            return json.dumps(self.handle_error(e, "JestTool._list_tests"))

    def _get_coverage(self, path: str) -> str:
        """Get test coverage for a specific path or the entire project."""
        try:
            # In a real implementation, we would run Jest with coverage and parse the results
            # For this mock, we'll return simulated coverage data

            coverage_data = {
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
                    }
                ]
            }

            # Filter by path if specified
            if path:
                filtered_files = [
                    file for file in coverage_data["files"] if path in file["path"]]
                coverage_data["files"] = filtered_files

                if not filtered_files:
                    return json.dumps(
                        self.format_response(
                            data={
                                "message": f"No coverage data found for path: {path}",
                                "coverage": None}))

            return json.dumps(
                self.format_response(
                    data={
                        "message": (
                            f"Coverage data retrieved for {path or 'the entire project'}"
                        ),
                        "coverage": coverage_data,
                    }))
        except Exception as e:
            return json.dumps(self.handle_error(e, "JestTool._get_coverage"))
