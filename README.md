# Databricks MCP servers
![status: WIP](https://img.shields.io/badge/status-WIP-red?style=flat-square&logo=databricks)

## 🚧 Work in Progress 🚧

**This repo is still under initial development and must not be shared outside Databricks.**

## Overview
A collection of [MCP](https://modelcontextprotocol.io/introduction) servers to help AI agents take common developer actions on Databricks, fetch data from Databricks, etc:

* 🚧 [Databricks Unity Catalog server](./unity_catalog): Fetch data and run tools registered in from Unity Catalog, making agents aware of your enterprise data
* 🚧 [Databricks developer tools server](./developer_tools): Perform common developer actions in Databricks, like creating and updating notebooks, running jobs, etc.

## Usage
See the `README.md` in each server's directory for detailed instructions.
For most servers, the following steps work: 

1. Install uv from Astral
1. Install Python using `uv python install 3.12`
1. [Configure Databricks credentials](https://docs.databricks.com/aws/en/dev-tools/cli/authentication) with access to the required APIs
1. Add the server to your MCP client configuration. For example, to use the Databricks Unity Catalog MCP server with Claude Desktop, add the following to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "databricks_unity_catalog": {
      "command": "uv",
      "args": [
        "--directory",
        "/path/to/this/repo/servers/unity_catalog",
        "-s",
        "prod.genai"
      ]
    }
  }
}
```

## Support
Please note that all projects in the /databrickslabs github account are provided for your exploration only, and are not formally supported by Databricks with Service Level Agreements (SLAs).  They are provided AS-IS and we do not make any guarantees of any kind.  Please do not submit a support ticket relating to any issues arising from the use of these projects.

Any issues discovered through the use of this project should be filed as GitHub Issues on the Repo.  They will be reviewed as time permits, but there are no formal SLAs for support.

## Contributing

We welcome contributions :) - see [CONTRIBUTING.md](./CONTRIBUTING.md) for details. Please make sure to read this guide before 
submitting pull requests, to ensure your contribution has the best chance of being accepted.
