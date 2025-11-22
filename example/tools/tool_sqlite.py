import sqlite3
from smolagents import Tool

class SQLiteTool(Tool):
    """
    A tool that executes SQL queries on a specified SQLite database.
    """
    name = "sqlite_tool"
    description = "Execute SQL queries on a specified SQLite database."
    inputs = {
        "db_path": {
            "type": "string",
            "description": "Path to the SQLite database file."
        },
        "sql": {
            "type": "string",
            "description": "The SQL query to be executed."
        }
    }
    output_type = "string"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def forward(self, db_path: str, sql: str) -> str:
        """
        Connects to the SQLite database at 'db_path', executes the provided 'sql' query,
        and returns the query result as a formatted string.
        """
        try:
            with sqlite3.connect(db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(sql)
                # Fetch rows (if any)
                rows = cursor.fetchall()
                # If the query returns rows (e.g., SELECT), format them:
                if cursor.description:
                    columns = [desc[0] for desc in cursor.description]
                    output_lines = []
                    # Header row with column names
                    output_lines.append(" | ".join(columns))
                    # Rows of data
                    for row in rows:
                        output_lines.append(" | ".join(str(value) for value in row))
                    return "\n".join(output_lines) if rows else "Query executed, but no rows returned."
                else:
                    # If cursor.description is None, it might be an UPDATE or INSERT
                    return f"Query executed successfully; {cursor.rowcount} row(s) affected."
        except Exception as e:
            return f"Error executing query: {e}"
