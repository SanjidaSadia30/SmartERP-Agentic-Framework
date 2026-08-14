import os
import sys
import re
import pandas as pd
from dotenv import load_dotenv
from groq import Groq

# Root path attatch
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from utils.db_helper import run_query, get_db_schema

load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")


class ERPAgent:
    def __init__(self):
        # Groq Client initial
        self.client = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None

    def ask_agent(self, user_query: str):
        """Processes user natural language query, generates SQL, and returns result."""
        schema_info = get_db_schema()

        # Prompt instruction (Strict Output Format)
        prompt = f"""
        You are an intelligent ERP AI Assistant for an enterprise system.
        Based on the database schema below, write ONLY a valid SQL query to answer the user request.
        
        {schema_info}
        
        User Query: {user_query}
        
        Return ONLY the raw SQL query inside SQL code block like ```sql ... ```. Do not add any extra text, intro, or explanation.
        """

        # Fallback handler (If API Key is missing)
        if not self.client:
            sql_query = (
                "SELECT * FROM sales"
                if "sale" in user_query.lower()
                else "SELECT * FROM inventory"
            )
            df_result = run_query(sql_query)
            return {
                "sql": sql_query,
                "data": df_result,
                "summary": "Mock Mode (No API key found): Generated default query response.",
            }

        try:
            # Query Groq Llama model for SQL generation
            response = self.client.chat.completions.create(
                
                model="llama-3.1-70b-versatile",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
            )

            raw_content = response.choices[0].message.content.strip()

            # Robust SQL extraction (Regex matching or string cleanup)
            match = re.search(r"```sql\s*(.*?)\s*```", raw_content, re.DOTALL)
            if match:
                sql_query = match.group(1).strip()
            else:
                # Code block না থাকলেও ব্যাকটিক মুছে ক্লিন SQL নেওয়া
                sql_query = raw_content.replace("```", "").strip()

            # Execute query using db_helper
            df_result = run_query(sql_query)

            record_count = len(df_result) if isinstance(df_result, pd.DataFrame) else 0
            summary = (
                f"Query executed successfully. Retrieved {record_count} record(s)."
            )

            return {"sql": sql_query, "data": df_result, "summary": summary}

        except Exception as e:
            return {
                "sql": "N/A",
                "data": pd.DataFrame(),
                "summary": f"Error interacting with AI Agent: {str(e)}",
            }
