import json
from typing import Optional
from pydantic import BaseModel
from databricks.sdk import WorkspaceClient
from databricks.labs.mcp.servers.unity_catalog.tools.base_tool import BaseTool
from databricks.labs.mcp.servers.unity_catalog.cli import CliSettings
from mcp.types import TextContent, Tool as ToolSpec


class ListTablesInput(BaseModel):
    catalog_name: Optional[str] = None
    schema_name: Optional[str] = None
    max_results: Optional[int] = None


class GetTableInput(BaseModel):
    full_name: str


class ListTableSummariesInput(BaseModel):
    catalog_name: Optional[str] = None
    schema_name_pattern: Optional[str] = None
    table_name_pattern: Optional[str] = None
    max_results: Optional[int] = None


class ListCatalogsInput(BaseModel):
    max_results: Optional[int] = None


class ListSchemasInput(BaseModel):
    catalog_name: Optional[str] = None
    max_results: Optional[int] = None


class TableBaseTool(BaseTool):
    def __init__(self, tool_spec: ToolSpec):
        self.tool_spec = tool_spec


class ListTablesTool(TableBaseTool):
    def __init__(self):
        tool_spec = ToolSpec(
            name="list_tables",
            description="List tables in a Unity Catalog schema. Returns detailed information about tables including columns, properties, and metadata.",
            inputSchema=ListTablesInput.model_json_schema(),
        )
        super().__init__(tool_spec)

    def execute(self, **kwargs):
        model = ListTablesInput.model_validate(kwargs)
        workspace_client = WorkspaceClient()

        # Use settings if catalog_name/schema_name not provided
        settings = CliSettings()
        catalog_name = model.catalog_name or settings.get_catalog_name()
        schema_name = model.schema_name or settings.get_schema_name()

        if not catalog_name or not schema_name:
            raise ValueError(
                "catalog_name and schema_name must be provided or configured in settings"
            )

        tables = list(
            workspace_client.tables.list(
                catalog_name=catalog_name,
                schema_name=schema_name,
                max_results=model.max_results,
            )
        )

        # Convert to JSON-serializable format using the SDK's as_dict() method
        tables_data = [table.as_dict() for table in tables]

        return [TextContent(type="text", text=json.dumps(tables_data, indent=2))]


class GetTableTool(TableBaseTool):
    def __init__(self):
        tool_spec = ToolSpec(
            name="get_table",
            description="Get detailed information about a specific table including its schema, properties, and metadata.",
            inputSchema=GetTableInput.model_json_schema(),
        )
        super().__init__(tool_spec)

    def execute(self, **kwargs):
        model = GetTableInput.model_validate(kwargs)
        workspace_client = WorkspaceClient()

        table = workspace_client.tables.get(full_name=model.full_name)

        # Convert to JSON-serializable format using the SDK's as_dict() method
        table_data = table.as_dict()

        return [TextContent(type="text", text=json.dumps(table_data, indent=2))]


class ListTableSummariesTool(TableBaseTool):
    def __init__(self):
        tool_spec = ToolSpec(
            name="list_table_summaries",
            description="List table summaries for a catalog and schema. Returns concise information about tables including name, type, and basic metadata.",
            inputSchema=ListTableSummariesInput.model_json_schema(),
        )
        super().__init__(tool_spec)

    def execute(self, **kwargs):
        model = ListTableSummariesInput.model_validate(kwargs)
        workspace_client = WorkspaceClient()

        # Use settings if catalog_name not provided
        settings = CliSettings()
        catalog_name = model.catalog_name or settings.get_catalog_name()

        if not catalog_name:
            raise ValueError("catalog_name must be provided or configured in settings")

        summaries = list(
            workspace_client.tables.list_summaries(
                catalog_name=catalog_name,
                schema_name_pattern=model.schema_name_pattern,
                table_name_pattern=model.table_name_pattern,
                max_results=model.max_results,
            )
        )

        # Convert to JSON-serializable format using the SDK's as_dict() method
        summaries_data = [summary.as_dict() for summary in summaries]

        return [TextContent(type="text", text=json.dumps(summaries_data, indent=2))]


class ListCatalogsTool(TableBaseTool):
    def __init__(self):
        tool_spec = ToolSpec(
            name="list_catalogs",
            description="List all catalogs in the Unity Catalog metastore that the user has access to.",
            inputSchema=ListCatalogsInput.model_json_schema(),
        )
        super().__init__(tool_spec)

    def execute(self, **kwargs):
        model = ListCatalogsInput.model_validate(kwargs)
        workspace_client = WorkspaceClient()

        catalogs = list(workspace_client.catalogs.list(max_results=model.max_results))

        # Convert to JSON-serializable format using the SDK's as_dict() method
        catalogs_data = [catalog.as_dict() for catalog in catalogs]

        return [TextContent(type="text", text=json.dumps(catalogs_data, indent=2))]


class ListSchemasTool(TableBaseTool):
    def __init__(self):
        tool_spec = ToolSpec(
            name="list_schemas",
            description="List schemas in a Unity Catalog catalog that the user has access to.",
            inputSchema=ListSchemasInput.model_json_schema(),
        )
        super().__init__(tool_spec)

    def execute(self, **kwargs):
        model = ListSchemasInput.model_validate(kwargs)
        workspace_client = WorkspaceClient()

        # Use settings if catalog_name not provided
        settings = CliSettings()
        catalog_name = model.catalog_name or settings.get_catalog_name()

        if not catalog_name:
            raise ValueError("catalog_name must be provided or configured in settings")

        schemas = list(
            workspace_client.schemas.list(
                catalog_name=catalog_name, max_results=model.max_results
            )
        )

        # Convert to JSON-serializable format using the SDK's as_dict() method
        schemas_data = [schema.as_dict() for schema in schemas]

        return [TextContent(type="text", text=json.dumps(schemas_data, indent=2))]


def list_table_tools(settings: CliSettings) -> list[TableBaseTool]:
    """Returns a list of all table tools."""
    return [
        ListTablesTool(),
        GetTableTool(),
        ListTableSummariesTool(),
        ListCatalogsTool(),
        ListSchemasTool(),
    ]
