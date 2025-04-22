import logging
import sys
from traceback import format_exc
from mcp_server_unitycatalog.cli import get_settings as Cli
from mcp_server_unitycatalog.logging_config import configure_logging
from mcp_server_unitycatalog.server import start


def main() -> None:
    import asyncio
    configure_logging()
    asyncio.run(start())


if __name__ == "__main__":
    try:
        main()
    except Exception as _:
        print(format_exc(), file=sys.stderr)
