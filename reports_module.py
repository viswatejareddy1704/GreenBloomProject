import streamlit as st
import pandas as pd

from db_connection import get_connection


# =========================================================
# DATABASE HELPER
# =========================================================

def get_data(query):

    connection = None
    cursor = None

    try:

        connection = get_connection()

        cursor = connection.cursor(dictionary=True)

        cursor.execute(query)

        data = cursor.fetchall()

        return pd.DataFrame(data)

    except Exception as e:

        st.error(f"Database error: {e}")

        return pd.DataFrame()

    finally:

        if cursor:
            cursor.close()

        if connection:
            connection.close()


# =========================================================
# REPORTS MANAGEMENT
# =========================================================

def reports_management():

    st.title("📊 Reports & Analytics")

    st.write(
        "View plant stock, sales, customer purchases and business summaries."
    )

    st.markdown("---")

    # =====================================================
    # REPORT MENU
    # =====================================================

    report_type = st.selectbox(
        "Select Report",
        [
            "📈 Sales Overview",
            "🌿 Plant Stock Report",
            "⚠️ Low Stock Report",
            "👥 Customer Purchase History",
            "📋 Complete Sales Report"
        ]
    )

    st.markdown("---")

    # =====================================================
    # SALES OVERVIEW
    # =====================================================

    if report_type == "📈 Sales Overview":

        st.subheader("📈 Sales Overview")

        sales = get_data(
            """
            SELECT
                sale_id,
                customer_name,
                plant_name,
                quantity,
                total_amount,
                sale_date
            FROM sales
            ORDER BY sale_date ASC
            """
        )

        if sales.empty:

            st.info(
                "No sales data available yet."
            )

        else:

            # ---------------------------------------------
            # Convert values
            # ---------------------------------------------

            sales["total_amount"] = pd.to_numeric(
                sales["total_amount"],
                errors="coerce"
            ).fillna(0)

            sales["quantity"] = pd.to_numeric(
                sales["quantity"],
                errors="coerce"
            ).fillna(0)

            # ---------------------------------------------
            # Summary
            # ---------------------------------------------

            total_revenue = sales["total_amount"].sum()

            total_items = sales["quantity"].sum()

            total_orders = len(sales)

            average_order = (
                total_revenue / total_orders
                if total_orders > 0
                else 0
            )

            c1, c2, c3, c4 = st.columns(4)

            with c1:

                st.metric(
                    "💰 Total Revenue",
                    f"₹{total_revenue:,.2f}"
                )

            with c2:

                st.metric(
                    "🛒 Total Items Sold",
                    int(total_items)
                )

            with c3:

                st.metric(
                    "🧾 Total Orders",
                    total_orders
                )

            with c4:

                st.metric(
                    "📊 Average Order",
                    f"₹{average_order:,.2f}"
                )

            st.markdown("---")

            # ---------------------------------------------
            # Sales by Plant
            # ---------------------------------------------

            st.subheader("🌿 Sales by Plant")

            plant_sales = (
                sales
                .groupby("plant_name")["total_amount"]
                .sum()
                .sort_values(ascending=False)
            )

            if not plant_sales.empty:

                st.bar_chart(
                    plant_sales,
                    width="stretch"
                )

            # ---------------------------------------------
            # Daily Sales
            # ---------------------------------------------

            st.subheader("📅 Daily Sales")

            sales["sale_date"] = pd.to_datetime(
                sales["sale_date"],
                errors="coerce"
            )

            daily_sales = (
                sales
                .dropna(subset=["sale_date"])
                .groupby("sale_date")["total_amount"]
                .sum()
            )

            if not daily_sales.empty:

                st.line_chart(
                    daily_sales,
                    width="stretch"
                )

            # ---------------------------------------------
            # Sales table
            # ---------------------------------------------

            st.subheader("📋 Sales Details")

            display_sales = sales.copy()

            display_sales["total_amount"] = (
                display_sales["total_amount"]
                .apply(
                    lambda x: f"₹{x:,.2f}"
                )
            )

            st.dataframe(
                display_sales,
                width="stretch",
                hide_index=True
            )

    # =====================================================
    # PLANT STOCK REPORT
    # =====================================================

    elif report_type == "🌿 Plant Stock Report":

        st.subheader("🌿 Plant Stock Report")

        plants = get_data(
            """
            SELECT
                plant_id,
                plant_name,
                category,
                price,
                quantity,
                supplier_name
            FROM plants
            ORDER BY plant_name
            """
        )

        if plants.empty:

            st.info(
                "No plants available."
            )

        else:

            plants["price"] = pd.to_numeric(
                plants["price"],
                errors="coerce"
            ).fillna(0)

            plants["quantity"] = pd.to_numeric(
                plants["quantity"],
                errors="coerce"
            ).fillna(0)

            plants["stock_value"] = (
                plants["price"]
                * plants["quantity"]
            )

            # ---------------------------------------------
            # Summary
            # ---------------------------------------------

            total_quantity = plants["quantity"].sum()

            total_stock_value = plants["stock_value"].sum()

            plant_count = len(plants)

            categories = plants["category"].nunique()

            c1, c2, c3, c4 = st.columns(4)

            with c1:

                st.metric(
                    "🌱 Plant Types",
                    plant_count
                )

            with c2:

                st.metric(
                    "📦 Total Stock",
                    int(total_quantity)
                )

            with c3:

                st.metric(
                    "💰 Stock Value",
                    f"₹{total_stock_value:,.2f}"
                )

            with c4:

                st.metric(
                    "🗂️ Categories",
                    categories
                )

            st.markdown("---")

            # ---------------------------------------------
            # Stock chart
            # ---------------------------------------------

            st.subheader("📦 Current Stock by Plant")

            stock_chart = (
                plants
                .set_index("plant_name")["quantity"]
                .sort_values(ascending=False)
            )

            st.bar_chart(
                stock_chart,
                width="stretch"
            )

            # ---------------------------------------------
            # Category stock
            # ---------------------------------------------

            if "category" in plants.columns:

                st.subheader("🗂️ Stock by Category")

                category_stock = (
                    plants
                    .groupby("category")["quantity"]
                    .sum()
                    .sort_values(ascending=False)
                )

                if not category_stock.empty:

                    st.bar_chart(
                        category_stock,
                        width="stretch"
                    )

            # ---------------------------------------------
            # Table
            # ---------------------------------------------

            st.subheader("📋 Inventory Details")

            display_plants = plants.copy()

            display_plants["price"] = (
                display_plants["price"]
                .apply(
                    lambda x: f"₹{x:,.2f}"
                )
            )

            display_plants["stock_value"] = (
                plants["stock_value"]
                .apply(
                    lambda x: f"₹{x:,.2f}"
                )
            )

            st.dataframe(
                display_plants,
                width="stretch",
                hide_index=True
            )

    # =====================================================
    # LOW STOCK REPORT
    # =====================================================

    elif report_type == "⚠️ Low Stock Report":

        st.subheader("⚠️ Low Stock Report")

        plants = get_data(
            """
            SELECT
                plant_id,
                plant_name,
                category,
                price,
                quantity,
                supplier_name
            FROM plants
            WHERE quantity <= 5
            ORDER BY quantity ASC
            """
        )

        if plants.empty:

            st.success(
                "✅ No plants currently have low stock."
            )

        else:

            plants["quantity"] = pd.to_numeric(
                plants["quantity"],
                errors="coerce"
            ).fillna(0)

            out_of_stock = plants[
                plants["quantity"] == 0
            ]

            low_stock = plants[
                (plants["quantity"] > 0)
                & (plants["quantity"] <= 5)
            ]

            c1, c2 = st.columns(2)

            with c1:

                st.metric(
                    "🚨 Out of Stock",
                    len(out_of_stock)
                )

            with c2:

                st.metric(
                    "⚠️ Low Stock",
                    len(low_stock)
                )

            st.markdown("---")

            st.dataframe(
                plants,
                width="stretch",
                hide_index=True
            )

    # =====================================================
    # CUSTOMER PURCHASE HISTORY
    # =====================================================

    elif report_type == "👥 Customer Purchase History":

        st.subheader("👥 Customer Purchase History")

        sales = get_data(
            """
            SELECT
                customer_name,
                plant_name,
                quantity,
                total_amount,
                sale_date
            FROM sales
            ORDER BY sale_date DESC
            """
        )

        if sales.empty:

            st.info(
                "No customer purchases found."
            )

        else:

            sales["quantity"] = pd.to_numeric(
                sales["quantity"],
                errors="coerce"
            ).fillna(0)

            sales["total_amount"] = pd.to_numeric(
                sales["total_amount"],
                errors="coerce"
            ).fillna(0)

            # ---------------------------------------------
            # Customer selection
            # ---------------------------------------------

            customers = sorted(
                sales["customer_name"]
                .dropna()
                .unique()
                .tolist()
            )

            selected_customer = st.selectbox(
                "Select Customer",
                ["All Customers"] + customers
            )

            if selected_customer == "All Customers":

                customer_sales = sales.copy()

            else:

                customer_sales = sales[
                    sales["customer_name"]
                    == selected_customer
                ].copy()

            # ---------------------------------------------
            # Summary
            # ---------------------------------------------

            total_spent = (
                customer_sales["total_amount"].sum()
            )

            total_items = (
                customer_sales["quantity"].sum()
            )

            total_orders = len(customer_sales)

            c1, c2, c3 = st.columns(3)

            with c1:

                st.metric(
                    "💰 Total Spent",
                    f"₹{total_spent:,.2f}"
                )

            with c2:

                st.metric(
                    "🌱 Items Purchased",
                    int(total_items)
                )

            with c3:

                st.metric(
                    "🧾 Orders",
                    total_orders
                )

            st.markdown("---")

            # ---------------------------------------------
            # Customer sales chart
            # ---------------------------------------------

            if not customer_sales.empty:

                customer_chart = (
                    customer_sales
                    .groupby("plant_name")[
                        "quantity"
                    ]
                    .sum()
                )

                st.subheader(
                    "🌿 Plants Purchased"
                )

                st.bar_chart(
                    customer_chart,
                    width="stretch"
                )

            # ---------------------------------------------
            # Purchase table
            # ---------------------------------------------

            display_customer = customer_sales.copy()

            display_customer["total_amount"] = (
                display_customer["total_amount"]
                .apply(
                    lambda x: f"₹{x:,.2f}"
                )
            )

            st.dataframe(
                display_customer,
                width="stretch",
                hide_index=True
            )

    # =====================================================
    # COMPLETE SALES REPORT
    # =====================================================

    elif report_type == "📋 Complete Sales Report":

        st.subheader("📋 Complete Sales Report")

        sales = get_data(
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

        if sales.empty:

            st.info(
                "No sales records available."
            )

        else:

            sales["quantity"] = pd.to_numeric(
                sales["quantity"],
                errors="coerce"
            ).fillna(0)

            sales["total_amount"] = pd.to_numeric(
                sales["total_amount"],
                errors="coerce"
            ).fillna(0)

            # ---------------------------------------------
            # Date filter
            # ---------------------------------------------

            sales["sale_date"] = pd.to_datetime(
                sales["sale_date"],
                errors="coerce"
            )

            min_date = sales["sale_date"].min().date()

            max_date = sales["sale_date"].max().date()

            date_range = st.date_input(
                "Select Date Range",
                value=(min_date, max_date)
            )

            if isinstance(date_range, tuple) and len(date_range) == 2:

                start_date = pd.Timestamp(
                    date_range[0]
                )

                end_date = pd.Timestamp(
                    date_range[1]
                )

                filtered_sales = sales[
                    (sales["sale_date"] >= start_date)
                    &
                    (sales["sale_date"] <= end_date)
                ].copy()

            else:

                filtered_sales = sales.copy()

            # ---------------------------------------------
            # Summary
            # ---------------------------------------------

            revenue = (
                filtered_sales["total_amount"].sum()
            )

            quantity = (
                filtered_sales["quantity"].sum()
            )

            orders = len(filtered_sales)

            c1, c2, c3 = st.columns(3)

            with c1:

                st.metric(
                    "💰 Revenue",
                    f"₹{revenue:,.2f}"
                )

            with c2:

                st.metric(
                    "🌿 Items Sold",
                    int(quantity)
                )

            with c3:

                st.metric(
                    "🧾 Orders",
                    orders
                )

            st.markdown("---")

            # ---------------------------------------------
            # Display report
            # ---------------------------------------------

            display_sales = filtered_sales.copy()

            display_sales["total_amount"] = (
                display_sales["total_amount"]
                .apply(
                    lambda x: f"₹{x:,.2f}"
                )
            )

            display_sales["sale_date"] = (
                display_sales["sale_date"]
                .dt.strftime("%Y-%m-%d")
            )

            st.dataframe(
                display_sales,
                width="stretch",
                hide_index=True
            )

            # ---------------------------------------------
            # Download CSV
            # ---------------------------------------------

            csv_data = filtered_sales.to_csv(
                index=False
            )

            st.download_button(
                label="⬇️ Download Sales Report",
                data=csv_data,
                file_name="greenbloom_sales_report.csv",
                mime="text/csv"
            )
