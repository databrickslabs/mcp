import os
import random
import string
import pytest
from unitycatalog_mcp.cli import CliSettings, get_settings


def _random_alpha_num(length: int) -> str:
    """Generates a random alphanumeric string of the specified length.

    This function creates a string containing random letters (both uppercase and lowercase)
    and digits. The length of the generated string is determined by the input parameter.

    Args:
        length (int): The length of the random alphanumeric string to generate.

    Returns:
        str: A randomly generated alphanumeric string of the specified length.
    """
    return "".join(random.choices(string.ascii_letters + string.digits, k=length))


def _random_port() -> int:
    """Returns a random port number within the range of ephemeral ports.

    The selected port falls between 1024 and 65535, avoiding well-known reserved ports (0–1023).

    Returns:
        int: A randomly chosen port number.
    """
    return random.randint(1024, 65535)


@pytest.fixture
def server():
    """Fixture that generates a random URL with a random hostname, domain, and port.

    This fixture constructs a URL using:
    - A randomly generated hostname (10-character alphanumeric string).
    - A randomly generated top-level domain (3-character alphanumeric string).
    - A randomly selected port number.

    Returns:
        str: A randomly generated URL in the format "http://<hostname>.<tld>:<port>".
    """
    return f"http://{_random_alpha_num(10)}.{_random_alpha_num(3)}:{_random_port()}"


@pytest.fixture
def catalog():
    """Fixture that generates a random alphanumeric string to be used as a catalog name.

    This fixture calls the _random_alpha_num function to create a 10-character
    alphanumeric string that can be used as a mock catalog name in tests.

    Returns:
        str: A randomly generated catalog name.
    """
    return _random_alpha_num(10)


@pytest.fixture
def schema():
    """Fixture that generates a random alphanumeric string to be used as a schema name.

    This fixture calls the _random_alpha_num function to create a 10-character
    alphanumeric string that can be used as a mock schema name in tests.

    Returns:
        str: A randomly generated schema name.
    """
    return _random_alpha_num(10)


@pytest.fixture(autouse=True)
def setup_function():
    """Automatically clears the settings cache before each test.

    This fixture ensures that `get_settings()` does not retain cached
    values between tests, preventing state leakage and ensuring each
    test runs with fresh settings.

    This fixture runs automatically for all tests.

    Returns:
        None
    """
    CliSettings.model_config["env_file"] = ""
    get_settings.cache_clear()
