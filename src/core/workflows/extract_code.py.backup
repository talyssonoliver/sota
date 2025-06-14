#!/usr/bin/env python3
"""
Step 4.5 — Code Extraction (Postprocessing)

Automated code block extraction from agent outputs using regex patterns.
Features include multi-language support, Git integration, batch processing,
and comprehensive testing.
"""

import json
import os
import re
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional


@dataclass
class CodeExtractionResult:
    """Result of code extraction operation."""
    task_id: str
    agent_id: str
    source_file: str
    extracted_files: List[str]
    extraction_time: str
    total_code_blocks: int
    languages_detected: List[str]
    git_commit_hash: Optional[str] = None


class CodeExtractor:
    """Advanced code extraction system for AI agent outputs."""

    def __init__(self, base_outputs_dir: Optional[str] = None):
        """
        Initialize code extractor.

        Args:
            base_outputs_dir: Base directory containing task outputs (default: ./outputs)
        """
        if base_outputs_dir:
            self.base_outputs_dir = Path(base_outputs_dir)
        else:
            self.base_outputs_dir = Path("outputs")

        # Language to file extension mapping
        self.language_extensions = {
            'typescript': '.ts',
            'ts': '.ts',
            'javascript': '.js',
            'js': '.js',
            'python': '.py',
            'py': '.py',
            'sql': '.sql',
            'yaml': '.yaml',
            'yml': '.yml',
            'json': '.json',
            'html': '.html',
            'css': '.css',
            'scss': '.scss',
            'sass': '.sass',
            'less': '.less',
            'xml': '.xml',
            'dockerfile': '.dockerfile',
            'docker': '.dockerfile',
            'bash': '.sh',
            'sh': '.sh',
            'zsh': '.zsh',
            'powershell': '.ps1',
            'ps1': '.ps1',
            'go': '.go',
            'rust': '.rs',
            'java': '.java',
            'c': '.c',
            'cpp': '.cpp',
            'csharp': '.cs',
            'cs': '.cs',
            'php': '.php',
            'ruby': '.rb',
            'swift': '.swift',
            'kotlin': '.kt'
        }

        # Code block patterns (ordered from most specific to least specific)
        self.code_patterns = [
            # Pattern 1: JSON-structured metadata (most specific)
            r'```(\w+)?\s*\{\s*"filename":\s*"([^"]+)"[^}]*\}\n(.*?)\n```',
            # Pattern 2: Standard with filename comment
            r'```(\w+)?\s*(?:(?:\/\/|--|#)\s*filename:\s*([^\n]+))\n(.*?)\n```',
            # Pattern 3: Simple language block (no filename, least specific)
            r'```(\w+)\n(.*?)\n```'
        ]

    def extract_from_task_agent(
        self,
        task_id: str,
        agent_id: str,
        commit_to_git: bool = False,
        force_reextract: bool = False
    ) -> CodeExtractionResult:
        """
        Extract code from a specific task's agent output.

        Args:
            task_id: Task identifier (e.g., 'BE-07')
            agent_id: Agent identifier (e.g., 'backend', 'frontend')
            commit_to_git: Whether to commit extracted code to Git
            force_reextract: Whether to force re-extraction even if already done

        Returns:
            CodeExtractionResult with extraction details
        """
        task_dir = self.base_outputs_dir / task_id

        # Find the agent output file
        output_file = None
        for potential_file in [
            task_dir / f"output_{agent_id}.md",
            task_dir / f"{agent_id}_output.md",
            task_dir / f"output_{agent_id}.txt"
        ]:
            if potential_file.exists():
                output_file = potential_file
                break

        if not output_file:
            raise FileNotFoundError(
                f"No output file found for task {task_id}, agent {agent_id}")

        # Check if extraction already done (unless force re-extract)
        code_dir = task_dir / "code"
        if code_dir.exists() and not force_reextract and any(code_dir.iterdir()):
            print(
                f"ℹ️  Code already extracted for {task_id}:{agent_id}. Use --force to re-extract.")
            # Return existing extraction info
            return self._get_existing_extraction_info(
                task_id, agent_id, str(output_file))

        # Perform extraction
        return self._extract_code_blocks(
            task_id, agent_id, output_file, commit_to_git)

    def _extract_code_blocks(
        self,
        task_id: str,
        agent_id: str,
        source_file: Path,
        commit_to_git: bool = False
    ) -> CodeExtractionResult:
        """Extract code blocks from markdown file using advanced pattern matching."""
        print(f"🔍 Extracting code from {source_file.name}...")

        content = source_file.read_text(encoding='utf-8')
        task_dir = self.base_outputs_dir / task_id
        code_dir = task_dir / "code"
        code_dir.mkdir(exist_ok=True)

        extracted_files = []
        languages_detected = []
        total_blocks = 0
        # Collect all matches from all patterns, avoiding duplicates
        seen_blocks = set()
        block_counter = 0

        for pattern in self.code_patterns:
            matches = list(re.finditer(pattern, content, re.DOTALL))
            for match in matches:
                # Create a unique identifier for this code block
                block_id = (match.start(), match.end())
                if block_id in seen_blocks:
                    continue  # Skip duplicate blocks
                seen_blocks.add(block_id)

                block_counter += 1
                total_blocks += 1

                if len(match.groups()) == 3:  # Pattern with filename
                    language, filename, code_content = match.groups()
                elif len(match.groups()) == 2:  # Pattern without filename
                    language, code_content = match.groups()
                    filename = None
                else:
                    continue

                # Process the extracted code
                extracted_file = self._save_code_block(
                    code_dir, language, filename, code_content, block_counter
                )

                if extracted_file:
                    extracted_files.append(str(extracted_file))
                    if language and language.lower() not in languages_detected:
                        languages_detected.append(language.lower())

        # Handle Git commit if requested
        git_commit_hash = None
        if commit_to_git and extracted_files:
            git_commit_hash = self._commit_to_git(
                task_id, agent_id, extracted_files)

        # Create result metadata
        result = CodeExtractionResult(
            task_id=task_id,
            agent_id=agent_id,
            source_file=str(source_file),
            extracted_files=extracted_files,
            extraction_time=datetime.now().isoformat(),
            total_code_blocks=total_blocks,
            languages_detected=languages_detected,
            git_commit_hash=git_commit_hash
        )

        # Save extraction metadata
        self._save_extraction_metadata(task_dir, result)

        print(
            f"✅ Extracted {
                len(extracted_files)} code files from {total_blocks} blocks")
        print(f"   📁 Languages: {', '.join(languages_detected)}")
        if git_commit_hash:
            print(f"   🔗 Git commit: {git_commit_hash}")

        return result

    def _save_code_block(
        self,
        code_dir: Path,
        language: Optional[str],
        filename: Optional[str],
        code_content: str,
        block_index: int
    ) -> Optional[Path]:
        """Save a single code block to file with proper naming."""
        if not code_content.strip():
            return None

        # Determine filename
        if filename:
            # Clean up filename
            filename = filename.strip().strip('"\'')
            if filename.startswith('./'):
                filename = filename[2:]
            # Flatten directory structure for simplicity
            filename = filename.replace('/', '_').replace('\\', '_')
        else:
            # Generate filename from language and index
            language = language or 'txt'
            ext = self.language_extensions.get(language.lower(), '.txt')
            filename = f"extracted_code_{block_index}{ext}"

        # Ensure we have a valid filename
        if not filename:
            filename = f"code_block_{block_index}.txt"

        # Write the file
        code_file_path = code_dir / filename
        try:
            code_file_path.write_text(code_content, encoding='utf-8')
            print(f"   📄 {filename} ({len(code_content)} chars)")
            return code_file_path
        except Exception as e:
            print(f"   ❌ Error saving {filename}: {e}")
            return None

    def _commit_to_git(self, task_id: str, agent_id: str,
                       extracted_files: List[str]) -> Optional[str]:
        """Commit extracted code files to Git repository."""
        try:
            # Check if we're in a Git repository
            result = subprocess.run(['git',
                                     'rev-parse',
                                     '--is-inside-work-tree'],
                                    capture_output=True,
                                    text=True,
                                    cwd=self.base_outputs_dir.parent)
            if result.returncode != 0:
                print("⚠️  Not in a Git repository. Skipping commit.")
                return None

            # Add extracted files to Git
            for file_path in extracted_files:
                subprocess.run(['git', 'add', file_path],
                               cwd=self.base_outputs_dir.parent)

            # Create commit message
            commit_msg = f"Extract code from {task_id}:{agent_id} - {
                len(extracted_files)} files"

            # Commit the changes
            result = subprocess.run(['git',
                                     'commit',
                                     '-m',
                                     commit_msg],
                                    capture_output=True,
                                    text=True,
                                    cwd=self.base_outputs_dir.parent)

            if result.returncode == 0:
                # Get commit hash
                hash_result = subprocess.run(['git',
                                              'rev-parse',
                                              'HEAD'],
                                             capture_output=True,
                                             text=True,
                                             cwd=self.base_outputs_dir.parent)
                return hash_result.stdout.strip()[:8]
            else:
                print(f"⚠️  Git commit failed: {result.stderr}")
                return None

        except Exception as e:
            print(f"⚠️  Git commit error: {e}")
            return None

    def _save_extraction_metadata(
            self,
            task_dir: Path,
            result: CodeExtractionResult):
        """Save extraction metadata to JSON file."""
        metadata_file = task_dir / "code_extraction_metadata.json"
        metadata = {
            "task_id": result.task_id,
            "agent_id": result.agent_id,
            "source_file": result.source_file,
            "extracted_files": result.extracted_files,
            "extraction_time": result.extraction_time,
            "total_code_blocks": result.total_code_blocks,
            "languages_detected": result.languages_detected,
            "git_commit_hash": result.git_commit_hash
        }

        try:
            metadata_file.write_text(json.dumps(
                metadata, indent=2), encoding='utf-8')
        except Exception as e:
            print(f"⚠️  Could not save metadata: {e}")

    def _get_existing_extraction_info(
            self,
            task_id: str,
            agent_id: str,
            source_file: str) -> CodeExtractionResult:
        """Get information about existing extraction."""
        task_dir = self.base_outputs_dir / task_id
        metadata_file = task_dir / "code_extraction_metadata.json"

        if metadata_file.exists():
            try:
                metadata = json.loads(
                    metadata_file.read_text(encoding='utf-8'))
                return CodeExtractionResult(
                    task_id=metadata.get("task_id", task_id),
                    agent_id=metadata.get("agent_id", agent_id),
                    source_file=metadata.get("source_file", source_file),
                    extracted_files=metadata.get("extracted_files", []),
                    extraction_time=metadata.get("extraction_time", ""),
                    total_code_blocks=metadata.get("total_code_blocks", 0),
                    languages_detected=metadata.get("languages_detected", []),
                    git_commit_hash=metadata.get("git_commit_hash")
                )
            except Exception:
                pass

        # Fallback to scanning the code directory
        code_dir = task_dir / "code"
        extracted_files = []
        languages_detected = []

        if code_dir.exists():
            for file_path in code_dir.iterdir():
                if file_path.is_file():
                    extracted_files.append(str(file_path))
                    # Try to detect language from extension
                    ext = file_path.suffix.lower()
                    for lang, lang_ext in self.language_extensions.items():
                        if lang_ext == ext and lang not in languages_detected:
                            languages_detected.append(lang)
                            break

        return CodeExtractionResult(
            task_id=task_id,
            agent_id=agent_id,
            source_file=source_file,
            extracted_files=extracted_files,
            extraction_time="",
            total_code_blocks=len(extracted_files),
            languages_detected=languages_detected
        )

    def extract_from_all_agents(self,
                                task_id: str,
                                commit_to_git: bool = False) -> Dict[str,
                                                                     CodeExtractionResult]:
        """Extract code from all agents for a given task."""
        task_dir = self.base_outputs_dir / task_id
        if not task_dir.exists():
            raise FileNotFoundError(f"Task directory not found: {task_dir}")

        results = {}
        agents = ['backend', 'frontend', 'qa', 'doc', 'technical']

        for agent_id in agents:
            try:
                result = self.extract_from_task_agent(
                    task_id, agent_id, commit_to_git)
                results[agent_id] = result
            except FileNotFoundError:
                # Agent output file doesn't exist, skip
                continue

        return results

    def batch_extract(self,
                      task_ids: List[str],
                      commit_to_git: bool = False) -> Dict[str,
                                                           Dict[str,
                                                                CodeExtractionResult]]:
        """Batch extract code from multiple tasks."""
        all_results = {}

        for task_id in task_ids:
            try:
                task_results = self.extract_from_all_agents(
                    task_id, commit_to_git)
                if task_results:
                    all_results[task_id] = task_results
            except Exception as e:
                print(f"⚠️  Error processing task {task_id}: {e}")

        return all_results


