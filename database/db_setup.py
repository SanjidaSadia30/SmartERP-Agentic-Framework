import os
import sqlite3

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "database", "erp_data.db")


def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    #1. Inventory Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS inventory (
            product_id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_name TEXT UNIQUE NOT NULL,
            category TEXT,
            stock_level INTEGER,
            min_threshold INTEGER,
            unit_price REAL,
            supplier_id INTEGER
        )
    """)

    # 2. Sales Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sales (
            sale_id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_name TEXT,
            quantity INTEGER,
            price REAL,
            sale_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # 3. Suppliers Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS suppliers (
            supplier_id INTEGER PRIMARY KEY AUTOINCREMENT,
            supplier_name TEXT,
            product_supplied TEXT,
            contact_email TEXT
        )
    """)

    # ---------------------------------------------------------
    # Suppliers Data
    # ---------------------------------------------------------
    suppliers_data = [
        (1, "Global Packaging Ltd", "Packaging Boxes", "supplier1@example.com"),
        (2, "ChemTech Supplies", "Industrial Lubricant", "supplier2@example.com"),
        (3, "Apex Textile Mills", "Raw Cotton", "sales@apextextiles.com"),
        (4, "Polymer World Bangladesh", "Stretch Wrap", "info@polymerworld.bd"),
        (5, "Safety First BD", "Safety Goggles", "orders@safetyfirst.com"),
    ]

    cursor.executemany(
        """
        INSERT OR IGNORE INTO suppliers (supplier_id, supplier_name, product_supplied, contact_email) 
        VALUES (?, ?, ?, ?)
    """,
        suppliers_data,
    )

    # ---------------------------------------------------------
    # Inventory Data (Rich Dataset)
    # ---------------------------------------------------------
    inventory_data = [
        ("Packaging Boxes", "Packaging", 500, 260, 15.0, 1),
        ("Industrial Lubricant", "Chemicals", 120, 200, 45.0, 2),  # Low Stock
        ("Raw Cotton", "Textile", 350, 100, 25.0, 3),
        ("Stretch Wrap Film", "Packaging", 80, 150, 12.0, 4),  # Low Stock
        ("Adhesive Tape Rolls", "Packaging", 600, 200, 5.0, 1),
        ("Chemical Solvent B", "Chemicals", 90, 100, 85.0, 2),  # Low Stock
        ("Yarn Thread Spools", "Textile", 450, 150, 18.0, 3),
        ("Safety Goggles", "Safety Equipment", 40, 80, 22.0, 5),  # Low Stock
        ("Industrial Gloves", "Safety Equipment", 250, 100, 8.0, 5),
    ]

    cursor.executemany(
        """
        INSERT OR IGNORE INTO inventory (product_name, category, stock_level, min_threshold, unit_price, supplier_id) 
        VALUES (?, ?, ?, ?, ?, ?)
    """,
        inventory_data,
    )

    # ---------------------------------------------------------
    # Sales Data
    # ---------------------------------------------------------
    sales_data = [
        ("Packaging Boxes", 20, 15.0),
        ("Industrial Lubricant", 8, 45.0),
        ("Raw Cotton", 15, 25.0),
        ("Stretch Wrap Film", 30, 12.0),
        ("Adhesive Tape Rolls", 50, 5.0),
        ("Chemical Solvent B", 5, 85.0),
        ("Yarn Thread Spools", 25, 18.0),
        ("Safety Goggles", 10, 22.0),
        ("Industrial Gloves", 15, 8.0),
        ("Packaging Boxes", 12, 15.0),
    ]

    cursor.executemany(
        """
        INSERT OR IGNORE INTO sales (product_name, quantity, price) 
        VALUES (?, ?, ?)
    """,
        sales_data,
    )

    conn.commit()
    conn.close()
    print("Database updated successfully with rich sample rows!")


if __name__ == "__main__":
    init_db()
