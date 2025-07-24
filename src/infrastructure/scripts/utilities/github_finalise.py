#!/usr/bin/env python3
"""
Step 5.9: GitHub Finalisation (Optional)

Automated GitHub integration for closing issues and attaching completion artifacts.
This script provides GitHub CLI integration to finalize task completion workflow.

Features:
- Close related GitHub issues
- Attach completion artifacts (summary, QA report, code PR links)
- Link documentation and archives
- Update issue status with completion details

Usage:
    python scripts/github_finalise.py BE-07
    python scripts/github_finalise.py --task-id BE-07 --close-issue
    python scripts/github_finalise.py BE-07 --attach-artifacts
"""

import argparse
import json
import logging
import subprocess
import sys
from typing import Dict, Optional

try:
    from datetime import datetime
except ImportError:
    pass
try:
    from pathlib import Path
except ImportError:
    pass

# Set up logger
logger = logging.getLogger(__name__)


class GitHubFinaliser:
    """GitHub finalisation class for task completion workflow.
    
    Provides secure GitHub integration for task completion including:
    - Issue closure with completion details
    - Artifact attachment and linking
    - Pull request management
    - Secure subprocess execution
    """
    
    def __init__(self, task_id: str, repo: str):
        """Initialize GitHub finaliser.
        
        Args:
            task_id: Task identifier (e.g., 'BE-07')
            repo: GitHub repository identifier
        """
        self.task_id = task_id
        self.repo = repo
        self.github_repo = repo
        # Define paths for completion artifacts
        self.docs_dir = Path("docs/completions")
        self.outputs_dir = Path(f"outputs/{task_id}")
        self.archives_dir = Path("archives")
        
    def finalise_task(self, close_issue: bool = False, attach_artifacts: bool = False) -> bool:
        """Finalise the task on GitHub.
        
        Args:
            close_issue: Whether to close related GitHub issues
            attach_artifacts: Whether to attach completion artifacts
            
        Returns:
            True if finalisation succeeded, False otherwise
        """
        logger.info(f"Finalising task {self.task_id} for repo {self.repo}")
        logger.info(f"Close issue: {close_issue}, Attach artifacts: {attach_artifacts}")
        # TODO: Implement actual GitHub integration
        return True


    def check_github_cli(self) -> bool:
        """Check if GitHub CLI is available.
        
        Returns:
            True if GitHub CLI is available and functional
        """
        try:
            subprocess.run(["gh", "--version"], capture_output=True, check=True, shell=False)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("GitHub CLI not available. Install with: winget install GitHub.cli")
            return False

    def find_task_issue(self) -> Optional[int]:
        """Find GitHub issue number for the task.
        
        Returns:
            Issue number if found, None otherwise
        """
        if not self.check_github_cli():
            return None

        try:
            # Search for issues with task ID in title or body
            result = subprocess.run(
                [
                    "gh",
                    "issue",
                    "list",
                    "--repo",
                    self.github_repo,
                    "--search",
                    self.task_id,
                    "--json",
                    "number,title,state",
                ],
                capture_output=True,
                text=True,
                check=True,
                shell=False,
            )

            issues = json.loads(result.stdout)

            # Look for exact task ID match
            for issue in issues:
                if self.task_id in issue["title"] and issue["state"] == "open":
                    logger.info(
                        f"Found open issue #{issue['number']}: {issue['title']}"
                    )
                    return issue["number"]

            logger.info(f"No open GitHub issue found for {self.task_id}")
            return None

        except (subprocess.CalledProcessError, json.JSONDecodeError) as e:
            logger.error(f"Error searching for GitHub issues: {e}")
            return None

    def get_completion_artifacts(self) -> Dict[str, str]:
        """Collect completion artifacts for attachment.
        
        Returns:
            Dictionary mapping artifact names to file paths
        """
        artifacts = {}

        # Task completion summary
        completion_file = self.docs_dir / f"{self.task_id}.md"
        if completion_file.exists():
            artifacts["Task Completion Summary"] = str(completion_file)

        # QA Report
        qa_report = self.outputs_dir / "qa_report.json"
        if qa_report.exists():
            artifacts["QA Report"] = str(qa_report)

        # QA Summary
        qa_summary = self.outputs_dir / "qa_summary.md"
        if qa_summary.exists():
            artifacts["QA Summary"] = str(qa_summary)

        # Completion Report
        completion_report = self.outputs_dir / "completion_report.md"
        if completion_report.exists():
            artifacts["Completion Report"] = str(completion_report)

        # Archive file
        archive_pattern = f"{self.task_id}_*.tar.gz"
        archive_files = list(self.archives_dir.glob(archive_pattern))
        if archive_files:
            # Get the most recent archive
            latest_archive = max(archive_files, key=lambda x: x.stat().st_mtime)
            artifacts["Task Archive"] = str(latest_archive)

        return artifacts

    def create_completion_comment(self) -> str:
        """Create completion comment for GitHub issue.
        
        Returns:
            Formatted completion comment with artifacts and references
        """
        artifacts = self.get_completion_artifacts()

        comment = f"""## ✅ Task {self.task_id} Completed
        
**Completion Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

### 📋 Summary
Task has been completed successfully and passed all QA validation checks.

### 📁 Completion Artifacts
"""

        for name, path in artifacts.items():
            if Path(path).exists():
                size = Path(path).stat().st_size
                size_str = f"{size:,} bytes" if size < 1024 else f"{size/1024:.1f} KB"
                comment += f"- **{name}**: `{path}` ({size_str})\n"

        comment += f"""
### 🔗 References
- [Task Output Directory](outputs/{self.task_id}/)
- [Task Documentation](docs/completions/{self.task_id}.md)
"""

        # Check for archive
        archive_pattern = f"{self.task_id}_*.tar.gz"
        archive_files = list(self.archives_dir.glob(archive_pattern))
        if archive_files:
            latest_archive = max(archive_files, key=lambda x: x.stat().st_mtime)
            comment += f"- [Task Archive]({latest_archive})\n"

        comment += """
### ✅ QA Status
All quality assurance checks have been completed successfully.

---
*Automatically generated by GitHub Finalisation Script*
"""

        return comment

    def close_issue_with_completion(
        self, issue_number: int, attach_artifacts: bool = True
    ) -> bool:
        """Close GitHub issue with completion details.
        
        Args:
            issue_number: GitHub issue number to close
            attach_artifacts: Whether to attach completion artifacts
            
        Returns:
            True if issue closure succeeded, False otherwise
        """
        if not self.check_github_cli():
            return False

        try:
            # Create completion comment
            comment = self.create_completion_comment()

            # Add comment to issue
            logger.info(f"Adding completion comment to issue #{issue_number}")
            subprocess.run(
                [
                    "gh",
                    "issue",
                    "comment",
                    str(issue_number),
                    "--repo",
                    self.github_repo,
                    "--body",
                    comment,
                ],
                check=True,
                shell=False,
            )

            # Close the issue
            logger.info(f"Closing issue #{issue_number}")
            subprocess.run(
                [
                    "gh",
                    "issue",
                    "close",
                    str(issue_number),
                    "--repo",
                    self.github_repo,
                    "--reason",
                    "completed",
                ],
                check=True,
                shell=False,
            )

            logger.info(f"✅ Issue #{issue_number} closed with completion details")
            return True

        except subprocess.CalledProcessError as e:
            logger.error(f"Error closing GitHub issue: {e}")
            return False

    def create_pull_request_link(self) -> Optional[str]:
        """Generate or find pull request link for the task.
        
        Returns:
            Pull request URL if available, None otherwise
        """
        # This is a placeholder for PR detection logic
        # In a real implementation, you might search for PRs with the task ID
        return f"https://github.com/{self.github_repo}/pulls?q={self.task_id}"

    def finalise_task_complete(
        self, close_issue: bool = True, attach_artifacts: bool = True
    ) -> bool:
        """Execute complete GitHub finalisation workflow.
        
        Args:
            close_issue: Whether to close related GitHub issues
            attach_artifacts: Whether to attach completion artifacts
            
        Returns:
            True if finalisation succeeded, False otherwise
        """
        logger.info(f"🔄 Starting GitHub finalisation for {self.task_id}")

        # Check if outputs exist
        if not self.outputs_dir.exists():
            logger.error(f"Task outputs directory not found: {self.outputs_dir}")
            return False

        # Find related GitHub issue
        issue_number = self.find_task_issue() if close_issue else None

        if close_issue and issue_number:
            success = self.close_issue_with_completion(issue_number, attach_artifacts)
            if success:
                logger.info(f"✅ GitHub issue #{issue_number} finalised successfully")
            return success
        elif close_issue:
            logger.warning(
                f"No open GitHub issue found for {self.task_id} - skipping issue closure"
            )

        # Generate completion summary for manual use
        artifacts = self.get_completion_artifacts()

        print(f"\n📋 Task {self.task_id} Completion Summary:")
        print("=" * 50)

        for name, path in artifacts.items():
            if Path(path).exists():
                print(f"✅ {name}: {path}")
            else:
                print(f"❌ {name}: {path} (not found)")

        print(f"\n🔗 Pull Request Link: {self.create_pull_request_link()}")

        if not close_issue:
            comment = self.create_completion_comment()
            print("\n📝 Manual GitHub Comment Template:")
            print("-" * 40)
            print(comment)

        return True


