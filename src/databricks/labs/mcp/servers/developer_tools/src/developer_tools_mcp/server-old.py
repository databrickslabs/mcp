import os
from typing import Dict
from dotenv import load_dotenv
from databricks.sql import connect, exc as db_exc # Import Databricks SQL exceptions
from databricks.sql.client import Connection
from mcp.server.fastmcp import FastMCP
import requests
from requests import exceptions as req_exc # Import requests exceptions
import logging
import functools # Import functools for wraps

# Load environment variables
load_dotenv()

# Get Databricks credentials from environment variables
DATABRICKS_HOST = os.getenv("DATABRICKS_HOST")
DATABRICKS_TOKEN = os.getenv("DATABRICKS_TOKEN")
DATABRICKS_HTTP_PATH = os.getenv("DATABRICKS_HTTP_PATH")

# Set up the MCP server
mcp = FastMCP("Databricks API Explorer")

# Global variable to hold the Databricks SQL connection
_db_connection: Connection | None = None

# Error handling decorator for MCP tools
def log_tool_errors(func):
    """Decorator to handle common exceptions for MCP tools, log them, and return standardized error messages."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        tool_name = func.__name__
        try:
            # Execute the original tool function
            return func(*args, **kwargs)
        except ValueError as e:
            # Configuration/Input errors (raised by helpers or tool validation)
            logging.error(f"Configuration/Input Error in {tool_name}: {e}", exc_info=False)
            return f"Configuration/Input Error: {str(e)}"
        except db_exc.Error as db_error:
            # Databricks SQL specific errors
            logging.error(f"Databricks SQL Error in {tool_name}: {db_error}", exc_info=True)
            return f"Database Error: {str(db_error)}"
        except req_exc.HTTPError as http_err:
             # HTTP errors from API requests
            status_code = http_err.response.status_code
            reason = http_err.response.reason
            # Note: Specific status code handling (like 404) should be done within the tool function
            # if a custom message is needed, before this general handler catches it.
            logging.error(f"API Request Failed in {tool_name}: {status_code} {reason} - Response: {http_err.response.text}", exc_info=False)
            return f"API Request Failed: {status_code} {reason}"
        except req_exc.RequestException as req_err:
            # Other requests errors (connection, timeout, etc.)
            logging.error(f"API Connection/Request Error in {tool_name}: {req_err}", exc_info=True)
            return f"API Connection/Request Error: {str(req_err)}"
        except (KeyError, TypeError, AttributeError, IndexError) as data_err: # Added IndexError for safety
            # Errors processing data (e.g., API responses)
            logging.error(f"Error processing data in {tool_name}: {data_err}", exc_info=True)
            return f"Error processing data: {str(data_err)}"
        except Exception as e:
            # Catch-all for unexpected errors
            logging.error(f"Unexpected Error in {tool_name}: {e}", exc_info=True)
            return f"An unexpected error occurred: {str(e)}"
    return wrapper

# Helper function to get a reusable Databricks SQL connection
def get_databricks_connection() -> Connection:
    """Create and return a reusable Databricks SQL connection."""
    global _db_connection
    
    # Check if connection exists and is open
    if _db_connection is not None:
        try:
            # TODO: Easier way to check if the connection is still valid?
            cursor = _db_connection.cursor()
            cursor.execute("SELECT 1")
            cursor.close()
            logging.info("Reusing existing Databricks SQL connection.")
            return _db_connection
        except db_exc.Error as db_error:
            logging.warning(f"Existing connection seems invalid (DB Error: {db_error}), creating a new one.")
            try:
                if _db_connection: 
                    _db_connection.close()
            except db_exc.Error:
                pass 
            except Exception as close_exc:
                 logging.error(f"Unexpected error closing potentially broken DB connection: {close_exc}")
            _db_connection = None 
        except Exception as e: 
            logging.warning(f"Unexpected error checking connection liveness ({e}), creating a new one.")
            _db_connection = None

    if not all([DATABRICKS_HOST, DATABRICKS_TOKEN, DATABRICKS_HTTP_PATH]):
        # This case is critical configuration error, raising is appropriate
        raise ValueError("Missing required Databricks connection details in .env file")

    try:
        logging.info("Creating new Databricks SQL connection.")
        _db_connection = connect(
            server_hostname=DATABRICKS_HOST,
            http_path=DATABRICKS_HTTP_PATH,
            access_token=DATABRICKS_TOKEN
        )
        return _db_connection
    except db_exc.Error as db_connect_error: 
        logging.error(f"Failed to connect to Databricks SQL Warehouse: {db_connect_error}")
        raise 
    except Exception as connect_exc:
        logging.error(f"Unexpected error creating Databricks SQL connection: {connect_exc}")
        raise 

# Helper function for Databricks REST API requests
def databricks_api_request(endpoint: str, method: str = "GET", data: Dict = None) -> Dict:
    """Make a request to the Databricks REST API, handling common errors."""
    if not all([DATABRICKS_HOST, DATABRICKS_TOKEN]):
        # This case is critical configuration error, raising is appropriate
        raise ValueError("Missing required Databricks API credentials in .env file")
    
    headers = {
        "Authorization": f"Bearer {DATABRICKS_TOKEN}",
        "Content-Type": "application/json"
    }
    
    url = f"https://{DATABRICKS_HOST}/api/2.0/{endpoint}"
    
    try:
        if method.upper() == "GET":
            response = requests.get(url, headers=headers)
        elif method.upper() == "POST":
            response = requests.post(url, headers=headers, json=data)
        else:
            # Internal programming error
            raise ValueError(f"Unsupported HTTP method: {method}")
        
        response.raise_for_status() # Raise HTTPError for bad responses (4xx or 5xx)
        return response.json()
    
    except req_exc.HTTPError as http_err:
        logging.error(f"HTTP error occurred: {http_err} - Response: {http_err.response.text}")
        raise
    except req_exc.ConnectionError as conn_err:
        logging.error(f"Connection error occurred: {conn_err}")
        raise
    except req_exc.Timeout as timeout_err:
        logging.error(f"Request timed out: {timeout_err}")
        raise
    except req_exc.RequestException as req_err:
        logging.error(f"An error occurred during the API request: {req_err}")
        raise
    except ValueError as val_err:
        logging.error(f"API Request internal error: {val_err}")
        raise

@mcp.resource("schema://tables")
@log_tool_errors
def get_schema() -> str:
    """Provide the list of tables in the Databricks SQL warehouse as a resource"""
    # The decorator will handle exceptions
    conn = get_databricks_connection() # Use the shared connection
    cursor = conn.cursor()
    tables = cursor.tables().fetchall()
    
    table_info = []
    for table in tables:
        table_info.append(f"Database: {table.TABLE_CAT}, Schema: {table.TABLE_SCHEM}, Table: {table.TABLE_NAME}")
    
    cursor.close()
    return "\n".join(table_info)

@mcp.tool()
@log_tool_errors
def run_sql_query(sql: str) -> str:
    """Execute SQL queries on Databricks SQL warehouse"""
    # The decorator will handle exceptions
    conn = get_databricks_connection() # Use the shared connection
    cursor = conn.cursor()
    result = cursor.execute(sql)
    
    if result.description:
        columns = [col[0] for col in result.description]
        rows = result.fetchall()
        cursor.close()
        
        if not rows:
            return "Query executed successfully. No results returned."
        
        # Format as markdown table
        # Keep internal try/except for formatting issues, but let others bubble up
        try:
            table = "| " + " | ".join(columns) + " |\n"
            table += "| " + " | ".join(["---" for _ in columns]) + " |\n"
            for row in rows:
                table += "| " + " | ".join([str(cell) for cell in row]) + " |\n"
            return table
        except Exception as format_exc:
             logging.error(f"Error formatting SQL results: {format_exc}", exc_info=True)
             # Return a specific error for formatting, not the generic one from the decorator
             return f"Error formatting results: {str(format_exc)}"
    else:
        cursor.close()
        return "Query executed successfully. No results returned."

@mcp.tool()
@log_tool_errors
def list_jobs() -> str:
    """List all Databricks jobs"""
    # The decorator will handle exceptions
    response = databricks_api_request("jobs/list")
    
    if not isinstance(response, dict):
         logging.error(f"Unexpected API response type for list_jobs: {type(response)}")
         # Raise an error for the decorator to catch with a standard message
         raise TypeError("Received unexpected API response format.")

    jobs = response.get("jobs")
    if jobs is None:
        if "error_code" in response:
             logging.error(f"API error in list_jobs response: {response}")
             # Let the decorator handle this as likely an API/Request error or data error
             # depending on what databricks_api_request raised or if it succeeded but gave error payload
             raise ValueError(f"API Error: {response.get('message', 'Unknown error')}")
        else:
             return "No jobs found."
    if not isinstance(jobs, list):
         logging.error(f"Unexpected 'jobs' format in list_jobs response: {type(jobs)}")
         raise TypeError("Received unexpected API response format for jobs list.")

    # Format as markdown table
    table_rows = ["| Job ID | Job Name | Created By |", "| ------ | -------- | ---------- |"]
    for job in jobs:
        if not isinstance(job, dict):
             logging.warning(f"Skipping invalid job item in list_jobs: {job}")
             continue
        job_id = job.get("job_id", "N/A")
        job_name = job.get("settings", {}).get("name", "N/A") 
        creator = job.get("creator_user_name", "N/A") 
        
        table_rows.append(f"| {job_id} | {job_name} | {creator} |")
    
    return "\n".join(table_rows)

@mcp.tool()
@log_tool_errors
def get_job_status(job_id: int) -> str:
    """Get the status of a specific Databricks job"""
    # The decorator will handle general exceptions
    
    # Add basic input validation (can raise ValueError handled by decorator)
    if not isinstance(job_id, int) or job_id <= 0:
        raise ValueError("Invalid Job ID provided.")
        
    response = databricks_api_request("jobs/runs/list", data={"job_id": job_id})
    
    # Error handling for unexpected API response structure (raise for decorator)
    if not isinstance(response, dict):
         logging.error(f"Unexpected API response type for get_job_status: {type(response)}")
         raise TypeError("Received unexpected API response format.")
         
    runs = response.get("runs")
    if runs is None:
         if "error_code" in response:
             logging.error(f"API error in get_job_status response: {response}")
             raise ValueError(f"API Error: {response.get('message', 'Unknown error')}")
         else:
            return f"No runs found for job ID {job_id}."
    if not isinstance(runs, list):
         logging.error(f"Unexpected 'runs' format in get_job_status response: {type(runs)}")
         raise TypeError("Received unexpected API response format for runs list.")

    if not runs: # Check if list is empty after verifying it's a list
        return f"No runs found for job ID {job_id}."
        
    # Format as markdown table
    import datetime # Import moved inside for scope
    table_rows = ["| Run ID | State | Start Time | End Time | Duration |", "| ------ | ----- | ---------- | -------- | -------- |"]
    
    for run in runs:
        if not isinstance(run, dict):
            logging.warning(f"Skipping invalid run item in get_job_status: {run}")
            continue
        
        run_id = run.get("run_id", "N/A")
        # Safer access to nested state
        state_info = run.get("state", {})
        state = state_info.get("life_cycle_state", "N/A") # life_cycle_state is often more useful
        result_state = state_info.get("result_state")
        if result_state:
            state += f" ({result_state})"
        
        start_time = run.get("start_time")
        end_time = run.get("end_time")
        duration_ms = run.get("execution_duration") # Use execution_duration if available

        duration = "N/A"
        if duration_ms is not None and duration_ms > 0:
            duration = f"{duration_ms / 1000:.2f}s"
        elif start_time and end_time:
            # Fallback calculation if execution_duration missing
             duration = f"{(end_time - start_time) / 1000:.2f}s"

        start_time_str = datetime.datetime.fromtimestamp(start_time / 1000).strftime('%Y-%m-%d %H:%M:%S') if start_time else "N/A"
        end_time_str = datetime.datetime.fromtimestamp(end_time / 1000).strftime('%Y-%m-%d %H:%M:%S') if end_time else "N/A"
        
        table_rows.append(f"| {run_id} | {state} | {start_time_str} | {end_time_str} | {duration} |")
    
    return "\n".join(table_rows)

@mcp.tool()
@log_tool_errors
def get_job_details(job_id: int) -> str:
    """Get detailed information about a specific Databricks job"""
    # Decorator handles most exceptions
    
    # Basic input validation (raises ValueError handled by decorator)
    if not isinstance(job_id, int) or job_id <= 0:
        raise ValueError("Invalid Job ID provided.")
        
    try:
        response = databricks_api_request(f"jobs/get?job_id={job_id}", method="GET")
    except req_exc.HTTPError as http_err:
         # Specifically check for 404 for job not found before decorator
         if http_err.response.status_code == 404:
              logging.warning(f"Job ID {job_id} not found (404) in get_job_details.") # Log warning
              return f"Error: Job ID {job_id} not found." # Return specific message
         else:
              raise # Re-raise other HTTP errors for the decorator to handle

    # Error handling for unexpected API response structure (raise for decorator)
    if not isinstance(response, dict):
         logging.error(f"Unexpected API response type for get_job_details: {type(response)}")
         raise TypeError("Received unexpected API response format.")

    # Safer access using .get()
    settings = response.get("settings", {})
    job_name = settings.get("name", "N/A")
    created_time = response.get("created_time")
    creator_user_name = response.get('creator_user_name', 'N/A')
    tasks = settings.get("tasks", [])
    
    # Convert timestamp to readable format
    import datetime # Import moved inside for scope
    created_time_str = datetime.datetime.fromtimestamp(created_time / 1000).strftime('%Y-%m-%d %H:%M:%S') if created_time else "N/A"
    
    result_lines = [f"## Job Details: {job_name}\n"]
    result_lines.append(f"- **Job ID:** {job_id}")
    result_lines.append(f"- **Created:** {created_time_str}")
    result_lines.append(f"- **Creator:** {creator_user_name}\n")
    
    if isinstance(tasks, list) and tasks: # Check tasks is a non-empty list
        result_lines.append("### Tasks:\n")
        result_lines.append("| Task Key | Task Type | Description |")
        result_lines.append("| -------- | --------- | ----------- |")
        
        for task in tasks:
            if not isinstance(task, dict):
                logging.warning(f"Skipping invalid task item in get_job_details: {task}")
                continue
                
            task_key = task.get("task_key", "N/A")
            # Simplified task type extraction (assuming one _task key)
            task_type = next((k.replace('_task', '') for k in task if k.endswith('_task')), "N/A")
            description = task.get("description", "N/A")
            
            result_lines.append(f"| {task_key} | {task_type} | {description} |")
    else:
        result_lines.append("No tasks defined for this job.")
    
    return "\n".join(result_lines)

@mcp.tool()
@log_tool_errors # Apply decorator for fallback error handling
def test_databricks_connections() -> str:
    """Tests connections to Databricks API and SQL Warehouse using configured credentials."""
    results = []
    env_ok = True
    api_ok = False
    sql_ok = False

    # 1. Check Environment Variables (implicitly by trying to use helpers)
    results.append("### Environment Variable Check")
    try:
        # Check if critical vars are present (databricks_api_request checks HOST/TOKEN)
        if not all([DATABRICKS_HOST, DATABRICKS_TOKEN]):
             raise ValueError("DATABRICKS_HOST or DATABRICKS_TOKEN missing")
        # Check if SQL vars are present (get_databricks_connection checks all three)
        if not DATABRICKS_HTTP_PATH:
            raise ValueError("DATABRICKS_HTTP_PATH missing")
        # Attempt to get connection which checks all three SQL vars
        results.append("✅ Required environment variables seem configured.")
        
    except ValueError as e:
        results.append(f"❌ Failed: {str(e)}")
        env_ok = False
    except Exception as e: # Catch other potential issues during connection check
        results.append(f"❌ Unexpected error checking environment/connection init: {str(e)}")
        env_ok = False

    # 2. Test Databricks API Connection (only if env vars seem okay)
    results.append("\n### Databricks API Test")
    if env_ok:
        try:
            # Use a simple, common API endpoint
            databricks_api_request("clusters/list-node-types") 
            results.append("✅ Successfully connected to Databricks API.")
            api_ok = True
        except req_exc.HTTPError as http_err:
            results.append(f"❌ API Connection Failed: {http_err.response.status_code} {http_err.response.reason}")
        except req_exc.RequestException as req_err:
            results.append(f"❌ API Connection Error: {str(req_err)}")
        except ValueError as e: # From databricks_api_request internal checks
             results.append(f"❌ API Configuration Error: {str(e)}")
        # Let decorator handle other unexpected errors
    else:
        results.append("⚪ Skipped (due to environment variable issues).")

    # 3. Test Databricks SQL Warehouse Connection (only if env vars seem okay)
    results.append("\n### Databricks SQL Warehouse Test")
    if env_ok:
        try:
            conn = get_databricks_connection() # Re-establish connection
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            result = cursor.fetchall()
            cursor.close()
            # Do not close conn here, let get_databricks_connection manage it
            if result and result[0][0] == 1:
                results.append("✅ Successfully connected and queried SQL warehouse.")
                sql_ok = True
            else:
                results.append("❌ Connected to SQL warehouse, but test query failed.")
        except db_exc.Error as db_error:
            results.append(f"❌ SQL Connection/Query Failed: {str(db_error)}")
        except ValueError as e: # From get_databricks_connection internal checks
             results.append(f"❌ SQL Configuration Error: {str(e)}")
        # Let decorator handle other unexpected errors
    else:
        results.append("⚪ Skipped (due to environment variable issues).")

    # 4. Summary
    results.append("\n### Summary")
    results.append(f"- Environment Variables: {'✅ OK' if env_ok else '❌ Failed'}")
    results.append(f"- Databricks API: {'✅ OK' if api_ok else ('❌ Failed' if env_ok else '⚪ Skipped')}")
    results.append(f"- Databricks SQL: {'✅ OK' if sql_ok else ('❌ Failed' if env_ok else '⚪ Skipped')}")

    if env_ok and api_ok and sql_ok:
        results.append("\n✅ All connection tests passed!")
    else:
        results.append("\n❌ One or more connection tests failed.")

    return "\n".join(results) + DATABRICKS_HOST
    

if __name__ == "__main__":
    test_databricks_connections()
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    mcp.run()
