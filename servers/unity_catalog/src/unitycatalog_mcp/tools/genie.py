import functools
import time
import json
import logging
from typing import Union
from pydantic import BaseModel, Field
from pydantic.json import pydantic_encoder

from databricks.sdk import WorkspaceClient
from mcp.types import TextContent, Tool as ToolSpec

from unitycatalog_mcp.tools.base_tool import BaseTool

# Logger
LOGGER = logging.getLogger(__name__)


def dump_json(maybe_model: Union[BaseModel, list, dict, None]) -> str:
    if maybe_model is None:
        return ""
    elif isinstance(maybe_model, list) or isinstance(maybe_model, dict):
        return json.dumps(maybe_model, default=pydantic_encoder, separators=(",", ":"))
    else:
        return maybe_model.model_dump_json(by_alias=True, exclude_unset=True)


# --- Input Schemas ---


class StartConversationInput(BaseModel):
    space_id: str = Field(..., description="The ID of the Genie space.")
    content: str = Field(..., description="The text to start the conversation.")


class CreateMessageInput(BaseModel):
    space_id: str
    conversation_id: str
    content: str


class GetMessageInput(BaseModel):
    space_id: str
    conversation_id: str
    message_id: str


class GetAttachmentQueryResultInput(BaseModel):
    space_id: str
    conversation_id: str
    message_id: str
    attachment_id: str


class ExecuteAttachmentQueryInput(GetAttachmentQueryResultInput):
    pass


class GetSpaceInput(BaseModel):
    space_id: str


class GenerateDownloadInput(GetAttachmentQueryResultInput):
    pass


class PollMessageUntilCompleteInput(BaseModel):
    space_id: str
    conversation_id: str
    message_id: str
    timeout_seconds: int = Field(default=600)
    poll_interval_seconds: int = Field(default=5)


class ListSpacesInput(BaseModel):
    pass


# --- Tool Implementations ---


def _start_conversation(client, args) -> list[TextContent]:
    model = StartConversationInput.model_validate(args)
    message = client.genie.start_conversation_and_wait(model.space_id, model.content)
    return [
        TextContent(
            type="text",
            text=dump_json(
                {
                    "conversation_id": message.conversation_id,
                    "message_id": message.message_id,
                    "content": message.content,
                    "status": message.status.value if message.status else None,
                    "attachments": getattr(message, "attachments", None),
                }
            ),
        )
    ]


def _create_message(client, args) -> list[TextContent]:
    model = CreateMessageInput.model_validate(args)
    message = client.genie.create_message_and_wait(
        model.space_id, model.conversation_id, model.content
    )
    return [
        TextContent(
            type="text",
            text=dump_json(
                {
                    "message_id": message.message_id,
                    "content": message.content,
                    "status": message.status.value if message.status else None,
                    "attachments": getattr(message, "attachments", None),
                    "conversation_id": message.conversation_id,
                }
            ),
        )
    ]


def _get_message(client, args) -> list[TextContent]:
    model = GetMessageInput.model_validate(args)
    message = client.genie.get_message(
        model.space_id, model.conversation_id, model.message_id
    )
    return [
        TextContent(
            type="text",
            text=dump_json(
                {
                    "message_id": message.message_id,
                    "content": message.content,
                    "status": message.status.value if message.status else None,
                    "conversation_id": message.conversation_id,
                    "space_id": model.space_id,
                    "attachments": getattr(message, "attachments", None),
                    "error": getattr(message, "error", None),
                }
            ),
        )
    ]


def _get_attachment_query_result(client, args) -> list[TextContent]:
    model = GetAttachmentQueryResultInput.model_validate(args)
    result = client.genie.get_message_attachment_query_result(
        model.space_id, model.conversation_id, model.message_id, model.attachment_id
    )
    return [
        TextContent(
            type="text",
            text=dump_json(
                result.statement_response.as_dict()
                if result.statement_response
                else {"error": "No statement response found."}
            ),
        )
    ]


def _execute_attachment_query(client, args) -> list[TextContent]:
    model = ExecuteAttachmentQueryInput.model_validate(args)
    result = client.genie.execute_message_attachment_query(
        model.space_id, model.conversation_id, model.message_id, model.attachment_id
    )
    return [
        TextContent(
            type="text",
            text=dump_json(
                result.statement_response.as_dict()
                if result.statement_response
                else {"error": "No statement response found."}
            ),
        )
    ]


def _get_space(client, args) -> list[TextContent]:
    model = GetSpaceInput.model_validate(args)
    space = client.genie.get_space(model.space_id)
    return [
        TextContent(
            type="text",
            text=dump_json(
                {
                    "space_id": model.space_id,
                    "title": space.title,
                    "description": getattr(space, "description", None),
                }
            ),
        )
    ]


