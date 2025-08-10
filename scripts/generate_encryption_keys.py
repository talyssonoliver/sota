#!/usr/bin/env python3
"""Generate secure encryption keys for the AI system."""

import os
import secrets
from pathlib import Path
from cryptography.fernet import Fernet

def generate_memory_key():
    """Generate a secure key for memory encryption."""
    key = Fernet.generate_key()
    return key.decode('utf-8')

def generate_auth_secret():
    """Generate a secure secret for authentication."""
    return secrets.token_urlsafe(32)

def generate_webhook_secret():
    """Generate a secure secret for webhook validation."""
    return secrets.token_hex(32)

def main():
    """Generate all system keys."""
    print("🔐 AI System Encryption Key Generator")
    print("=" * 50)
    
    # Generate keys
    memory_key = generate_memory_key()
    auth_secret = generate_auth_secret()
    webhook_secret = generate_webhook_secret()
    
    print("\n📋 Environment Variables (add to .env):")
    print(f"MEMORY_ENGINE_KEY={memory_key}")
    print(f"AI_SYSTEM_SECRET_KEY={auth_secret}")
    print(f"WEBHOOK_SECRET={webhook_secret}")
    
    print("\n🔒 Security Notes:")
    print("- Store these keys securely")
    print("- Never commit keys to version control")
    print("- Use different keys for different environments")
    print("- Rotate keys regularly")
    
    # Create .env template
    env_content = f"""# AI System Environment Variables
# Generated: {os.popen('date').read().strip()}

# Memory encryption key (required for production)
MEMORY_ENGINE_KEY={memory_key}

# Authentication secret key
AI_SYSTEM_SECRET_KEY={auth_secret}

# Webhook validation secret
WEBHOOK_SECRET={webhook_secret}

# Environment setting
ENVIRONMENT=development

# Optional: External service tokens (replace with actual values)
# OPENAI_API_KEY=your_openai_key_here
# PERSONAL_ACCESS_TOKEN=your_github_token_here
# SLACK_TOKEN=your_slack_token_here
# JIRA_TOKEN=your_jira_token_here
"""
    
    env_file = Path(".env.example")
    env_file.write_text(env_content)
    print(f"\n📝 Created {env_file} template")

if __name__ == "__main__":
    main()
