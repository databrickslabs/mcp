import os
import json
import logging
import requests
from typing import Union, Dict
from pydantic import BaseModel

from databricks.sdk import WorkspaceClient
from databricks.sql import connect
from mcp.types import TextContent, Tool as ToolSpec

from developer_tools_mcp.tools.base_tool import BaseTool

# Logger
LOGGER = logging.getLogger(__name__)

# --- Input Schemas ---

class TestConnectionInput(BaseModel):
    pass

# --- Tool Implementations ---

def _test_connection(client, args) -> list[TextContent]:
    model = TestConnectionInput.model_validate(args)
    
    results = {
        "databricks_api": False,
        "sql_warehouse": False,
        "host": os.getenv("DATABRICKS_HOST", "Not set"),
        "token": os.getenv("DATABRICKS_TOKEN", "Not set"),
        "http_path": os.getenv("DATABRICKS_HTTP_PATH", "Not set"),
        "details": {}
    }
    
    # Test 1: Databricks API
    try:
        # Test Databricks API access
        me = client.current_user.me()
        results["databricks_api"] = True
        results["details"]["current_user"] = me.user_name
        results["details"]["user_info"] = me.as_dict()
    except Exception as e:
        LOGGER.error(f"Error connecting to Databricks API: {e}")
        results["details"]["api_error"] = str(e)
    
    # Test 2: Databricks SQL Warehouse
    if "Not set" not in [results["host"], results["token"], results["http_path"]]:
        try:
            # Connect to SQL warehouse and execute a simple query
            sql_connection = connect(
                server_hostname=os.getenv("DATABRICKS_HOST"),
                http_path=os.getenv("DATABRICKS_HTTP_PATH"),
                access_token=os.getenv("DATABRICKS_TOKEN"),
                _socket_timeout=10 #TODO: This is not actually timing out the connection
            )
            cursor = sql_connection.cursor()
            cursor.execute("SELECT 1 AS test_value")
            result = cursor.fetchall()
            cursor.close()
            sql_connection.close()
            
            results["sql_warehouse"] = True
            results["details"]["sql_test_query"] = "Successfully executed test query: SELECT 1"
            results["details"]["sql_result"] = str(result)
            
            
        except Exception as e:
            LOGGER.error(f"Error connecting to Databricks SQL Warehouse: {e}")
            results["details"]["sql_error"] = str(e)
    
    # Summarize overall status
    if results["databricks_api"]:
        if results.get("sql_warehouse", False):
            results["status"] = "Success"
            results["message"] = "All connections successful"
        else:
            results["status"] = "Partial Success"
            results["message"] = "API connected, but SQL Warehouse connection failed"
    else:
        results["status"] = "Failed"
        results["message"] = "Unable to connect to Databricks"
    
    return [
        TextContent(
            type="text",
            text=json.dumps(results),
        )
    ]

# --- Tool Registry ---

class TestConnectionTool(BaseTool):
    def __init__(self, name, description, input_schema, func):
        self.func = func
        tool_spec = ToolSpec(
            name=name,
            description=description,
            inputSchema=input_schema,
        )
        super().__init__(tool_spec)

    def execute(self, **kwargs):
        return self.func(client=WorkspaceClient(
            host=os.getenv("DATABRICKS_HOST"),
            token=os.getenv("DATABRICKS_TOKEN")
        ), args=kwargs)
    
def test_connection_tool() -> list[TestConnectionTool]:
    return [TestConnectionTool(
        name="test_connection",
        description="Tests Databricks connections (API and SQL Warehouse).",
        input_schema=TestConnectionInput.model_json_schema(),
        func=_test_connection,
    )] 