#!/usr/bin/env python3
"""
Report Management Script
Implements retention policies for generated reports to prevent accumulation
"""

import shutil
import time
from datetime import datetime
from pathlib import Path
from typing import List, Optional


class ReportManager:
    """Manages generated reports with retention policies."""
    
    def __init__(self, root_path: Optional[Path] = None):
        self.root_path = root_path or Path.cwd()
        self.reports_dir = self.root_path / "reports" / "archived"
        self.reports_dir.mkdir(parents=True, exist_ok=True)
        
        # Retention policies (in days)
        self.retention_policies = {
            "bandit-report.json": 7,  # Keep security reports for 1 week
            "*_ruff_report.json": 3,   # Keep linting reports for 3 days
            "coverage.xml": 1,         # Coverage reports only for current run
            "htmlcov": 0,              # HTML coverage - delete immediately after use
            "validation_report.json": 14,  # Keep validation reports for 2 weeks
        }
    
    def archive_report(self, report_path: Path) -> bool:
        """Archive a report file with timestamp."""
        if not report_path.exists():
            return False
            
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        archive_name = f"{report_path.stem}_{timestamp}{report_path.suffix}"
        archive_path = self.reports_dir / archive_name
        
        try:
            if report_path.is_dir():
                shutil.copytree(report_path, archive_path)
            else:
                shutil.copy2(report_path, archive_path)
            
            print(f"✅ Archived: {report_path.name} -> {archive_name}")
            return True
        except Exception as e:
            print(f"❌ Failed to archive {report_path.name}: {e}")
            return False
    
    def clean_report(self, report_path: Path) -> bool:
        """Remove a report file or directory."""
        if not report_path.exists():
            return True
            
        try:
            if report_path.is_dir():
                shutil.rmtree(report_path)
            else:
                report_path.unlink()
            
            print(f"🗑️  Removed: {report_path.name}")
            return True
        except Exception as e:
            print(f"❌ Failed to remove {report_path.name}: {e}")
            return False
    
    def get_matching_files(self, pattern: str) -> List[Path]:
        """Get files matching a pattern."""
        if "*" in pattern:
            # Handle wildcard patterns
            import glob
            return [Path(p) for p in glob.glob(str(self.root_path / pattern))]
        else:
            # Handle exact paths
            path = self.root_path / pattern
            return [path] if path.exists() else []
    
    def manage_report(self, pattern: str, retention_days: int) -> None:
        """Manage reports according to retention policy."""
        matching_files = self.get_matching_files(pattern)
        
        for report_path in matching_files:
            if not report_path.exists():
                continue
                
            # Get file age
            try:
                file_age = time.time() - report_path.stat().st_mtime
                age_days = file_age / (24 * 3600)
            except OSError:
                continue
            
            # Apply retention policy
            if retention_days == 0:
                # Immediate deletion
                self.clean_report(report_path)
            elif age_days > retention_days:
                # Archive then delete if old enough
                if self.archive_report(report_path):
                    self.clean_report(report_path)
            else:
                print(f"📁 Keeping: {report_path.name} (age: {age_days:.1f} days)")
    
    def clean_old_archives(self, max_age_days: int = 30) -> None:
        """Clean old archived reports."""
        if not self.reports_dir.exists():
            return
            
        cutoff_time = time.time() - (max_age_days * 24 * 3600)
        
        for archive_file in self.reports_dir.iterdir():
            try:
                if archive_file.stat().st_mtime < cutoff_time:
                    if archive_file.is_dir():
                        shutil.rmtree(archive_file)
                    else:
                        archive_file.unlink()
                    print(f"🗑️  Cleaned old archive: {archive_file.name}")
            except OSError:
                continue
    
    def run_retention_policies(self) -> None:
        """Run all retention policies."""
        print("🗂️  Running report retention policies...")
        
        for pattern, retention_days in self.retention_policies.items():
            print(f"\n📋 Processing pattern: {pattern} (retention: {retention_days} days)")
            self.manage_report(pattern, retention_days)
        
        # Clean old archives
        print("\n🗄️  Cleaning archives older than 30 days...")
        self.clean_old_archives()
        
        print("\n✅ Report retention policies completed!")
    
    def immediate_cleanup(self) -> None:
        """Immediately clean all generated reports (emergency cleanup)."""
        print("🚨 Emergency cleanup: Removing all generated reports...")
        
        cleanup_patterns = [
            "bandit-report.json",
            "*_ruff_report.json", 
            "coverage.xml",
            "htmlcov",
            ".coverage*"
        ]
        
        for pattern in cleanup_patterns:
            matching_files = self.get_matching_files(pattern)
            for report_path in matching_files:
                self.clean_report(report_path)
        
        print("✅ Emergency cleanup completed!")


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Manage generated reports with retention policies")
    parser.add_argument("--emergency-cleanup", action="store_true", 
                       help="Immediately remove all generated reports")
    parser.add_argument("--dry-run", action="store_true", 
                       help="Show what would be done without making changes")
    
    args = parser.parse_args()
    
    manager = ReportManager()
    
    if args.emergency_cleanup:
        if not args.dry_run:
            manager.immediate_cleanup()
        else:
            print("🔍 Dry run: Would perform emergency cleanup of all reports")
    else:
        if not args.dry_run:
            manager.run_retention_policies()
        else:
            print("🔍 Dry run: Would run retention policies (not implemented)")


if __name__ == "__main__":
    main()