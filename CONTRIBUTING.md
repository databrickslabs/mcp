## Contributing

We happily welcome contributions to the MCP servers in this repo. We use GitHub Issues to track community reported issues and feature requests, 
and GitHub Pull Requests for accepting changes.

See [issues](https://github.com/databrickslabs/mcp/issues) with the "help wanted" or "bug" labels for items that we'd especially like help with.

For major new features or changes (e.g. adding a new server, removing tool(s) from an existing server), please file an issue to facilitate initial discussion,
before sending a pull request. For smaller changes (e.g. fixing a bug, adding a new tool, improving test coverage), feel free to send a pull request directly.

### Running tests

First, install test requirements from within the directory of the server you're working on:

```bash
uv sync
uv pip install --group dev
```

To run tests:

```bash
uv run pytest tests
```

To run and fix lint errors, run the following from the repo root directory:
```bash
./dev/lint.sh --fix
```

### Guidelines for MCP servers

For consistency, MCP servers in this repo:
* Must be implemented using https://github.com/modelcontextprotocol/python-sdk (which implies they’re written as Python FastAPI servers), for ease of maintenance and to help ensure servers follow MCP’s best practices.
* Must be unit-tested
