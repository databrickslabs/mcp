import sys
import pytest
from pydantic import ValidationError
from unittest.mock import patch
from unitycatalog_mcp.cli import get_settings


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


@pytest.mark.parametrize(
    "argv",
    [
        ["unitycatalog-mcp"],  # neither -s nor -g
        ["unitycatalog-mcp", "-s", "schema_no_catalog"],
    ],
)
def test_required_arguments(argv) -> None:
    with patch.object(sys, "argv", argv):
        with pytest.raises(ValidationError) as exc_info:
            get_settings()
        errors = exc_info.value.errors()
        assert len(errors) > 0
        assert any(
            err["type"] in ("missing", "string_type", "value_error") for err in errors
        )


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
