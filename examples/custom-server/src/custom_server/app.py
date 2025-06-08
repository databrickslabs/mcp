from pathlib import Path
from mcp.server.fastmcp import FastMCP
from fastapi import FastAPI
from fastapi.responses import FileResponse

STATIC_DIR = Path(__file__).parent / "static"

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


app = FastAPI(
    lifespan=lambda _: mcp.session_manager.run(),
)


@app.get("/", include_in_schema=False)
async def serve_index():
    return FileResponse(STATIC_DIR / "index.html")


app.mount("/", mcp_app)
