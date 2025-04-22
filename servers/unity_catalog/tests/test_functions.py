import pytest
from mcp_server_unitycatalog.tools.functions import list_uc_function_tools, _list_uc_function_tools, UCFunctionTool

# Dummy toolkit to replace UCFunctionToolkit
class DummyToolkit:
    def __init__(self, client, function_names):
        # record that client and names are passed
        self.client = client
        self.function_names = function_names
        # simulate two functions
        self.tools_dict = {
            "func1": {"function": {"name": "func1", "description": "desc1", "parameters": {}}},
            "func2": {"function": {"name": "func2", "description": "desc2", "parameters": {}}},
        }

# Dummy client stub
class DummyClient:
    pass

class DummySettings:
    schema_full_name = "catalog.schema"

@pytest.fixture(autouse=True)
def patch_dependencies(monkeypatch):
    # Patch UCFunctionToolkit and DatabricksFunctionClient
    monkeypatch.setattr(
        'mcp_server_unitycatalog.tools.functions.UCFunctionToolkit',
        DummyToolkit
    )
    monkeypatch.setattr(
        'mcp_server_unitycatalog.tools.functions.DatabricksFunctionClient',
        lambda: DummyClient()
    )


def test_list_uc_function_tools_calls_internal():
    settings = DummySettings()
    tools = list_uc_function_tools(settings)
    # Should return list of UCFunctionTool instances
    assert len(tools) == 2
    assert all(isinstance(t, UCFunctionTool) for t in tools)
    names = {t.uc_function_name for t in tools}
    assert names == {"func1", "func2"}


def test_internal_list_tool_client_and_names():
    dummy_client = DummyClient()
    tools = _list_uc_function_tools(dummy_client, "catalog", "schema")
    # Confirm that DummyToolkit was used
    assert len(tools) == 2
    for tool in tools:
        assert tool.client is dummy_client
        assert tool.uc_function_name in ("func1", "func2")
