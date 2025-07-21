from mcp.types import Tool as ToolSpec

# Define a new abstract class for a tool
from abc import ABC, abstractmethod


class BaseTool(ABC):
    def __init__(self, tool_spec: ToolSpec):
        self.tool_spec = tool_spec

    @abstractmethod
    def execute(self, **kwargs):
        pass