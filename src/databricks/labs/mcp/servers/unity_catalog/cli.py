from typing import List, Optional
from pydantic import field_validator
from functools import lru_cache
from pydantic import (
    Field,
    AliasChoices,
    model_validator,
)
from pydantic_settings import BaseSettings, SettingsConfigDict


class CliSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        cli_parse_args=True,
        cli_ignore_unknown_args=True,
        extra="ignore",
    )

    schema_full_name: Optional[str] = Field(
        default=None,
        description="The name of the schema within a Unity Catalog "
        "catalog. Schemas organize assets, providing a structured "
        "namespace for data objects.",
        validation_alias=AliasChoices("s", "schema_full_name", "schema_name"),
    )

    genie_space_ids: List[str] = Field(
        default_factory=list,
        description="Comma-separated list of Genie space IDs.",
        validation_alias=AliasChoices("g", "genie_space_ids"),
    )

    vector_search_num_results: int = Field(
        default=5,
        description="Number of results to return from vector search queries",
        validation_alias=AliasChoices("vn", "vector_search_num_results", "vector_num_results"),
    )

    def get_catalog_name(self):
        return self.schema_full_name.split(".")[0] if self.schema_full_name else None

    def get_schema_name(self):
        return self.schema_full_name.split(".")[1] if self.schema_full_name else None

    @field_validator("genie_space_ids", mode="before")
    @classmethod
    def split_genie_space_ids(cls, v):
        if isinstance(v, str):
            return [s.strip() for s in v.split(",") if s.strip()]
        return v

    @model_validator(mode="after")
    def check_schema_name_or_genie_space_ids(self):
        if not self.schema_full_name and not self.genie_space_ids:
            raise ValueError(
                "At least one of --schema (-s) or --genie-space-ids (-g) must be provided."
            )
        return self

    @field_validator("schema_full_name", mode="before")
    @classmethod
    def validate_schema_full_name(cls, v):
        if v is not None and len(v.split(".")) != 2:
            raise ValueError("schema_full_name must be in the format 'catalog.schema'")
        return v


@lru_cache
def get_settings():
    return CliSettings()
