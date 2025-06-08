from pathlib import Path
from fastapi.staticfiles import StaticFiles
from mcp.server.fastmcp import FastMCP
from fastapi import FastAPI

# Create an MCP server
mcp = FastMCP("Custom MCP Server on Databricks Apps")


# Add an addition tool
@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two numbers"""
    return a + b


# Add a dynamic greeting resource
@mcp.resource("greeting://{name}")
def get_greeting(name: str) -> str:
    """Get a personalized greeting"""
    return f"Hello, {name}!"


mcp_app = mcp.streamable_http_app()
static = StaticFiles(directory=Path(__file__).parent / "static", html=True)


app = FastAPI(
    lifespan=lambda _: mcp.session_manager.run(),
)

# note the order of mounting here,
# and don't change it unless you know what you're doing
app.mount("/", mcp_app)
app.mount("/", static)
