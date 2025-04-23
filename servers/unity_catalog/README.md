# Databricks Unity Catalog MCP server
![status: Beta](https://img.shields.io/badge/status-Beta-yellow?style=flat-square&logo=databricks)

## Overview
A Model Context Protocol server that exposes structured and unstructured data in Unity Catalog ([vector search indexes](https://docs.databricks.com/gcp/en/generative-ai/vector-search), [functions](https://docs.databricks.com/aws/en/generative-ai/agent-framework/create-custom-tool), and 
[Genie spaces](https://docs.databricks.com/aws/en/genie/)), as tools.

<img src="docs/images/demo.png" alt="Demo image" height="400px">

![Demo image](docs/images/demo.png)

## Usage
1. Install [uv](https://docs.astral.sh/uv/getting-started/installation/)
1. Install Python using `uv python install 3.12`
1. [Configure Databricks credentials](https://docs.databricks.com/aws/en/dev-tools/cli/authentication) with access to the required APIs
1. Add the server to your MCP client configuration. For example, to use this server with Claude Desktop, add the following to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "databricks_unity_catalog": {
      "command": "/path/to/uv/executable/uv",
      "args": [
        "--directory",
        "/path/to/this/repo/servers/unity_catalog",
        "run",
        "unitycatalog-mcp",
        "-s",
        "your_catalog.your_schema",
        "-g",
        "genie_space_id_1,genie_space_id_2"
      ]
    }
  }
}
```

## Supported tools

The list of tools supported by this server is dynamically inferred at startup time based on the functions and vector search indexes
within the specified Unity Catalog schema, as well as any specified Genie spaces. In particular, the server exposes
the following tools:

* **UC Functions**: for each UC function, the server exposes a tool with the same name, arguments, and return type as the function
* **Vector search indexes**: for each vector search index, the server exposes a tool for querying that vector search index
* **Genie spaces**: for each Genie space, the server exposes tools for managing conversations and sending questions to the space
