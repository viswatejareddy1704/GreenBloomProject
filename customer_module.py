import streamlit as st
import pandas as pd

from db_connection import get_connection


# ============================================================
# DATABASE HELPER
# ============================================================

def fetch_dataframe(query, params=None):

    connection = None
    cursor = None

    try:

        connection = get_connection()

        cursor = connection.cursor(
            dictionary=True
        )

        cursor.execute(
            query,
            params or ()
        )

        data = cursor.fetchall()

        return pd.DataFrame(data)

    except Exception as e:

        st.error(
            f"Database error: {e}"
        )

        return pd.DataFrame()

    finally:

        if cursor:
            cursor.close()

        if connection:
            connection.close()


# ============================================================
# CUSTOMER STATISTICS
# ============================================================

def get_customer_statistics():

    customers = fetch_dataframe(
        """
        SELECT
            customer_id,
            customer_name,
            phone,
            city
        FROM customers
        ORDER BY customer_id
        """
    )

    if customers.empty:

        return customers, 0, 0

    total_customers = len(
        customers
    )

    total_cities = (
        customers["city"]
        .fillna("")
        .astype(str)
        .str.strip()
        .replace("", pd.NA)
        .nunique()
    )

    return (
        customers,
        total_customers,
        total_cities
    )


# ============================================================
# CUSTOMER MANAGEMENT
# ============================================================

def customer_management():

    # --------------------------------------------------------
    # HEADER
    # --------------------------------------------------------

    st.title("👤 Customer Management")

    st.write(
        "Manage customer details and purchase history."
    )

    st.divider()


    # --------------------------------------------------------
    # LOAD CUSTOMERS
    # --------------------------------------------------------

    customers, total_customers, total_cities = (
        get_customer_statistics()
    )


    # --------------------------------------------------------
    # STATISTICS
    # --------------------------------------------------------

    col1, col2, col3 = st.columns(3)

    with col1:

        st.metric(
            "👥 Total Customers",
            total_customers
        )

    with col2:

        st.metric(
            "🏙️ Cities",
            total_cities
        )

    with col3:

        st.metric(
            "📋 Customer Records",
            total_customers
        )


    st.divider()


    # --------------------------------------------------------
    # ACTION MENU
    # --------------------------------------------------------

    option = st.selectbox(
        "Choose an action",
        [
            "View Customers",
            "Add Customer",
            "Update Customer",
            "Delete Customer",
            "Purchase History"
        ]
    )


    # --------------------------------------------------------
    # ROUTING
    # --------------------------------------------------------

    if option == "View Customers":

        view_customers(
            customers
        )

    elif option == "Add Customer":

        add_customer()

    elif option == "Update Customer":

        update_customer(
            customers
        )

    elif option == "Delete Customer":

        delete_customer(
            customers
        )

    elif option == "Purchase History":

        purchase_history()


# ============================================================
# VIEW CUSTOMERS
# ============================================================

def view_customers(customers=None):

    st.subheader(
        "👥 All Customers"
    )

    if customers is None:

        customers = fetch_dataframe(
            """
            SELECT
                customer_id,
                customer_name,
                phone,
                city
            FROM customers
            ORDER BY customer_id
            """
        )


    if customers.empty:

        st.info(
            "No customers found. Add your first customer."
        )

        return


    # --------------------------------------------------------
    # CUSTOMER CARDS
    # --------------------------------------------------------

    st.subheader(
        "📇 Customer Directory"
    )


    for start in range(
        0,
        len(customers),
        3
    ):

        columns = st.columns(3)

        row = customers.iloc[
            start:start + 3
        ]


        for column, (_, customer) in zip(
            columns,
            row.iterrows()
        ):

            with column:

                with st.container(
                    border=True
                ):

                    st.markdown(
                        f"### 👤 {customer['customer_name']}"
                    )

                    st.write(
                        f"**Customer ID:** "
                        f"{customer['customer_id']}"
                    )

                    st.write(
                        f"**📞 Phone:** "
                        f"{customer['phone'] or 'Not provided'}"
                    )

                    st.write(
                        f"**🏙️ City:** "
                        f"{customer['city'] or 'Not provided'}"
                    )


    st.divider()


    # --------------------------------------------------------
    # CUSTOMER TABLE
    # --------------------------------------------------------

    st.subheader(
        "📋 Customer Details"
    )

    st.dataframe(
        customers,
        width="stretch",
        hide_index=True
    )


# ============================================================
# ADD CUSTOMER
# ============================================================

