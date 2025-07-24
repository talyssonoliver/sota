#!/usr/bin/env python3
"""
GitHub Actions Workflow Validation Script
Validates the deploy.yml workflow configuration
"""

import sys
from pathlib import Path

import yaml


def validate_workflow():
    """Validate the deploy.yml workflow"""
    print("🔍 Validating GitHub Actions Workflow")
    print("=" * 50)
    
    workflow_path = Path(".github/workflows/deploy.yml")
    
    if not workflow_path.exists():
        print("❌ deploy.yml not found")
        return False
    
    try:
        with open(workflow_path, 'r', encoding='utf-8') as f:
            workflow = yaml.safe_load(f)
        print("✅ YAML syntax is valid")
    except yaml.YAMLError as e:
        print(f"❌ YAML syntax error: {e}")
        return False
    
    # Check for updated actions
    print("\n📋 Checking Action Versions")
    print("-" * 30)
    
    issues = []
    improvements = []
    
    # Convert workflow to string for searching
    workflow_str = str(workflow)
    
    # Check for outdated Slack action
    if "8398a7/action-slack@v3" in workflow_str:
        issues.append("❌ Using outdated 8398a7/action-slack@v3")
    elif "rtCamp/action-slack-notify@v2" in workflow_str:
        improvements.append("✅ Using modern rtCamp/action-slack-notify@v2")
    
    # Check for deprecated release action
    if "actions/create-release@v1" in workflow_str:
        issues.append("❌ Using deprecated actions/create-release@v1")
    elif "ncipollo/release-action@v1" in workflow_str:
        improvements.append("✅ Using modern ncipollo/release-action@v1")
    
    # Check for proper secret usage
    if "SLACK_WEBHOOK_URL" in workflow_str:
        issues.append("❌ Using old SLACK_WEBHOOK_URL (should be SLACK_WEBHOOK)")
    elif "SLACK_WEBHOOK" in workflow_str:
        improvements.append("✅ Using correct SLACK_WEBHOOK secret name")
    
    # Print results
    for improvement in improvements:
        print(improvement)
    
    for issue in issues:
        print(issue)
    
    # Check jobs structure
    print("\n🏗️ Checking Job Structure")
    print("-" * 25)
    
    jobs = workflow.get('jobs', {})
    expected_jobs = ['deploy-staging', 'deploy-production', 'rollback']
    
    for job in expected_jobs:
        if job in jobs:
            print(f"✅ Job '{job}' found")
        else:
            print(f"❌ Job '{job}' missing")
            issues.append(f"Missing job: {job}")
    
    # Overall assessment
    print("\n" + "=" * 50)
    print("📊 VALIDATION SUMMARY")
    print("=" * 50)
    
    if not issues:
        print("🎉 WORKFLOW IS READY!")
        print("✅ All modern actions in use")
        print("✅ Proper configuration detected")
        print("✅ No deprecated actions found")
        print("\n🚀 Next step: Add SLACK_WEBHOOK secret to GitHub")
        return True
    else:
        print("⚠️ ISSUES FOUND:")
        for issue in issues:
            print(f"  {issue}")
        print(f"\n🔧 {len(issues)} issue(s) need attention")
        return False

def check_secrets_guide():
    """Provide guidance on setting up secrets"""
    print("\n🔑 SLACK WEBHOOK SETUP GUIDE")
    print("=" * 40)
    print("1. Create Slack webhook at: https://api.slack.com/apps")
    print("2. Add secret to GitHub:")
    print("   - Go to: Settings → Secrets and variables → Actions")
    print("   - Name: SLACK_WEBHOOK")
    print("   - Value: Your webhook URL")
    print("3. Test by pushing to main branch")

def main():
    """Main function"""
    print("🛡️ GitHub Actions Deploy Workflow Validator")
    print("=" * 60)
    
    is_valid = validate_workflow()
    check_secrets_guide()
    
    if is_valid:
        print("\n✅ Workflow validation passed!")
        sys.exit(0)
    else:
        print("\n❌ Workflow validation failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()
