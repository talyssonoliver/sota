#!/usr/bin/env python3
"""
from cryptography.fernet import Fernet
Generate Memory Engine Encryption Key
Creates a secure encryption key for the Memory Engine system.
"""

import sys
from pathlib import Path
from cryptography.fernet import Fernet

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

try:
    pass
    CRYPTO_AVAILABLE = True
except ImportError:
    CRYPTO_AVAILABLE = False
    print("ERROR: cryptography package not found!")
    print("Please install it with: pip install cryptography")
    sys.exit(1)

def generate_key():
    """Generate a new Fernet encryption key."""
    return Fernet.generate_key()

def main():
    """Main function to generate and display encryption key."""
    print("=== Memory Engine Encryption Key Generator ===")
    print()
    print("🔒 CRITICAL SECURITY NOTICE:")
    print("   This tool generates encryption keys for sensitive data.")
    print("   NEVER commit these keys to version control!")
    print("   Use unique keys for each environment (dev/staging/prod).")
    print()
    
    # Generate a new key
    key = generate_key()
    key_str = key.decode('utf-8')
    
    print("✅ New encryption key generated successfully!")
    print()
    
    # Display the key
    print("Your MEMORY_ENGINE_KEY:")
    print(f"MEMORY_ENGINE_KEY={key_str}")
    print()
    
    # Provide instructions
    print("📝 Next steps:")
    print("1. Copy the key above")
    print("2. Add it to your .env file")
    print("3. Keep this key secure - anyone with access can decrypt your memory store")
    print("4. Never commit this key to version control")
    print()
    
    # Check if .env file exists and offer to update it
    env_file = project_root / ".env"
    if env_file.exists():
        print("📁 .env file found!")
        
        # Read current .env content
        with open(env_file, 'r') as f:
            content = f.read()
        
        # Check if MEMORY_ENGINE_KEY already exists
        if 'MEMORY_ENGINE_KEY=' in content:
            print("⚠️  MEMORY_ENGINE_KEY already exists in .env file")
            response = input("Do you want to replace it? (y/N): ").strip().lower()
            
            if response == 'y':
                # Replace existing key
                lines = content.split('\n')
                new_lines = []
                for line in lines:
                    if line.startswith('MEMORY_ENGINE_KEY='):
                        new_lines.append(f'MEMORY_ENGINE_KEY={key_str}')
                    else:
                        new_lines.append(line)
                
                with open(env_file, 'w') as f:
                    f.write('\n'.join(new_lines))
                
                print("✅ .env file updated successfully!")
            else:
                print("⏭️  Keeping existing key in .env file")
        else:
            # Add new key
            response = input("Do you want to add the key to your .env file? (Y/n): ").strip().lower()
            
            if response != 'n':
                # Append the key to .env file
                with open(env_file, 'a') as f:
                    if not content.endswith('\n'):
                        f.write('\n')
                    f.write(f'MEMORY_ENGINE_KEY={key_str}\n')
                
                print("✅ Key added to .env file successfully!")
            else:
                print("⏭️  You'll need to manually add the key to your .env file")
    else:
        print("⚠️  No .env file found. Please create one from .env.template")
    
    print()
    print("🔐 Security reminders:")
    print("- This key encrypts sensitive data in your memory store")
    print("- Store it securely (password manager, secure vault, etc.)")
    print("- Don't share it in chat, email, or commit it to git")
    print("- Consider using different keys for different environments")

if __name__ == "__main__":
    main()
