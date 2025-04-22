from unittest import mock
from unitycatalog_mcp.tools.functions import list_uc_function_tools, UCFunctionTool

SCHEMA_FULL_NAME = "catalog.schema"


class DummyToolkit:
    def __init__(self, client, function_names):
        self.client = client
        self.function_names = function_names
        if function_names != [f"{SCHEMA_FULL_NAME}.*"]:
            raise ValueError(f"Expected function names to be ['{SCHEMA_FULL_NAME}.*']")
        self.tools_dict = {
            "catalog.schema.func1": {
                "function": {
                    "name": "catalog__schema__func1",
                    "description": "desc1",
                    "parameters": {},
                }
            },
            "catalog.schema.func2": {
                "function": {
                    "name": "catalog__schema__func2",
                    "description": "desc2",
                    "parameters": {},
                }
            },
        }


class DummyClient:
    pass


class DummySettings:
    schema_full_name = SCHEMA_FULL_NAME


@mock.patch(
    "unitycatalog_mcp.tools.functions.DatabricksFunctionClient", new=DummyClient
)
@mock.patch("unitycatalog_mcp.tools.functions.UCFunctionToolkit", new=DummyToolkit)
def test_list_uc_function_tools():
    settings = DummySettings()
    tools = list_uc_function_tools(settings)
    assert len(tools) == 2
    assert all(isinstance(t, UCFunctionTool) for t in tools)
    orig_uc_names = {t.uc_function_name for t in tools}
    assert orig_uc_names == {"catalog.schema.func1", "catalog.schema.func2"}
