"""
Configuration file for robot_scanner module.
Set your database preferences here.
"""
from pathlib import Path

# Database Configuration
# Options: "sqlite", "postgresql", "mysql", "mongodb", "json"
DATABASE_TYPE = "sqlite"

# SQLite Configuration (default - no setup required)
SQLITE_DB_PATH = str(Path(__file__).parent / "test_results.db")

# PostgreSQL Configuration
POSTGRESQL_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "database": "test_scanner",
    "user": "postgres",
    "password": ""
}

# MySQL Configuration
MYSQL_CONFIG = {
    "host": "localhost",
    "port": 3306,
    "database": "test_scanner",
    "user": "root",
    "password": ""
}

# MongoDB Configuration
MONGODB_CONFIG = {
    "connection_string": "mongodb://localhost:27017/",
    "database": "test_scanner",
    "collection": "test_results"
}

# JSON File Configuration
JSON_FILE_PATH = str(Path(__file__).parent / "test_results.json")

