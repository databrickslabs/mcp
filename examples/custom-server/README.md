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

Both approaches require first configuring Databricks authentication:
```bash
export DATABRICKS_CONFIG_PROFILE=<your-profile-name> # e.g. custom-mcp-server
databricks auth login --profile "$DATABRICKS_CONFIG_PROFILE"
```

### Using `databricks apps` CLI

To deploy the server using the `databricks apps` CLI, follow these steps:

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

[//]: # (TODO: would be nice to also be able to use the same uv command to auto-install dependencies and run the app)
Update the `app.yaml` file in this directory to use the following command:
```yaml
command: ["uvicorn", "custom_server.app:app"]
```

- In this directory, run the following command to deploy and run the MCP server on Databricks Apps:

```bash
uv build --wheel
databricks bundle deploy
databricks bundle run custom-mcp-server
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
