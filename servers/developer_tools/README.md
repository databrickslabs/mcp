# Databricks developer tools MCP server
![status: WIP](https://img.shields.io/badge/status-WIP-red?style=flat-square&logo=databricks)

## 🚧 Work in Progress 🚧
**This server is still under initial development and must not be shared outside Databricks.**

## Overview
A Model Context Protocol server that exposes common Databricks developer actions as tools.

## Usage
1. Install uv from Astral
1. Install Python using `uv python install 3.12`
1. [Configure Databricks credentials](https://docs.databricks.com/aws/en/dev-tools/cli/authentication) with access to the required APIs
1. Add the server to your MCP client configuration. For example, to use this server with Claude Desktop, add the following to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "databricks_unity_catalog": {
      "command": "uv",
      "args": [
        "--directory",
        "/path/to/this/repo/servers/developer_tools"
      ]
    }
  }
}
```

## Supported tools

TODO: add a list here
