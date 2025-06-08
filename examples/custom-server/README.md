# Example - custom MCP server on Databricks Apps

This example shows how to create and launch a custom agent on Databricks Apps.
Please note that this example doesn't use any Databricks SDK, and is independent of the `mcp` package in the root dir of this repo.

## Prerequisites

- Databricks CLI installed and configured
- `uv`

## Local development

- run `uv` sync:

```bash
uv sync
```

- start the server locally. Changes will trigger a reload:

```bash
uvicorn custom-server.app:mcp --reload
```

## Deploying a custom MCP server on Databricks Apps

There are two ways to deploy the server on Databricks Apps: using the `databricks apps` CLI or using the `databricks bundle` CLI. Depending on your preference, you can choose either method.

### Using `databricks apps` CLI

To deploy the server using the `databricks apps` CLI, follow these steps:

Ensure Databricks authentication is configured:
```bash
databricks auth login # Skip specifying a profile name when prompted
```

Create a Databricks app to host your MCP server:
```bash
databricks apps create mcp-custom-server
```

Upload the source code to Databricks and deploy the app:

```bash
DATABRICKS_USERNAME=$(databricks current-user me | jq -r .userName)
databricks sync . "/Users/$DATABRICKS_USERNAME/my-mcp-server"
databricks apps deploy mcp-custom-server --source-code-path "/Workspace/Users/$DATABRICKS_USERNAME/my-mcp-server"
```

### Using `databricks bundle` CLI

To deploy the server using the `databricks bundle` CLI, follow these steps

- In this directory, run the following command to deploy and run the MCP server on Databricks Apps:

```bash
uv build --wheel
databricks bundle deploy -p <name-of-your-profile>
databricks bundle run custom-server -p <name-of-your-profile>
```


3. Deploy the app using the `databricks apps` CLI:
```bash
databricks sync ./build -p <your-profile-name> /Workspace/Users/my-email@org.com/my-app
databricks apps deploy my-app-name -p <your-profile-name> --source-code-path /Workspace/Users/my-email@org.com/my-app
databricks apps start my-app-name -p <your-profile-name>
```

## Connecting to the MCP server

[//]: # (TODO: once official Databricks docs for using MCP servers in agents are live, replace this with a link)
[//]: # (to that section)

To connect to the MCP server, use the `Streamable HTTP` transport with the following URL:

```
https://your-app-url.usually.ends.with.databricksapps.com/mcp/
```

For authentication, you can use the `Bearer` token from your Databricks profile.
You can get the token by running the following command:

```bash
databricks auth token -p <name-of-your-profile>
```

Please note that the URL should end with `/mcp/` (including the trailing slash), as this is required for the server to work correctly.
