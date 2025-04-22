import pytest
from unittest import mock
from mcp_server_unitycatalog.tools.vector_search import (_list_vector_search_tools,
                                                         list_vector_search_tools,
                                                         VectorSearchTool)

class DummyTable:
    def __init__(self, full_name, properties):
        self.full_name = full_name
        self.properties = properties

class DummyTablesAPI:
    def list(self, catalog_name=None, schema_name=None):
        return [
            DummyTable(full_name="cat.sch.tbl1", properties={"model_endpoint_url": "url1"}),
            DummyTable(full_name="cat.sch.tbl2", properties={}),
        ]

class DummyWorkspaceClient:
    def __init__(self):
        self.tables = DummyTablesAPI()

class DummySettings:
    schema_full_name = "cat.sch"

@mock.patch("mcp_server_unitycatalog.tools.vector_search.WorkspaceClient", new=DummyWorkspaceClient)
@mock.patch("mcp_server_unitycatalog.tools.vector_search.VectorSearchRetrieverTool")
def test_list_vector_search_tools_filters_and_returns_expected(MockVectorSearchRetrieverTool):
    MockVectorSearchRetrieverTool.side_effect = lambda index_name: mock.Mock(
        tool={"function": {"name": index_name, "description": "", "parameters": {}}},
        index_name=index_name
    )
    settings = DummySettings()
    tools = list_vector_search_tools(settings)
    assert len(tools) == 1
    tool = tools[0]
    assert isinstance(tool, VectorSearchTool)
    assert tool.tool_obj.index_name == "cat.sch.tbl1"


def test_internal_list_vector_search_tools_direct():
    with mock.patch("mcp_server_unitycatalog.tools.vector_search.VectorSearchRetrieverTool") as MockVectorSearchRetrieverTool:
        MockVectorSearchRetrieverTool.side_effect = lambda index_name: mock.Mock(
            tool={"function": {"name": index_name, "description": "", "parameters": {}}},
            index_name=index_name
        )
        client = DummyWorkspaceClient()
        tools = _list_vector_search_tools(client, "cat", "sch")
        assert len(tools) == 1
        assert tools[0].tool_obj.index_name == "cat.sch.tbl1"