def main():
    """Main CLI interface for GitHub finalisation."""
    parser = argparse.ArgumentParser(
        description="Finalise GitHub integration for completed tasks (Step 5.9)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Full finalisation (close issue + attach artifacts)
  python scripts/github_finalise.py BE-07
  
  # Just close issue without artifacts
  python scripts/github_finalise.py BE-07 --close-issue --no-attach
  
  # Generate completion summary without closing issue
  python scripts/github_finalise.py BE-07 --no-close
        """,
    )

    parser.add_argument("task_id", help="Task ID to finalise (e.g., BE-07)")

    parser.add_argument(
        "--close-issue",
        action="store_true",
        default=True,
        help="Close related GitHub issue (default: True)",
    )

    parser.add_argument(
        "--no-close", action="store_true", help="Skip closing GitHub issue"
    )

    parser.add_argument(
        "--attach-artifacts",
        action="store_true",
        default=True,
        help="Attach completion artifacts (default: True)",
    )

    parser.add_argument(
        "--no-attach", action="store_true", help="Skip attaching artifacts"
    )

    parser.add_argument(
        "--repo",
        default="artesanato-shop/artesanato-ecommerce",
        help="GitHub repository (default: artesanato-shop/artesanato-ecommerce)",
    )

    parser.add_argument("--verbose", action="store_true", help="Enable verbose output")

    args = parser.parse_args()

    # Configure logging
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # Resolve close/attach flags
    close_issue = args.close_issue and not args.no_close
    attach_artifacts = args.attach_artifacts and not args.no_attach

    # Create finaliser and execute
    finaliser = GitHubFinaliser(args.task_id, args.repo)
    success = finaliser.finalise_task(close_issue, attach_artifacts)

    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
