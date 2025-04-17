## Contributing

We happily welcome contributions to the MCP servers in this repo. We use GitHub Issues to track community reported issues and GitHub Pull Requests for accepting changes.

For new feature requests or contributions (e.g. adding a new server), please file an issue or reach out [via Slack](https://databricks.enterprise.slack.com/archives/C065NC65Q9F) to facilitate initial discussion,
before sending a pull request

### Guidelines for MCP servers

For consistency, MCP servers in this repo:
* Must be implemented using https://github.com/modelcontextprotocol/python-sdk (which implies they’re written as Python FastAPI servers), for ease of maintenance and to help ensure servers follow MCP’s best practices.
* Must be unit-tested
