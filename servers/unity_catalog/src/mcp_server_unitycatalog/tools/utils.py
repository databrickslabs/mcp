import json
from contextlib import contextmanager
from importlib.util import spec_from_file_location, module_from_spec
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Any, Callable, Iterator, Optional, TypeVar, Union
from types import ModuleType
from pydantic import BaseModel
from pydantic.json import pydantic_encoder


def dump_json(maybe_model: Union[BaseModel, list, dict, None]) -> str:
    if maybe_model is None:
        return ""
    elif isinstance(maybe_model, list) or isinstance(maybe_model, dict):
        return json.dumps(maybe_model, default=pydantic_encoder, separators=(",", ":"))
    else:
        return maybe_model.model_dump_json(by_alias=True, exclude_unset=True)
