# Databricks MCP servers

![Test Status](https://github.com/databrickslabs/mcp/actions/workflows/unit_tests.yml/badge.svg)

## Overview
An experimental collection of [MCP](https://modelcontextprotocol.io/introduction) servers to help AI agents fetch enterprise data from Databricks, automate common developer actions on Databricks, etc:

* ![status: Beta](https://img.shields.io/badge/status-Beta-yellow?style=flat-square&logo=databricks)
  [Databricks Unity Catalog server](./servers/unity_catalog/README.md): Fetch data and run tools registered in from Unity Catalog, making agents aware of your enterprise data
* ![status: Under construction](https://img.shields.io/badge/status-Under_construction-red?style=flat-square&logo=databricks)
  [Databricks developer tools server](./servers/developer_tools/README.md): Perform common developer actions in Databricks, like creating and updating notebooks, running jobs, etc. This server is not yet usable, but contributions are welcome!

The set of servers and tools in this repo is fluid and will evolve over time. We welcome contributions to this repo - please first
read the [contributor guidelines](CONTRIBUTING.md) to streamline the process and discover areas where help is needed.

## Usage
See the `README.md` in each server's directory for detailed instructions.
For most servers, the following steps work: 

1. Install [uv](https://docs.astral.sh/uv/getting-started/installation/)
1. Install Python using `uv python install 3.12`
1. [Configure Databricks credentials](https://docs.databricks.com/aws/en/dev-tools/cli/authentication) with access to the required APIs
1. Add the server to your MCP client configuration. For example, to use the Databricks Unity Catalog MCP server with Claude Desktop, add the following to your `claude_desktop_config.json`:

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

## Support
Please note that all projects in the `databrickslabs` GitHub organization are provided for your exploration only, and are not formally supported by Databricks with Service Level Agreements (SLAs).  They are provided AS-IS and we do not make any guarantees of any kind.  Please do not submit a support ticket relating to any issues arising from the use of these projects.

Any issues discovered through the use of this project should be filed as GitHub Issues on the Repo.  They will be reviewed as time permits, but there are no formal SLAs for support.

## Contributing

We welcome contributions :) - see [CONTRIBUTING.md](./CONTRIBUTING.md) for details. Please make sure to read this guide before 
submitting pull requests, to ensure your contribution has the best chance of being accepted.
