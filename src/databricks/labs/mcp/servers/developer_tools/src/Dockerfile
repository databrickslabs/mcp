FROM python:3.10-slim

# Set the working directory in the container
WORKDIR /app

# Copy requirements first to leverage Docker cache
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt


# Copy the rest of the application code into the container at /app
COPY . .

# Make port 8000 available to the world outside this container
# (MCP servers typically run on port 8000 by default)
EXPOSE 8000

# Define environment variables (these will be overridden by docker run -e flags)
ENV DATABRICKS_HOST=""
ENV DATABRICKS_TOKEN=""
ENV DATABRICKS_HTTP_PATH=""

# Run main.py when the container launches
CMD ["python", "server.py"]