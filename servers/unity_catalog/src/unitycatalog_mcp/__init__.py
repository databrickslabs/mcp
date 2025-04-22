import sys
from traceback import format_exc
from unitycatalog_mcp.server import start
from databricks.sdk.config import with_user_agent_extra

def main() -> None:
    import asyncio
    with_user_agent_extra("unitycatalog-mcp")
    asyncio.run(start())


if __name__ == "__main__":
    try:
        main()
    except Exception as _:
        print(format_exc(), file=sys.stderr)
