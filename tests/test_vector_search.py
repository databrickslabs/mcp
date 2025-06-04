from unittest import mock
from databricks.labs.mcp.servers.unity_catalog.tools.vector_search import (
    _list_vector_search_tools,
    list_vector_search_tools,
    VectorSearchTool,
)


class DummyTable:
    def __init__(self, full_name, properties):
        self.full_name = full_name
        self.name = full_name.split(".")[-1]
        self.properties = properties


class DummyTablesAPI:
    def list(self, catalog_name=None, schema_name=None):
        return [
            DummyTable(
                full_name="cat.sch.tbl1", properties={"model_endpoint_url": "url1"}
            ),
            DummyTable(full_name="cat.sch.tbl2", properties={}),
        ]

    def get(self, full_table_name):
        # Mock get_table_columns behavior
        class DummyColumn:
            def __init__(self, name):
                self.name = name

        class DummyTableInfo:
            columns = [DummyColumn("col1"), DummyColumn("col2"), DummyColumn("__db_content_vector")]

        return DummyTableInfo()


class DummyWorkspaceClient:
    def __init__(self):
        self.tables = DummyTablesAPI()


class DummySettings:
    schema_full_name = "cat.sch"


@mock.patch(
    "databricks.labs.mcp.servers.unity_catalog.tools.vector_search.WorkspaceClient",
    new=DummyWorkspaceClient,
)
def test_list_vector_search_tools_filters_and_returns_expected():
    settings = DummySettings()
    tools = list_vector_search_tools(settings)
    assert len(tools) == 1
    tool = tools[0]
    assert isinstance(tool, VectorSearchTool)
    assert tool.index_name == "cat.sch.tbl1"
    assert tool.columns == ["col1", "col2"]  # filtered out "__db_content_vector"


def test_internal_list_vector_search_tools_direct():
    client = DummyWorkspaceClient()
    tools = _list_vector_search_tools(client, "cat", "sch")
    assert len(tools) == 1
    assert isinstance(tools[0], VectorSearchTool)
    assert tools[0].index_name == "cat.sch.tbl1"
    assert tools[0].columns == ["col1", "col2"]


@mock.patch("databricks.labs.mcp.servers.unity_catalog.tools.vector_search.VectorSearchClient")
def test_vector_search_tool_execute(MockVectorSearchClient):
    mock_index = mock.Mock()
    mock_index.similarity_search.return_value = {
        "result": {"data_array": [{"id": 1, "score": 0.9}]}
    }

    # Make get_index return our mock_index
    MockVectorSearchClient.return_value.get_index.return_value = mock_index

    tool = VectorSearchTool(
        endpoint_name="endpoint1",
        index_name="cat.sch.tbl1",
        tool_name="vector_search_test",
        columns=["col1", "col2"],
    )

    result = tool.execute(query="test query")

    assert isinstance(result, list)
    assert result[0].text.strip().startswith("[")  # It should be JSON string
    assert "score" in result[0].text