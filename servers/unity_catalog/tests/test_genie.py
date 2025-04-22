from pydantic import BaseModel
from unitycatalog_mcp.tools.genie import list_genie_tools, GenieTool, dump_json
from unittest import mock


class DummySettings:
    # settings.genie_space_ids not used by list_genie_tools
    genie_space_ids = ["s1", "s2"]


def test_list_genie_tools_names_and_types():
    tools = list_genie_tools(DummySettings())
    assert len(tools) >= 5  # expecting several GenieTool instances
    # Each should be a GenieTool
    assert all(isinstance(t, GenieTool) for t in tools)
    # Check that expected tool names are present
    names = {t.tool_spec.name for t in tools}
    expected = {
        "genie_start_conversation",
        "genie_create_message",
        "genie_get_message",
        "genie_generate_download",
        "genie_poll_until_complete",
        "genie_list_spaces",
    }
    assert expected.issubset(names)


class DummyModel(BaseModel):
    a: int
    b: str


def test_dump_json_none():
    assert dump_json(None) == ""


def test_dump_json_dict():
    data = {"x": 1, "y": "test"}
    result = dump_json(data)
    assert result == '{"x":1,"y":"test"}'


def test_dump_json_list():
    data = [1, 2, 3]
    result = dump_json(data)
    assert result == "[1,2,3]"


def test_dump_json_model():
    model = DummyModel(a=5, b="hello")
    result = dump_json(model)
    # ensure JSON string contains the fields
    assert '"a":5' in result
    assert '"b":"hello"' in result


class DummyWorkspaceClient:
    pass


@mock.patch("unitycatalog_mcp.tools.genie.WorkspaceClient", new=DummyWorkspaceClient)
def test_genie_tool_execute():
    mock_func = mock.Mock()
    mock_func.return_value = [mock.Mock(text="hello world")]
    tool = GenieTool("foo", "desc", {"type": "object", "properties": {}}, mock_func)
    result = tool.execute()
    assert isinstance(result, list)
    assert result[0].text == "hello world"
