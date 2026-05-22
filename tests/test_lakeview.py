import json
from unittest import mock

from databricks.labs.mcp.servers.unity_catalog.tools.lakeview import (
    LakeviewTool,
    _create_dashboard,
    _delete_dashboard,
    _get_dashboard,
    _get_published_dashboard,
    _list_dashboards,
    _publish_dashboard,
    _unpublish_dashboard,
    _update_dashboard,
    list_lakeview_tools,
)


class DummySettings:
    schema_full_name = "main.default"
    genie_space_ids = []


class DummyLifecycleState:
    value = "ACTIVE"


class DummyDashboard:
    def __init__(self, dashboard_id="d1", display_name="Test Dashboard"):
        self.dashboard_id = dashboard_id
        self.display_name = display_name
        self.parent_path = "/Users/test@example.com"
        self.warehouse_id = "wh-123"
        self.lifecycle_state = DummyLifecycleState()
        self.serialized_dashboard = '{"pages":[]}'
        self.create_time = "2024-01-01T00:00:00Z"
        self.update_time = "2024-01-02T00:00:00Z"


class DummyPublishedDashboard:
    def __init__(self):
        self.warehouse_id = "wh-123"
        self.embed_credentials = True
        self.revision_create_time = "2024-01-03T00:00:00Z"


class DummyLakeviewAPI:
    def list(self, page_size=None, page_token=None):
        return [
            DummyDashboard("d1", "Dashboard 1"),
            DummyDashboard("d2", "Dashboard 2"),
        ]

    def get(self, dashboard_id):
        return DummyDashboard(dashboard_id, "Retrieved Dashboard")

    def create(self, **kwargs):
        d = DummyDashboard("new-id", kwargs.get("display_name", "New"))
        return d

    def update(self, **kwargs):
        d = DummyDashboard(
            kwargs["dashboard_id"], kwargs.get("display_name", "Updated")
        )
        return d

    def trash(self, dashboard_id):
        return None

    def publish(self, **kwargs):
        return DummyPublishedDashboard()

    def unpublish(self, dashboard_id):
        return None

    def get_published(self, dashboard_id):
        return DummyPublishedDashboard()


class DummyWorkspaceClient:
    def __init__(self):
        self.lakeview = DummyLakeviewAPI()


# --- Tool Listing Tests ---


def test_list_lakeview_tools_count_and_types():
    tools = list_lakeview_tools(DummySettings())
    assert len(tools) == 8
    assert all(isinstance(t, LakeviewTool) for t in tools)


def test_list_lakeview_tools_names():
    tools = list_lakeview_tools(DummySettings())
    names = {t.tool_spec.name for t in tools}
    expected = {
        "lakeview_list_dashboards",
        "lakeview_get_dashboard",
        "lakeview_create_dashboard",
        "lakeview_update_dashboard",
        "lakeview_delete_dashboard",
        "lakeview_publish_dashboard",
        "lakeview_unpublish_dashboard",
        "lakeview_get_published_dashboard",
    }
    assert names == expected


def test_list_lakeview_tools_have_descriptions():
    tools = list_lakeview_tools(DummySettings())
    for tool in tools:
        assert tool.tool_spec.description
        assert len(tool.tool_spec.description) > 10


def test_list_lakeview_tools_have_input_schemas():
    tools = list_lakeview_tools(DummySettings())
    for tool in tools:
        assert tool.tool_spec.inputSchema is not None
        assert "properties" in tool.tool_spec.inputSchema


# --- Execution Tests ---


def test_list_dashboards():
    client = DummyWorkspaceClient()
    result = _list_dashboards(client, {})
    assert isinstance(result, list)
    data = json.loads(result[0].text)
    assert len(data) == 2
    assert data[0]["dashboard_id"] == "d1"
    assert data[1]["display_name"] == "Dashboard 2"


def test_list_dashboards_with_page_size():
    client = DummyWorkspaceClient()
    result = _list_dashboards(client, {"page_size": 1})
    data = json.loads(result[0].text)
    assert len(data) == 1


def test_get_dashboard():
    client = DummyWorkspaceClient()
    result = _get_dashboard(client, {"dashboard_id": "d1"})
    data = json.loads(result[0].text)
    assert data["dashboard_id"] == "d1"
    assert data["display_name"] == "Retrieved Dashboard"
    assert data["serialized_dashboard"] == '{"pages":[]}'
    assert data["warehouse_id"] == "wh-123"


