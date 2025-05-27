#!/usr/bin/env python3
"""
QA CLI Tool - Command Line Interface for Enhanced QA Agent
Provides command-line access to QA agent capabilities including test generation,
coverage analysis, integration gap detection, and quality validation.
"""

import argparse
import json
import logging
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

from agents.qa import EnhancedQAAgent, create_enhanced_qa_workflow
from utils.coverage_analyzer import CoverageAnalyzer
from utils.integration_analyzer import IntegrationAnalyzer
from utils.test_generator import QATestFramework, QATestGenerator

# Add the project root to the path
sys.path.insert(0, str(Path(__file__).parent.parent))


def setup_logging(verbose: bool = False):
    """Setup logging configuration."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )


def generate_tests_command(args) -> int:
    """Generate tests for specified files or entire project."""
    try:
        qa_agent = EnhancedQAAgent(args.project_root, args.config)

        # Determine source files
        source_files = None
        if args.files:
            source_files = args.files
        elif args.pattern:
            project_path = Path(args.project_root)
            source_files = [str(f) for f in project_path.glob(args.pattern)]

        print(f"🧪 Generating tests for project: {args.project_root}")
        if source_files:
            print(f"📁 Processing {len(source_files)} files")

        # Generate comprehensive tests
        results = qa_agent.generate_comprehensive_tests(source_files)

        # Display results
        print("\n📊 Test Generation Results:")
        print(
            f"✅ Successfully generated: {
                results['quality_metrics']['files_with_tests']} files")
        print(
            f"📝 Total tests created: {
                results['quality_metrics']['total_generated_tests']}")
        print(
            f"📈 Quality score: {
                results['quality_metrics']['quality_score']:.1f}%")

        # Show recommendations
        if results['recommendations']:
            print("\n💡 Recommendations:")
            for i, rec in enumerate(results['recommendations'], 1):
                print(f"  {i}. {rec}")

        # Save detailed results if requested
        if args.output:
            output_path = Path(args.output)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, 'w') as f:
                json.dump(results, f, indent=2)
            print(f"\n💾 Detailed results saved to: {args.output}")

        return 0

    except Exception as e:
        print(f"❌ Error generating tests: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1


def analyze_coverage_command(args) -> int:
    """Analyze code coverage patterns."""
    try:
        analyzer = CoverageAnalyzer(args.project_root)

        print(f"📊 Analyzing coverage for project: {args.project_root}")

        results = analyzer.analyze_coverage_patterns(args.project_root)

        print("\n📈 Coverage Analysis Results:")
        print(
            f"Overall Quality Score: {
                results.get(
                    'overall_quality_score',
                    'N/A')}%")
        print(
            f"Improvement Potential: {
                results.get(
                    'improvement_potential',
                    'N/A')}%")

        # Display patterns
        patterns = results.get('patterns', [])
        if patterns:
            print(f"\n🔍 Found {len(patterns)} coverage patterns:")
            for pattern in patterns[:5]:  # Show first 5
                print(f"  • {pattern.get('description', 'Pattern')}")

        # Display gaps
        gaps = results.get('gaps', [])
        if gaps:
            print(f"\n⚠️  Found {len(gaps)} coverage gaps:")
            for gap in gaps[:5]:  # Show first 5
                severity = gap.get('severity', 'unknown')
                print(
                    f"  • [{
                        severity.upper()}] {
                        gap.get(
                            'description',
                            'Gap')}")

        # Save results if requested
        if args.output:
            output_path = Path(args.output)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, 'w') as f:
                json.dump(results, f, indent=2)
            print(f"\n💾 Results saved to: {args.output}")

        return 0

    except Exception as e:
        print(f"❌ Error analyzing coverage: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1


def detect_integration_gaps_command(args) -> int:
    """Detect integration gaps in the project."""
    try:
        analyzer = IntegrationAnalyzer(args.project_root)

        print(f"🔗 Detecting integration gaps in: {args.project_root}")

        results = analyzer.analyze_project(args.project_root)

        gaps = results.get('gaps', [])
        components = results.get('components', [])

        print(f"\n📊 Integration Analysis Results:")
        print(f"Components analyzed: {len(components)}")
        print(f"Integration gaps found: {len(gaps)}")

        if gaps:
            print("\n⚠️  Integration Gaps:")
            for gap in gaps:
                severity = gap.get('severity', 'medium')
                gap_type = gap.get('type', 'unknown')
                description = gap.get('description', 'No description')
                print(f"  • [{severity.upper()}] {gap_type}: {description}")
        else:
            print("✅ No integration gaps detected!")

        # Save results if requested
        if args.output:
            output_path = Path(args.output)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, 'w') as f:
                json.dump(results, f, indent=2)
            print(f"\n💾 Results saved to: {args.output}")

        return 0

    except Exception as e:
        print(f"❌ Error detecting integration gaps: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1


def validate_quality_command(args) -> int:
    """Validate project quality against quality gates."""
    try:
        qa_agent = EnhancedQAAgent(args.project_root, args.config)

        print(f"🎯 Validating quality for project: {args.project_root}")

        # Generate comprehensive analysis
        results = qa_agent.generate_comprehensive_tests()

        # Validate against quality gates
        validation = qa_agent.validate_quality_gates(results)

        print(f"\n🎯 Quality Gate Validation:")
        print(f"Overall Status: {validation['overall_status']}")
        print(f"Summary: {validation['summary']}")

        print("\n📋 Gate Details:")
        for gate_name, gate_data in validation['gates'].items():
            status = "✅ PASS" if gate_data['passed'] else "❌ FAIL"
            current = gate_data['current']
            threshold = gate_data['threshold']
            print(
                f"  {gate_name}: {status} ({current} vs {threshold} threshold)")

        # Show recommendations if quality gates failed
        if validation['overall_status'] == 'FAILED':
            recommendations = results.get('recommendations', [])
            if recommendations:
                print("\n💡 Improvement Recommendations:")
                for i, rec in enumerate(recommendations, 1):
                    print(f"  {i}. {rec}")

        # Save validation results
        if args.output:
            output_path = Path(args.output)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            validation_data = {
                "validation": validation,
                "detailed_results": results
            }
            with open(output_path, 'w') as f:
                json.dump(validation_data, f, indent=2)
            print(f"\n💾 Validation results saved to: {args.output}")

        # Return appropriate exit code
        return 0 if validation['overall_status'] == 'PASSED' else 1

    except Exception as e:
        print(f"❌ Error validating quality: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1


def report_command(args) -> int:
    """Generate comprehensive QA report."""
    try:
        qa_agent = EnhancedQAAgent(args.project_root, args.config)

        print(f"📋 Generating QA report for project: {args.project_root}")

        # Generate all analyses
        results = qa_agent.generate_comprehensive_tests()
        validation = qa_agent.validate_quality_gates(results)

        # Create comprehensive report
        report = {
            "project_root": args.project_root,
            "timestamp": __import__("datetime").datetime.now().isoformat(),
            "summary": {
                "overall_status": validation['overall_status'],
                "quality_score": results['quality_metrics']['quality_score'],
                "total_tests_generated": results['quality_metrics']['total_generated_tests'],
                "files_processed": results['quality_metrics']['total_source_files'],
                "integration_gaps": len(
                    results['integration_gaps'])},
            "detailed_results": results,
            "quality_validation": validation}

        # Save report
        output_path = Path(args.output) if args.output else Path(
            "qa_report.json")
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w') as f:
            json.dump(report, f, indent=2)

        print(f"\n📊 QA Report Summary:")
        print(f"Quality Status: {validation['overall_status']}")
        print(
            f"Quality Score: {
                results['quality_metrics']['quality_score']:.1f}%")
        print(
            f"Tests Generated: {
                results['quality_metrics']['total_generated_tests']}")
        print(f"Integration Gaps: {len(results['integration_gaps'])}")
        print(f"\n💾 Full report saved to: {output_path}")

        return 0

    except Exception as e:
        print(f"❌ Error generating report: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Enhanced QA Agent CLI Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s generate --project-root ./src
  %(prog)s analyze-coverage --project-root ./src --output coverage_report.json
  %(prog)s detect-gaps --project-root ./src
  %(prog)s validate --project-root ./src --config qa_config.json
  %(prog)s report --project-root ./src --output qa_report.json
        """
    )

    # Global arguments
    parser.add_argument("--verbose", "-v", action="store_true",
                        help="Enable verbose output")
    parser.add_argument(
        "--project-root",
        default=".",
        help="Project root directory (default: current directory)")
    parser.add_argument("--config", help="Path to QA configuration file")
    parser.add_argument("--output", "-o", help="Output file for results")

    # Subcommands
    subparsers = parser.add_subparsers(
        dest="command", help="Available commands")

    # Generate tests command
    generate_parser = subparsers.add_parser(
        "generate", help="Generate tests for project files")
    generate_parser.add_argument(
        "--files", nargs="+", help="Specific files to generate tests for")
    generate_parser.add_argument(
        "--pattern", help="Glob pattern for files to process")
    generate_parser.set_defaults(func=generate_tests_command)

    # Analyze coverage command
    coverage_parser = subparsers.add_parser(
        "analyze-coverage", help="Analyze code coverage patterns")
    coverage_parser.set_defaults(func=analyze_coverage_command)

    # Detect integration gaps command
    gaps_parser = subparsers.add_parser(
        "detect-gaps", help="Detect integration gaps")
    gaps_parser.set_defaults(func=detect_integration_gaps_command)

    # Validate quality command
    validate_parser = subparsers.add_parser(
        "validate", help="Validate project quality against gates")
    validate_parser.set_defaults(func=validate_quality_command)

    # Generate report command
    report_parser = subparsers.add_parser(
        "report", help="Generate comprehensive QA report")
    report_parser.set_defaults(func=report_command)

    # Parse arguments
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    # Setup logging
    setup_logging(args.verbose)

    # Execute command
    try:
        return args.func(args)
    except KeyboardInterrupt:
        print("\n⚠️  Operation cancelled by user")
        return 130
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
