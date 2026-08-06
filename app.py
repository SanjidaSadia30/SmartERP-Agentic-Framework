import os
import sys
import pandas as pd
import plotly.express as px
import streamlit as st
from dotenv import load_dotenv

# Environment variables load
load_dotenv()

# Add root directory to sys.path
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from agents.auto_engine import ERPAutomationEngine
from agents.erp_agent import ERPAgent
from utils.db_helper import run_query

# Page Configuration
st.set_page_config(
    page_title="SmartERP Agentic Framework", page_icon="⚙️", layout="wide"
)

# ---------------------------------------------------------
# 🎨 CUSTOM CSS FOR COMPACT, SINGLE-SCREEN & EXECUTIVE UI
# ---------------------------------------------------------
st.markdown(
    """
    <style>
        /* Main Container Spacing Fix */
        .block-container { 
            padding-top: 1.2rem !important; 
            padding-bottom: 0rem !important;
            padding-left: 1.5rem !important;
            padding-right: 1.5rem !important;
        }
        /* Sidebar Padding Fix so inputs don't get cut at the top */
        section[data-testid="stSidebar"] > div {
            padding-top: 1.5rem !important;
            padding-bottom: 1rem !important;
        }
        div[data-testid="stSidebarUserContent"] {
            padding-top: 0.5rem !important;
        }
        .sidebar-title {
            font-size: 1.05rem !important;
            font-weight: 800 !important;
            color: #1E3A8A;
            margin-bottom: 8px !important;
        }
        .main-header {
            font-size: 1.7rem !important;
            font-weight: 800 !important;
            background: linear-gradient(90deg, #1E3A8A, #2563EB);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 0.5rem !important;
            margin-top: 0.2rem !important; 
            line-height: 1.2 !important;
        }
        div[data-testid="stMetric"] {
            background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
            border: 1px solid #cbd5e1;
            border-left: 5px solid #2563eb;
            padding: 8px 12px !important;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.04);
        }
        div[data-testid="stMetricLabel"] { 
            font-size: 0.78rem !important; 
            font-weight: 700 !important; 
            color: #475569 !important; 
        }
        div[data-testid="stMetricValue"] { 
            font-size: 1.3rem !important; 
            font-weight: 900 !important; 
            color: #0f172a !important; 
        }
        .section-title {
            font-size: 1.05rem !important;
            font-weight: 800 !important;
            color: #1e293b;
            border-bottom: 2px solid #e2e8f0;
            padding-bottom: 4px;
            margin-top: 8px;
            margin-bottom: 8px;
        }
    </style>
""",
    unsafe_allow_html=True,
)

# Header Title
st.markdown(
    "<h1 class='main-header'>⚙️ SmartERP Agentic Framework</h1>",
    unsafe_allow_html=True,
)

# Initialize Session State
if "messages" not in st.session_state:
    st.session_state.messages = []

# ---------------------------------------------------------
# 📌 SIDEBAR: CONTROL CENTER & DATA MANAGEMENT
# ---------------------------------------------------------
st.sidebar.markdown(
    "<div class='sidebar-title'>Control Center</div>", unsafe_allow_html=True
)

page = st.sidebar.radio(
    "Select Module",
    ["Dashboard & Analytics", "Enterprise AI Assistant", "Autonomous Operations"],
    label_visibility="collapsed",
)

st.sidebar.markdown("---")
st.sidebar.markdown(
    "<div class='sidebar-title' style='font-size: 0.95rem !important;'>Data Management</div>",
    unsafe_allow_html=True,
)

