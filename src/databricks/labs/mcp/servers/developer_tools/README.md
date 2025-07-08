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
1. Create a file named `.env`
1. Add to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "databricks-developer-tools": {
      "command": "uv",
      "args": [
        "run",
        "--directory",
        "path/to/developer/tools/folder",
        "--env-file",
        "path/to/envfile/.env",
        "developer-tools-mcp"
      ]
    }
  }
}
```

Create the file named `.env` with the following content:

```
DATABRICKS_HOST=dbc-123abc45-6def.cloud.databricks.com
DATABRICKS_TOKEN=dapi123456789abcdef
DATABRICKS_HTTP_PATH=/sql/1.0/warehouses/abc123def456ghi
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
        "/path/to/databricks-developer-tools/src/developer_tools_mcp"
      ],
      "env": {
        "DATABRICKS_HOST": "<YOUR-DATABRICKS-HOST>",
        "DATABRICKS_TOKEN": "<YOUR-DATABRICKS-TOKEN>",
        "DATABRICKS_HTTP_PATH": "<YOUR-DATABRICKS-HTTP-PATH>"
      }
    }
  }
}
```

</details>

## Supported tools

The following tools are currently implemented and available:

### Jobs Management
- **list_jobs**: Lists all jobs in the workspace with basic information like job ID, name, and creator.
- **get_job**: Gets detailed information about a specific job by ID.

### SQL Querying
- **run_sql_query**: Executes SQL queries on Databricks SQL warehouse and returns results as a markdown table. Useful for data exploration and extraction.

### Connection Testing
- **test_connection**: Tests connectivity to both the Databricks API and SQL warehouse to verify your credentials and configuration.

## TODO: 
- Publish the MCP as pypi package to avoid cloning the repo when using uv.
- Publish Docker image to dockerHub to avoid building the image when using docker.
