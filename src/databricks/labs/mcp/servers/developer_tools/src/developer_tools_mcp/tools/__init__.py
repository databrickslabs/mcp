from typing import TypeAlias, Union
from mcp.types import (
    TextContent,
    ImageContent,
    EmbeddedResource,
)

from developer_tools_mcp.tools.jobs import list_jobs_tool
from developer_tools_mcp.tools.test_connection import test_connection_tool
from developer_tools_mcp.tools.sql_query import sql_query_tool

Content: TypeAlias = Union[TextContent, ImageContent, EmbeddedResource]


def list_all_tools():
    tools = []
    tools.extend(list_jobs_tool())
    tools.extend(test_connection_tool())
    tools.extend(sql_query_tool())
    return tools