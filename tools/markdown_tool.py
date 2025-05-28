"""
Markdown Tool - Helps agents generate and format markdown documentation
"""

import json
import os
import re
from datetime import datetime
from typing import Any, Dict

import frontmatter
from pydantic import BaseModel, ValidationError

from tools.base_tool import ArtesanatoBaseTool


class MarkdownTool(ArtesanatoBaseTool):
    """Tool for generating and formatting markdown documentation."""

    name: str = "markdown_tool"
    description: str = "Tool for generating, formatting, and managing markdown documentation."
    docs_dir: str = "docs"
    templates_dir: str = "docs/templates"

    class InputSchema(BaseModel):
        query: str

    def _run(self, query: str) -> str:
        """Execute a markdown operation based on the query with input validation and error handling."""
        try:
            validated = self.InputSchema(query=query)
            query = validated.query
            query_lower = query.lower()

            if "format" in query_lower:
                # Extract content and format it
                content_start = query.find("content:") + 8
                content = query[content_start:].strip()
                return self._format_markdown(content)

            elif "generate template" in query_lower:
                # Generate a documentation template
                template_type = self._extract_param(query, "type")
                title = self._extract_param(query, "title")
                return self._generate_template(template_type, title)

            elif "extract frontmatter" in query_lower:
                # Extract frontmatter from markdown content
                content_start = query.find("content:") + 8
                content = query[content_start:].trip()
                return self._extract_frontmatter(content)

            elif "add frontmatter" in query_lower:
                # Add frontmatter to markdown content
                content_start = query.find("content:") + 8
                content_end = query.find(
                    "metadata:") if "metadata:" in query else len(query)
                content = query[content_start:content_end].strip()

                metadata_str = self._extract_param(query, "metadata")
                try:
                    metadata = json.loads(metadata_str)
                except BaseException:
                    metadata = {"title": "Untitled Document",
                                "created": datetime.now().strftime("%Y-%m-%d")}

                return self._add_frontmatter(content, metadata)

            else:
                return json.dumps(
                    self.format_response(
                        data=None,
                        error="Unsupported markdown operation. Supported operations: format, generate template, extract frontmatter, add frontmatter"))

        except ValidationError as ve:
            return json.dumps(
                self.handle_error(
                    ve, f"{
                        self.name}._run.input_validation"))
        except Exception as e:
            return json.dumps(self.handle_error(e, f"{self.name}._run"))

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

    def _format_markdown(self, content: str) -> str:
        """Format and clean up markdown content."""
        try:
            # Fix headers without space after #
            content = re.sub(r'#(\w)', r'# \1', content)

            # Ensure code blocks have proper syntax highlighting
            content = re.sub(r'```(\s*\n)', r'```text\1', content)

            # Normalize list formatting
            content = re.sub(r'^\s*[-*]\s', '- ', content, flags=re.MULTILINE)

            # Fix trailing whitespace
            content = re.sub(r'[ \t]+$', '', content, flags=re.MULTILINE)

            # Ensure single blank line between sections
            content = re.sub(r'\n{3,}', '\n\n', content)

            return json.dumps(self.format_response(
                data={
                    "formatted_content": content
                }
            ))
        except Exception as e:
            return json.dumps(
                self.handle_error(
                    e, "MarkdownTool._format_markdown"))

    def _generate_template(self, template_type: str, title: str) -> str:
        """Generate a markdown documentation template."""
        now = datetime.now().strftime("%Y-%m-%d")

        if not title:
            title = "Untitled Document"

        try:
            if template_type == "api":
                template = f"""---
title: {title}
author: AI Documentation Agent
created: {now}
last_updated: {now}
version: 0.1
status: Draft
---

# {title}

## Overview
Brief description of this API.

## Endpoints

### `GET /api/resource`

**Description**: Get a list of resources.

**Query Parameters**:
- `limit` (number, optional): Maximum number of items to return
- `offset` (number, optional): Number of items to skip

**Response**:
```json
{{
  "data": [
    {{
      "id": "string",
      "name": "string"
    }}
  ],
  "error": null
}}
```

### `POST /api/resource`

**Description**: Create a new resource.

**Request Body**:
```json
{{
  "name": "string",
  "description": "string"
}}
```

**Response**:
```json
{{
  "data": {{
    "id": "string",
    "name": "string",
    "description": "string",
    "created_at": "string"
  }},
  "error": null
}}
```

## Error Handling
All endpoints return errors in the following format:

```json
{{
  "data": null,
  "error": {{
    "message": "Error description",
    "code": "ERROR_CODE"
  }}
}}
```

## Authentication
This API requires authentication using Bearer token.
"""
            elif template_type == "component":
                template = f"""---
title: {title} Component
author: AI Documentation Agent
created: {now}
last_updated: {now}
version: 0.1
status: Draft
---

# {title} Component

## Overview
Brief description of this component.

## Props / Properties

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `prop1` | `string` | `""` | Description of prop1 |
| `prop2` | `number` | `0` | Description of prop2 |

## Usage Example

```tsx
import {{ {title.replace(' ', '')} }} from '@/components/{title.lower().replace(' ', '-')}''';

export default function Example() {{
  return (
    <{title.replace(' ', '')}
      prop1="value1"
      prop2={42}
    />
  );
}}
```

## Accessibility
Accessibility considerations for this component.

## Notes
Additional implementation details or usage guidelines.
"""
            else:
                # Default generic template
                template = f"""---
title: {title}
author: AI Documentation Agent
created: {now}
last_updated: {now}
version: 0.1
status: Draft
---

# {title}

## Overview
Brief description of this document.

## Details
Main content and details.

## References
- [Link to related resource](#)
"""

            return json.dumps(self.format_response(
                data={
                    "template": template,
                    "template_type": template_type
                }
            ))
        except Exception as e:
            return json.dumps(
                self.handle_error(
                    e, "MarkdownTool._generate_template"))

    def _extract_frontmatter(self, content: str) -> str:
        """Extract frontmatter from markdown content."""
        try:
            post = frontmatter.loads(content)

            return json.dumps(self.format_response(
                data={
                    "frontmatter": dict(post.metadata),
                    "content": post.content
                }
            ))
        except Exception as e:
            return json.dumps(
                self.handle_error(
                    e, "MarkdownTool._extract_frontmatter"))

    def _add_frontmatter(self, content: str, metadata: Dict[str, Any]) -> str:
        """Add or update frontmatter in markdown content."""
        try:
            # Check if content already has frontmatter
            if content.startswith('---'):
                post = frontmatter.loads(content)
                # Update existing frontmatter
                for key, value in metadata.items():
                    post[key] = value
                result = frontmatter.dumps(post)
            else:
                # Create new frontmatter
                post = frontmatter.Post(content, **metadata)
                result = frontmatter.dumps(post)

            return json.dumps(self.format_response(
                data={
                    "content_with_frontmatter": result
                }
            ))
        except Exception as e:
            return json.dumps(
                self.handle_error(
                    e, "MarkdownTool._add_frontmatter"))
