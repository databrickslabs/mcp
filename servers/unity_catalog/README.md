# Databricks developer tools MCP server
![status: WIP](https://img.shields.io/badge/status-WIP-red?style=flat-square&logo=databricks)

## 🚧 Work in Progress 🚧
**This server is still under initial development and must not be shared outside Databricks.**

## Overview
A Model Context Protocol server that exposes data in Unity Catalog (functions, vector search indexes), as well as Unity Catalog-powered 
Genie spaces, as tools.

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
        "/path/to/this/repo/servers/unity_catalog",
        "-s",
        // Replace with the name of your Unity Catalog schema
        "prod.genai" 
      ]
    }
  }
}
```

## Supported tools

The list of tools supported by this server is dynamically inferred based on the functions and vector search indexes
within the specified Unity Catalog schema, as well as any specified Genie spaces. In particular, the server exposes
the following tools:

* **UC Functions**: for each UC function, the server exposes a tool with the same name, arguments, and return type as the function
* **Vector search indexes**: for each vector search index, the server exposes a tool for querying that vector search index
* **Genie spaces**: for each Genie space, the server exposes tools for managing conversations and sending questions to the space
