import sys
from unittest.mock import patch

import pytest
from pydantic import ValidationError

from databricks.labs.mcp.servers.unity_catalog.cli import get_settings


@pytest.mark.parametrize(
    "catalog,schema",
    [
        ("main", "default"),
        ("dev", "analytics"),
        ("prod", "public"),
    ],
)
def test_cache(catalog: str, schema: str) -> None:
    argv = ["unitycatalog-mcp", "-s", f"{catalog}.{schema}"]
    with patch.object(sys, "argv", argv):
        lhs = get_settings()
        rhs = get_settings()
        assert lhs is rhs


@pytest.mark.parametrize(
    "catalog,schema",
    [
        ("main", "default"),
        ("dev", "analytics"),
        ("prod", "public"),
    ],
)
def test_arguments(catalog: str, schema: str) -> None:
    argv = ["unitycatalog-mcp", "-s", f"{catalog}.{schema}"]
    with patch.object(sys, "argv", argv):
        settings = get_settings()
        assert settings.get_catalog_name() == catalog
        assert settings.get_schema_name() == schema


def test_required_arguments_invalid_schema() -> None:
    argv = ["unitycatalog-mcp", "-s", "schema_no_catalog"]
    with patch.object(sys, "argv", argv):
        with pytest.raises(ValidationError) as exc_info:
            get_settings()
        errors = exc_info.value.errors()
        assert len(errors) > 0
        assert any(
            err["type"] in ("missing", "string_type", "value_error") for err in errors
        )


def test_required_arguments_all_disabled() -> None:
    from databricks.labs.mcp.servers.unity_catalog.cli import CliSettings

    with pytest.raises(ValidationError):
        CliSettings(
            schema_full_name=None,
            genie_space_ids=[],
            enable_lakeview=False,
            _env_file=None,
            _cli_parse_args=False,
        )


def test_lakeview_enabled_by_default() -> None:
    argv = ["unitycatalog-mcp"]
    with patch.object(sys, "argv", argv):
        settings = get_settings()
        assert settings.enable_lakeview is True


@pytest.mark.parametrize(
    "argv,expected_catalog,expected_schema,expected_genie_space_ids",
    [
        (
            ["unitycatalog-mcp", "-g", "spaceid1,spaceid2"],
            None,
            None,
            ["spaceid1", "spaceid2"],
        ),
        (["unitycatalog-mcp", "-g", "spaceid1"], None, None, ["spaceid1"]),
        (
            ["unitycatalog-mcp", "-g", "spaceid1,spaceid2", "-s", "catalog.schema"],
            "catalog",
            "schema",
            ["spaceid1", "spaceid2"],
        ),
        (["unitycatalog-mcp", "-s", "catalog.schema"], "catalog", "schema", []),
    ],
)
def test_valid_combinations(
    argv, expected_catalog, expected_schema, expected_genie_space_ids
) -> None:
    with patch.object(sys, "argv", argv):
        settings = get_settings()
        assert settings.get_catalog_name() == expected_catalog
        assert settings.get_schema_name() == expected_schema
        assert settings.genie_space_ids == expected_genie_space_ids
