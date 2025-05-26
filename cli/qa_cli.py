#!/usr/bin/env python3
"""
Enhanced QA System CLI
Command-line interface for comprehensive QA validation, test generation, and quality analysis.
"""

import argparse
import json
import sys
import logging
from pathlib import Path
from typing import Optional, List

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from agents.qa import EnhancedQAAgent, create_enhanced_qa_workflow
from orchestration.qa_validation import QAValidationPipeline
from utils.coverage_analyzer import CoverageAnalyzer
from utils.test_generator import TestGenerator, TestFramework


def setup_logging(verbose: bool = False):
    """Setup logging configuration."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler('qa_cli.log')
        ]
    )


def cmd_generate_tests(args):
    """Generate comprehensive test suite."""
    print(f"🧪 Generating tests for project: {args.project_root}")
    
    try:
        qa_agent = EnhancedQAAgent(args.project_root, args.config)
        
        source_files = None
        if args.files:
            source_files = args.files.split(',')
        
        results = qa_agent.generate_comprehensive_tests(source_files)
        
        # Save results
        output_file = Path(args.output) / "qa_test_generation_report.json"
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2)
        
        # Print summary
        print(f"✅ Test generation completed!")
        print(f"📊 Generated {results['quality_metrics']['total_generated_tests']} tests")
        print(f"📁 Processed {results['quality_metrics']['total_source_files']} files")
        print(f"⭐ Quality Score: {results['quality_metrics']['quality_score']:.1f}%")
        print(f"📄 Report saved to: {output_file}")
        
        # Print recommendations
        if results['recommendations']:
            print("\n💡 Recommendations:")
            for rec in results['recommendations']:
                print(f"  • {rec}")
        
    except Exception as e:
        print(f"❌ Error generating tests: {e}")
        sys.exit(1)


def cmd_analyze_coverage(args):
    """Analyze test coverage patterns."""
    print(f"📈 Analyzing coverage for: {args.project_root}")
    
    try:
        analyzer = CoverageAnalyzer(args.project_root)
        analysis = analyzer.analyze_coverage_patterns(args.project_root)
        
        # Save results
        output_file = Path(args.output) / "coverage_analysis_report.json"
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w') as f:
            json.dump(analysis, f, indent=2)
        
        print(f"✅ Coverage analysis completed!")
        print(f"📊 Quality Score: {analysis.get('overall_quality_score', 0):.1f}%")
        print(f"🎯 Coverage Gaps: {len(analysis.get('coverage_gaps', []))}")
        print(f"📄 Report saved to: {output_file}")
        
    except Exception as e:
        print(f"❌ Error analyzing coverage: {e}")
        sys.exit(1)


def cmd_validate_quality(args):
    """Run comprehensive QA validation."""
    print(f"🔍 Running QA validation for task: {args.task_id}")
    
    try:
        pipeline = QAValidationPipeline(args.project_root)
        results = pipeline.run_validation(args.task_id)
        
        # Save results
        output_file = Path(args.output) / f"qa_validation_{args.task_id}.json"
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2)
        
        # Print summary
        print(f"✅ QA validation completed!")
        print(f"📊 Overall Status: {results.get('overall_status', 'UNKNOWN')}")
        print(f"📄 Report saved to: {output_file}")
        
        # Show quality gates status
        if 'quality_gates' in results:
            gates = results['quality_gates']['gates']
            passed = sum(1 for g in gates.values() if g['passed'])
            total = len(gates)
            print(f"🚪 Quality Gates: {passed}/{total} passed")
            
            for gate_name, gate_info in gates.items():
                status = "✅" if gate_info['passed'] else "❌"
                print(f"  {status} {gate_name}: {gate_info['current']:.1f}% (threshold: {gate_info['threshold']}%)")
        
    except Exception as e:
        print(f"❌ Error running QA validation: {e}")
        sys.exit(1)


def cmd_run_workflow(args):
    """Run complete enhanced QA workflow."""
    print(f"🚀 Running complete QA workflow for: {args.project_root}")
    
    try:
        qa_agent = create_enhanced_qa_workflow(args.project_root, args.config)
        
        # Step 1: Generate tests
        print("📝 Step 1: Generating comprehensive tests...")
        test_results = qa_agent.generate_comprehensive_tests()
        
        # Step 2: Validate quality gates
        print("🔍 Step 2: Validating quality gates...")
        gate_results = qa_agent.validate_quality_gates(test_results)
        
        # Combine results
        workflow_results = {
            "workflow_status": "COMPLETED",
            "test_generation": test_results,
            "quality_gates": gate_results,
            "timestamp": str(Path().cwd())
        }
        
        # Save comprehensive report
        output_file = Path(args.output) / "qa_workflow_report.json"
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w') as f:
            json.dump(workflow_results, f, indent=2)
        
        print(f"✅ QA workflow completed!")
        print(f"📊 Overall Quality: {test_results['quality_metrics']['quality_score']:.1f}%")
        print(f"🚪 Quality Gates: {gate_results['summary']}")
        print(f"📄 Complete report saved to: {output_file}")
        
    except Exception as e:
        print(f"❌ Error running QA workflow: {e}")
        sys.exit(1)


def cmd_show_config(args):
    """Show current QA configuration."""
    print(f"⚙️ QA Configuration for: {args.project_root}")
    
    try:
        qa_agent = EnhancedQAAgent(args.project_root, args.config)
        config = qa_agent.config
        
        print("\n📋 Coverage Thresholds:")
        for key, value in config['coverage_thresholds'].items():
            print(f"  {key}: {value}%")
        
        print("\n🎯 Quality Gates:")
        for key, value in config['quality_gates'].items():
            print(f"  {key}: {value}")
        
        print("\n🧪 Test Patterns:")
        for key, value in config['test_patterns'].items():
            print(f"  {key}: {value}")
        
    except Exception as e:
        print(f"❌ Error loading configuration: {e}")
        sys.exit(1)


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Enhanced QA System CLI - Comprehensive quality assurance and testing",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate tests for entire project
  python cli/qa_cli.py generate-tests --project-root . --output outputs/qa

  # Analyze coverage patterns
  python cli/qa_cli.py analyze-coverage --project-root . --output outputs/coverage

  # Validate QA for specific task
  python cli/qa_cli.py validate-quality --task-id BE-07 --output outputs/validation

  # Run complete QA workflow
  python cli/qa_cli.py run-workflow --project-root . --output outputs/workflow

  # Show current configuration
  python cli/qa_cli.py show-config --project-root .
        """
    )
    
    # Global arguments
    parser.add_argument('--verbose', '-v', action='store_true', help='Enable verbose logging')
    parser.add_argument('--project-root', default='.', help='Project root directory (default: current directory)')
    parser.add_argument('--config', help='QA configuration file path')
    parser.add_argument('--output', default='outputs', help='Output directory (default: outputs)')
    
    # Subcommands
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Generate tests command
    gen_parser = subparsers.add_parser('generate-tests', help='Generate comprehensive test suite')
    gen_parser.add_argument('--files', help='Comma-separated list of source files (default: auto-discover)')
    gen_parser.set_defaults(func=cmd_generate_tests)
    
    # Analyze coverage command
    cov_parser = subparsers.add_parser('analyze-coverage', help='Analyze test coverage patterns')
    cov_parser.set_defaults(func=cmd_analyze_coverage)
    
    # Validate quality command
    val_parser = subparsers.add_parser('validate-quality', help='Run comprehensive QA validation')
    val_parser.add_argument('--task-id', required=True, help='Task ID to validate')
    val_parser.set_defaults(func=cmd_validate_quality)
    
    # Run workflow command
    wf_parser = subparsers.add_parser('run-workflow', help='Run complete enhanced QA workflow')
    wf_parser.set_defaults(func=cmd_run_workflow)
    
    # Show config command
    cfg_parser = subparsers.add_parser('show-config', help='Show current QA configuration')
    cfg_parser.set_defaults(func=cmd_show_config)
    
    # Parse arguments
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    # Setup logging
    setup_logging(args.verbose)
    
    # Run command
    args.func(args)


if __name__ == "__main__":
    main()
