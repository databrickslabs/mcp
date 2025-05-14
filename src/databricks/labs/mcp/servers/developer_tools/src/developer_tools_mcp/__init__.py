import sys
from traceback import format_exc
from developer_tools_mcp.server import start
from developer_tools_mcp.version import VERSION

from databricks.sdk.config import with_user_agent_extra


def main() -> None:
    import asyncio

    with_user_agent_extra(key="developer-tools-mcp", value=VERSION)
    asyncio.run(start())


if __name__ == "__main__":
    try:
        main()
    except Exception as _:
        print(format_exc(), file=sys.stderr)