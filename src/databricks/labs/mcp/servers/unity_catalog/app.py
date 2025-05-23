from fastapi import FastAPI
from mcp.server import Server
from databricks.labs.mcp.servers.unity_catalog.cli import get_settings

from databricks.labs.mcp._version import __version__ as VERSION
from databricks.labs.mcp.servers.unity_catalog.server import get_tools_dict
from databricks.labs.mcp.servers.unity_catalog.tools.base_tool import BaseTool
from mcp.server.fastmcp import FastMCP

mcp_server = Server(name="mcp-unitycatalog", version=VERSION)
tools_dict: dict[str, BaseTool] = get_tools_dict(settings=get_settings())


mcp = FastMCP(
    name="mcp-unitycatalog",
)

for tool_name, tool in tools_dict.items():
    mcp.add_tool(
        tool.execute,
        name=tool_name,
        description=tool.tool_spec.description,
        annotations=tool.tool_spec.annotations,
    )

app = FastAPI(
    lifespan=lambda _: mcp.session_manager.run(),
)

streamable_app = mcp.streamable_http_app()

app.mount("/api", streamable_app)
