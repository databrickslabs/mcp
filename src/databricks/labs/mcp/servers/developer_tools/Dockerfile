FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim

# Set the working directory in the container
WORKDIR /app

# Copy package configuration and requirements
COPY ./pyproject.toml ./pyproject.toml
COPY ./uv.lock ./uv.lock
COPY ./README.md ./README.md

# Copy the package code
COPY ./src ./src

# Make port 8000 available to the world outside this container
# (MCP servers typically run on port 8000 by default)
EXPOSE 8000

# Define environment variables (these will be overridden by docker run -e flags)
ENV DATABRICKS_HOST=""
ENV DATABRICKS_TOKEN=""
ENV DATABRICKS_HTTP_PATH=""

# Run the module properly
CMD ["uv", "run", "developer-tools-mcp"]