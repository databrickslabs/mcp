import random
import sys
import pytest
from pydantic import ValidationError
from unittest.mock import patch
from unitycatalog_mcp.cli import get_settings


def test_cache(server: str, catalog: str, schema: str) -> None:
    argv = [
        "mcp-server-unitycatalog",
        "--uc_server",
        server,
        "--uc_catalog",
        catalog,
        "--uc_schema",
        schema,
    ]
    with patch.object(sys, "argv", argv):
        lhs = get_settings()
        rhs = get_settings()
        assert lhs is rhs


def test_arguments(server: str, catalog: str, schema: str) -> None:
    argv = [
        "mcp-server-unitycatalog",
        "--uc_server",
        server,
        "--uc_catalog",
        catalog,
        "--uc_schema",
        schema,
    ]
    with patch.object(sys, "argv", argv):
        settings = get_settings()
        assert settings.uc_server == server
        assert settings.uc_catalog == catalog
        assert settings.uc_schema == schema


def test_required_arguments(server: str, catalog: str, schema: str) -> None:
    argv = random.choice(
        [
            ["mcp-server-unitycatalog", "--uc_catalog", catalog, "--uc_schema", schema],
            ["mcp-server-unitycatalog", "--uc_server", server, "--uc_schema", schema],
            ["mcp-server-unitycatalog", "--uc_server", server, "--uc_catalog", catalog],
        ]
    )
    with patch.object(sys, "argv", argv):
        with pytest.raises(ValidationError) as exc_info:
            settings = get_settings()
        assert "Field required" in str(exc_info.value)
