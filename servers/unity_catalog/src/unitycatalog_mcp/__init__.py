import sys
from traceback import format_exc
from unitycatalog_mcp.server import start


def main() -> None:
    import asyncio

    asyncio.run(start())


if __name__ == "__main__":
    try:
        main()
    except Exception as _:
        print(format_exc(), file=sys.stderr)
