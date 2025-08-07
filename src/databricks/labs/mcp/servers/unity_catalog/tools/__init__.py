import collections
from typing import TypeAlias, Union
from mcp.server.fastmcp import FastMCP
from mcp.types import (
    TextContent,
    ImageContent,
    EmbeddedResource,
)

from databricks.labs.mcp._version import __version__ as VERSION
from databricks.labs.mcp.servers.unity_catalog.cli import get_settings
from databricks.labs.mcp.servers.unity_catalog.tools.base_tool import BaseTool
from databricks.labs.mcp.servers.unity_catalog.tools.genie import (
    GenieTool,
    list_genie_tools,
)
from databricks.labs.mcp.servers.unity_catalog.tools.functions import (
    UCFunctionTool,
    list_uc_function_tools,
)
from databricks.labs.mcp.servers.unity_catalog.tools.vector_search import (
    VectorSearchTool,
    list_vector_search_tools,
)
from databricks.labs.mcp.servers.unity_catalog.tools.tables import (
    TableBaseTool,
    list_table_tools,
)
from databricks.labs.mcp.utils import logger

Content: TypeAlias = Union[TextContent, ImageContent, EmbeddedResource]
AvailableTool = UCFunctionTool | VectorSearchTool | GenieTool | BaseTool | TableBaseTool


def list_all_tools(settings) -> list[AvailableTool]:
    """
    Returns a list of all available tools, including Genie tools, UC functions, vector search tools, and metadata tools.
    This function aggregates tools from different sources and returns them in a single list.
    """

    return (
        list_genie_tools(settings)
        + list_vector_search_tools(settings)
        + list_uc_function_tools(settings)
        + list_table_tools(settings)
    )


def _warn_if_duplicate_tool_names(tools: list[AvailableTool]):
    tool_names = [tool.tool_spec.name for tool in tools]
    duplicate_tool_names = [
        item for item, count in collections.Counter(tool_names).items() if count > 1
    ]
    if duplicate_tool_names:
        logger.warning(
            f"Duplicate tool names detected: {duplicate_tool_names}. For each duplicate tool name, "
            f"picking one of the tools with that name. This can happen if your UC schema "
            f"contains a function and a vector search index with the same name"
        )


def get_tools_dict() -> dict[str, AvailableTool]:
    """
    Returns a dictionary of all tools with their names as keys and tool objects as values.
    """
    # TODO: if LLM tool name length limits allow, dedup tool names by tool type
    # (e.g. function name and vector search index name)
    settings = get_settings()
    all_tools = list_all_tools(settings=settings)
    _warn_if_duplicate_tool_names(all_tools)
    return {tool.tool_spec.name: tool for tool in list_all_tools(settings=settings)}


def get_prepared_mcp_app() -> FastMCP:
    logger.info(
        f"Starting MCP Unity Catalog server version {VERSION} with settings: {get_settings()}"
    )
    mcp = FastMCP(
        name="mcp-unitycatalog",
    )
    tools_dict = get_tools_dict()

    @mcp._mcp_server.list_tools()
    async def list_tools():
        return [tool.tool_spec for tool in tools_dict.values()]

    @mcp._mcp_server.call_tool()
    async def call_tool(name: str, arguments: dict):
        tool = tools_dict[name]
        return tool.execute(**arguments)

    logger.info(f"Registered {len(tools_dict)} tools: {', '.join(tools_dict.keys())}")
    return mcp