# 1. Live Data Entry (Proper Input Label Visibility)
with st.sidebar.expander("➕ Live Entry", expanded=False):
    with st.form("live_data_entry_form", clear_on_submit=True):
        product_name = st.text_input(
            "Product Name", key="p_name", help="Enter unique product title"
        )
        c1, c2 = st.columns(2)
        with c1:
            stock_level = st.number_input("Stock", min_value=0, step=1, value=50)
            unit_cost = st.number_input(
                "Unit Cost ($)", min_value=0.0, step=1.0, value=10.0
            )
        with c2:
            min_threshold = st.number_input("Min Thresh", min_value=0, step=1, value=20)
            supplier_id = st.number_input("Supplier ID", min_value=1, step=1, value=1)

        add_sale = st.checkbox("Add Initial Sale?")
        quantity_sold = st.number_input("Qty Sold", min_value=0, step=1, value=0)

        submitted = st.form_submit_button("Submit Data", use_container_width=True)

    if submitted and product_name.strip():
        try:
            # Check if product already exists to avoid raw SQL UNIQUE error
            existing = run_query(
                "SELECT product_name FROM inventory WHERE product_name = ?",
                (product_name.strip(),),
            )
            if isinstance(existing, pd.DataFrame) and not existing.empty:
                st.sidebar.warning(f"⚠️ '{product_name.strip()}' already exists!")
            else:
                run_query(
                    """
                    INSERT INTO inventory (product_name, stock_level, min_threshold, unit_price, supplier_id)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (
                        product_name.strip(),
                        stock_level,
                        min_threshold,
                        unit_cost,
                        supplier_id,
                    ),
                )

                if add_sale and quantity_sold > 0:
                    total_price = quantity_sold * unit_cost
                    run_query(
                        """
                        INSERT INTO sales (product_name, quantity, price)
                        VALUES (?, ?, ?)
                        """,
                        (product_name.strip(), quantity_sold, total_price),
                    )

                st.sidebar.success(f"Added '{product_name.strip()}'!")
                st.rerun()
        except Exception as e:
            st.sidebar.error(f"Error saving data: {e}")

# 2. View Database Whitelist
with st.sidebar.expander("🗄️ View Full Database", expanded=False):
    ALLOWED_TABLES = ["inventory", "sales", "suppliers"]
    table_choice = st.selectbox("Select Table", ALLOWED_TABLES)

    if st.button("Fetch Table Data", use_container_width=True):
        if table_choice in ALLOWED_TABLES:
            try:
                db_df = run_query(f"SELECT * FROM {table_choice}")
                st.session_state["active_table"] = table_choice
                st.session_state["active_df"] = db_df
            except Exception as e:
                st.error(f"Error: {e}")

# 3. Delete Product
with st.sidebar.expander("🗑️ Delete Product", expanded=False):
    try:
        products_df = run_query("SELECT product_name FROM inventory")
        if isinstance(products_df, pd.DataFrame) and not products_df.empty:
            product_list = products_df["product_name"].tolist()
            selected_product = st.selectbox("Select Product", product_list)

            if st.button("Delete Product", type="primary", use_container_width=True):
                run_query(
                    "DELETE FROM inventory WHERE product_name = ?",
                    (selected_product,),
                )
                run_query(
                    "DELETE FROM sales WHERE product_name = ?", (selected_product,)
                )
                st.success(f"Deleted '{selected_product}'!")
                st.rerun()
        else:
            st.info("No products available.")
    except Exception as e:
        st.error(f"Error: {e}")


# =========================================================
# MODULE 1: DASHBOARD & ANALYTICS
# =========================================================
if page == "Dashboard & Analytics":
    if "active_df" in st.session_state and st.session_state["active_df"] is not None:
        st.subheader(f"📋 Live Database Records: `{st.session_state['active_table']}`")
        st.dataframe(
            st.session_state["active_df"], use_container_width=True, hide_index=True
        )
        if st.button("Close Database View", type="secondary"):
            st.session_state["active_df"] = None
            st.rerun()
        st.markdown("---")

    # Real-Time KPI Metric Cards
    try:
        total_items_df = run_query("SELECT COUNT(*) as count FROM inventory")
        total_items = (
            total_items_df["count"].iloc[0]
            if isinstance(total_items_df, pd.DataFrame)
            else 0
        )

        total_val_df = run_query(
            "SELECT SUM(stock_level * unit_price) as val FROM inventory"
        )
        total_val = (
            total_val_df["val"].iloc[0]
            if isinstance(total_val_df, pd.DataFrame)
            and pd.notna(total_val_df["val"].iloc[0])
            else 0.0
        )

        total_rev_df = run_query("SELECT SUM(quantity * price) as rev FROM sales")
        total_rev = (
            total_rev_df["rev"].iloc[0]
            if isinstance(total_rev_df, pd.DataFrame)
            and pd.notna(total_rev_df["rev"].iloc[0])
            else 0.0
        )

        low_stock_df = run_query(
            "SELECT COUNT(*) as count FROM inventory WHERE stock_level < min_threshold"
        )
        low_stock_count = (
            low_stock_df["count"].iloc[0]
            if isinstance(low_stock_df, pd.DataFrame)
            else 0
        )

        kpi1, kpi2, kpi3, kpi4 = st.columns(4)
        kpi1.metric("📦 Total Products", f"{total_items} Items")
        kpi2.metric("💵 Total Stock Value", f"${total_val:,.2f}")
        kpi3.metric("💰 Total Sales Revenue", f"${total_rev:,.2f}")
        kpi4.metric(
            "⚠️ Low Stock Alerts",
            f"{low_stock_count} Items",
            delta_color="inverse",
        )
    except Exception as e:
        pass

    # Charts and Data Tables
    st.markdown(
        "<div class='section-title'>📊 Enterprise Data Overview</div>",
        unsafe_allow_html=True,
    )
    col1, col2 = st.columns([1.1, 0.9])

    with col1:
        inventory_df = run_query("""
            SELECT product_name, stock_level, min_threshold 
            FROM inventory
        """)

        if isinstance(inventory_df, pd.DataFrame) and not inventory_df.empty:
            inventory_df["stock_level"] = pd.to_numeric(
                inventory_df["stock_level"], errors="coerce"
            )
            inventory_df["min_threshold"] = pd.to_numeric(
                inventory_df["min_threshold"], errors="coerce"
            )

            fig_inv = px.bar(
                inventory_df,
                x="product_name",
                y=["stock_level", "min_threshold"],
                barmode="group",
                title="<b>Stock Level vs Minimum Threshold</b>",
                labels={
                    "value": "Quantity",
                    "product_name": "Product Name",
                    "variable": "Metrics",
                },
                color_discrete_sequence=["#00CC96", "#EF553B"],
                height=310,
            )
            fig_inv.update_layout(
                title_font=dict(size=14, color="#0f172a"),
                xaxis_tickangle=-30,
                margin=dict(l=10, r=10, t=35, b=60),
                legend=dict(
                    orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1
                ),
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
            )

            st.plotly_chart(
                fig_inv, use_container_width=True, config={"displayModeBar": False}
            )
            st.markdown("##### **Inventory Data Table**")
            st.dataframe(
                inventory_df,
                use_container_width=True,
                hide_index=True,
                height=170,
            )
        else:
            st.warning("⚠️ No inventory data available.")

    with col2:
        sales_df = run_query("""
            SELECT product_name, SUM(quantity * price) as total_revenue 
            FROM sales 
            GROUP BY product_name
            ORDER BY total_revenue DESC
        """)

        if isinstance(sales_df, pd.DataFrame) and not sales_df.empty:
            sales_df["total_revenue"] = pd.to_numeric(
                sales_df["total_revenue"], errors="coerce"
            )

            fig_sales = px.pie(
                sales_df,
                names="product_name",
                values="total_revenue",
                title="<b>Revenue Distribution by Product</b>",
                hole=0.45,
                height=310,
                color_discrete_sequence=px.colors.qualitative.Pastel,
            )
            fig_sales.update_layout(
                title_font=dict(size=14, color="#0f172a"),
                margin=dict(l=10, r=10, t=35, b=20),
                legend=dict(orientation="h", yanchor="top", y=-0.15),
                paper_bgcolor="rgba(0,0,0,0)",
            )

            st.plotly_chart(
                fig_sales, use_container_width=True, config={"displayModeBar": False}
            )
            st.markdown("#####  **Sales Revenue Summary Table**")
            st.dataframe(
                sales_df,
                use_container_width=True,
                hide_index=True,
                height=170,
            )
        else:
            st.info("ℹ️ No sales records found.")


# =========================================================
# MODULE 2: ENTERPRISE AI ASSISTANT
# =========================================================
elif page == "Enterprise AI Assistant":
    st.markdown(
        "<h3 style='margin-bottom: -10px;'>AI ERP Assistant</h3>",
        unsafe_allow_html=True,
    )
    st.caption(
        "Query enterprise sales, inventory, and supplier data using simple natural language."
    )

    agent = ERPAgent()

    # 5 Quick Sample Query Buttons
    st.markdown("**Quick Queries:**")
    b1, b2, b3, b4, b5 = st.columns(5)

    selected_prompt = None
    with b1:
        if st.button("Low Stock", use_container_width=True):
            selected_prompt = "Show low stock products"
    with b2:
        if st.button("Total Revenue", use_container_width=True):
            selected_prompt = "What is the total sales revenue?"
    with b3:
        if st.button("Suppliers", use_container_width=True):
            selected_prompt = "List all suppliers and their products"
    with b4:
        if st.button("Top Selling", use_container_width=True):
            selected_prompt = "Which product generated highest revenue?"
    with b5:
        if st.button("Category Stock", use_container_width=True):
            selected_prompt = "Show total stock quantity by category"

    # Chat Input Bar
    user_input = st.chat_input("Enter your query (e.g., Show low stock products)...")
    prompt_to_process = selected_prompt if selected_prompt else user_input

    # Process Query
    if prompt_to_process:
        st.session_state.messages.append({"role": "user", "content": prompt_to_process})
        with st.spinner("Analyzing schema & executing SQL query..."):
            response = agent.ask_agent(prompt_to_process)
            st.session_state.messages.append(
                {
                    "role": "assistant",
                    "content": response["summary"],
                    "sql": response.get("sql", ""),
                    "df": response.get("data", None),
                }
            )

    # Dynamic Height Single Screen Result Panel
    if st.session_state.messages:
        last_user_msg = None
        last_assistant_msg = None

        for msg in reversed(st.session_state.messages):
            if msg["role"] == "assistant" and not last_assistant_msg:
                last_assistant_msg = msg
            elif msg["role"] == "user" and not last_user_msg:
                last_user_msg = msg

            if last_user_msg and last_assistant_msg:
                break

        if last_user_msg and last_assistant_msg:
            with st.container(border=True):
                q_col, reset_col = st.columns([5, 1])
                with q_col:
                    st.markdown(f"**Query:** *\"{last_user_msg['content']}\"*")
                with reset_col:
                    if st.button("Clear", type="secondary", use_container_width=True):
                        st.session_state.messages = []
                        st.rerun()

                st.info(f"**Summary:** {last_assistant_msg['content']}")

                # Dynamic height based on row count (Prevents large empty grid gaps)
                if (
                    isinstance(last_assistant_msg.get("df"), pd.DataFrame)
                    and not last_assistant_msg["df"].empty
                ):
                    df_res = last_assistant_msg["df"]
                    num_rows = len(df_res)
                    calculated_height = min(150, max(78, num_rows * 38 + 40))

                    st.dataframe(
                        df_res,
                        use_container_width=True,
                        hide_index=True,
                        height=calculated_height,
                    )

                if last_assistant_msg.get("sql"):
                    with st.expander("🔍 View Generated SQL Query"):
                        st.code(last_assistant_msg["sql"], language="sql")


# =========================================================
# MODULE 3: AUTONOMOUS OPERATIONS
# =========================================================
elif page == "Autonomous Operations":
    st.subheader("Autonomous Operations & Procurement Hub")
    st.caption("Automated inventory monitoring and purchase order generation system.")

    auto_engine = ERPAutomationEngine()

    # Stock Audit Trigger Button
    if st.button("Execute Stock Audit", type="primary"):
        with st.spinner("Analyzing inventory levels..."):
            audit_results = auto_engine.check_low_stock_and_reorder()
            if audit_results.get("status") == "success":
                st.session_state["pending_actions"] = audit_results.get("actions", [])
                st.session_state["audit_executed"] = True
                st.session_state["action_statuses"] = {}

    # Display Audit Results
    if st.session_state.get("audit_executed", False):
        actions = st.session_state.get("pending_actions", [])

        if not actions:
            st.success("✅ All safety stock thresholds met. No pending actions.")
        else:
            st.markdown(
                f"""
                <div style="background-color: #FEF2F2; border: 1px solid #FECACA; border-left: 4px solid #DC2626; padding: 6px 12px; border-radius: 6px; margin: 8px 0px;">
                    <span style="color: #991B1B; font-weight: 700; font-size: 0.85rem;">
                        Alert: {len(actions)} item(s) below safety stock threshold. Action required.
                    </span>
                </div>
                """,
                unsafe_allow_html=True,
            )

            st.markdown("##### Pending Purchase Requisitions")

            for idx, item in enumerate(actions):
                product_name = item["product"]
                current_status = st.session_state.get("action_statuses", {}).get(
                    product_name, "pending"
                )

                with st.container(border=True):
                    (
                        c_prod,
                        c_stock,
                        c_thresh,
                        c_action,
                        c_status,
                    ) = st.columns([1.8, 1.0, 1.0, 3.2, 2.2])

                    with c_prod:
                        st.caption("Product")
                        st.markdown(f"**{product_name}**")

                    with c_stock:
                        st.caption("Current")
                        st.markdown(f"**{item['current_stock']}**")

                    with c_thresh:
                        st.caption("Min Threshold")
                        st.markdown(f"**{item.get('min_threshold', 'N/A')}**")

                    with c_action:
                        st.caption("Recommended Action")
                        action_text = item["action"].replace(
                            "Auto Purchase Requisition Drafted to ", "Drafted to: "
                        )
                        st.markdown(
                            f"<span style='font-size: 0.82rem;'>{action_text}</span>",
                            unsafe_allow_html=True,
                        )

                    with c_status:
                        st.caption("Status / Action")
                        if current_status == "pending":
                            b1, b2 = st.columns(2)
                            with b1:
                                if st.button(
                                    "Approve",
                                    key=f"app_{product_name}",
                                    type="primary",
                                    use_container_width=True,
                                ):
                                    st.session_state["action_statuses"][
                                        product_name
                                    ] = "approved"
                                    st.toast(
                                        f"✅ Purchase order approved for {product_name}!"
                                    )
                                    st.rerun()
                            with b2:
                                if st.button(
                                    "Reject",
                                    key=f"rej_{product_name}",
                                    use_container_width=True,
                                ):
                                    st.session_state["action_statuses"][
                                        product_name
                                    ] = "rejected"
                                    st.toast(
                                        f"❌ Requisition rejected for {product_name}."
                                    )
                                    st.rerun()

                        elif current_status == "approved":
                            st.markdown(
                                "<span style='color: #16a34a; font-weight: 700;'>✅ Approved</span>",
                                unsafe_allow_html=True,
                            )
                        elif current_status == "rejected":
                            st.markdown(
                                "<span style='color: #dc2626; font-weight: 700;'>❌ Rejected</span>",
                                unsafe_allow_html=True,
                            )