def add_customer():

    st.subheader(
        "➕ Add New Customer"
    )

    st.caption(
        "Enter the customer's basic information."
    )


    with st.form(
        "add_customer_form",
        clear_on_submit=True
    ):

        col1, col2 = st.columns(2)


        with col1:

            name = st.text_input(
                "Customer Name",
                placeholder="Example: Ravi Kumar"
            )

        with col2:

            phone = st.text_input(
                "Phone",
                placeholder="Example: 9876543210"
            )


        city = st.text_input(
            "City",
            placeholder="Example: Nandyal"
        )


        st.divider()


        submitted = st.form_submit_button(
            "➕ Add Customer",
            type="primary",
            width="stretch"
        )


    if submitted:

        name = name.strip()
        phone = phone.strip()
        city = city.strip()


        # ----------------------------------------------------
        # VALIDATION
        # ----------------------------------------------------

        if not name:

            st.error(
                "Please enter the customer name."
            )

            return


        if not phone:

            st.error(
                "Please enter the phone number."
            )

            return


        if not city:

            st.error(
                "Please enter the city."
            )

            return


        if not phone.isdigit():

            st.error(
                "Phone number should contain only digits."
            )

            return


        if len(phone) != 10:

            st.error(
                "Phone number must contain 10 digits."
            )

            return


        # ----------------------------------------------------
        # DATABASE
        # ----------------------------------------------------

        connection = None
        cursor = None

        try:

            connection = get_connection()

            cursor = connection.cursor()


            cursor.execute(
                """
                INSERT INTO customers
                (
                    customer_name,
                    phone,
                    city
                )
                VALUES
                (%s, %s, %s)
                """,
                (
                    name,
                    phone,
                    city
                )
            )


            connection.commit()


            st.success(
                f"👤 {name} added successfully!"
            )

            st.rerun()


        except Exception as e:

            if connection:

                connection.rollback()

            st.error(
                f"Database error: {e}"
            )


        finally:

            if cursor:

                cursor.close()

            if connection:

                connection.close()


# ============================================================
# UPDATE CUSTOMER
# ============================================================

def update_customer(customers=None):

    st.subheader(
        "✏️ Update Customer"
    )


    if customers is None:

        customers = fetch_dataframe(
            """
            SELECT
                customer_id,
                customer_name,
                phone,
                city
            FROM customers
            ORDER BY customer_id
            """
        )


    if customers.empty:

        st.info(
            "No customers found."
        )

        return


    # --------------------------------------------------------
    # SELECT CUSTOMER
    # --------------------------------------------------------

    customer_options = {}

    for _, customer in customers.iterrows():

        label = (
            f"{customer['customer_name']} "
            f"(ID: {customer['customer_id']})"
        )

        customer_options[label] = customer


    selected_label = st.selectbox(
        "Select Customer",
        list(customer_options.keys())
    )


    selected_customer = customer_options[
        selected_label
    ]


    st.divider()


    with st.form(
        "update_customer_form"
    ):

        col1, col2 = st.columns(2)


        with col1:

            new_name = st.text_input(
                "Customer Name",
                value=str(
                    selected_customer[
                        "customer_name"
                    ] or ""
                )
            )

            new_phone = st.text_input(
                "Phone",
                value=str(
                    selected_customer[
                        "phone"
                    ] or ""
                )
            )


        with col2:

            new_city = st.text_input(
                "City",
                value=str(
                    selected_customer[
                        "city"
                    ] or ""
                )
            )

            st.text_input(
                "Customer ID",
                value=str(
                    selected_customer[
                        "customer_id"
                    ]
                ),
                disabled=True
            )


        st.divider()


        update_button = st.form_submit_button(
            "💾 Update Customer",
            type="primary",
            width="stretch"
        )


    if update_button:

        new_name = new_name.strip()
        new_phone = new_phone.strip()
        new_city = new_city.strip()


        # ----------------------------------------------------
        # VALIDATION
        # ----------------------------------------------------

        if not new_name:

            st.error(
                "Customer name cannot be empty."
            )

            return


        if not new_phone:

            st.error(
                "Phone number cannot be empty."
            )

            return


        if not new_phone.isdigit():

            st.error(
                "Phone number should contain only digits."
            )

            return


        if len(new_phone) != 10:

            st.error(
                "Phone number must contain 10 digits."
            )

            return


        if not new_city:

            st.error(
                "City cannot be empty."
            )

            return


        # ----------------------------------------------------
        # UPDATE DATABASE
        # ----------------------------------------------------

        connection = None
        cursor = None

        try:

            connection = get_connection()

            cursor = connection.cursor()


            cursor.execute(
                """
                UPDATE customers
                SET
                    customer_name = %s,
                    phone = %s,
                    city = %s
                WHERE customer_id = %s
                """,
                (
                    new_name,
                    new_phone,
                    new_city,
                    int(
                        selected_customer[
                            "customer_id"
                        ]
                    )
                )
            )


            connection.commit()


            st.success(
                f"👤 {new_name} updated successfully!"
            )

            st.rerun()


        except Exception as e:

            if connection:

                connection.rollback()

            st.error(
                f"Database error: {e}"
            )


        finally:

            if cursor:

                cursor.close()

            if connection:

                connection.close()


# ============================================================
# DELETE CUSTOMER
# ============================================================

