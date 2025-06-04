import os
import functools
import time
import json
import logging
from typing import Union
from pydantic import BaseModel, Field
from pydantic.json import pydantic_encoder

from databricks.sdk import WorkspaceClient
from databricks.sdk.service import jobs
from mcp.types import TextContent, Tool as ToolSpec

from developer_tools_mcp.tools.base_tool import BaseTool

# Logger
LOGGER = logging.getLogger(__name__)

# --- Input Schemas ---

class ListJobsInput(BaseModel):
    pass


class GetJobInput(BaseModel):
    job_id: int    
    
# --- Tool Implementations ---

def _list_jobs(client, args) -> list[TextContent]:
    model = ListJobsInput.model_validate(args)

    jobs = client.jobs.list()
    # iterator to json
    jobs_json = [job.as_dict() for job in jobs]
    return [
        TextContent(
            type="text",
            text=json.dumps(jobs_json),
        )
    ]

def _get_job(client, args) -> list[TextContent]:
    model = GetJobInput.model_validate(args)
    job = client.jobs.get(model.job_id)

    return [
        TextContent(
            type="text",
            text=json.dumps(job.as_dict()),
        )
    ]

# --- Tool Registry ---

class JobsTool(BaseTool):
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
    
def list_jobs_tool() -> list[JobsTool]:
    return [JobsTool(
        name="list_jobs",
        description="List all jobs in the workspace.",
        input_schema=ListJobsInput.model_json_schema(),
        func=_list_jobs,
    ),
    JobsTool(
        name="get_job",
        description="Get a job by ID.",
        input_schema=GetJobInput.model_json_schema(),
        func=_get_job,
    )]