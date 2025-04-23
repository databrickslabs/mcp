# Databricks developer tools MCP server
![status: Under Construction](https://img.shields.io/badge/status-Under_Construction-red?style=flat-square&logo=databricks)

## 🚧 Work in Progress 🚧
**This server is still under initial development and is not yet usable. Contributions are welcome!**

## Overview
A Model Context Protocol server that exposes common Databricks developer actions as tools.

## Usage
1. Install [uv](https://docs.astral.sh/uv/getting-started/installation/)
1. Install Python using `uv python install 3.12`
1. [Configure Databricks credentials](https://docs.databricks.com/aws/en/dev-tools/cli/authentication) with access to the required APIs
1. Add the server to your MCP client configuration. For example, to use this server with Claude Desktop, add the following to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "databricks_developer_tools": {
      "command": "/path/to/uv/executable/uv",
      "args": [
        "--directory",
        "/path/to/this/repo/servers/developer_tools",
        "run",
        "databricks-developer-tools"
      ]
    }
  }
}
```

## Supported tools

TODO: add a list here