def main():
    """CLI interface for code extraction."""
    import argparse

    parser = argparse.ArgumentParser(
        description='Extract code blocks from AI agent outputs')
    parser.add_argument('--task-id', required=True,
                        help='Task ID (e.g., BE-07)')
    parser.add_argument(
        '--agent-id', help='Agent ID (e.g., backend, frontend)')
    parser.add_argument('--outputs-dir', default='outputs',
                        help='Base outputs directory')
    parser.add_argument('--commit', action='store_true',
                        help='Commit extracted code to Git')
    parser.add_argument('--force', action='store_true',
                        help='Force re-extraction')
    parser.add_argument('--all-agents', action='store_true',
                        help='Extract from all agents')
    parser.add_argument('--batch', nargs='+',
                        help='Batch process multiple task IDs')

    args = parser.parse_args()

    extractor = CodeExtractor(args.outputs_dir)

    try:
        if args.batch:
            # Batch processing
            results = extractor.batch_extract(args.batch, args.commit)
            print(
                f"\n🎯 Batch processing complete: {
                    len(results)} tasks processed")

        elif args.all_agents:
            # All agents for one task
            results = extractor.extract_from_all_agents(
                args.task_id, args.commit)
            print(
                f"\n🎯 Extracted from {
                    len(results)} agents for task {
                    args.task_id}")

        else:
            # Single task/agent
            if not args.agent_id:
                parser.error(
                    "--agent-id is required when not using --all-agents")

            result = extractor.extract_from_task_agent(
                args.task_id,
                args.agent_id,
                args.commit,
                args.force
            )

            print(f"\n🎯 Extraction complete:")
            print(f"   📁 {len(result.extracted_files)} files extracted")
            print(f"   🔤 Languages: {', '.join(result.languages_detected)}")

    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
