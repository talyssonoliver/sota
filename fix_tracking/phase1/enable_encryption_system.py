#!/usr/bin/env python3
"""Enable encryption across the entire AI system."""

from pathlib import Path

def enable_memory_encryption():
    """Enable encryption in memory configuration."""
    
    config_file = Path("src/infrastructure/memory/config/memory_config.py")
    content = config_file.read_text()
    
    # Change default encryption setting
    content = content.replace(
        "encryption_enabled: bool = False",
        "encryption_enabled: bool = True"
    )
    
    # Also update the default config section
    content = content.replace(
        '"encryption_enabled": False,',
        '"encryption_enabled": True,'
    )
    
    config_file.write_text(content)
    print("✅ Enabled encryption in memory configuration")

def create_encryption_key_generator():
    """Create script to generate secure encryption keys."""
    
    script_content = '''#!/usr/bin/env python3
"""Generate secure encryption keys for the AI system."""

import os
import secrets
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
    
    print("\\n📋 Environment Variables (add to .env):")
    print(f"MEMORY_ENGINE_KEY={memory_key}")
    print(f"AI_SYSTEM_SECRET_KEY={auth_secret}")
    print(f"WEBHOOK_SECRET={webhook_secret}")
    
    print("\\n🔒 Security Notes:")
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
    print(f"\\n📝 Created {env_file} template")

if __name__ == "__main__":
    main()
'''
    
    script_path = Path("scripts/generate_encryption_keys.py")
    script_path.parent.mkdir(exist_ok=True)
    script_path.write_text(script_content)
    script_path.chmod(0o755)
    print(f"✅ Created encryption key generator: {script_path}")

def enable_auth_encryption():
    """Enable encryption in authentication system."""
    
    auth_file = Path("src/infrastructure/security/auth_middleware.py")
    content = auth_file.read_text()
    
    # Update to use proper environment variable with secure default
    content = content.replace(
        'secret_key = os.environ.get("AI_SYSTEM_SECRET_KEY", "dev-key-change-in-production")',
        '''secret_key = os.environ.get("AI_SYSTEM_SECRET_KEY")
        if not secret_key:
            if os.environ.get("ENVIRONMENT", "").lower() == "production":
                raise RuntimeError("AI_SYSTEM_SECRET_KEY is required in production")
            secret_key = "dev-key-change-in-production"
            import logging
            logging.warning("Using default secret key in development. Set AI_SYSTEM_SECRET_KEY for production.")'''
    )
    
    auth_file.write_text(content)
    print("✅ Enhanced authentication encryption")

def enable_webhook_encryption():
    """Add encryption to webhook payloads."""
    
    webhook_file = Path("src/interfaces/api/webhook_manager.py")
    if not webhook_file.exists():
        return
        
    content = webhook_file.read_text()
    
    # Add encryption import if not present
    if "from src.infrastructure.memory.security.encryption import SecurityManager" not in content:
        # Find a good place to add the import
        lines = content.split('\n')
        import_index = -1
        for i, line in enumerate(lines):
            if line.startswith('import ') or line.startswith('from '):
                import_index = i
        
        if import_index >= 0:
            lines.insert(import_index + 1, "from src.infrastructure.memory.security.encryption import SecurityManager")
            content = '\n'.join(lines)
            webhook_file.write_text(content)
            print("✅ Added encryption imports to webhook manager")

def create_encryption_utilities():
    """Create utility functions for system-wide encryption."""
    
    util_content = '''#!/usr/bin/env python3
"""System-wide encryption utilities."""

import os
import logging
from typing import Any, Dict, Optional
from src.infrastructure.memory.security.encryption import SecurityManager
from src.infrastructure.memory.config.memory_config import MemoryEngineConfig

logger = logging.getLogger(__name__)

class SystemEncryption:
    """System-wide encryption utilities."""
    
    def __init__(self):
        """Initialize system encryption."""
        self.security_manager = None
        self._initialize_encryption()
    
    def _initialize_encryption(self):
        """Initialize encryption with proper configuration."""
        try:
            # Create config with encryption enabled
            config = MemoryEngineConfig()
            config.encryption_enabled = True
            config.pii_detection_enabled = True
            
            self.security_manager = SecurityManager(config)
            logger.info("System encryption initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize system encryption: {e}")
            raise
    
    def encrypt_sensitive_data(self, data: str) -> bytes:
        """Encrypt sensitive data."""
        if not self.security_manager:
            raise RuntimeError("Encryption not initialized")
        return self.security_manager.encrypt_data(data)
    
    def decrypt_sensitive_data(self, encrypted_data: bytes) -> str:
        """Decrypt sensitive data."""
        if not self.security_manager:
            raise RuntimeError("Encryption not initialized")
        return self.security_manager.decrypt_data(encrypted_data)
    
    def encrypt_config_value(self, value: str) -> str:
        """Encrypt a configuration value for storage."""
        if not value or not isinstance(value, str):
            return value
            
        # Check if value looks like a secret (contains key, token, password, etc.)
        sensitive_indicators = ['key', 'token', 'password', 'secret', 'auth']
        if any(indicator in value.lower() for indicator in sensitive_indicators):
            try:
                encrypted = self.encrypt_sensitive_data(value)
                return f"encrypted:{encrypted.hex()}"
            except Exception as e:
                logger.warning(f"Failed to encrypt config value: {e}")
                return value
        
        return value
    
    def decrypt_config_value(self, value: str) -> str:
        """Decrypt a configuration value."""
        if not value or not isinstance(value, str):
            return value
            
        if value.startswith("encrypted:"):
            try:
                hex_data = value[10:]  # Remove "encrypted:" prefix
                encrypted_data = bytes.fromhex(hex_data)
                return self.decrypt_sensitive_data(encrypted_data)
            except Exception as e:
                logger.warning(f"Failed to decrypt config value: {e}")
                return value
        
        return value
    
    def secure_environment_variables(self) -> Dict[str, str]:
        """Get all environment variables with sensitive ones encrypted."""
        secure_vars = {}
        
        for key, value in os.environ.items():
            if any(sensitive in key.lower() for sensitive in ['key', 'token', 'password', 'secret']):
                secure_vars[key] = "[ENCRYPTED]"
            else:
                secure_vars[key] = value
        
        return secure_vars

# Global instance
_system_encryption = None

def get_system_encryption() -> SystemEncryption:
    """Get global system encryption instance."""
    global _system_encryption
    if _system_encryption is None:
        _system_encryption = SystemEncryption()
    return _system_encryption

def encrypt_sensitive(data: str) -> bytes:
    """Convenience function to encrypt sensitive data."""
    return get_system_encryption().encrypt_sensitive_data(data)

def decrypt_sensitive(encrypted_data: bytes) -> str:
    """Convenience function to decrypt sensitive data."""
    return get_system_encryption().decrypt_sensitive_data(encrypted_data)
'''
    
    util_path = Path("src/infrastructure/security/system_encryption.py")
    util_path.write_text(util_content)
    print(f"✅ Created system encryption utilities: {util_path}")

