# Security Guidelines

⚠️ **CRITICAL SECURITY NOTICE**: Never commit actual encryption keys or API keys to version control. This repository has been configured to prevent such issues, but always verify that `.env` files containing real secrets are properly ignored.

## Memory Engine Encryption

The Memory Engine uses AES encryption via the Fernet implementation to protect sensitive data in memory storage.

### Key Management

#### Environment Variable (Recommended)
The encryption key should be provided via the `MEMORY_ENGINE_KEY` environment variable:

```bash
# In your .env file
MEMORY_ENGINE_KEY=your_32_byte_base64_encoded_key_here
```

#### Key Generation
Use the provided script to generate secure encryption keys:

```bash
python scripts/generate_memory_key.py
```

This script will:
- Generate a cryptographically secure 32-byte key
- Display the key in the correct format
- Optionally add it to your `.env` file
- Provide security reminders

#### Manual Key Generation
If you prefer to generate keys manually:

```bash
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

### Security Best Practices

#### Key Storage
- ✅ **DO**: Store keys in environment variables or secure vaults
- ✅ **DO**: Use different keys for different environments (dev/staging/prod)
- ✅ **DO**: Rotate keys periodically
- ❌ **DON'T**: Commit keys to version control
- ❌ **DON'T**: Share keys in chat, email, or other insecure channels
- ❌ **DON'T**: Use the same key across multiple projects

#### Production Deployment
In production environments:
- The system will refuse to start without a `MEMORY_ENGINE_KEY`
- Keys should be managed through your deployment platform's secret management
- Consider using HashiCorp Vault, AWS Secrets Manager, or similar for key rotation

#### Development
For development:
- The system will generate temporary keys if none are provided
- These temporary keys are NOT persistent and will change on restart
- For consistent development, set a key in your `.env` file

### Environment-Specific Configuration

#### Development
```bash
# .env (development)
ENVIRONMENT=development
MEMORY_ENGINE_KEY=your_dev_key_here
```

#### Production
```bash
# Production environment
ENVIRONMENT=production
MEMORY_ENGINE_KEY=your_production_key_here
```

The system enforces stricter security in production mode:
- Requires `MEMORY_ENGINE_KEY` to be set (no fallback generation)
- Enhanced logging for security events
- Stricter access controls

### Troubleshooting

#### Invalid Key Error
If you see "Invalid MEMORY_ENGINE_KEY environment variable":
1. Ensure the key is properly base64 encoded
2. Check for whitespace or special characters
3. Regenerate the key using the provided script

#### Missing Key in Production
If you see "Missing encryption key in production environment":
1. Set the `MEMORY_ENGINE_KEY` environment variable
2. Ensure your deployment platform is configured correctly
3. Check that the `ENVIRONMENT` variable is set correctly

#### Key Migration
If upgrading from an older version that used file-based keys:
1. The old `.memory_engine_key` file is no longer supported
2. Extract your key and set it as an environment variable
3. Remove the old key file for security

### Encryption Details

- **Algorithm**: AES 128 (via Fernet)
- **Key Length**: 32 bytes (256 bits when base64 decoded)
- **Key Format**: Base64 encoded string
- **Use Cases**: 
  - Memory store content encryption
  - PII data protection
  - Sensitive configuration data

### Access Control

The security system includes:
- Role-based access control
- User authentication for sensitive operations
- Audit logging for all security events
- Rate limiting for expensive operations

### Compliance

This implementation follows:
- OWASP security guidelines
- Industry best practices for encryption key management
- Zero-trust security principles
- Principle of least privilege

For questions about security, please review the code in:
- `tools/memory/security.py`
- `src/infrastructure/memory/security/encryption.py`
