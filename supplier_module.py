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

        cursor = connection.cursor(dictionary=True)

        cursor.execute(
            query,
            params or ()
        )

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


# ============================================================
# SUPPLIER STATISTICS
# ============================================================

def get_supplier_statistics():

    suppliers = fetch_dataframe(
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

    if suppliers.empty:

        return suppliers, 0, 0

    total_suppliers = len(suppliers)

    total_cities = suppliers["city"].fillna(
        ""
    ).astype(str).str.strip().replace(
        "",
        pd.NA
    ).nunique()

    return (
        suppliers,
        total_suppliers,
        total_cities
    )


# ============================================================
# SUPPLIER MANAGEMENT
# ============================================================

def supplier_management():

    # --------------------------------------------------------
    # HEADER
    # --------------------------------------------------------

    st.title("🚚 Supplier Management")

    st.write(
        "Manage nursery suppliers and their contact information."
    )

    st.divider()


    # --------------------------------------------------------
    # LOAD DATA
    # --------------------------------------------------------

    suppliers, total_suppliers, total_cities = (
        get_supplier_statistics()
    )


    # --------------------------------------------------------
    # STATISTICS
    # --------------------------------------------------------

    col1, col2, col3 = st.columns(3)

    with col1:

        st.metric(
            "🚚 Total Suppliers",
            total_suppliers
        )

    with col2:

        st.metric(
            "🏙️ Cities",
            total_cities
        )

    with col3:

        st.metric(
            "📋 Supplier Records",
            total_suppliers
        )


    st.divider()


    # --------------------------------------------------------
    # ACTION
    # --------------------------------------------------------

    option = st.selectbox(
        "Choose an action",
        [
            "View Suppliers",
            "Add Supplier",
            "Update Supplier",
            "Delete Supplier"
        ]
    )


    # --------------------------------------------------------
    # ROUTING
    # --------------------------------------------------------

    if option == "View Suppliers":

        view_suppliers(
            suppliers
        )

    elif option == "Add Supplier":

        add_supplier()

    elif option == "Update Supplier":

        update_supplier(
            suppliers
        )

    elif option == "Delete Supplier":

        delete_supplier(
            suppliers
        )


# ============================================================
# VIEW SUPPLIERS
# ============================================================

def view_suppliers(suppliers=None):

    st.subheader(
        "🚚 All Suppliers"
    )

    if suppliers is None:

        suppliers = fetch_dataframe(
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


    if suppliers.empty:

        st.info(
            "No suppliers found. Add your first supplier."
        )

        return


    # --------------------------------------------------------
    # SUPPLIER CARDS
    # --------------------------------------------------------

    st.subheader(
        "📇 Supplier Directory"
    )


    for start in range(
        0,
        len(suppliers),
        3
    ):

        columns = st.columns(3)

        row = suppliers.iloc[
            start:start + 3
        ]


        for column, (_, supplier) in zip(
            columns,
            row.iterrows()
        ):

            with column:

                with st.container(
                    border=True
                ):

                    st.markdown(
                        f"### 🚚 {supplier['supplier_name']}"
                    )

                    st.write(
                        f"**Supplier ID:** "
                        f"{supplier['supplier_id']}"
                    )

                    st.write(
                        f"**📞 Phone:** "
                        f"{supplier['phone'] or 'Not provided'}"
                    )

                    st.write(
                        f"**🏙️ City:** "
                        f"{supplier['city'] or 'Not provided'}"
                    )


    st.divider()


    # --------------------------------------------------------
    # SUPPLIER TABLE
    # --------------------------------------------------------

    st.subheader(
        "📋 Supplier Details"
    )

    st.dataframe(
        suppliers,
        width="stretch",
        hide_index=True
    )


# ============================================================
# ADD SUPPLIER
# ============================================================

def add_supplier():

    st.subheader(
        "➕ Add New Supplier"
    )

    st.caption(
        "Enter the supplier's basic contact information."
    )


    with st.form(
        "add_supplier_form",
        clear_on_submit=True
    ):

        col1, col2 = st.columns(2)


        with col1:

            supplier_id = st.text_input(
                "Supplier ID",
                placeholder="Example: SUP001"
            )

            supplier_name = st.text_input(
                "Supplier Name",
                placeholder="Example: Green Nursery"
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
            "➕ Add Supplier",
            type="primary",
            width="stretch"
        )


    if submitted:

        # ----------------------------------------------------
        # VALIDATION
        # ----------------------------------------------------

        supplier_id = supplier_id.strip()
        supplier_name = supplier_name.strip()
        phone = phone.strip()
        city = city.strip()


        if not supplier_id:

            st.error(
                "Please enter a Supplier ID."
            )

            return


        if not supplier_name:

            st.error(
                "Please enter the Supplier Name."
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


        # ----------------------------------------------------
        # PHONE VALIDATION
        # ----------------------------------------------------

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


            # Check duplicate ID
            cursor.execute(
                """
                SELECT supplier_id
                FROM suppliers
                WHERE supplier_id = %s
                """,
                (supplier_id,)
            )

            existing = cursor.fetchone()


            if existing:

                st.error(
                    "Supplier ID already exists."
                )

                return


            cursor.execute(
                """
                INSERT INTO suppliers
                (
                    supplier_id,
                    supplier_name,
                    phone,
                    city
                )
                VALUES
                (%s, %s, %s, %s)
                """,
                (
                    supplier_id,
                    supplier_name,
                    phone,
                    city
                )
            )

            connection.commit()


            st.success(
                f"🚚 {supplier_name} added successfully!"
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
# UPDATE SUPPLIER
# ============================================================

def update_supplier(suppliers=None):

    st.subheader(
        "✏️ Update Supplier"
    )


    if suppliers is None:

        suppliers = fetch_dataframe(
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


    if suppliers.empty:

        st.info(
            "No suppliers found."
        )

        return


    # --------------------------------------------------------
    # SELECT SUPPLIER
    # --------------------------------------------------------

    supplier_options = {}

    for _, supplier in suppliers.iterrows():

        label = (
            f"{supplier['supplier_name']} "
            f"(ID: {supplier['supplier_id']})"
        )

        supplier_options[label] = supplier


    selected_label = st.selectbox(
        "Select Supplier",
        list(supplier_options.keys())
    )


    selected_supplier = supplier_options[
        selected_label
    ]


    st.divider()


    with st.form(
        "update_supplier_form"
    ):

        col1, col2 = st.columns(2)


        with col1:

            new_name = st.text_input(
                "Supplier Name",
                value=str(
                    selected_supplier[
                        "supplier_name"
                    ] or ""
                )
            )

            new_phone = st.text_input(
                "Phone",
                value=str(
                    selected_supplier[
                        "phone"
                    ] or ""
                )
            )


        with col2:

            new_city = st.text_input(
                "City",
                value=str(
                    selected_supplier[
                        "city"
                    ] or ""
                )
            )

            st.text_input(
                "Supplier ID",
                value=str(
                    selected_supplier[
                        "supplier_id"
                    ]
                ),
                disabled=True
            )


        st.divider()


        update_button = st.form_submit_button(
            "💾 Update Supplier",
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
                "Supplier name cannot be empty."
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
                UPDATE suppliers
                SET
                    supplier_name = %s,
                    phone = %s,
                    city = %s
                WHERE supplier_id = %s
                """,
                (
                    new_name,
                    new_phone,
                    new_city,
                    selected_supplier[
                        "supplier_id"
                    ]
                )
            )


            connection.commit()


            st.success(
                f"🚚 {new_name} updated successfully!"
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
# DELETE SUPPLIER
# ============================================================

def delete_supplier(suppliers=None):

    st.subheader(
        "🗑️ Delete Supplier"
    )


    if suppliers is None:

        suppliers = fetch_dataframe(
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


    if suppliers.empty:

        st.info(
            "No suppliers found."
        )

        return


    # --------------------------------------------------------
    # SELECT SUPPLIER
    # --------------------------------------------------------

    supplier_options = {}

    for _, supplier in suppliers.iterrows():

        label = (
            f"{supplier['supplier_name']} "
            f"(ID: {supplier['supplier_id']})"
        )

        supplier_options[label] = supplier


    selected_label = st.selectbox(
        "Select Supplier to Delete",
        list(supplier_options.keys())
    )


    selected_supplier = supplier_options[
        selected_label
    ]


    st.divider()


    # --------------------------------------------------------
    # SUPPLIER DETAILS
    # --------------------------------------------------------

    col1, col2 = st.columns(2)


    with col1:

        st.warning(
            f"You are about to delete "
            f"**{selected_supplier['supplier_name']}**."
        )

        st.write(
            f"**Supplier ID:** "
            f"{selected_supplier['supplier_id']}"
        )

        st.write(
            f"**📞 Phone:** "
            f"{selected_supplier['phone'] or 'Not provided'}"
        )

        st.write(
            f"**🏙️ City:** "
            f"{selected_supplier['city'] or 'Not provided'}"
        )


    with col2:

        with st.container(
            border=True
        ):

            st.markdown(
                "### ⚠️ Warning"
            )

            st.write(
                "Deleting this supplier will permanently "
                "remove the supplier record from the database."
            )

            st.write(
                "Please confirm before continuing."
            )


    st.divider()


    confirm = st.checkbox(
        "I understand that this supplier will be permanently deleted."
    )


    if st.button(
        "🗑️ Delete Supplier",
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
                DELETE FROM suppliers
                WHERE supplier_id = %s
                """,
                (
                    selected_supplier[
                        "supplier_id"
                    ],
                )
            )


            connection.commit()


            st.success(
                f"🚚 {selected_supplier['supplier_name']} "
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