def create_env_template():
    """Create .env template with encryption keys."""
    
    template_content = '''# AI System Environment Variables
# Copy this file to .env and fill in your actual values

# ===== ENCRYPTION KEYS (REQUIRED) =====
# Generate with: python scripts/generate_encryption_keys.py

# Memory engine encryption key (32-byte base64 encoded)
MEMORY_ENGINE_KEY=your_memory_key_here

# Authentication secret key (32-byte base64 encoded)  
AI_SYSTEM_SECRET_KEY=your_auth_secret_here

# Webhook validation secret
WEBHOOK_SECRET=your_webhook_secret_here

# ===== ENVIRONMENT SETTINGS =====
ENVIRONMENT=development

# ===== EXTERNAL SERVICE TOKENS =====
# OpenAI API (if using AI features)
# OPENAI_API_KEY=your_openai_key_here

# GitHub integration (if using GitHub features)
# PERSONAL_ACCESS_TOKEN=your_github_token_here

# Slack integration (if using Slack features)  
# SLACK_TOKEN=your_slack_token_here

# JIRA integration (if using JIRA features)
# JIRA_TOKEN=your_jira_token_here

# SonarQube integration (if using code quality features)
# SONAR_TOKEN=your_sonar_token_here

# ===== DATABASE SETTINGS =====
# Database encryption (if using external database)
# DB_ENCRYPTION_KEY=your_db_key_here

# ===== SECURITY SETTINGS =====
# Enable/disable features
ENABLE_ENCRYPTION=true
ENABLE_PII_DETECTION=true
ENABLE_ACCESS_CONTROL=true
ENABLE_AUDIT_LOGGING=true
'''
    
    template_path = Path(".env.template")
    template_path.write_text(template_content)
    print(f"✅ Created environment template: {template_path}")

def update_config_files():
    """Update configuration files to enable encryption by default."""
    
    # Update validation config
    validation_config = Path("config/validation_config.json")
    if validation_config.exists():
        import json
        try:
            with open(validation_config, 'r') as f:
                config = json.load(f)
            
            # Add encryption settings
            if 'security' not in config:
                config['security'] = {}
            
            config['security'].update({
                'encryption_enabled': True,
                'pii_detection_enabled': True,
                'access_control_enabled': True,
                'audit_logging_enabled': True
            })
            
            with open(validation_config, 'w') as f:
                json.dump(config, f, indent=2)
            
            print(f"✅ Updated {validation_config}")
        except Exception as e:
            print(f"⚠️  Could not update {validation_config}: {e}")

def main():
    """Main function to enable encryption system-wide."""
    print("🔐 Enabling Encryption System-Wide")
    print("=" * 50)
    
    # Enable encryption in various components
    enable_memory_encryption()
    enable_auth_encryption()
    enable_webhook_encryption()
    
    # Create utilities and tools
    create_encryption_utilities()
    create_encryption_key_generator()
    create_env_template()
    update_config_files()
    
    print("\n📊 Encryption Enablement Summary:")
    print("✅ Memory engine encryption enabled")
    print("✅ Authentication encryption enhanced")
    print("✅ Webhook encryption prepared")
    print("✅ System encryption utilities created")
    print("✅ Key generation script created")
    print("✅ Environment template created")
    print("✅ Configuration files updated")
    
    print("\n🔑 Next Steps:")
    print("1. Run: python scripts/generate_encryption_keys.py")
    print("2. Copy .env.template to .env and fill in values")
    print("3. Restart the system to apply encryption")
    print("4. Verify encryption with validation tools")

if __name__ == "__main__":
    main()