#!/usr/bin/env python
"""
Databricks Connection Test Script
This script tests the connection to Databricks using credentials from the .env file.
It attempts to connect to both the SQL warehouse and the Databricks API.
"""

import os
from dotenv import load_dotenv
import sys

# Load environment variables
load_dotenv()

# Get Databricks credentials from environment variables
DATABRICKS_HOST = os.getenv("DATABRICKS_HOST")
DATABRICKS_TOKEN = os.getenv("DATABRICKS_TOKEN")
DATABRICKS_HTTP_PATH = os.getenv("DATABRICKS_HTTP_PATH")

def check_env_vars():
    """Check if all required environment variables are set"""
    missing = []
    if not DATABRICKS_HOST:
        missing.append("DATABRICKS_HOST")
    if not DATABRICKS_TOKEN:
        missing.append("DATABRICKS_TOKEN")
    if not DATABRICKS_HTTP_PATH:
        missing.append("DATABRICKS_HTTP_PATH")
    
    if missing:
        print("❌ Missing required environment variables:")
        for var in missing:
            print(f"  - {var}")
        print("\nPlease check your .env file and make sure all required variables are set.")
        return False
    
    print("✅ All required environment variables are set")
    return True

def test_databricks_api():
    """Test connection to Databricks API"""
    import requests
    
    print("\nTesting Databricks API connection...")
    
    try:
        headers = {
            "Authorization": f"Bearer {DATABRICKS_TOKEN}",
            "Content-Type": "application/json"
        }
        
        url = f"https://{DATABRICKS_HOST}/api/2.0/clusters/list-node-types"
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            print("✅ Successfully connected to Databricks API")
            return True
        else:
            print(f"❌ Failed to connect to Databricks API: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error connecting to Databricks API: {str(e)}")
        return False

def test_sql_connection():
    """Test connection to Databricks SQL warehouse"""
    print("\nTesting Databricks SQL warehouse connection...")
    
    try:
        from databricks.sql import connect
        
        conn = connect(
            server_hostname=DATABRICKS_HOST,
            http_path=DATABRICKS_HTTP_PATH,
            access_token=DATABRICKS_TOKEN
        )
        
        cursor = conn.cursor()
        cursor.execute("SELECT 1 AS test")
        result = cursor.fetchall()
        
        if result and result[0][0] == 1:
            print("✅ Successfully connected to Databricks SQL warehouse")
            conn.close()
            return True
        else:
            print("❌ Failed to get expected result from SQL warehouse")
            conn.close()
            return False
    except Exception as e:
        print(f"❌ Error connecting to Databricks SQL warehouse: {str(e)}")
        return False

if __name__ == "__main__":
    print("Databricks Connection Test")
    print("=========================\n")
    
    # Check for dependencies
    try:
        import requests
        from databricks.sql import connect
    except ImportError as e:
        print(f"❌ Missing dependency: {str(e)}")
        print("Please run: pip install -r requirements.txt")
        sys.exit(1)
    
    # Run tests
    env_ok = check_env_vars()
    
    if not env_ok:
        sys.exit(1)
    
    api_ok = test_databricks_api()
    sql_ok = test_sql_connection()
    
    # Summary
    print("\nTest Summary")
    print("===========")
    print(f"Environment Variables: {'✅ OK' if env_ok else '❌ Failed'}")
    print(f"Databricks API: {'✅ OK' if api_ok else '❌ Failed'}")
    print(f"Databricks SQL: {'✅ OK' if sql_ok else '❌ Failed'}")
    
    if env_ok and api_ok and sql_ok:
        print("\n✅ All tests passed! Your Databricks MCP server should work correctly.")
        sys.exit(0)
    else:
        print("\n❌ Some tests failed. Please check the errors above and fix your configuration.")
        sys.exit(1) 