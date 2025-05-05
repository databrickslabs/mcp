# Databricks MCP servers

![Test Status](https://github.com/databrickslabs/mcp/actions/workflows/unit_tests.yml/badge.svg)

Table of Contents
=================

- [Databricks MCP servers](#databricks-mcp-servers)
- [Table of Contents](#table-of-contents)
  - [Overview](#overview)
  - [Unity Catalog Server](#unity-catalog-server)
    - [Overview](#overview-1)
    - [Usage](#usage)
    - [Supported tools](#supported-tools)
  - [Developer Tools Server](#developer-tools-server)
  - [Deploying the MCP server on Databricks Apps](#deploying-the-mcp-server-on-databricks-apps)
  - [Support](#support)
  - [Contributing](#contributing)

## Overview
An experimental collection of [MCP](https://modelcontextprotocol.io/introduction) servers to help AI agents fetch enterprise data from Databricks, automate common developer actions on Databricks, etc:

* ![status: Beta](https://img.shields.io/badge/status-Beta-yellow?style=flat-square&logo=databricks)
  [Databricks Unity Catalog server](#unity-catalog-server): Fetch data and run tools registered in from Unity Catalog, making agents aware of your enterprise data
* ![status: Under construction](https://img.shields.io/badge/status-Under_construction-red?style=flat-square&logo=databricks)
  [Databricks developer tools server](#developer-tools-server): Perform common developer actions in Databricks, like creating and updating notebooks, running jobs, etc. This server is not yet usable, but contributions are welcome! 
  Note: if developing from within the Databricks product (e.g. using Databricks notebooks), we recommend using [Databricks Assistant](https://docs.databricks.com/aws/en/notebooks/databricks-assistant-faq)

The set of servers and tools in this repo is fluid and will evolve over time. We welcome contributions to this repo - please first
read the [contributor guidelines](CONTRIBUTING.md) to streamline the process and discover areas where help is needed.

## Unity Catalog Server

![status: Beta](https://img.shields.io/badge/status-Beta-yellow?style=flat-square&logo=databricks)

### Overview
A Model Context Protocol server that exposes structured and unstructured data in Unity Catalog ([vector search indexes](https://docs.databricks.com/gcp/en/generative-ai/vector-search), [functions](https://docs.databricks.com/aws/en/generative-ai/agent-framework/create-custom-tool), and [Genie spaces](https://docs.databricks.com/aws/en/genie/)), as tools.

<img src="docs/images/demo.png" alt="Demo image" height="400px">

### Usage
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
        "/path/to/this/repo",
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

### Supported tools

The list of tools supported by this server is dynamically inferred at startup time based on the functions and vector search indexes
within the specified Unity Catalog schema, as well as any specified Genie spaces. In particular, the server exposes
the following tools:

* **UC Functions**: for each UC function, the server exposes a tool with the same name, arguments, and return type as the function
* **Vector search indexes**: for each vector search index, the server exposes a tool for querying that vector search index
* **Genie spaces**: for each Genie space, the server exposes tools for managing conversations and sending questions to the space

## Developer Tools Server

This server is currently under construction. It is not yet usable, but contributions are welcome!

## Deploying the MCP server on Databricks Apps

This server can be deployed on Databricks Apps. To do so, follow the instructions below:
1. Move into the project directory:
```bash
cd /path/to/this/repo
```

2. Deploy the app:
```bash
databricks bundle deploy -p <name-of-your-profile>
```

3. Run the app:
```bash
databricks bundle run mcp-on-apps -p <name-of-your-profile>
```

## Support
Please note that all projects in the `databrickslabs` GitHub organization are provided for your exploration only, and are not formally supported by Databricks with Service Level Agreements (SLAs).  They are provided AS-IS and we do not make any guarantees of any kind.  Please do not submit a support ticket relating to any issues arising from the use of these projects.

Any issues discovered through the use of this project should be filed as GitHub Issues on the Repo.  They will be reviewed as time permits, but there are no formal SLAs for support.

## Contributing

We welcome contributions :) - see [CONTRIBUTING.md](./CONTRIBUTING.md) for details. Please make sure to read this guide before 
submitting pull requests, to ensure your contribution has the best chance of being accepted.

