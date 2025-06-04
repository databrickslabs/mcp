import os
import json
import logging
from typing import Union
from pydantic import BaseModel, Field
from pydantic.json import pydantic_encoder

from databricks.sql import connect
from mcp.types import TextContent, Tool as ToolSpec

from developer_tools_mcp.tools.base_tool import BaseTool

# Logger
LOGGER = logging.getLogger(__name__)

# --- Input Schemas ---

class SqlQueryInput(BaseModel):
    query: str = Field(..., description="The SQL query to execute")


# --- Tool Implementations ---

def _run_sql_query(client, args) -> list[TextContent]:
    model = SqlQueryInput.model_validate(args)
    
    try:
        # Connect to SQL warehouse
        if not all([os.getenv("DATABRICKS_HOST"), os.getenv("DATABRICKS_TOKEN"), os.getenv("DATABRICKS_HTTP_PATH")]):
            raise ValueError("Missing required Databricks connection details in environment variables")
        
        sql_connection = connect(
            server_hostname=os.getenv("DATABRICKS_HOST"),
            http_path=os.getenv("DATABRICKS_HTTP_PATH"),
            access_token=os.getenv("DATABRICKS_TOKEN")
        )
        
        cursor = sql_connection.cursor()
        result = cursor.execute(model.query)
        
        if result.description:
            columns = [col[0] for col in result.description]
            rows = result.fetchall()
            
            if not rows:
                cursor.close()
                sql_connection.close()
                return [
                    TextContent(
                        type="text",
                        text="Query executed successfully. No results returned."
                    )
                ]
            
            # Format as markdown table
            table = "| " + " | ".join(columns) + " |\n"
            table += "| " + " | ".join(["---" for _ in columns]) + " |\n"
            for row in rows:
                table += "| " + " | ".join([str(cell) for cell in row]) + " |\n"
            
            cursor.close()
            sql_connection.close()
            
            return [
                TextContent(
                    type="text",
                    text=table
                )
            ]
        else:
            cursor.close()
            sql_connection.close()
            return [
                TextContent(
                    type="text",
                    text="Query executed successfully. No results returned."
                )
            ]
            
    except Exception as e:
        LOGGER.error(f"Error executing SQL query: {e}")
        return [
            TextContent(
                type="text",
                text=f"Error executing SQL query: {str(e)}"
            )
        ]


# --- Tool Registry ---

class SqlQueryTool(BaseTool):
    def __init__(self, name, description, input_schema, func):
        self.func = func
        tool_spec = ToolSpec(
            name=name,
            description=description,
            inputSchema=input_schema,
        )
        super().__init__(tool_spec)

    def execute(self, **kwargs):
        return self.func(client=None, args=kwargs)
    
def sql_query_tool() -> list[SqlQueryTool]:
    return [SqlQueryTool(
        name="run_sql_query",
        description="Execute SQL queries on Databricks SQL warehouse and return results as a markdown table.",
        input_schema=SqlQueryInput.model_json_schema(),
        func=_run_sql_query,
    )]
