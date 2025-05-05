from mcp.server import NotificationOptions, Server
from mcp.types import Tool as ToolSpec
from mcp.server.sse import SseServerTransport
import uvicorn
from databricks.labs.mcp.servers.unity_catalog.tools import (
    Content,
)
from starlette.applications import Starlette
from starlette.routing import Mount, Route
from databricks.labs.mcp.servers.unity_catalog.cli import get_settings

from databricks.labs.mcp._version import __version__ as VERSION
from databricks.labs.mcp.servers.unity_catalog.server import get_tools_dict


server = Server(name="mcp-unitycatalog", version=VERSION)
tools_dict = get_tools_dict(settings=get_settings())


@server.list_tools()
async def list_tools() -> list[ToolSpec]:
    return [tool.tool_spec for tool in tools_dict.values()]


@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[Content]:
    tool = tools_dict[name]
    return tool.execute(**arguments)


sse = SseServerTransport("/messages/")


# Define handler functions
async def handle_sse(request):
    async with sse.connect_sse(
        request.scope, request.receive, request._send
    ) as streams:
        await server.run(
            streams[0],
            streams[1],
            server.create_initialization_options(
                notification_options=NotificationOptions(
                    resources_changed=True, tools_changed=True
                )
            ),
        )


# Create Starlette routes for SSE and message handling
routes = [
    Route("/sse", endpoint=handle_sse),
    Mount("/messages/", app=sse.handle_post_message),
]

# Create and run Starlette app
app = Starlette(routes=routes)


def start_app():
    uvicorn.run(app, host="0.0.0.0", port=8000)


if __name__ == "__main__":
    start_app()
