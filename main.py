import streamlit as st
import pandas as pd

from db_connection import get_connection
from plant_module import plant_management
from supplier_module import supplier_management
from customer_module import customer_management
from billing_module import billing_management
from reports_module import reports_management


# =========================================================
# PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="GreenBloom",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded"
)


# =========================================================
# CUSTOM CSS
# Only CSS is used here.
# No HTML is used for the dashboard content.
# =========================================================

st.markdown(
    """
    <style>

    .stApp {
        background-color: #f4f8f5;
    }

    section[data-testid="stSidebar"] {
        background: linear-gradient(
            180deg,
            #103d28 0%,
            #1f5c3a 50%,
            #2e7d4f 100%
        );
    }

    section[data-testid="stSidebar"] * {
        color: white !important;
    }

    .block-container {
        padding-top: 2rem;
        padding-bottom: 3rem;
    }

    div[data-testid="stMetric"] {
        background-color: white;
        border: 1px solid #dce9df;
        border-radius: 16px;
        padding: 18px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
    }

    div[data-testid="stMetricLabel"] {
        color: #607d68;
    }

    div[data-testid="stMetricValue"] {
        color: #1b5e20;
        font-weight: 800;
    }

    .stButton > button {
        border-radius: 10px;
        font-weight: 600;
    }

    div[data-testid="stDataFrame"] {
        border-radius: 12px;
        overflow: hidden;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# =========================================================
# DATABASE DATA
# =========================================================

def get_dashboard_data():

    connection = None
    cursor = None

    try:

        connection = get_connection()

        cursor = connection.cursor(dictionary=True)

        # -------------------------------------------------
        # PLANTS
        # -------------------------------------------------

        cursor.execute(
            """
            SELECT
                plant_id,
                plant_name,
                category,
                price,
                quantity,
                supplier_name,
                image_file
            FROM plants
            ORDER BY plant_id DESC
            """
        )

        plants = pd.DataFrame(
            cursor.fetchall()
        )

        # -------------------------------------------------
        # SUPPLIERS
        # -------------------------------------------------

        cursor.execute(
            """
            SELECT
                supplier_id,
                supplier_name,
                phone,
                city
            FROM suppliers
            ORDER BY supplier_id
            """
        )

        suppliers = pd.DataFrame(
            cursor.fetchall()
        )

        # -------------------------------------------------
        # CUSTOMERS
        # -------------------------------------------------

        cursor.execute(
            """
            SELECT
                customer_id,
                customer_name,
                phone,
                city
            FROM customers
            ORDER BY customer_id DESC
            """
        )

        customers = pd.DataFrame(
            cursor.fetchall()
        )

        # -------------------------------------------------
        # SALES
        # -------------------------------------------------

        cursor.execute(
            """
            SELECT
                sale_id,
                customer_name,
                plant_name,
                quantity,
                total_amount,
                sale_date
            FROM sales
            ORDER BY sale_id DESC
            """
        )

        sales = pd.DataFrame(
            cursor.fetchall()
        )

        return (
            plants,
            suppliers,
            customers,
            sales
        )

    except Exception as e:

        st.error(
            f"Database error: {e}"
        )

        return (
            pd.DataFrame(),
            pd.DataFrame(),
            pd.DataFrame(),
            pd.DataFrame()
        )

    finally:

        if cursor is not None:
            cursor.close()

        if connection is not None:
            connection.close()


# =========================================================
# DASHBOARD
# =========================================================

def dashboard():

    plants, suppliers, customers, sales = get_dashboard_data()

    # =====================================================
    # TITLE
    # =====================================================

    st.title("🌿 Welcome to GreenBloom")

    st.subheader(
        "Plant Nursery Management System"
    )

    st.write(
        "Manage plants, suppliers, customers, "
        "billing and reports in one place."
    )

    st.divider()

    # =====================================================
    # WELCOME MESSAGE
    # =====================================================

    st.success(
        "🌱 Grow Green. Manage Smart. "
        "Keep your nursery organized and monitor "
        "your plants, customers and sales easily."
    )

    # =====================================================
    # PREPARE PLANT DATA
    # =====================================================

    if plants.empty:

        total_plants = 0
        total_stock = 0
        stock_value = 0

    else:

        plants["quantity"] = pd.to_numeric(
            plants["quantity"],
            errors="coerce"
        ).fillna(0)

        plants["price"] = pd.to_numeric(
            plants["price"],
            errors="coerce"
        ).fillna(0)

        total_plants = len(plants)

        total_stock = int(
            plants["quantity"].sum()
        )

        stock_value = (
            plants["price"]
            * plants["quantity"]
        ).sum()

    # =====================================================
    # SUPPLIERS
    # =====================================================

    supplier_count = len(
        suppliers
    )

    # =====================================================
    # CUSTOMERS
    # =====================================================

    customer_count = len(
        customers
    )

    # =====================================================
    # SALES
    # =====================================================

    if sales.empty:

        total_sales = 0

    else:

        sales["total_amount"] = pd.to_numeric(
            sales["total_amount"],
            errors="coerce"
        ).fillna(0)

        total_sales = sales[
            "total_amount"
        ].sum()

    # =====================================================
    # DASHBOARD METRICS
    # =====================================================

    st.subheader("📊 Dashboard Overview")

    c1, c2, c3 = st.columns(3)

    with c1:

        st.metric(
            "🌱 Total Plant Types",
            total_plants
        )

    with c2:

        st.metric(
            "📦 Total Stock",
            total_stock
        )

    with c3:

        st.metric(
            "🚚 Suppliers",
            supplier_count
        )

    c4, c5, c6 = st.columns(3)

    with c4:

        st.metric(
            "👥 Customers",
            customer_count
        )

    with c5:

        st.metric(
            "💰 Current Stock Value",
            f"₹{stock_value:,.2f}"
        )

    with c6:

        st.metric(
            "📈 Total Sales",
            f"₹{total_sales:,.2f}"
        )

    st.divider()

    # =====================================================
    # STOCK ALERTS
    # =====================================================

    st.subheader("⚠️ Stock Alerts")

    if plants.empty:

        low_stock = pd.DataFrame()

        out_of_stock = pd.DataFrame()

    else:

        low_stock = plants[
            plants["quantity"] <= 5
        ].copy()

        out_of_stock = plants[
            plants["quantity"] == 0
        ].copy()

    alert_col1, alert_col2 = st.columns(2)

    # -----------------------------------------------------
    # LOW STOCK
    # -----------------------------------------------------

    with alert_col1:

        if not low_stock.empty:

            st.warning(
                f"⚠️ {len(low_stock)} plant(s) "
                "have low stock."
            )

            st.dataframe(
                low_stock[
                    [
                        "plant_name",
                        "quantity"
                    ]
                ],
                use_container_width=True,
                hide_index=True
            )

        else:

            st.success(
                "✅ No low-stock plants."
            )

    # -----------------------------------------------------
    # OUT OF STOCK
    # -----------------------------------------------------

    with alert_col2:

        if not out_of_stock.empty:

            st.error(
                f"🚨 {len(out_of_stock)} plant(s) "
                "are out of stock."
            )

            st.dataframe(
                out_of_stock[
                    [
                        "plant_name",
                        "quantity"
                    ]
                ],
                use_container_width=True,
                hide_index=True
            )

        else:

            st.success(
                "✅ No plants are out of stock."
            )

    st.divider()

    # =====================================================
    # CURRENT PLANT INVENTORY
    # =====================================================

    st.subheader("🌿 Current Plant Inventory")

    if plants.empty:

        st.info(
            "🌱 No plants have been added yet."
        )

    else:

        inventory = plants[
            [
                "plant_id",
                "plant_name",
                "category",
                "price",
                "quantity",
                "supplier_name"
            ]
        ].copy()

        inventory["price"] = inventory[
            "price"
        ].apply(
            lambda x: f"₹{float(x):,.2f}"
        )

        st.dataframe(
            inventory,
            use_container_width=True,
            hide_index=True
        )

    st.divider()

    # =====================================================
    # RECENT SALES
    # =====================================================

    st.subheader("💰 Recent Sales")

    if sales.empty:

        st.info(
            "🛒 No sales have been recorded yet."
        )

    else:

        recent_sales = sales.head(
            10
        ).copy()

        recent_sales["total_amount"] = (
            recent_sales["total_amount"]
            .apply(
                lambda x:
                f"₹{float(x):,.2f}"
            )
        )

        st.dataframe(
            recent_sales,
            use_container_width=True,
            hide_index=True
        )

    st.divider()

    # =====================================================
    # FOOTER
    # =====================================================

    st.caption(
        "🌿 GreenBloom Plant Management System | "
        "Plant Management • Suppliers • Customers • "
        "Billing • Reports"
    )

    st.caption(
        "🌱 Grow Green • Manage Smart • Protect Nature 🌍"
    )


# =========================================================
# SIDEBAR
# =========================================================

def sidebar_menu():

    # -----------------------------------------------------
    # SIDEBAR TITLE
    # -----------------------------------------------------

    st.sidebar.title(
        "🌿 GreenBloom"
    )

    st.sidebar.caption(
        "Plant Nursery Management"
    )

    st.sidebar.divider()

    # -----------------------------------------------------
    # NAVIGATION
    # -----------------------------------------------------

    menu = st.sidebar.radio(
        "🌱 Navigation",
        [
            "🏠 Dashboard",
            "🌿 Plant Management",
            "🚚 Supplier Management",
            "👤 Customer Management",
            "💰 Billing",
            "📊 Reports"
        ]
    )

    st.sidebar.divider()

    # -----------------------------------------------------
    # SIDEBAR INFORMATION
    # -----------------------------------------------------

    st.sidebar.success(
        "🌱 Grow Green\n\n"
        "🌍 Protect Nature"
    )

    st.sidebar.caption(
        "GreenBloom v1.0"
    )

    return menu


# =========================================================
# MAIN APPLICATION
# =========================================================

def main():

    menu = sidebar_menu()

    # -----------------------------------------------------
    # DASHBOARD
    # -----------------------------------------------------

    if menu == "🏠 Dashboard":

        dashboard()

    # -----------------------------------------------------
    # PLANT MANAGEMENT
    # -----------------------------------------------------

    elif menu == "🌿 Plant Management":

        plant_management()

    # -----------------------------------------------------
    # SUPPLIER MANAGEMENT
    # -----------------------------------------------------

    elif menu == "🚚 Supplier Management":

        supplier_management()

    # -----------------------------------------------------
    # CUSTOMER MANAGEMENT
    # -----------------------------------------------------

    elif menu == "👤 Customer Management":

        customer_management()

    # -----------------------------------------------------
    # BILLING
    # -----------------------------------------------------

    elif menu == "💰 Billing":

        billing_management()

    # -----------------------------------------------------
    # REPORTS
    # -----------------------------------------------------

    elif menu == "📊 Reports":

        reports_management()


# =========================================================
# START APPLICATION
# =========================================================

if __name__ == "__main__":

    main()