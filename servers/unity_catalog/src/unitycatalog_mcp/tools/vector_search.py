import io
import json
from contextlib import redirect_stdout

from databricks_openai import VectorSearchRetrieverTool
from databricks.sdk import WorkspaceClient

from mcp.types import Tool as ToolSpec, TextContent

from unitycatalog_mcp.tools.base_tool import BaseTool


class VectorSearchTool(BaseTool):
    def __init__(self, tool_obj: VectorSearchRetrieverTool):
        self.tool_obj = tool_obj
        tool_info = tool_obj.tool["function"]
        llm_friendly_tool_name = tool_info["name"]
        tool_spec = ToolSpec(
            name=llm_friendly_tool_name,
            description=tool_info["description"],
            inputSchema=tool_info["parameters"],
        )
        super().__init__(tool_spec=tool_spec)

    def execute(self, **kwargs):
        """
        Executes the vector search tool with the provided arguments.
        """
        # Create a buffer to capture stdout from vector search client
        # print statements
        f = io.StringIO()
        with redirect_stdout(f):
            res = self.tool_obj.execute(**kwargs)
            return [
                TextContent(
                    type="text",
                    text=json.dumps(vs_res),
                )
                for vs_res in res
            ]

def _list_vector_search_tools(workspace_client: WorkspaceClient, catalog_name: str, schema_name: str) -> list[VectorSearchTool]:
    tools = []
    for table in workspace_client.tables.list(
            catalog_name=catalog_name, schema_name=schema_name
    ):
        # TODO: support filtering tables by securable kind (e.g. by making securable
        # kind accessible here)
        if not table.properties or "model_endpoint_url" not in table.properties:
            continue
        tool_obj = VectorSearchRetrieverTool(index_name=table.full_name)
        tools.append(VectorSearchTool(tool_obj))
    return tools

def list_vector_search_tools(settings) -> list[VectorSearchTool]:
    workspace_client = WorkspaceClient()
    catalog_name, schema_name = settings.schema_full_name.split(".")
    return _list_vector_search_tools(workspace_client, catalog_name, schema_name)
