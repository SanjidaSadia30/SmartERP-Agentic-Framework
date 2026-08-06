import os
import sqlite3
import pandas as pd

# main database path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "database", "erp_data.db")


def run_query(query: str, params: tuple = ()):
    """
    Executes a SQL query and returns a DataFrame for SELECT queries,
    or commits changes for INSERT, UPDATE, DELETE queries.
    """
    conn = sqlite3.connect(DB_PATH)
    try:
        # if Select Query then return  DataFrame
        if query.strip().upper().startswith("SELECT"):
            df = pd.read_sql_query(query, conn, params=params)
            return df
        # if any changes INSERT, UPDATE, DELETE Query then  Save
        else:
            cursor = conn.cursor()
            cursor.execute(query, params)
            conn.commit()
            return None
    finally:
        conn.close()


def get_db_schema() -> str:
    """
    database main table and column name  retrive for AI Agent
    """
    conn = sqlite3.connect(DB_PATH)
    try:
        cursor = conn.cursor()
        # sqlite_sequence internal table bad diye main table  searching
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name != 'sqlite_sequence';"
        )
        tables = cursor.fetchall()

        schema_info = ""
        for table in tables:
            table_name = table[0]
            cursor.execute(f"PRAGMA table_info({table_name});")
            columns = cursor.fetchall()
            col_names = [col[1] for col in columns]
            schema_info += f"Table: {table_name}\nColumns: {', '.join(col_names)}\n\n"

        return schema_info
    finally:
        conn.close()