def test_create_dashboard():
    client = DummyWorkspaceClient()
    result = _create_dashboard(client, {"display_name": "My New Dashboard"})
    data = json.loads(result[0].text)
    assert data["dashboard_id"] == "new-id"
    assert data["display_name"] == "My New Dashboard"


def test_create_dashboard_with_all_fields():
    client = DummyWorkspaceClient()
    result = _create_dashboard(
        client,
        {
            "display_name": "Full Dashboard",
            "warehouse_id": "wh-456",
            "parent_path": "/Users/test@example.com",
            "serialized_dashboard": '{"pages":[{"name":"p1"}]}',
        },
    )
    data = json.loads(result[0].text)
    assert data["dashboard_id"] == "new-id"


def test_update_dashboard():
    client = DummyWorkspaceClient()
    result = _update_dashboard(
        client, {"dashboard_id": "d1", "display_name": "Renamed"}
    )
    data = json.loads(result[0].text)
    assert data["dashboard_id"] == "d1"
    assert data["display_name"] == "Renamed"


def test_delete_dashboard():
    client = DummyWorkspaceClient()
    result = _delete_dashboard(client, {"dashboard_id": "d1"})
    data = json.loads(result[0].text)
    assert data["dashboard_id"] == "d1"
    assert data["status"] == "trashed"


def test_publish_dashboard():
    client = DummyWorkspaceClient()
    result = _publish_dashboard(
        client, {"dashboard_id": "d1", "embed_credentials": True}
    )
    data = json.loads(result[0].text)
    assert data["dashboard_id"] == "d1"
    assert data["warehouse_id"] == "wh-123"


def test_publish_dashboard_with_warehouse():
    client = DummyWorkspaceClient()
    result = _publish_dashboard(
        client,
        {
            "dashboard_id": "d1",
            "warehouse_id": "wh-override",
            "embed_credentials": False,
        },
    )
    data = json.loads(result[0].text)
    assert data["dashboard_id"] == "d1"


def test_unpublish_dashboard():
    client = DummyWorkspaceClient()
    result = _unpublish_dashboard(client, {"dashboard_id": "d1"})
    data = json.loads(result[0].text)
    assert data["dashboard_id"] == "d1"
    assert data["status"] == "unpublished"


def test_get_published_dashboard():
    client = DummyWorkspaceClient()
    result = _get_published_dashboard(client, {"dashboard_id": "d1"})
    data = json.loads(result[0].text)
    assert data["dashboard_id"] == "d1"
    assert data["warehouse_id"] == "wh-123"
    assert data["embed_credentials"] is True


# --- LakeviewTool.execute() integration ---


@mock.patch(
    "databricks.labs.mcp.servers.unity_catalog.tools.lakeview.WorkspaceClient",
    new=DummyWorkspaceClient,
)
def test_lakeview_tool_execute_list():
    tools = list_lakeview_tools(DummySettings())
    list_tool = next(t for t in tools if t.tool_spec.name == "lakeview_list_dashboards")
    result = list_tool.execute()
    assert isinstance(result, list)
    data = json.loads(result[0].text)
    assert len(data) == 2


@mock.patch(
    "databricks.labs.mcp.servers.unity_catalog.tools.lakeview.WorkspaceClient",
    new=DummyWorkspaceClient,
)
def test_lakeview_tool_execute_get():
    tools = list_lakeview_tools(DummySettings())
    get_tool = next(t for t in tools if t.tool_spec.name == "lakeview_get_dashboard")
    result = get_tool.execute(dashboard_id="abc-123")
    data = json.loads(result[0].text)
    assert data["dashboard_id"] == "abc-123"


@mock.patch(
    "databricks.labs.mcp.servers.unity_catalog.tools.lakeview.WorkspaceClient",
    new=DummyWorkspaceClient,
)
def test_lakeview_tool_execute_delete():
    tools = list_lakeview_tools(DummySettings())
    del_tool = next(t for t in tools if t.tool_spec.name == "lakeview_delete_dashboard")
    result = del_tool.execute(dashboard_id="abc-123")
    data = json.loads(result[0].text)
    assert data["status"] == "trashed"
