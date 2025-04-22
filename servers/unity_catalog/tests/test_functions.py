import pytest
from unittest import mock
from mcp_server_unitycatalog.tools.functions import list_uc_function_tools, _list_uc_function_tools, UCFunctionTool

# Dummy toolkit to replace UCFunctionToolkit
class DummyToolkit:
    def __init__(self, client, function_names):
        self.client = client
        self.function_names = function_names
        self.tools_dict = {
            "func1": {"function": {"name": "func1", "description": "desc1", "parameters": {}}},
            "func2": {"function": {"name": "func2", "description": "desc2", "parameters": {}}},
        }

class DummyClient:
    pass

class DummySettings:
    schema_full_name = "catalog.schema"

@mock.patch("mcp_server_unitycatalog.tools.functions.DatabricksFunctionClient", new_callable=lambda: DummyClient)
@mock.patch("mcp_server_unitycatalog.tools.functions.UCFunctionToolkit", new=DummyToolkit)
def test_list_uc_function_tools_calls_internal(mock_toolkit, mock_client):
    settings = DummySettings()
    tools = list_uc_function_tools(settings)
    assert len(tools) == 2
    assert all(isinstance(t, UCFunctionTool) for t in tools)
    names = {t.uc_function_name for t in tools}
    assert names == {"func1", "func2"}


def test_internal_list_tool_client_and_names():
    dummy_client = DummyClient()
    tools = _list_uc_function_tools(dummy_client, "catalog", "schema")
    assert len(tools) == 2
    for tool in tools:
        assert tool.client is dummy_client
        assert tool.uc_function_name in ("func1", "func2")
