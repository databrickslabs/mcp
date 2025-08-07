import pytest
from unittest.mock import Mock, patch
from databricks.sdk.service.catalog import (
    TableInfo,
    TableSummary,
    CatalogInfo,
    SchemaInfo,
    TableType,
)
from databricks.labs.mcp.servers.unity_catalog.tools.tables import (
    ListTablesTool,
    GetTableTool,
    ListTableSummariesTool,
    ListCatalogsTool,
    ListSchemasTool,
    list_table_tools,
)


class DummyTablesAPI:
    def list(self, catalog_name=None, schema_name=None, max_results=None):
        # Create a real TableInfo object
        table_info = TableInfo(
            name="test_table",
            full_name="catalog.schema.test_table",
            catalog_name="catalog",
            schema_name="schema",
            table_type=TableType.MANAGED,
            columns=[],
            properties={},
            comment="Test table",
            created_by="test_user",
            updated_by="test_user",
            owner="test_user",
        )
        return [table_info]

    def get(self, full_name):
        # Create a real TableInfo object
        return TableInfo(
            name="test_table",
            full_name=full_name,
            catalog_name="catalog",
            schema_name="schema",
            table_type=TableType.MANAGED,
            columns=[],
            properties={},
            comment="Test table",
            created_by="test_user",
            updated_by="test_user",
            owner="test_user",
        )

    def list_summaries(
        self,
        catalog_name=None,
        schema_name_pattern=None,
        table_name_pattern=None,
        max_results=None,
    ):
        # Create a real TableSummary object
        summary = TableSummary(
            full_name="catalog.schema.test_table",
            table_type=TableType.MANAGED,
        )
        return [summary]


class DummyCatalogsAPI:
    def list(self, max_results=None):
        # Create a real CatalogInfo object
        catalog = CatalogInfo(
            name="test_catalog",
            comment="Test catalog",
            properties={},
            created_by="test_user",
            updated_by="test_user",
            owner="test_user",
        )
        return [catalog]


class DummySchemasAPI:
    def list(self, catalog_name=None, max_results=None):
        # Create a real SchemaInfo object
        schema = SchemaInfo(
            name="test_schema",
            full_name="catalog.test_schema",
            catalog_name="catalog",
            comment="Test schema",
            properties={},
            created_by="test_user",
            updated_by="test_user",
            owner="test_user",
        )
        return [schema]


class DummyWorkspaceClient:
    def __init__(self):
        self.tables = DummyTablesAPI()
        self.catalogs = DummyCatalogsAPI()
        self.schemas = DummySchemasAPI()


@pytest.fixture
def mock_workspace_client():
    with patch(
        "databricks.labs.mcp.servers.unity_catalog.tools.tables.WorkspaceClient"
    ) as mock_client:
        mock_client.return_value = DummyWorkspaceClient()
        yield mock_client


@pytest.fixture
def mock_settings():
    with patch(
        "databricks.labs.mcp.servers.unity_catalog.tools.tables.CliSettings"
    ) as mock_settings:
        mock_instance = Mock()
        mock_instance.get_catalog_name.return_value = "test_catalog"
        mock_instance.get_schema_name.return_value = "test_schema"
        mock_settings.return_value = mock_instance
        yield mock_settings


def test_list_tables_tool(mock_workspace_client, mock_settings):
    tool = ListTablesTool()
    result = tool.execute()

    assert len(result) == 1
    assert result[0].type == "text"
    data = result[0].text
    assert "test_table" in data
    assert "catalog" in data
    assert "schema" in data


def test_get_table_tool(mock_workspace_client):
    tool = GetTableTool()
    result = tool.execute(full_name="catalog.schema.test_table")

    assert len(result) == 1
    assert result[0].type == "text"
    data = result[0].text
    assert "catalog.schema.test_table" in data


def test_list_table_summaries_tool(mock_workspace_client, mock_settings):
    tool = ListTableSummariesTool()
    result = tool.execute()

    assert len(result) == 1
    assert result[0].type == "text"
    data = result[0].text
    assert "test_table" in data


def test_list_catalogs_tool(mock_workspace_client):
    tool = ListCatalogsTool()
    result = tool.execute()

    assert len(result) == 1
    assert result[0].type == "text"
    data = result[0].text
    assert "test_catalog" in data


def test_list_schemas_tool(mock_workspace_client, mock_settings):
    tool = ListSchemasTool()
    result = tool.execute()

    assert len(result) == 1
    assert result[0].type == "text"
    data = result[0].text
    assert "test_schema" in data


def test_list_table_tools():
    tools = list_table_tools(Mock())
    assert len(tools) == 5
    assert any(isinstance(tool, ListTablesTool) for tool in tools)
    assert any(isinstance(tool, GetTableTool) for tool in tools)
    assert any(isinstance(tool, ListTableSummariesTool) for tool in tools)
    assert any(isinstance(tool, ListCatalogsTool) for tool in tools)
    assert any(isinstance(tool, ListSchemasTool) for tool in tools)


def test_list_tables_tool_with_parameters(mock_workspace_client, mock_settings):
    tool = ListTablesTool()
    result = tool.execute(catalog_name="custom_catalog", schema_name="custom_schema")

    assert len(result) == 1
    assert result[0].type == "text"


def test_get_table_tool_missing_full_name(mock_workspace_client):
    tool = GetTableTool()
    with pytest.raises(ValueError):
        tool.execute()


def test_list_tables_tool_missing_catalog_schema(mock_workspace_client):
    with patch(
        "databricks.labs.mcp.servers.unity_catalog.tools.tables.CliSettings"
    ) as mock_settings:
        mock_instance = Mock()
        mock_instance.get_catalog_name.return_value = None
        mock_instance.get_schema_name.return_value = None
        mock_settings.return_value = mock_instance

        tool = ListTablesTool()
        with pytest.raises(ValueError):
            tool.execute()
