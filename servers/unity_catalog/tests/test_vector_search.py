import pytest
from mcp_server_unitycatalog.tools.vector_search import (_list_vector_search_tools,
                                                         list_vector_search_tools,
                                                         VectorSearchTool)
from databricks_openai import VectorSearchRetrieverTool

# Dummy table object
class DummyTable:
    def __init__(self, full_name, properties):
        self.full_name = full_name
        self.properties = properties

# Dummy workspace client with tables.list
class DummyTablesAPI:
    def list(self, catalog_name=None, schema_name=None):
        # simulate two tables, one with endpoint and one without
        return [
            DummyTable(full_name="cat.sch.tbl1", properties={"model_endpoint_url": "url1"}),
            DummyTable(full_name="cat.sch.tbl2", properties={}),
        ]

class DummyWorkspaceClient:
    def __init__(self):
        self.tables = DummyTablesAPI()

class DummySettings:
    schema_full_name = "cat.sch"

@pytest.fixture(autouse=True)
def patch_workspace_and_tool(monkeypatch):
    # Patch the WorkspaceClient to return our dummy
    monkeypatch.setattr(
        'mcp_server_unitycatalog.tools.vector_search.WorkspaceClient',
        DummyWorkspaceClient
    )
    # Patch VectorSearchRetrieverTool to just record index_name
    monkeypatch.setattr(
        'mcp_server_unitycatalog.tools.vector_search.VectorSearchRetrieverTool',
        lambda index_name: type('T', (), {'tool': {'function': {'name': index_name, 'description': '', 'parameters': []}} , 'index_name': index_name})()
    )


def test_list_vector_search_tools_filters_and_returns_expected():
    settings = DummySettings()
    tools = list_vector_search_tools(settings)
    # Only one table has model_endpoint_url
    assert len(tools) == 1
    tool = tools[0]
    assert isinstance(tool, VectorSearchTool)
    # index_name should match the full_name of the dummy table
    assert tool.tool_obj.index_name == "cat.sch.tbl1"


def test_internal_list_vector_search_tools_direct():
    client = DummyWorkspaceClient()
    tools = _list_vector_search_tools(client, "cat", "sch")
    assert len(tools) == 1
    assert tools[0].tool_obj.index_name == "cat.sch.tbl1"
