import logging
import collections

from mcp.server import NotificationOptions, Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool as ToolSpec
from unitycatalog_mcp.tools import (
    list_all_tools,
    Content,
)

from unitycatalog_mcp.cli import get_settings

from unitycatalog_mcp.tools.base_tool import BaseTool

# The logger instance for this module.
LOGGER = logging.getLogger(__name__)

def _warn_if_duplicate_tool_names(tools: list[BaseTool]):
    tool_names = [tool.tool_spec.name for tool in tools]
    duplicate_tool_names = [item for item, count in collections.Counter(tool_names).items() if count > 1]
    if duplicate_tool_names:
        LOGGER.warning(f"Duplicate tool names detected: {duplicate_tool_names}. For each duplicate tool name, "
                       f"picking one of the tools with that name. This can happen if your UC schema "
                       f"contains a function and a vector search index with the same name")

def get_tools_dict(settings) -> dict[str, BaseTool]:
    """
    Returns a dictionary of all tools with their names as keys and tool objects as values.
    """
    # TODO: if LLM tool name length limits allow, dedup tool names by tool type
    # (e.g. function name and vector search index name)
    all_tools = list_all_tools(settings=get_settings())
    _warn_if_duplicate_tool_names(all_tools)
    return {tool.tool_spec.name: tool for tool in list_all_tools(settings=get_settings())}

async def start() -> None:
    server = Server("mcp-unitycatalog")
    tools_dict = get_tools_dict(settings=get_settings())

    @server.list_tools()
    async def list_tools() -> list[ToolSpec]:
        return [tool.tool_spec for tool in tools_dict.values()]

    @server.call_tool()
    async def call_tool(name: str, arguments: dict) -> list[Content]:
        tool = tools_dict[name]
        return tool.execute(**arguments)

    options = server.create_initialization_options(
        notification_options=NotificationOptions(
            resources_changed=True, tools_changed=True
        )
    )
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, options, raise_exceptions=True)
