import streamlit as st
import pandas as pd

from db_connection import get_connection


def billing_management():

    # =========================================================
    # PAGE TITLE
    # =========================================================

    st.title("💰 Billing & Sales")

    st.caption(
        "Generate customer bills, manage plant sales and automatically update stock."
    )

    st.divider()

    connection = get_connection()

    try:

        # =====================================================
        # LOAD CUSTOMERS
        # =====================================================

        customers = pd.read_sql(
            """
            SELECT
                customer_id,
                customer_name,
                phone,
                city
            FROM customers
            ORDER BY customer_name
            """,
            connection
        )

        # =====================================================
        # LOAD PLANTS
        # =====================================================

        plants = pd.read_sql(
            """
            SELECT
                plant_id,
                plant_name,
                category,
                price,
                quantity
            FROM plants
            WHERE quantity > 0
            ORDER BY plant_name
            """,
            connection
        )

        # =====================================================
        # BASIC VALIDATION
        # =====================================================

        if customers.empty:

            st.warning(
                "👤 No customers found. Please add a customer first."
            )

            return

        if plants.empty:

            st.warning(
                "🌱 No plants are currently available in stock."
            )

            return

        # =====================================================
        # BILLING SUMMARY
        # =====================================================

        total_stock = int(plants["quantity"].sum())

        total_stock_value = (
            plants["price"] * plants["quantity"]
        ).sum()

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric(
                "👤 Customers",
                len(customers)
            )

        with col2:
            st.metric(
                "🌱 Plants Available",
                len(plants)
            )

        with col3:
            st.metric(
                "📦 Total Stock",
                total_stock
            )

        st.divider()

        # =====================================================
        # BILLING FORM
        # =====================================================

        st.subheader("🧾 Create New Bill")

        # -----------------------------------------------------
        # CUSTOMER
        # -----------------------------------------------------

        customer_options = customers.apply(
            lambda row:
            f"{row['customer_name']}  |  ID: {row['customer_id']}",
            axis=1
        ).tolist()

        selected_customer = st.selectbox(
            "👤 Select Customer",
            customer_options
        )

        selected_customer_index = customer_options.index(
            selected_customer
        )

        customer_row = customers.iloc[
            selected_customer_index
        ]

        customer_name = customer_row["customer_name"]

        customer_phone = customer_row["phone"]

        customer_city = customer_row["city"]

        # -----------------------------------------------------
        # CUSTOMER INFORMATION
        # -----------------------------------------------------

        st.info(
            f"👤 **Customer:** {customer_name}   |   "
            f"📞 **Phone:** {customer_phone or 'Not available'}   |   "
            f"🏙️ **City:** {customer_city or 'Not available'}"
        )

        # =====================================================
        # PLANT SELECTION
        # =====================================================

        plant_options = plants.apply(
            lambda row:
            f"{row['plant_name']}  |  ₹{float(row['price']):.2f}  |  Stock: {int(row['quantity'])}",
            axis=1
        ).tolist()

        selected_plant = st.selectbox(
            "🌱 Select Plant",
            plant_options
        )

        selected_plant_index = plant_options.index(
            selected_plant
        )

        plant_row = plants.iloc[
            selected_plant_index
        ]

        plant_id = int(
            plant_row["plant_id"]
        )

        plant_name = plant_row["plant_name"]

        category = plant_row["category"]

        price = float(
            plant_row["price"]
        )

        stock = int(
            plant_row["quantity"]
        )

        # =====================================================
        # PLANT DETAILS
        # =====================================================

        st.subheader("🌿 Plant Details")

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric(
                "Plant",
                plant_name
            )

        with col2:
            st.metric(
                "Category",
                category or "N/A"
            )

        with col3:
            st.metric(
                "Price",
                f"₹{price:.2f}"
            )

        with col4:
            st.metric(
                "Available",
                stock
            )

        st.divider()

        # =====================================================
        # QUANTITY
        # =====================================================

        quantity = st.number_input(
            "🔢 Quantity",
            min_value=1,
            max_value=stock,
            value=1,
            step=1
        )

        # =====================================================
        # CALCULATE TOTAL
        # =====================================================

        total = price * quantity

        st.subheader("💵 Bill Summary")

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric(
                "Unit Price",
                f"₹{price:.2f}"
            )

        with col2:
            st.metric(
                "Quantity",
                quantity
            )

        with col3:
            st.metric(
                "Total Amount",
                f"₹{total:.2f}"
            )

        # =====================================================
        # BILL PREVIEW
        # =====================================================

        with st.expander("👁️ Preview Bill"):

            st.markdown(
                f"""
                **🌿 GreenBloom Plant Nursery**

                ---

                **Customer:** {customer_name}

                **Phone:** {customer_phone or "Not available"}

                **City:** {customer_city or "Not available"}

                ---

                | Item | Quantity | Unit Price | Total |
                |---|---:|---:|---:|
                | {plant_name} | {quantity} | ₹{price:.2f} | ₹{total:.2f} |

                ---

                **Grand Total: ₹{total:.2f}**
                """
            )

        st.divider()

        # =====================================================
        # GENERATE BILL
        # =====================================================

        generate_bill = st.button(
            "🧾 Generate Bill",
            type="primary",
            width="stretch"
        )

        if generate_bill:

            cursor = connection.cursor()

            try:

                # -------------------------------------------------
                # Check latest stock before sale
                # -------------------------------------------------

                cursor.execute(
                    """
                    SELECT quantity
                    FROM plants
                    WHERE plant_id = %s
                    FOR UPDATE
                    """,
                    (plant_id,)
                )

                latest_stock_result = cursor.fetchone()

                if latest_stock_result is None:

                    connection.rollback()

                    st.error(
                        "❌ Plant could not be found."
                    )

                    return

                latest_stock = int(
                    latest_stock_result[0]
                )

                if latest_stock < quantity:

                    connection.rollback()

                    st.error(
                        f"❌ Not enough stock. "
                        f"Only {latest_stock} item(s) are available."
                    )

                    return

                # -------------------------------------------------
                # Insert sale
                # -------------------------------------------------

                cursor.execute(
                    """
                    INSERT INTO sales
                    (
                        customer_name,
                        plant_name,
                        quantity,
                        total_amount,
                        sale_date
                    )
                    VALUES
                    (
                        %s,
                        %s,
                        %s,
                        %s,
                        CURDATE()
                    )
                    """,
                    (
                        customer_name,
                        plant_name,
                        quantity,
                        total
                    )
                )

                sale_id = cursor.lastrowid

                # -------------------------------------------------
                # Reduce plant stock
                # -------------------------------------------------

                cursor.execute(
                    """
                    UPDATE plants
                    SET quantity = quantity - %s
                    WHERE plant_id = %s
                    AND quantity >= %s
                    """,
                    (
                        quantity,
                        plant_id,
                        quantity
                    )
                )

                if cursor.rowcount == 0:

                    connection.rollback()

                    st.error(
                        "❌ Stock could not be updated. "
                        "The bill was not generated."
                    )

                    return

                # -------------------------------------------------
                # Commit transaction
                # -------------------------------------------------

                connection.commit()

                # =================================================
                # SUCCESS MESSAGE
                # =================================================

                st.success(
                    "✅ Bill generated successfully!"
                )

                # =================================================
                # FINAL BILL
                # =================================================

                st.markdown("---")

                st.subheader("🧾 Generated Bill")

                bill_col1, bill_col2 = st.columns(2)

                with bill_col1:

                    st.write(
                        f"**Bill ID:** #{sale_id}"
                    )

                    st.write(
                        f"**Customer:** {customer_name}"
                    )

                    st.write(
                        f"**Phone:** {customer_phone or 'Not available'}"
                    )

                    st.write(
                        f"**City:** {customer_city or 'Not available'}"
                    )

                with bill_col2:

                    st.write(
                        f"**Plant:** {plant_name}"
                    )

                    st.write(
                        f"**Category:** {category or 'N/A'}"
                    )

                    st.write(
                        f"**Quantity:** {quantity}"
                    )

                    st.write(
                        f"**Date:** {pd.Timestamp.now().strftime('%d-%m-%Y')}"
                    )

                st.divider()

                bill_data = pd.DataFrame(
                    [
                        {
                            "Plant": plant_name,
                            "Quantity": quantity,
                            "Unit Price": f"₹{price:.2f}",
                            "Total": f"₹{total:.2f}"
                        }
                    ]
                )

                st.table(
                    bill_data
                )

                st.success(
                    f"💰 **Grand Total: ₹{total:.2f}**"
                )

                new_stock = latest_stock - quantity

                st.info(
                    f"📦 Remaining stock for {plant_name}: "
                    f"**{new_stock}**"
                )

                # -------------------------------------------------
                # Refresh application
                # -------------------------------------------------

                st.button(
                    "🔄 Refresh Billing",
                    on_click=st.rerun
                )

            except Exception as e:

                connection.rollback()

                st.error(
                    f"❌ Billing error: {e}"
                )

            finally:

                cursor.close()

    except Exception as e:

        st.error(
            f"❌ Unable to load billing information: {e}"
        )

    finally:

        connection.close()
