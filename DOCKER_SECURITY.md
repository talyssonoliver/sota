# Docker Security Configuration

This document outlines the security requirements and best practices for running the SOTA AI System with Docker.

## Required Environment Variables

The following environment variables **must** be set in your `.env` file before running Docker Compose:

### Database Security
```bash
# PostgreSQL - Use a strong password (16+ characters, mixed case, numbers, symbols)
POSTGRES_PASSWORD=your_secure_postgres_password_here

# Redis - Optional but recommended for production-like environments
REDIS_PASSWORD=your_redis_password_here
```

### Development Tools Security
```bash
# Jupyter Lab - Use a secure token (32+ characters random string)
JUPYTER_TOKEN=your_secure_jupyter_token_here

# Grafana - Use a strong admin password
GRAFANA_PASSWORD=your_secure_grafana_password_here
```

## Setting Up Secure Passwords

### Generate Secure Passwords
```bash
# Generate a secure 32-character password
openssl rand -base64 32

# Generate multiple passwords at once
for i in {1..4}; do echo "Password $i: $(openssl rand -base64 32)"; done
```

### Example .env Configuration
```bash
# Copy from .env.template
cp .env.template .env

# Edit with your secure values
nano .env
```

## Security Best Practices

### 1. Environment File Security
- Never commit `.env` files to version control
- Set restrictive permissions: `chmod 600 .env`
- Use different passwords for each environment (dev/staging/prod)

### 2. Password Requirements
- **Minimum 16 characters** for database passwords
- **Minimum 32 characters** for tokens and API keys
- Use a mix of uppercase, lowercase, numbers, and symbols
- Avoid dictionary words and common patterns

### 3. Docker Security
- Run containers as non-root users where possible
- Use Docker secrets in production environments
- Regularly update container images
- Monitor container logs for security events

### 4. Network Security
- Use Docker networks to isolate services
- Expose only necessary ports to the host
- Consider using a reverse proxy for production

## Production Considerations

For production deployments:

1. **Use Docker Secrets** instead of environment variables
2. **Enable TLS/SSL** for all external communications
3. **Set up proper logging** and monitoring
4. **Use a secrets management system** (HashiCorp Vault, AWS Secrets Manager, etc.)
5. **Enable container scanning** for vulnerabilities

## Troubleshooting

### Missing Environment Variables
If you see errors about missing environment variables:

1. Check that `.env` file exists: `ls -la .env`
2. Verify all required variables are set: `grep -E "(POSTGRES_PASSWORD|JUPYTER_TOKEN|GRAFANA_PASSWORD)" .env`
3. Ensure no trailing spaces or quotes around values

### Docker Compose Profiles
Different profiles require different environment variables:

- **minimal**: No additional passwords required
- **testing**: Requires `REDIS_PASSWORD`
- **full**: Requires all passwords
- **jupyter**: Requires `JUPYTER_TOKEN`
- **monitoring**: Requires `GRAFANA_PASSWORD`
- **database**: Requires `POSTGRES_PASSWORD`

## Security Incident Response

If you suspect a security incident:

1. **Immediately rotate** all passwords and tokens
2. **Check logs** for unauthorized access
3. **Update** all container images
4. **Review** network access and firewall rules
5. **Document** the incident and response actions

---

⚠️ **Warning**: Never use default or example passwords in any environment. Always generate unique, strong passwords for each deployment.