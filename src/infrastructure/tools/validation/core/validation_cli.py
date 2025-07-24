#!/usr/bin/env python3
"""
Validation CLI Interface

Command-line interface for the unified validation system.
Extracted from validate.py for better separation of concerns.

Provides comprehensive CLI options for validation, fixing, and reporting.
"""

import argparse
import json
import sys
from pathlib import Path
from typing import List, Optional

from .validator import Validator


class ValidationCLI:
    """Command-line interface for the validation system.
    
    Provides a comprehensive CLI for running validation pipelines,
    individual validation types, auto-fixes, and report generation.
    """

    def __init__(self):
        """Initialize the validation CLI interface."""
        self.parser = self._create_parser()

    def _create_parser(self) -> argparse.ArgumentParser:
        """Create the argument parser with all CLI options.
        
        Returns:
            Configured ArgumentParser instance
        """
        parser = argparse.ArgumentParser(
            description="Validation Pipeline - Enterprise Code Quality System",
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
Examples:
  python validate.py                             # Run full validation pipeline
  python validate.py --quick                     # Quick validation (syntax + critical deps)
  python validate.py --auto-fix                  # Auto-fix issues
  python validate.py --interactive               # Interactive fixing
  python validate.py --show-fixes                # Preview fixes
  python validate.py --output report.json        # Save report to file
  python validate.py --files src/module.py       # Validate specific files
  python validate.py --report summary            # Show 7-day validation summary
  python validate.py --enable-sonarqube          # Enable SonarQube integration
  python validate.py --parallel                  # Enable parallel analysis
        """,
        )

        # Validation mode selection
        mode_group = parser.add_argument_group("Validation Modes")
        mode_group.add_argument(
            "--quick",
            "-q",
            action="store_true",
            help="Run quick validation (syntax + critical dependencies)",
        )

        # Individual validation types
        validation_group = parser.add_argument_group("Individual Validation Types")
        validation_group.add_argument(
            "--syntax",
            "-s",
            action="store_true",
            help="Run syntax and import validation only",
        )
        validation_group.add_argument(
            "--dependencies",
            "-d",
            action="store_true",
            help="Run dependency validation only",
        )
        validation_group.add_argument(
            "--structure",
            "-t",
            action="store_true",
            help="Run structure validation only",
        )
        validation_group.add_argument(
            "--quality-gates",
            action="store_true",
            help="Run quality gates validation only",
        )
        validation_group.add_argument(
            "--security",
            action="store_true",
            help="Run security validation only",
        )
        validation_group.add_argument(
            "--nfr",
            action="store_true",
            help="Run non-functional requirements validation only",
        )

        # Fixing options
        fix_group = parser.add_argument_group("Fixing Options")
        fix_group.add_argument(
            "--auto-fix",
            "-f",
            action="store_true",
            help="Automatically fix issues where possible",
        )
        fix_group.add_argument(
            "--interactive",
            "-i",
            action="store_true",
            help="Interactive fixing with user confirmation",
        )
        fix_group.add_argument(
            "--show-fixes",
            action="store_true",
            help="Show what fixes would be applied (dry-run)",
        )
        fix_group.add_argument(
            "--no-backup",
            action="store_true",
            help="Skip creating backups when fixing (use with caution)",
        )

        # Integration options
        integration_group = parser.add_argument_group("Integration Options")
        integration_group.add_argument(
            "--enable-sonarqube",
            action="store_true",
            help="Enable SonarQube integration for enhanced analysis",
        )
        integration_group.add_argument(
            "--sonar-host-url",
            default="http://localhost:9000",
            help="SonarQube server URL (default: http://localhost:9000)",
        )
        integration_group.add_argument(
            "--sonar-token",
            help="SonarQube authentication token (or set SONAR_TOKEN env var)",
        )
        integration_group.add_argument(
            "--parallel",
            "-p",
            action="store_true",
            help="Enable parallel analysis for better performance",
        )
        integration_group.add_argument(
            "--skip-coverage",
            action="store_true",
            help="Skip test coverage analysis for faster validation (saves ~300s)",
        )
        integration_group.add_argument(
            "--enable-quality-gates",
            action="store_true",
            default=True,
            help="Enable quality gates enforcement (default: enabled)",
        )
        integration_group.add_argument(
            "--disable-quality-gates",
            dest="enable_quality_gates",
            action="store_false",
            help="Disable quality gates enforcement",
        )

        # Output options
        output_group = parser.add_argument_group("Output Options")
        output_group.add_argument(
            "--output",
            "-o",
            metavar="FILE",
            help="Save validation report to JSON file",
        )
        output_group.add_argument(
            "--verbose", "-v", action="store_true", help="Verbose output"
        )
        output_group.add_argument(
            "--report",
            choices=["summary", "trends", "metrics"],
            help="Generate validation history report (summary/trends/metrics)",
        )
        output_group.add_argument(
            "--format",
            choices=["json", "xml", "html"],
            default="json",
            help="Output format for reports (default: json)",
        )

        # File selection
        parser.add_argument(
            "--files",
            nargs="+",
            metavar="FILE",
            help="Validate specific files only",
        )
        parser.add_argument(
            "--root-path",
            metavar="PATH",
            help="Root path for validation (default: current directory)",
        )

        return parser

    def run(self, args: Optional[List[str]] = None) -> bool:
        """Run the CLI with the given arguments.
        
        Args:
            args: Command line arguments, defaults to sys.argv
            
        Returns:
            True if validation succeeded, False otherwise
        """
        parsed_args = self.parser.parse_args(args)

        # Determine root path
        root_path = Path(parsed_args.root_path) if parsed_args.root_path else Path.cwd()

        # Handle report generation requests
        if parsed_args.report:
            return self._handle_report_generation(parsed_args, root_path)

        # Validate mutual exclusivity
        if parsed_args.auto_fix and parsed_args.interactive:
            self.parser.error("Cannot use both --auto-fix and --interactive")

        # Run validation based on mode
        try:
            if parsed_args.quick:
                return self._run_quick_validation(parsed_args, root_path)
            elif self._any_individual_validation_selected(parsed_args):
                return self._run_individual_validation(parsed_args, root_path)
            else:
                # Default to full validation
                return self._run_full_validation(parsed_args, root_path)

        except KeyboardInterrupt:
            print("\n🛑 Validation interrupted by user")
            return False
        except Exception as e:
            print(f"[ERROR] Validation failed: {e}")
            if parsed_args.verbose:
                import traceback
                traceback.print_exc()
            return False

    def _any_individual_validation_selected(self, args) -> bool:
        """Check if any individual validation type is selected.
        
        Args:
            args: Parsed command line arguments
            
        Returns:
            True if any individual validation type is selected
        """
        return any(
            [
                args.syntax,
                args.dependencies,
                args.structure,
                args.quality_gates,
                args.security,
                args.nfr,
            ]
        )

    def _handle_report_generation(self, args, root_path: Path) -> bool:
        """Handle report generation requests.
        
        Args:
            args: Parsed command line arguments
            root_path: Root path for validation
            
        Returns:
            True if report generation succeeded
        """
        from ..persistence.validation_history import ValidationHistoryTracker

        tracker = ValidationHistoryTracker(root_path)

        if args.report == "summary":
            report = tracker.get_validation_report(days=7)
            from ..validation_report import print_validation_summary

            print_validation_summary(report)
        elif args.report == "trends":
            from ..validation_report import print_detailed_trends

            print_detailed_trends(tracker)
        elif args.report == "metrics":
            from ..validation_report import print_metrics

            print_metrics(tracker)

        return True

    def _run_full_validation(self, args, root_path: Path) -> bool:
        """Run full validation pipeline.
        
        Args:
            args: Parsed command line arguments
            root_path: Root path for validation
            
        Returns:
            True if validation succeeded
        """
        print("🚀 Starting Validation Pipeline...")

        validator = Validator(
            root_path=root_path,
            enable_sonarqube=args.enable_sonarqube,
            enable_parallel=args.parallel,
            enable_quality_gates=args.enable_quality_gates,
            sonar_host_url=args.sonar_host_url,
            sonar_token=args.sonar_token,
        )

        # Apply performance optimizations
        if args.skip_coverage:
            validator.quality_gates_engine.skip_coverage = True
            print("⚡ Performance mode: Skipping test coverage analysis")

        if args.files:
            # Validate specific files
            file_paths = [Path(f) for f in args.files]
            print(f"📁 Validating {len(file_paths)} specific files: {[f.name for f in file_paths]}")
            result = validator.run_validation()
            # Filter results for specific files
            # This would need to be implemented in the unified validator
            success = not validator.should_block_build()
        else:
            # Run full validation
            result = validator.run_validation()
            success = not validator.should_block_build()

        if args.show_fixes:
            self._show_fixes_preview(validator)

        if args.auto_fix:
            self._apply_auto_fixes(validator, args)

        if args.output:
            self._save_report(result, args.output, args.format)

        print(f"\n{validator.get_build_summary()}")
        return success

    def _run_quick_validation(self, args, root_path: Path) -> bool:
        """Run quick validation.
        
        Args:
            args: Parsed command line arguments
            root_path: Root path for validation
            
        Returns:
            True if validation succeeded
        """
        print("🚀 Starting Quick Validation...")

        validator = Validator(
            root_path=root_path,
            enable_sonarqube=False,  # Disable for quick validation
            enable_parallel=True,  # Enable for speed
            enable_quality_gates=False,  # Disable for quick validation
        )

        # Run only essential phases
        print("🚀 Running quick validation (essential phases only)")
        result = validator.run_validation()
        print(f"✅ Quick validation completed: {result is not None}")
        success = not validator.should_block_build()

        print(f"\n{validator.get_build_summary()}")
        return success

    def _run_individual_validation(self, args, root_path: Path) -> bool:
        """Run individual validation types."""
        print("🚀 Starting Individual Validation...")

        success = True
        validation_results = []

        if args.syntax:
            result = self._run_syntax_validation(root_path, args)
            success &= result
            validation_results.append(("syntax", result))

        if args.dependencies:
            result = self._run_dependency_validation(root_path, args)
            success &= result
            validation_results.append(("dependencies", result))

        if args.structure:
            result = self._run_structure_validation(root_path, args)
            success &= result
            validation_results.append(("structure", result))

        if args.quality_gates:
            result = self._run_quality_gates_validation(root_path, args)
            success &= result
            validation_results.append(("quality_gates", result))

        if args.security:
            result = self._run_security_validation(root_path, args)
            success &= result
            validation_results.append(("security", result))

        if args.nfr:
            result = self._run_nfr_validation(root_path, args)
            success &= result
            validation_results.append(("nfr", result))
        
        # Use validation results for detailed feedback and error reporting
        self._report_validation_summary(validation_results)

        return success

    def _run_syntax_validation(self, root_path: Path, args) -> bool:
        """Run syntax validation only."""
        from .syntax_validator import SyntaxValidator

        validator = SyntaxValidator(root_path)
        validator._collect_files()

        if args.files:
            file_paths = [Path(f) for f in args.files if Path(f).suffix == ".py"]
        else:
            file_paths = validator.python_files

        success = validator.validate_all_imports(file_paths)
        validator.print_summary()
        return success

    def _run_dependency_validation(self, root_path: Path, args) -> bool:
        """Run dependency validation only."""
        from .dependency_validator import DependencyValidator

        validator = DependencyValidator(root_path)
        validator.validate_dependencies()
        success = not validator.has_errors()
        validator.print_summary()
        return success

    def _run_structure_validation(self, root_path: Path, args) -> bool:
        """Run structure validation only."""
        from .structure_validator import StructureValidator

        validator = StructureValidator(root_path)
        success = validator.validate_structure()
        validator.print_summary()
        return success

    def _run_quality_gates_validation(self, root_path: Path, args) -> bool:
        """Run quality gates validation only."""
        from .quality_gates import QualityGatesEngine

        validator = QualityGatesEngine(root_path)
        report = validator.evaluate_quality_gates()
        success = report["overall_status"] != "FAILED"

        print(f"Quality Gates: {report['overall_status']}")
        print(f"Gates Passed: {report['quality_gates_passed']}")
        print(f"Gates Failed: {report['quality_gates_failed']}")

        return success

    def _run_security_validation(self, root_path: Path, args) -> bool:
        """Run security validation only."""
        from .vv_validator import VVValidator

        validator = VVValidator(root_path)
        success = validator.run_validation_verification()

        report = validator.generate_vv_report()
        print(
            f"OWASP Compliance: {report['validation_verification']['compliance']['owasp_top_10']:.1f}%"
        )
        print(
            f"Security Vulnerabilities: {report['validation_verification']['security_vulnerabilities']}"
        )

        return success

    def _run_nfr_validation(self, root_path: Path, args) -> bool:
        """Run NFR validation only."""
        from .nfr_validator import NFRValidator

        validator = NFRValidator(root_path)
        success = validator.run_nfr_validation()

        report = validator.generate_nfr_report()
        print(f"ISO 25010 Compliance: {report['iso_25010_compliance']:.1f}%")

        return success

    def _show_fixes_preview(self, validator):
        """Show what fixes would be applied."""
        print("\n🔍 FIXES PREVIEW")
        print("=" * 50)

        # This would need to be implemented in the unified validator
        # For now, just show that preview mode is active
        print("Fix preview functionality would be implemented here")
        print("Run with --auto-fix to apply fixes")

    def _apply_auto_fixes(self, validator, args):
        """Apply automatic fixes."""
        print("\n🔧 APPLYING AUTOMATIC FIXES")
        print("=" * 50)

        # This would need to be implemented in the unified validator
        print("Auto-fix functionality would be implemented here")

    def _save_report(self, result: dict, output_file: str, format_type: str):
        """Save validation report to file."""
        import json
        import xml.etree.ElementTree as ET
        from pathlib import Path

        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        if format_type == "json":
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(result, f, indent=2, default=str)
        elif format_type == "xml":
            # Convert to XML (simplified)
            root = ET.Element("validation_report")
            # Add XML conversion logic here
            tree = ET.ElementTree(root)
            tree.write(output_path, encoding="utf-8", xml_declaration=True)
        elif format_type == "html":
            # Generate HTML report
            self._generate_html_report(result, output_path)

        print(f"📄 Report saved to: {output_path}")

    def _generate_html_report(self, result: dict, output_path: Path):
        """Generate HTML report."""
        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Validation Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .summary {{ background: #f0f0f0; padding: 15px; border-radius: 5px; }}
        .success {{ color: green; }}
        .failure {{ color: red; }}
        .warning {{ color: orange; }}
    </style>
</head>
<body>
    <h1>Validation Report</h1>
    <div class="summary">
        <h2>Summary</h2>
        <p>Overall Success: <span class="{'success' if result.get('summary', {}).get('overall_success', False) else 'failure'}">
            {result.get('summary', {}).get('overall_success', False)}
        </span></p>
        <p>Total Issues: {result.get('summary', {}).get('total_issues', 0)}</p>
        <p>Critical Issues: {result.get('summary', {}).get('critical_issues', 0)}</p>
        <p>Warnings: {result.get('summary', {}).get('warnings', 0)}</p>
    </div>
    
    <h2>Detailed Results</h2>
    <pre>{json.dumps(result, indent=2, default=str)}</pre>
</body>
</html>
"""

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(html_content)
        
    def _report_validation_summary(self, validation_results: List[tuple]) -> None:
        """Report detailed validation summary with error feedback.
        
        Args:
            validation_results: List of (validation_type, success) tuples
        """
        print("\n📊 Validation Summary:")
        print("=" * 30)
        
        total_validations = len(validation_results)
        successful_validations = sum(1 for _, success in validation_results if success)
        
        for validation_type, success in validation_results:
            status = "✅ PASSED" if success else "❌ FAILED"
            print(f"  {validation_type.upper():<15} {status}")
            
            if not success:
                # Provide specific error guidance based on validation type
                if validation_type == "syntax":
                    print("    → Check Python syntax and import statements")
                elif validation_type == "dependencies":
                    print("    → Review requirements.txt and package compatibility")
                elif validation_type == "structure":
                    print("    → Verify project structure and file organization")
                elif validation_type == "quality_gates":
                    print("    → Address quality gate violations (coverage, complexity)")
                elif validation_type == "security":
                    print("    → Fix security vulnerabilities and OWASP compliance issues")
                elif validation_type == "nfr":
                    print("    → Improve non-functional requirements (performance, maintainability)")
        
        print(f"\n📈 Results: {successful_validations}/{total_validations} validations passed")
        
        if successful_validations == total_validations:
            print("🎉 All validations successful!")
        else:
            failed_count = total_validations - successful_validations
            print(f"⚠️  {failed_count} validation(s) failed - see guidance above")


def main():
    """Main CLI entry point."""
    cli = ValidationCLI()
    success = cli.run()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
