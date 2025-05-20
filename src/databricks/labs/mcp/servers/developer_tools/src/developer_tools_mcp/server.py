import logging
import collections

from mcp.server import NotificationOptions, Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool as ToolSpec

from developer_tools_mcp.tools import list_all_tools
from developer_tools_mcp.tools.base_tool import BaseTool
from developer_tools_mcp.version import VERSION

# The logger instance for this module.
LOGGER = logging.getLogger(__name__)


def _warn_if_duplicate_tool_names(tools: list[BaseTool]):
    tool_names = [tool.tool_spec.name for tool in tools]
    duplicate_tool_names = [
        item for item, count in collections.Counter(tool_names).items() if count > 1
    ]
    if duplicate_tool_names:
        LOGGER.warning(
            f"Duplicate tool names detected: {duplicate_tool_names}. "
            f"For each duplicate tool name, picking one of the tools with that name."
        )


def get_tools_dict() -> dict[str, BaseTool]:
    """
    Returns a dictionary of all tools with their names as keys and tool objects as values.
    """
    # Collect all tools from different modules
    all_tools = list_all_tools()
    
    # Add additional tools here as they become available
    # all_tools.extend(other_module_tools())
    
    _warn_if_duplicate_tool_names(all_tools)
    return {tool.tool_spec.name: tool for tool in all_tools}


async def start() -> None:
    server = Server(name="mcp-developer-tools", version=VERSION)
    tools_dict = get_tools_dict()

    @server.list_tools()
    async def list_tools() -> list[ToolSpec]:
        return [tool.tool_spec for tool in tools_dict.values()]

    @server.call_tool()
    async def call_tool(name: str, arguments: dict) -> list:
        tool = tools_dict[name]
        return tool.execute(**arguments)

    options = server.create_initialization_options(
        notification_options=NotificationOptions(
            resources_changed=True, tools_changed=True
        )
    )
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, options, raise_exceptions=True) 