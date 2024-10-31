import sqlite3
from contextlib import closing


# Establish connection to the SQLite database
def get_connection():
    return sqlite3.connect("projects.db")


# Initialize database and create projects table if it doesn't exist
def initialize_db():
    with closing(get_connection()) as conn:
        with conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS projects (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    project_id TEXT UNIQUE NOT NULL
                )
                """
            )


# Check if a project exists in the database by project_id
def project_exists(project_id):
    with closing(get_connection()) as conn:
        cursor = conn.execute(
            "SELECT 1 FROM projects WHERE project_id = ?", (project_id,)
        )
        return cursor.fetchone() is not None


# Add a new project to the database
def add_project(
    project_id,
):
    with closing(get_connection()) as conn:
        with conn:
            conn.execute("INSERT INTO projects (project_id) VALUES (?)", (project_id,))
