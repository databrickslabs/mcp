from typing import List
from pydantic import field_validator
from functools import lru_cache
from pydantic import AliasChoices, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class CliSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        cli_parse_args=True,
    )
    schema_full_name: str = Field(
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

    def get_catalog_name(self):
        return self.schema_full_name.split(".")[0]

    def get_schema_name(self):
        return self.schema_full_name.split(".")[1]


    @field_validator("genie_space_ids", mode="before")
    @classmethod
    def split_genie_space_ids(cls, v):
        if isinstance(v, str):
            return [s.strip() for s in v.split(",") if s.strip()]
        return v


@lru_cache
def get_settings():
    return CliSettings()
