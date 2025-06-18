import json
from pydantic import BaseModel
from databricks.sdk import WorkspaceClient
from databricks.vector_search.client import VectorSearchClient
from databricks.labs.mcp.servers.unity_catalog.tools.base_tool import BaseTool
from databricks.labs.mcp.servers.unity_catalog.cli import CliSettings
from mcp.types import TextContent, Tool as ToolSpec

# Constant storing vector index content vector column name
CONTENT_VECTOR_COLUMN_NAME = "__db_content_vector"
CONTENT_VECTOR_COLUMN_STARTS_WITH= "__db_"


class QueryInput(BaseModel):
    query: str
    num_results: int


class VectorSearchTool(BaseTool):
    def __init__(
        self,
        endpoint_name: str,
        index_name: str,
        tool_name: str,
        columns: list[str],
        num_results: int = 5,
    ):
        self.endpoint_name = endpoint_name
        self.index_name = index_name
        self.tool_name = tool_name
        self.columns = columns
        self.num_results = num_results

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
            num_results=model.num_results,
        )

        docs = results.get("result", {}).get("data_array", [])

        return [TextContent(type="text", text=json.dumps(docs, indent=2))]


def get_table_columns(
    workspace_client: WorkspaceClient, full_table_name: str
) -> list[str]:
    table_info = workspace_client.tables.get(full_table_name)
    return [
        col.name for col in table_info.columns if (not col.name.startswith(CONTENT_VECTOR_COLUMN_STARTS_WITH) )  # col.name  != CONTENT_VECTOR_COLUMN_NAME
    ]


def _list_vector_search_tools(
    workspace_client: WorkspaceClient,
    catalog_name: str,
    schema_name: str,
    vector_search_num_results: int,
) -> list[VectorSearchTool]:
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

        tools.append(
            VectorSearchTool(
                endpoint, index_name, tool_name, columns, vector_search_num_results
            )
        )

    return tools


def list_vector_search_tools(settings: CliSettings) -> list[VectorSearchTool]:
    workspace_client = WorkspaceClient()
    catalog_name, schema_name = settings.schema_full_name.split(".")
    return _list_vector_search_tools(
        workspace_client, catalog_name, schema_name, settings.vector_search_num_results
    )
