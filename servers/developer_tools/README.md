# Databricks developer tools MCP server
![status: Under Construction](https://img.shields.io/badge/status-Under_Construction-red?style=flat-square&logo=databricks)

## 🚧 Work in Progress 🚧
**This server is still under initial development and is not yet usable. Contributions are welcome!**

## Overview
A Model Context Protocol server that exposes common Databricks developer actions as tools.

## Usage
1. [Configure Databricks credentials](https://docs.databricks.com/aws/en/dev-tools/cli/authentication) with access to the required APIs
1. Add the server to your MCP client configuration. For example:

<details>
<summary>Using uv</summary>

1. Install [uv](https://docs.astral.sh/uv/getting-started/installation/)
1. Install Python using `uv python install 3.12`
1. Clone this repo `git clone https://github.com/databrickslabs/mcp.git`
1. Add to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "databricks_developer_tools": {
      "command": "uv",
      "args": [
        "run",
        "/path/to/repo/servers/developer_tools/src/server.py"
      ]
    }
  }
}
```

</details>

<details>
<summary>Using docker</summary>

### Build the image 

```docker build -t databricks-mcp-dev-tools .```

Then update your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "databricks_developer_tools": {
      "command": "docker",
      "args": [
        "run", 
        "--rm", 
        "-i", 
        "-e",
        "DATABRICKS_HOST=<YOUR-DATABRICKS-HOST>",
        "-e",
        "DATABRICKS_TOKEN=<YOUR-DATABRICKS-TOKEN>",
        "-e",
        "DATABRICKS_HTTP_PATH=<YOUR-DATABRICKS-HTTP-PATH>",
        "databricks-mcp-dev-tools"
      ]
    }
  }
}
```
</details>

<details>
<summary>Using pip</summary>

```json
{
  "mcpServers": {
    "databricks_developer_tools": {
      "command": "python",
      "args": [
        "/path/to/databricks-developer-tools/src/server.py"
      ]
    }
  }
}
```

</details>

## Supported tools

## TODO: 
- Publish the MCP as pypi package to avoid cloning the repo when using uv.
- Publish Docker image to dockerHub to avoid building the image when using docker.
