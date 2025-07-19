# Configuration Reference

This document summarizes key configuration files and environment variables used throughout the project.

## Environment Variables

| Variable | Description | Used By |
|----------|-------------|--------|
| `SUPABASE_URL` | URL for Supabase instance | Supabase tools |
| `SUPABASE_KEY` | API key for Supabase | Supabase tools |
| `GITHUB_TOKEN` | Access token for GitHub API | GitHub tool, CI scripts |
| `VERCEL_TOKEN` | Deployment token for Vercel | Vercel tool |
| `OPENAI_API_KEY` | OpenAI API key | Agents, memory engine |
| `NEXT_PUBLIC_SUPABASE_URL` | Frontend Supabase URL | Dashboard scripts |
| `NEXT_PUBLIC_SUPABASE_ANON_KEY` | Supabase anon key for frontend | Dashboard scripts |

Additional variables may be referenced in specific scripts or tools. Check each tool documentation for details.

## Configuration Files

| File | Format | Purpose |
|------|--------|---------|
| `config/agents.yaml` | YAML | Defines all agent roles, prompts and tool assignments |
| `config/tools.yaml` | YAML | Lists available tools, their classes and environment variables |
| `config/daily_cycle.json` | JSON | Settings for the daily automation cycle including email notifications |
| `config/qa_thresholds.yaml` | YAML | QA coverage thresholds and quality gates |
| `config/schemas/task.schema.json` | JSON Schema | Validation schema for task YAML files |

## Build and Packaging

- **pyproject.toml** – declares the project package and dependencies.
- **requirements.txt** – Python package requirements.
- **requirements-enterprise.txt** – Additional enterprise dependencies.
- **pytest.ini** – Pytest configuration options.

