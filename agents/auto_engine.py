import os
import pandas as pd
from utils.db_helper import run_query


class ERPAutomationEngine:
    def check_low_stock_and_reorder(self):

        try:
            # Low stock items search query with supplier info
            query = """
            SELECT 
                i.product_name, 
                i.stock_level, 
                i.min_threshold, 
                s.supplier_name, 
                s.contact_email
            FROM inventory i
            LEFT JOIN suppliers s ON i.supplier_id = s.supplier_id
            WHERE i.stock_level < i.min_threshold
            """

            # db_helper central function
            low_stock_df = run_query(query)

            actions = []
            if isinstance(low_stock_df, pd.DataFrame) and not low_stock_df.empty:
                for _, row in low_stock_df.iterrows():
                    product = row["product_name"]
                    stock = row["stock_level"]

                    # Missing data handle
                    supplier = (
                        row["supplier_name"]
                        if pd.notna(row["supplier_name"]) and row["supplier_name"]
                        else "Default Supplier"
                    )
                    email = (
                        row["contact_email"]
                        if pd.notna(row["contact_email"]) and row["contact_email"]
                        else "procurement@company.com"
                    )

                    actions.append(
                        {
                            "product": product,
                            "current_stock": stock,
                            "min_threshold": row.get("min_threshold", "N/A"),
                            "action": f"Auto Purchase Requisition Drafted to {supplier} ({email})",
                        }
                    )

            return {
                "status": "success",
                "low_stock_items": low_stock_df,
                "actions": actions,
            }

        except Exception as e:
            return {"status": "error", "message": str(e)}
