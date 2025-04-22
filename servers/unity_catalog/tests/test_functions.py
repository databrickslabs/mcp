from unittest import mock

import pytest
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
    def execute_function(self, function_name, parameters):
        class Result:
            def __init__(self, value, error):
                self.value = value
                self.error = error

        if "required_parameter" not in parameters:
            return Result(
                value=None, error="Missing required parameter 'required_parameter'"
            )
        return Result(
            value=f"executed {function_name} with parameters {parameters}", error=None
        )


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


def test_uc_function_tool_execute():
    dummy_client = DummyClient()
    dummy_func = {"function": {"name": "foo", "description": "bar", "parameters": {}}}
    tool = UCFunctionTool(dummy_func, dummy_client, "foo")
    output = tool.execute(required_parameter=1)
    assert output[0].text == "executed foo with parameters {'required_parameter': 1}"
    with pytest.raises(Exception) as excinfo:
        tool.execute(x=3)
    assert "Missing required parameter 'required_parameter'" in str(excinfo.value)
