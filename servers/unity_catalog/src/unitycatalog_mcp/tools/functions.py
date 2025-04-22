import logging

from mcp.types import Tool as ToolSpec, TextContent
from unitycatalog_mcp.tools.base_tool import BaseTool
from unitycatalog.ai.core.databricks import DatabricksFunctionClient
from databricks_openai import UCFunctionToolkit

LOGGER = logging.getLogger(__name__)


class UCFunctionTool(BaseTool):
    def __init__(self, tool_obj, client: DatabricksFunctionClient, uc_function_name):
        self.tool_obj = tool_obj
        self.client = client
        self.uc_function_name = uc_function_name
        tool_info = tool_obj["function"]
        llm_friendly_tool_name = tool_info["name"]
        tool_spec = ToolSpec(
            name=llm_friendly_tool_name,
            description=tool_info["description"],
            inputSchema=tool_info["parameters"],
        )
        super().__init__(tool_spec=tool_spec)

    def execute(self, **kwargs) -> list[TextContent]:
        res = self.client.execute_function(
            function_name=self.uc_function_name, parameters=kwargs
        )
        return [
            TextContent(
                type="text",
                text=res.value or res.error,
            )
        ]


def _list_uc_function_tools(
    client: DatabricksFunctionClient,
    catalog_name: str,
    schema_name: str,
) -> list[UCFunctionTool]:
    toolkit = UCFunctionToolkit(
        client=client, function_names=[f"{catalog_name}.{schema_name}.*"]
    )
    return [
        UCFunctionTool(tool_obj, client, name)
        for name, tool_obj in toolkit.tools_dict.items()
    ]


def list_uc_function_tools(settings) -> list[UCFunctionTool]:
    catalog_name, schema_name = settings.schema_full_name.split(".")
    client = DatabricksFunctionClient()
    return _list_uc_function_tools(client, catalog_name, schema_name)
