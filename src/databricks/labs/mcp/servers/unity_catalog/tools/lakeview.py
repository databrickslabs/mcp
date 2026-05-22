import json
import logging

from databricks.sdk import WorkspaceClient
from mcp.types import TextContent
from mcp.types import Tool as ToolSpec
from pydantic import BaseModel, Field

from databricks.labs.mcp.servers.unity_catalog.tools.base_tool import BaseTool

LOGGER = logging.getLogger(__name__)


# --- Input Schemas ---


class ListDashboardsInput(BaseModel):
    page_size: int = Field(
        default=25, description="Number of dashboards per page (1-100).", ge=1, le=100
    )
    page_token: str = Field(
        default="", description="Pagination token from a previous response."
    )


class GetDashboardInput(BaseModel):
    dashboard_id: str = Field(..., description="The ID of the dashboard to retrieve.")


class CreateDashboardInput(BaseModel):
    display_name: str = Field(..., description="Display name of the new dashboard.")
    warehouse_id: str = Field(
        default="",
        description="SQL warehouse ID for the dashboard. If empty, uses serverless compute.",
    )
    parent_path: str = Field(
        default="",
        description="Workspace path where the dashboard will be created (e.g. /Users/user@example.com).",
    )
    serialized_dashboard: str = Field(
        default="",
        description="JSON-encoded Lakeview dashboard definition. If empty, creates a blank dashboard.",
    )


class UpdateDashboardInput(BaseModel):
    dashboard_id: str = Field(..., description="The ID of the dashboard to update.")
    display_name: str = Field(
        default="", description="New display name. Leave empty to keep current."
    )
    warehouse_id: str = Field(
        default="",
        description="New SQL warehouse ID. Leave empty to keep current.",
    )
    serialized_dashboard: str = Field(
        default="",
        description="Updated JSON-encoded Lakeview dashboard definition. Leave empty to keep current.",
    )


class DeleteDashboardInput(BaseModel):
    dashboard_id: str = Field(
        ..., description="The ID of the dashboard to move to trash."
    )


class PublishDashboardInput(BaseModel):
    dashboard_id: str = Field(..., description="The ID of the dashboard to publish.")
    warehouse_id: str = Field(
        default="",
        description="SQL warehouse ID for the published dashboard. If empty, uses serverless compute.",
    )
    embed_credentials: bool = Field(
        default=True,
        description="Whether viewers can run queries using the publisher's credentials.",
    )


class UnpublishDashboardInput(BaseModel):
    dashboard_id: str = Field(..., description="The ID of the dashboard to unpublish.")


class GetPublishedDashboardInput(BaseModel):
    dashboard_id: str = Field(
        ..., description="The ID of the dashboard whose published version to retrieve."
    )


# --- Tool Implementations ---


def _list_dashboards(client: WorkspaceClient, args) -> list[TextContent]:
    model = ListDashboardsInput.model_validate(args)
    response = client.lakeview.list(
        page_size=model.page_size,
        page_token=model.page_token or None,
    )
    dashboards = []
    for d in response:
        dashboards.append(
            {
                "dashboard_id": d.dashboard_id,
                "display_name": d.display_name,
                "parent_path": d.parent_path,
                "lifecycle_state": (
                    d.lifecycle_state.value if d.lifecycle_state else None
                ),
                "create_time": str(d.create_time) if d.create_time else None,
                "update_time": str(d.update_time) if d.update_time else None,
            }
        )
        if len(dashboards) >= model.page_size:
            break
    return [
        TextContent(
            type="text", text=json.dumps(dashboards, default=str, separators=(",", ":"))
        )
    ]


def _get_dashboard(client: WorkspaceClient, args) -> list[TextContent]:
    model = GetDashboardInput.model_validate(args)
    dashboard = client.lakeview.get(model.dashboard_id)
    result = {
        "dashboard_id": dashboard.dashboard_id,
        "display_name": dashboard.display_name,
        "parent_path": dashboard.parent_path,
        "warehouse_id": dashboard.warehouse_id,
        "lifecycle_state": (
            dashboard.lifecycle_state.value if dashboard.lifecycle_state else None
        ),
        "serialized_dashboard": dashboard.serialized_dashboard,
        "create_time": str(dashboard.create_time) if dashboard.create_time else None,
        "update_time": str(dashboard.update_time) if dashboard.update_time else None,
    }
    return [
        TextContent(
            type="text", text=json.dumps(result, default=str, separators=(",", ":"))
        )
    ]


def _create_dashboard(client: WorkspaceClient, args) -> list[TextContent]:
    model = CreateDashboardInput.model_validate(args)
    kwargs = {"display_name": model.display_name}
    if model.warehouse_id:
        kwargs["warehouse_id"] = model.warehouse_id
    if model.parent_path:
        kwargs["parent_path"] = model.parent_path
    if model.serialized_dashboard:
        kwargs["serialized_dashboard"] = model.serialized_dashboard

    dashboard = client.lakeview.create(**kwargs)
    result = {
        "dashboard_id": dashboard.dashboard_id,
        "display_name": dashboard.display_name,
        "parent_path": dashboard.parent_path,
        "lifecycle_state": (
            dashboard.lifecycle_state.value if dashboard.lifecycle_state else None
        ),
    }
    return [
        TextContent(
            type="text", text=json.dumps(result, default=str, separators=(",", ":"))
        )
    ]