def delete_customer(customers=None):

    st.subheader(
        "🗑️ Delete Customer"
    )


    if customers is None:

        customers = fetch_dataframe(
            """
            SELECT
                customer_id,
                customer_name,
                phone,
                city
            FROM customers
            ORDER BY customer_id
            """
        )


    if customers.empty:

        st.info(
            "No customers found."
        )

        return


    # --------------------------------------------------------
    # SELECT CUSTOMER
    # --------------------------------------------------------

    customer_options = {}

    for _, customer in customers.iterrows():

        label = (
            f"{customer['customer_name']} "
            f"(ID: {customer['customer_id']})"
        )

        customer_options[label] = customer


    selected_label = st.selectbox(
        "Select Customer to Delete",
        list(customer_options.keys())
    )


    selected_customer = customer_options[
        selected_label
    ]


    st.divider()


    # --------------------------------------------------------
    # CUSTOMER DETAILS
    # --------------------------------------------------------

    col1, col2 = st.columns(2)


    with col1:

        st.warning(
            f"You are about to delete "
            f"**{selected_customer['customer_name']}**."
        )

        st.write(
            f"**Customer ID:** "
            f"{selected_customer['customer_id']}"
        )

        st.write(
            f"**📞 Phone:** "
            f"{selected_customer['phone'] or 'Not provided'}"
        )

        st.write(
            f"**🏙️ City:** "
            f"{selected_customer['city'] or 'Not provided'}"
        )


    with col2:

        with st.container(
            border=True
        ):

            st.markdown(
                "### ⚠️ Warning"
            )

            st.write(
                "Deleting this customer will permanently "
                "remove the customer record."
            )

            st.write(
                "Purchase records in the sales table "
                "are not automatically removed."
            )


    st.divider()


    confirm = st.checkbox(
        "I understand that this customer will be permanently deleted."
    )


    if st.button(
        "🗑️ Delete Customer",
        type="primary",
        width="stretch"
    ):

        if not confirm:

            st.error(
                "Please confirm the deletion first."
            )

            return


        connection = None
        cursor = None

        try:

            connection = get_connection()

            cursor = connection.cursor()


            cursor.execute(
                """
                DELETE FROM customers
                WHERE customer_id = %s
                """,
                (
                    int(
                        selected_customer[
                            "customer_id"
                        ]
                    ),
                )
            )


            connection.commit()


            st.success(
                f"👤 {selected_customer['customer_name']} "
                "deleted successfully!"
            )

            st.rerun()


        except Exception as e:

            if connection:

                connection.rollback()

            st.error(
                f"Database error: {e}"
            )


        finally:

            if cursor:

                cursor.close()

            if connection:

                connection.close()


# ============================================================
# PURCHASE HISTORY
# ============================================================

def purchase_history():

    st.subheader(
        "📜 Customer Purchase History"
    )

    st.caption(
        "View previous purchases made by a customer."
    )


    # --------------------------------------------------------
    # CUSTOMER LIST
    # --------------------------------------------------------

    customers = fetch_dataframe(
        """
        SELECT
            customer_id,
            customer_name
        FROM customers
        ORDER BY customer_name
        """
    )


    if customers.empty:

        st.info(
            "No customers found."
        )

        return


    customer_options = {}

    for _, customer in customers.iterrows():

        label = (
            f"{customer['customer_name']} "
            f"(ID: {customer['customer_id']})"
        )

        customer_options[label] = customer[
            "customer_name"
        ]


    selected_label = st.selectbox(
        "Select Customer",
        list(customer_options.keys())
    )


    customer = customer_options[
        selected_label
    ]


    st.divider()


    # --------------------------------------------------------
    # PURCHASE HISTORY
    # --------------------------------------------------------

    history = fetch_dataframe(
        """
        SELECT
            sale_id,
            customer_name,
            plant_name,
            quantity,
            total_amount,
            sale_date
        FROM sales
        WHERE customer_name = %s
        ORDER BY sale_date DESC, sale_id DESC
        """,
        (customer,)
    )


    if history.empty:

        st.info(
            f"No purchases found for {customer}."
        )

        return


    # --------------------------------------------------------
    # PURCHASE METRICS
    # --------------------------------------------------------

    total_orders = len(
        history
    )

    total_items = int(
        pd.to_numeric(
            history["quantity"],
            errors="coerce"
        ).fillna(0).sum()
    )

    total_spent = (
        pd.to_numeric(
            history["total_amount"],
            errors="coerce"
        ).fillna(0).sum()
    )


    col1, col2, col3 = st.columns(3)


    with col1:

        st.metric(
            "🧾 Purchases",
            total_orders
        )


    with col2:

        st.metric(
            "🌱 Plants Purchased",
            total_items
        )


    with col3:

        st.metric(
            "💰 Total Spent",
            f"₹{total_spent:,.2f}"
        )


    st.divider()


    # --------------------------------------------------------
    # FORMAT TABLE
    # --------------------------------------------------------

    display_history = history.copy()


    if "total_amount" in display_history.columns:

        display_history["total_amount"] = (
            display_history[
                "total_amount"
            ]
            .apply(
                lambda value:
                f"₹{float(value):,.2f}"
            )
        )


    st.dataframe(
        display_history,
        width="stretch",
        hide_index=True
    )
