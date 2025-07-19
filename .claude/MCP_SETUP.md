# MCP Server Setup Instructions

## GitHub Token Setup

To use the GitHub MCP server, you need to set up a GitHub Personal Access Token:

1. **Create a GitHub Personal Access Token:**
   - Go to GitHub Settings → Developer Settings → Personal Access Tokens → Tokens (classic)
   - Click "Generate new token (classic)"
   - Select scopes: `repo`, `read:org`, `read:user`, `read:project`

2. **Set the environment variable:**
   
   **Linux/WSL:**
   ```bash
   # Add to ~/.bashrc or ~/.zshrc
   export GITHUB_TOKEN="your_token_here"
   
   # Or set for current session:
   export GITHUB_TOKEN="your_token_here"
   ```
   
   **Windows:**
   ```cmd
   # Set permanently
   setx GITHUB_TOKEN "your_token_here"
   
   # Or for current session:
   set GITHUB_TOKEN=your_token_here
   ```

3. **Verify setup:**
   ```bash
   echo $GITHUB_TOKEN  # Should show your token
   ```

## MCP Server Status

### ✅ Working Servers
- **Filesystem**: `@modelcontextprotocol/server-filesystem` - Provides file system access
- **GitHub**: `@modelcontextprotocol/server-github` - GitHub API integration (requires token)

### ❌ Removed Servers
- **Python**: `mcp_server_python` - Module not found, removed from config
- **Git**: Custom git server not available, may need separate setup
- **Pytest**: Custom pytest server not available, may need separate setup

## Current Configuration

The MCP servers are configured in `.mcp.json` and enabled in `.claude/settings.local.json`.

Active servers:
- `filesystem` - File operations within `/mnt/c/taly/ai-system`
- `github` - GitHub repository operations (when token is set)

## Troubleshooting

1. **"Missing environment variables: GITHUB_TOKEN"**
   - Set up the GITHUB_TOKEN as described above
   - Restart Claude Code after setting the token

2. **MCP server connection failed**
   - Check if npx is installed: `which npx`
   - Test server manually: `npx -y @modelcontextprotocol/server-filesystem /path/to/dir`

3. **Package not found errors**
   - Packages have been updated to correct names in configuration
   - Old `@anthropic-ai/*` packages don't exist, now using `@modelcontextprotocol/*`