def _update_dashboard(client: WorkspaceClient, args) -> list[TextContent]:
    model = UpdateDashboardInput.model_validate(args)
    kwargs = {"dashboard_id": model.dashboard_id}
    if model.display_name:
        kwargs["display_name"] = model.display_name
    if model.warehouse_id:
        kwargs["warehouse_id"] = model.warehouse_id
    if model.serialized_dashboard:
        kwargs["serialized_dashboard"] = model.serialized_dashboard

    dashboard = client.lakeview.update(**kwargs)
    result = {
        "dashboard_id": dashboard.dashboard_id,
        "display_name": dashboard.display_name,
        "lifecycle_state": (
            dashboard.lifecycle_state.value if dashboard.lifecycle_state else None
        ),
        "update_time": str(dashboard.update_time) if dashboard.update_time else None,
    }
    return [
        TextContent(
            type="text", text=json.dumps(result, default=str, separators=(",", ":"))
        )
    ]


def _delete_dashboard(client: WorkspaceClient, args) -> list[TextContent]:
    model = DeleteDashboardInput.model_validate(args)
    client.lakeview.trash(model.dashboard_id)
    return [
        TextContent(
            type="text",
            text=json.dumps(
                {"dashboard_id": model.dashboard_id, "status": "trashed"},
                separators=(",", ":"),
            ),
        )
    ]


def _publish_dashboard(client: WorkspaceClient, args) -> list[TextContent]:
    model = PublishDashboardInput.model_validate(args)
    kwargs = {
        "dashboard_id": model.dashboard_id,
        "embed_credentials": model.embed_credentials,
    }
    if model.warehouse_id:
        kwargs["warehouse_id"] = model.warehouse_id

    published = client.lakeview.publish(**kwargs)
    result = {
        "dashboard_id": model.dashboard_id,
        "warehouse_id": published.warehouse_id if published.warehouse_id else None,
        "embed_credentials": (
            published.embed_credentials
            if hasattr(published, "embed_credentials")
            else None
        ),
        "revision_create_time": (
            str(published.revision_create_time)
            if published.revision_create_time
            else None
        ),
    }
    return [
        TextContent(
            type="text", text=json.dumps(result, default=str, separators=(",", ":"))
        )
    ]


def _unpublish_dashboard(client: WorkspaceClient, args) -> list[TextContent]:
    model = UnpublishDashboardInput.model_validate(args)
    client.lakeview.unpublish(model.dashboard_id)
    return [
        TextContent(
            type="text",
            text=json.dumps(
                {"dashboard_id": model.dashboard_id, "status": "unpublished"},
                separators=(",", ":"),
            ),
        )
    ]


def _get_published_dashboard(client: WorkspaceClient, args) -> list[TextContent]:
    model = GetPublishedDashboardInput.model_validate(args)
    published = client.lakeview.get_published(model.dashboard_id)
    result = {
        "dashboard_id": model.dashboard_id,
        "warehouse_id": published.warehouse_id if published.warehouse_id else None,
        "embed_credentials": (
            published.embed_credentials
            if hasattr(published, "embed_credentials")
            else None
        ),
        "revision_create_time": (
            str(published.revision_create_time)
            if published.revision_create_time
            else None
        ),
    }
    return [
        TextContent(
            type="text", text=json.dumps(result, default=str, separators=(",", ":"))
        )
    ]


# --- Tool Registry ---


class LakeviewTool(BaseTool):

    def __init__(self, name, description, input_schema, func):
        self.func = func
        tool_spec = ToolSpec(
            name=name,
            description=description,
            inputSchema=input_schema,
        )
        super().__init__(tool_spec)

    def execute(self, **kwargs):
        return self.func(client=WorkspaceClient(), args=kwargs)


def list_lakeview_tools(settings) -> list[LakeviewTool]:
    return [
        LakeviewTool(
            name="lakeview_list_dashboards",
            description="List AI/BI (Lakeview) dashboards in the workspace with pagination support.",
            input_schema=ListDashboardsInput.model_json_schema(),
            func=_list_dashboards,
        ),
        LakeviewTool(
            name="lakeview_get_dashboard",
            description="Get full metadata and serialized definition of an AI/BI dashboard.",
            input_schema=GetDashboardInput.model_json_schema(),
            func=_get_dashboard,
        ),
        LakeviewTool(
            name="lakeview_create_dashboard",
            description="Create a new AI/BI (Lakeview) dashboard in the workspace.",
            input_schema=CreateDashboardInput.model_json_schema(),
            func=_create_dashboard,
        ),
        LakeviewTool(
            name="lakeview_update_dashboard",
            description="Update an existing AI/BI dashboard's display name, warehouse, or definition.",
            input_schema=UpdateDashboardInput.model_json_schema(),
            func=_update_dashboard,
        ),
        LakeviewTool(
            name="lakeview_delete_dashboard",
            description="Move an AI/BI dashboard to trash. This is recoverable.",
            input_schema=DeleteDashboardInput.model_json_schema(),
            func=_delete_dashboard,
        ),
        LakeviewTool(
            name="lakeview_publish_dashboard",
            description="Publish an AI/BI dashboard, making it accessible via its published URL.",
            input_schema=PublishDashboardInput.model_json_schema(),
            func=_publish_dashboard,
        ),
        LakeviewTool(
            name="lakeview_unpublish_dashboard",
            description="Remove the published version of an AI/BI dashboard.",
            input_schema=UnpublishDashboardInput.model_json_schema(),
            func=_unpublish_dashboard,
        ),
        LakeviewTool(
            name="lakeview_get_published_dashboard",
            description="Get details of the published version of an AI/BI dashboard.",
            input_schema=GetPublishedDashboardInput.model_json_schema(),
            func=_get_published_dashboard,
        ),
    ]
