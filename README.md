# Remote MCP Server Template

This is a template for creating **remote MCP servers** that can be deployed to DigitalOcean App Platform. Remote MCP servers allow you to deploy MCP functionality to the cloud and use it from any MCP-compatible client (Claude Desktop, Cursor, Windsurf, etc.) without local installation.

## This Specific Implementation: Domain Checker

This template demonstrates a domain availability checker that uses WHOIS lookups and DNS resolution. Built with the modern FastMCP framework for reliable domain availability checking.

## Deploy this Remote MCP Server to DigitalOcean
[![Deploy to DO](https://www.deploytodo.com/do-btn-blue.svg)](https://cloud.digitalocean.com/apps/new?repo=https://github.com/do-community/do-remote-mcp-server-template/tree/main)

## Quick Start (1-Click Deploy)

1. **Deploy to DigitalOcean** using the button above
2. **Get your deployed URL** from DigitalOcean (e.g., `https://your-app.ondigitalocean.app`)
3. **Add to your MCP client** using the URL + `/mcp` endpoint

![Image](https://github.com/user-attachments/assets/d5e7db9e-346d-436b-9c2f-53f014debe17)

## Features

- ✅ **Dual Verification**: Uses both WHOIS and DNS resolution for accurate results
- 🚀 **Async Operations**: Non-blocking operations with proper timeout handling
- 📊 **Batch Processing**: Check multiple domains concurrently
- 🔍 **Detailed Analysis**: Provides comprehensive availability information

## Using Your Remote MCP Server

### Option 1: Use Your Deployed Remote MCP Server (Recommended)

After deploying to DigitalOcean, add your server URL to your MCP client:

```json
{
  "mcpServers": {
    "domain-checker": {
      "url": "https://YOUR-APP-NAME.ondigitalocean.app/mcp",
      "description": "Check domain availability"
    }
  }
}
```

Replace `YOUR-APP-NAME` with your actual DigitalOcean app name.

![Image](https://github.com/user-attachments/assets/34b5228e-2bb8-4fb4-9326-248a62f9519a)

### Option 2: With FastMCP Development Tools

```bash
# Make sure your virtual environment is activated
fastmcp dev local-domain-checker.py
```
![Image](https://github.com/user-attachments/assets/beb32cf0-499f-40d3-aeda-a255291ca5f3)

### Option 3: Configure Local MCP Server

This MCP server works with Claude Desktop, Cursor, Windsurf, and other MCP-compatible applications.

#### Configuration Locations

- **Claude Desktop**:
  - macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
  - Windows: `%APPDATA%\Claude\claude_desktop_config.json`

![Image](https://github.com/user-attachments/assets/c855b19a-9498-47c5-88cd-a778d04319a0)
  
- **Cursor**:
  - macOS: `~/Library/Application Support/Cursor/cursor_desktop_config.json`
  - Windows: `%APPDATA%\Cursor\cursor_desktop_config.json`

[![Install MCP Server](https://cursor.com/deeplink/mcp-install-dark.svg)](https://cursor.com/install-mcp?name=domain-checker&config=eyJjb21tYW5kIjoicHl0aG9uIC9wYXRoL3RvL3lvdXIvZG9tYWluX2NoZWNrZXIucHkifQ%3D%3D)


- **Windsurf**:
  - macOS: `~/Library/Application Support/Windsurf/windsurf_desktop_config.json`
  - Windows: `%APPDATA%\Windsurf\windsurf_desktop_config.json`

Add the following configuration to the appropriate file, making sure to point to your virtual environment:

```json
{
  "mcpServers": {
    "domain-checker": {
      "command": "/path/to/your/venv/bin/python",
      "args": ["/path/to/your/local-domain-checker.py"]
    }
  }
}
```

**Important**: 
- Replace paths with the actual paths to your virtual environment and domain checker directory
- Use `local-domain-checker.py` for local development (it has simpler configuration without port/host settings)
- `domain-checker.py` is configured for remote deployment with additional parameters

## Installation (For Local Use)

### Prerequisites

- Python 3.8 or higher
- pip package manager

### Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/ajot/domain-checker-mcp-server.git
   cd domain-checker-mcp-server
   ```

2. **Create and activate a virtual environment (recommended)**
   ```bash
   python -m venv venv
   # On macOS/Linux
   source venv/bin/activate
   # On Windows
   venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

## Optional CI hardening

If you want a small optional GitHub Actions example for repos created from this template, see
`.github/workflows/mcp-trust.yml`.

It scans `python local-domain-checker.py`, uploads SARIF to GitHub code scanning, and stays
`workflow_dispatch`-only by default so it does not add a required CI gate.

## Deploy to DigitalOcean App Platform

This MCP server can be deployed as a remote MCP server on DigitalOcean App Platform.

### Prerequisites

- A DigitalOcean account
- The [doctl](https://docs.digitalocean.com/reference/doctl/how-to/install/) command-line tool (optional)
- Git repository with your code

### Deployment Steps

1. **Push your code to a Git repository**
   Make sure all your changes are committed and pushed to a GitHub, GitLab, or Bitbucket repository.

2. **Create a new App on DigitalOcean App Platform**
   - Go to the [DigitalOcean App Platform](https://cloud.digitalocean.com/apps) dashboard
   - Click "Create App" and select your Git repository
   - Select the branch you want to deploy
   - Choose "Python" as the environment

3. **Configure the App**
   - Set the source directory to `/`
   - Set the run command to: `python domain-checker.py`
   - Set the environment variable: `PORT=8080`
   - Set HTTP port to 8080

4. **Deploy the App**
   - Click "Deploy to Production"
   - Wait for the build and deployment to complete

5. **Configure as Remote MCP**
   Once deployed, you can use the app URL as a remote MCP server in your MCP-compatible applications:

   ```json
   {
     "mcpServers": {
       "domain-checker": {
         "url": "https://your-app-name.ondigitalocean.app/mcp",
         "description": "Check domain name availability"
       }
     }
   }
   ```

### Updating Your Deployment

To update your deployed app, simply push changes to your Git repository. DigitalOcean App Platform will automatically build and deploy the new version.

## Usage Examples

### Check Single Domain
"Check if myawesome-startup.com is available"

### Check Multiple Domains
"Check availability for these domains: mycompany.com, mycompany.net, mycompany.org"

## Understanding Results

### Availability Status

- **✅ LIKELY AVAILABLE**: Domain appears to be unregistered and available
- **❌ NOT AVAILABLE**: Domain is registered and not available
- **❓ UNCLEAR**: Mixed signals - manual verification recommended

### Sample Output

```
Domain: example-startup.com
Status: ✅ LIKELY AVAILABLE

WHOIS Check: Available
DNS Resolution: Not resolving

Details:
{
  "whois": {
    "available": true,
    "reason": "WHOIS parser error: No match for domain"
  },
  "dns": {
    "resolvable": false,
    "reason": "Domain does not resolve (NXDOMAIN)"
  }
}
```

## Troubleshooting

### Common Issues

**1. Import Errors**
- Make sure your virtual environment is activated
- Verify all dependencies are installed: `pip install -r requirements.txt`

**2. Timeout Issues**
- Some WHOIS servers have rate limits
- Network connectivity issues can cause timeouts

**3. DigitalOcean Deployment Issues**
- Check that the port is set to 8080 in both the code and the App Platform configuration
- Verify that all dependencies are in requirements.txt
- Check the deployment logs for any error messages

---

**Disclaimer**: This tool provides estimates of domain availability. Always verify availability through official domain registrars before making any purchase decisions.
