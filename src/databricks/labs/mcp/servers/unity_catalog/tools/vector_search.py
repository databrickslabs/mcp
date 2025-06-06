import json
from typing import List

from pydantic import BaseModel
from databricks.sdk import WorkspaceClient
from databricks.vector_search.client import VectorSearchClient
from databricks.labs.mcp.servers.unity_catalog.tools.base_tool import BaseTool
from mcp.types import TextContent, Tool as ToolSpec


class QueryInput(BaseModel):
    query: str


class VectorSearchTool(BaseTool):
    def __init__(self, endpoint_name: str, index_name: str, tool_name: str, columns: List[str]):
        self.endpoint_name = endpoint_name
        self.index_name = index_name
        self.tool_name = tool_name
        self.columns = columns

        tool_spec = ToolSpec(
            name=tool_name,
            description=f"Searches the vector index `{index_name}`.",
            inputSchema=QueryInput.model_json_schema(),
        )
        super().__init__(tool_spec)

    def execute(self, **kwargs):
        model = QueryInput.model_validate(kwargs)
        vsc = VectorSearchClient(disable_notice=True)

        index = vsc.get_index(index_name=self.index_name)

        results = index.similarity_search(
            query_text=model.query,
            columns=self.columns,
            num_results=5,
        )

        docs = results.get("result", {}).get("data_array", [])

        return [TextContent(type="text", text=json.dumps(docs, indent=2))]


def get_table_columns(workspace_client: WorkspaceClient, full_table_name: str) -> List[str]:
    table_info = workspace_client.tables.get(full_table_name)
    return [
        col.name
        for col in table_info.columns
        if col.name != "__db_content_vector"
    ]

def _list_vector_search_tools(
    workspace_client: WorkspaceClient, catalog_name: str, schema_name: str
) -> List[VectorSearchTool]:
    tools = []
    for table in workspace_client.tables.list(
        catalog_name=catalog_name, schema_name=schema_name
    ):
        if not table.properties or "model_endpoint_url" not in table.properties:
            continue

        endpoint = table.properties["model_endpoint_url"]
        index_name = table.full_name
        tool_name = f"vector_search_{table.name}"

        columns = get_table_columns(workspace_client, index_name)

        tools.append(VectorSearchTool(endpoint, index_name, tool_name, columns))

    return tools


def list_vector_search_tools(settings) -> List[VectorSearchTool]:
    workspace_client = WorkspaceClient()
    catalog_name, schema_name = settings.schema_full_name.split(".")
    return _list_vector_search_tools(workspace_client, catalog_name, schema_name)