def _generate_download_query_result(client, args) -> list[TextContent]:
    model = GenerateDownloadInput.model_validate(args)
    result = client.genie.generate_download_full_query_result(
        model.space_id, model.conversation_id, model.message_id, model.attachment_id
    )
    return [
        TextContent(
            type="text",
            text=dump_json(
                {
                    "transient_statement_id": result.transient_statement_id,
                    "status": result.status.value if result.status else None,
                }
            ),
        )
    ]


def _poll_message_until_complete(client, args) -> list[TextContent]:
    model = PollMessageUntilCompleteInput.model_validate(args)
    genie_api = client.genie
    start_time = time.time()
    elapsed = 0
    poll_count = 0

    while elapsed < model.timeout_seconds:
        message = genie_api.get_message(
            model.space_id, model.conversation_id, model.message_id
        )
        status = message.status.value if message.status else "UNKNOWN"
        poll_count += 1

        if status in ["COMPLETED", "FAILED", "QUERY_RESULT_EXPIRED", "CANCELLED"]:
            return [
                TextContent(
                    type="text",
                    text=dump_json(
                        {
                            "message_id": message.message_id,
                            "status": status,
                            "poll_count": poll_count,
                            "elapsed_time": elapsed,
                        }
                    ),
                )
            ]

        time.sleep(model.poll_interval_seconds)
        elapsed = time.time() - start_time

    return [
        TextContent(
            type="text",
            text=dump_json(
                {
                    "error": f"Timeout after {model.timeout_seconds} seconds",
                    "message_id": model.message_id,
                    "status": status,
                    "poll_count": poll_count,
                    "elapsed_time": elapsed,
                }
            ),
        )
    ]


def _list_spaces(client, args, space_ids) -> list[TextContent]:
    results = []
    for space_id in space_ids:
        try:
            space = client.genie.get_space(space_id)
            results.append(
                {
                    "space_id": space_id,
                    "title": space.title,
                    "description": getattr(space, "description", None),
                }
            )
        except Exception as e:
            results.append({"space_id": space_id, "error": str(e)})
    return [TextContent(type="text", text=dump_json(results))]


# --- Tool Registry ---


class GenieTool(BaseTool):

    def __init__(self, name, description, input_schema, func):
        self.func = func
        tool_spec = ToolSpec(
            name=name,
            description=description,
            inputSchema=input_schema,
        )
        super().__init__(tool_spec)

    def execute(self, **kwargs):
        # final_kwargs = {"client": WorkspaceClient()}
        # final_kwargs.update(kwargs)
        return self.func(client=WorkspaceClient(), args=kwargs)


def list_genie_tools(settings) -> list[GenieTool]:
    return [
        GenieTool(
            name="genie_start_conversation",
            description="Start a new conversation in a Genie space.",
            input_schema=StartConversationInput.model_json_schema(),
            func=_start_conversation,
        ),
        GenieTool(
            name="genie_create_message",
            description="Create a message in a conversation.",
            input_schema=CreateMessageInput.model_json_schema(),
            func=_create_message,
        ),
        GenieTool(
            name="genie_get_message",
            description="Get a message from a conversation.",
            input_schema=GetMessageInput.model_json_schema(),
            func=_get_message,
        ),
        GenieTool(
            name="genie_get_query_result",
            description="Get SQL query result from a message attachment.",
            input_schema=GetAttachmentQueryResultInput.model_json_schema(),
            func=_get_attachment_query_result,
        ),
        GenieTool(
            name="genie_execute_query",
            description="Execute SQL query from a message attachment.",
            input_schema=ExecuteAttachmentQueryInput.model_json_schema(),
            func=_execute_attachment_query,
        ),
        GenieTool(
            name="genie_get_space",
            description="Get details of a Genie space.",
            input_schema=GetSpaceInput.model_json_schema(),
            func=_get_space,
        ),
        GenieTool(
            name="genie_generate_download",
            description="Generate download link for full query result.",
            input_schema=GenerateDownloadInput.model_json_schema(),
            func=_generate_download_query_result,
        ),
        GenieTool(
            name="genie_poll_until_complete",
            description="Poll a message until its status is COMPLETED or timeout.",
            input_schema=PollMessageUntilCompleteInput.model_json_schema(),
            func=_poll_message_until_complete,
        ),
        GenieTool(
            name="genie_list_spaces",
            description=(
                "List available Genie spaces. Genie spaces enable structured data lookup "
                "via a text-to-SQL interface. NOTE: Consider proactively calling this tool for "
                "any knowledge or data retrieval question, especially including but not limited to questions "
                "about enterprise data, because it will help you discover available "
                "Genie spaces that you can subsequently chat with for insights. If the user asks a question that could be "
                "answered by a structure data (database table) lookup or query against tabular data, "
                "consider calling this tool to "
                "discover available Genie spaces and see if it makes sense to chat with "
                "any of them to help answer the question."
            ),
            input_schema=ListSpacesInput.model_json_schema(),
            func=functools.partial(_list_spaces, space_ids=settings.genie_space_ids),
        ),
    ]
