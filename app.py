import streamlit as st
import pandas as pd
from datetime import date
from pathlib import Path
from PIL import Image, UnidentifiedImageError

from db_connection import get_connection


# =========================================================
# PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="Green Bloom Plants",
    page_icon="🌱",
    layout="wide"
)


# =========================================================
# IMAGE CONFIGURATION
# =========================================================

BASE_DIR = Path(__file__).resolve().parent

# Your folder is named Images
IMAGE_DIR = BASE_DIR / "Images"

# EXACT image names from your Images folder
plant_images = {
    "tulsi": "Tulsi.jpg",
    "aloe vera": "Aloe vera.jpg",
    "money plant": "Money Plant.jpg",
    "jasmine": "Jasmine.jpg",
    "rose": "rose.jpg",
    "tulips": "Tulips.jpg",
    "tulis": "Tulips.jpg"
}


# =========================================================
# DISPLAY PLANT IMAGE
# =========================================================

def get_uploaded_image_path(plant_name):

    """Find an image uploaded for a plant name.

    Existing fixed image names are checked first. If no fixed
    mapping exists, the Images folder is searched by filename
    (case-insensitive) and supported image extension.
    """

    clean_name = str(plant_name).strip()
    lower_name = clean_name.lower()

    # First use the existing fixed image mapping.
    image_file = plant_images.get(lower_name)

    if image_file:
        image_path = IMAGE_DIR / image_file
        if image_path.exists():
            return image_path

    # Then look for images uploaded using the plant name.
    if IMAGE_DIR.exists():
        for path in IMAGE_DIR.iterdir():
            if not path.is_file():
                continue

            if path.suffix.lower() not in [".jpg", ".jpeg", ".png"]:
                continue

            if path.stem.strip().lower() == lower_name:
                return path

    return None


def display_plant_image(plant_name):

    image_path = get_uploaded_image_path(plant_name)

    if image_path is None:
        st.info(
            f"No image assigned for {plant_name}"
        )
        return

    try:
        with Image.open(image_path) as img:
            img.load()
            valid_image = img.convert("RGB").copy()

        st.image(
            valid_image,
            use_container_width=True
        )

    except (
        UnidentifiedImageError,
        OSError,
        ValueError
    ):
        st.error(
            f"Invalid image file: {image_path.name}"
        )


# =========================================================
# FETCH DATA FROM MYSQL
# =========================================================

def fetch_dataframe(
    query,
    params=None
):

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

        return pd.DataFrame(
            data
        )

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


# =========================================================
# INSERT / UPDATE / DELETE
# =========================================================

def execute_query(
    query,
    params=None
):

    connection = None
    cursor = None

    try:

        connection = get_connection()

        cursor = connection.cursor()

        cursor.execute(
            query,
            params or ()
        )

        connection.commit()

        return True

    except Exception as e:

        if connection:
            connection.rollback()

        st.error(
            f"Database error: {e}"
        )

        return False

    finally:

        if cursor:
            cursor.close()

        if connection:
            connection.close()


# =========================================================
# HOME PAGE
# =========================================================

def home_page():

    st.title(
        "🌱 Green Bloom Plants"
    )

    st.write(
        "Manage plants, suppliers, customers, "
        "billing, stock and sales reports."
    )

    st.subheader(
        "🌿 Available Plants"
    )

    df = fetch_dataframe(
        """
        SELECT *
        FROM plants
        ORDER BY plant_id
        """
    )

    if df.empty:

        st.info(
            "No plants available."
        )

        return

    # Create 3 columns
    columns = st.columns(3)

    for index, row in df.iterrows():

        plant_name = str(
            row["plant_name"]
        ).strip()

        with columns[index % 3]:

            # Display image
            display_plant_image(
                plant_name
            )

            # Plant name
            st.markdown(
                f"### {plant_name}"
            )

            # Price
            st.write(
                f"**Price:** ₹{row['price']}"
            )

            # Stock
            st.write(
                f"**Stock:** {row['quantity']}"
            )

            # Category
            st.write(
                f"**Category:** {row['category']}"
            )

            # Supplier
            st.write(
                f"**Supplier:** {row['supplier_name']}"
            )

            st.divider()


# =========================================================
# PLANT MANAGEMENT
# =========================================================

def plant_management():

    st.header(
        "🌿 Plant Management"
    )

    option = st.sidebar.radio(
        "Plant Options",
        [
            "View Plants",
            "Add Plant",
            "Update Plant",
            "Delete Plant",
            "Search Plant"
        ]
    )

    # =====================================================
    # VIEW PLANTS
    # =====================================================

    if option == "View Plants":

        st.subheader(
            "🌱 Available Plants"
        )

        df = fetch_dataframe(
            """
            SELECT *
            FROM plants
            ORDER BY plant_id
            """
        )

        if df.empty:

            st.info(
                "No plants found."
            )

            return

        # 3 columns
        columns = st.columns(3)

        for index, row in df.iterrows():

            plant_name = str(
                row["plant_name"]
            ).strip()

            with columns[index % 3]:

                display_plant_image(
                    plant_name
                )

                st.markdown(
                    f"### {plant_name}"
                )

                st.write(
                    f"**Price:** ₹{row['price']}"
                )

                st.write(
                    f"**Stock:** {row['quantity']}"
                )

                st.write(
                    f"**Category:** {row['category']}"
                )

                st.write(
                    f"**Supplier:** {row['supplier_name']}"
                )

                st.divider()

        st.subheader(
            "📋 Plant Table"
        )

        st.dataframe(
            df,
            use_container_width=True
        )

    # =====================================================
    # ADD PLANT
    # =====================================================

    elif option == "Add Plant":

        st.subheader(
            "➕ Add New Plant"
        )

        st.write(
            "Enter the plant details and upload an image for the new plant."
        )

        col1, col2 = st.columns(2)

        with col1:

            plant_id = st.number_input(
                "Plant ID",
                min_value=1,
                step=1
            )

            plant_name = st.text_input(
                "Plant Name"
            )

            category = st.text_input(
                "Category"
            )

            price = st.number_input(
                "Price",
                min_value=0.0,
                step=10.0
            )

            quantity = st.number_input(
                "Quantity",
                min_value=0,
                step=1
            )

            supplier_name = st.text_input(
                "Supplier Name"
            )

        with col2:

            st.markdown("### 📷 Plant Image")

            uploaded_image = st.file_uploader(
                "Upload Plant Image",
                type=["jpg", "jpeg", "png"],
                help="Upload a JPG, JPEG, or PNG image of the plant."
            )

            if uploaded_image is not None:

                try:
                    preview_image = Image.open(uploaded_image)
                    st.image(
                        preview_image,
                        caption="Image Preview",
                        use_container_width=True
                    )
                except Exception:
                    st.error(
                        "The selected file is not a valid image."
                    )

        if st.button(
            "Add Plant",
            type="primary"
        ):

            if not plant_name.strip():

                st.warning(
                    "Please enter plant name."
                )

            elif uploaded_image is None:

                st.warning(
                    "Please upload an image for the plant."
                )

            else:

                # Check whether the Plant ID already exists.
                existing_plant = fetch_dataframe(
                    "SELECT plant_id FROM plants WHERE plant_id = %s",
                    (plant_id,)
                )

                if not existing_plant.empty:

                    st.error(
                        "This Plant ID already exists. Please enter a different ID."
                    )

                else:

                    success = execute_query(
                        """
                        INSERT INTO plants
                        (
                            plant_id,
                            plant_name,
                            category,
                            price,
                            quantity,
                            supplier_name
                        )
                        VALUES
                        (
                            %s,
                            %s,
                            %s,
                            %s,
                            %s,
                            %s
                        )
                        """,
                        (
                            plant_id,
                            plant_name.strip(),
                            category.strip(),
                            price,
                            quantity,
                            supplier_name.strip()
                        )
                    )

                    if success:

                        try:

                            IMAGE_DIR.mkdir(
                                parents=True,
                                exist_ok=True
                            )

                            # Keep the plant name in the image filename.
                            safe_name = "".join(
                                character
                                if character.isalnum() or character in " _-"
                                else "_"
                                for character in plant_name.strip()
                            ).strip()

                            if not safe_name:
                                safe_name = f"plant_{plant_id}"

                            extension = Path(
                                uploaded_image.name
                            ).suffix.lower()

                            image_path = IMAGE_DIR / (
                                f"{safe_name}{extension}"
                            )

                            with open(
                                image_path,
                                "wb"
                            ) as image_file:
                                image_file.write(
                                    uploaded_image.getbuffer()
                                )

                            st.success(
                                "Plant added successfully!"
                            )

                            st.success(
                                f"Image saved as: {image_path.name}"
                            )

                            st.image(
                                image_path,
                                caption=plant_name.strip(),
                                use_container_width=True
                            )

                        except Exception as image_error:

                            st.warning(
                                "Plant was added, but the image could not be saved. "
                                f"Error: {image_error}"
                            )

    # =====================================================
    # UPDATE PLANT
    # =====================================================

    elif option == "Update Plant":

        st.subheader(
            "✏️ Update Plant"
        )

        plant_id = st.number_input(
            "Plant ID",
            min_value=1,
            step=1
        )

        new_name = st.text_input(
            "New Plant Name"
        )

        new_category = st.text_input(
            "New Category"
        )

        new_price = st.number_input(
            "New Price",
            min_value=0.0,
            step=10.0
        )

        new_quantity = st.number_input(
            "New Quantity",
            min_value=0,
            step=1
        )

        new_supplier = st.text_input(
            "New Supplier Name"
        )

        if st.button(
            "Update Plant"
        ):

            success = execute_query(
                """
                UPDATE plants
                SET
                    plant_name = %s,
                    category = %s,
                    price = %s,
                    quantity = %s,
                    supplier_name = %s
                WHERE plant_id = %s
                """,
                (
                    new_name,
                    new_category,
                    new_price,
                    new_quantity,
                    new_supplier,
                    plant_id
                )
            )

            if success:

                st.success(
                    "Plant updated successfully."
                )

    # =====================================================
    # DELETE PLANT
    # =====================================================

    elif option == "Delete Plant":

        st.subheader(
            "🗑️ Delete Plant"
        )

        plant_id = st.number_input(
            "Plant ID",
            min_value=1,
            step=1
        )

        if st.button(
            "Delete Plant"
        ):

            success = execute_query(
                """
                DELETE FROM plants
                WHERE plant_id = %s
                """,
                (plant_id,)
            )

            if success:

                st.success(
                    "Plant deleted successfully."
                )

    # =====================================================
    # SEARCH PLANT
    # =====================================================

    elif option == "Search Plant":

        st.subheader(
            "🔍 Search Plant"
        )

        search_name = st.text_input(
            "Enter Plant Name"
        )

        if st.button(
            "Search"
        ):

            df = fetch_dataframe(
                """
                SELECT *
                FROM plants
                WHERE plant_name LIKE %s
                """,
                (
                    f"%{search_name}%",
                )
            )

            if df.empty:

                st.warning(
                    "Plant not found."
                )

            else:

                st.dataframe(
                    df,
                    use_container_width=True
                )


# =========================================================
# SUPPLIER MANAGEMENT
# =========================================================

def supplier_management():

    st.header(
        "🚚 Supplier Management"
    )

    option = st.sidebar.radio(
        "Supplier Options",
        [
            "View Suppliers",
            "Add Supplier",
            "Update Supplier",
            "Delete Supplier"
        ]
    )

    # =====================================================
    # VIEW SUPPLIERS
    # =====================================================

    if option == "View Suppliers":

        st.subheader(
            "Supplier List"
        )

        df = fetch_dataframe(
            "SELECT * FROM suppliers"
        )

        if df.empty:

            st.info(
                "No suppliers found."
            )

        else:

            st.dataframe(
                df,
                use_container_width=True
            )

    # =====================================================
    # ADD SUPPLIER
    # =====================================================

    elif option == "Add Supplier":

        st.subheader(
            "➕ Add Supplier"
        )

        supplier_id = st.text_input(
            "Supplier ID"
        )

        supplier_name = st.text_input(
            "Supplier Name"
        )

        phone = st.text_input(
            "Phone"
        )

        city = st.text_input(
            "City"
        )

        if st.button(
            "Add Supplier"
        ):

            success = execute_query(
                """
                INSERT INTO suppliers
                (
                    supplier_id,
                    supplier_name,
                    phone,
                    city
                )
                VALUES
                (
                    %s,
                    %s,
                    %s,
                    %s
                )
                """,
                (
                    supplier_id,
                    supplier_name,
                    phone,
                    city
                )
            )

            if success:

                st.success(
                    "Supplier added successfully."
                )

    # =====================================================
    # UPDATE SUPPLIER
    # =====================================================

    elif option == "Update Supplier":

        st.subheader(
            "✏️ Update Supplier"
        )

        supplier_id = st.text_input(
            "Supplier ID"
        )

        supplier_name = st.text_input(
            "New Supplier Name"
        )

        phone = st.text_input(
            "New Phone"
        )

        city = st.text_input(
            "New City"
        )

        if st.button(
            "Update Supplier"
        ):

            success = execute_query(
                """
                UPDATE suppliers
                SET
                    supplier_name = %s,
                    phone = %s,
                    city = %s
                WHERE supplier_id = %s
                """,
                (
                    supplier_name,
                    phone,
                    city,
                    supplier_id
                )
            )

            if success:

                st.success(
                    "Supplier updated successfully."
                )

    # =====================================================
    # DELETE SUPPLIER
    # =====================================================

    elif option == "Delete Supplier":

        st.subheader(
            "🗑️ Delete Supplier"
        )

        supplier_id = st.text_input(
            "Supplier ID"
        )

        if st.button(
            "Delete Supplier"
        ):

            success = execute_query(
                """
                DELETE FROM suppliers
                WHERE supplier_id = %s
                """,
                (supplier_id,)
            )

            if success:

                st.success(
                    "Supplier deleted successfully."
                )


# =========================================================
# CUSTOMER MANAGEMENT
# =========================================================

def customer_management():

    st.header(
        "👤 Customer Management"
    )

    option = st.sidebar.radio(
        "Customer Options",
        [
            "View Customers",
            "Add Customer",
            "Purchase History",
            "Track Purchases"
        ]
    )

    # =====================================================
    # VIEW CUSTOMERS
    # =====================================================

    if option == "View Customers":

        st.subheader(
            "Customer List"
        )

        df = fetch_dataframe(
            "SELECT * FROM customers"
        )

        if df.empty:

            st.info(
                "No customers found."
            )

        else:

            st.dataframe(
                df,
                use_container_width=True
            )

    # =====================================================
    # ADD CUSTOMER
    # =====================================================

    elif option == "Add Customer":

        st.subheader(
            "➕ Add Customer"
        )

        customer_id = st.number_input(
            "Customer ID",
            min_value=1,
            step=1
        )

        customer_name = st.text_input(
            "Customer Name"
        )

        phone = st.text_input(
            "Phone"
        )

        city = st.text_input(
            "City"
        )

        if st.button(
            "Add Customer"
        ):

            success = execute_query(
                """
                INSERT INTO customers
                (
                    customer_id,
                    customer_name,
                    phone,
                    city
                )
                VALUES
                (
                    %s,
                    %s,
                    %s,
                    %s
                )
                """,
                (
                    customer_id,
                    customer_name,
                    phone,
                    city
                )
            )

            if success:

                st.success(
                    "Customer added successfully."
                )

    # =====================================================
    # PURCHASE HISTORY
    # =====================================================

    elif option == "Purchase History":

        st.subheader(
            "🧾 Customer Purchase History"
        )

        customer_name = st.text_input(
            "Customer Name"
        )

        if st.button(
            "Show History"
        ):

            df = fetch_dataframe(
                """
                SELECT *
                FROM sales
                WHERE customer_name = %s
                ORDER BY sale_id DESC
                """,
                (customer_name,)
            )

            if df.empty:

                st.warning(
                    "No purchase history found."
                )

            else:

                st.dataframe(
                    df,
                    use_container_width=True
                )

    # =====================================================
    # TRACK PURCHASES
    # =====================================================

    elif option == "Track Purchases":

        st.subheader(
            "📊 Track Purchases"
        )

        customer_name = st.text_input(
            "Customer Name"
        )

        if st.button(
            "Track"
        ):

            df = fetch_dataframe(
                """
                SELECT
                    customer_name,
                    COUNT(*) AS number_of_purchases,
                    SUM(quantity) AS total_items,
                    SUM(total_amount) AS total_spending
                FROM sales
                WHERE customer_name = %s
                GROUP BY customer_name
                """,
                (customer_name,)
            )

            if df.empty:

                st.warning(
                    "No purchases found."
                )

            else:

                st.dataframe(
                    df,
                    use_container_width=True
                )


# =========================================================
# BILLING MANAGEMENT
# =========================================================

def billing_management():

    st.header(
        "💰 Billing"
    )

    customers = fetch_dataframe(
        """
        SELECT
            customer_id,
            customer_name
        FROM customers
        ORDER BY customer_id
        """
    )

    plants = fetch_dataframe(
        """
        SELECT
            plant_id,
            plant_name,
            price,
            quantity
        FROM plants
        WHERE quantity > 0
        ORDER BY plant_id
        """
    )

    if customers.empty:

        st.warning(
            "Please add a customer first."
        )

        return

    if plants.empty:

        st.warning(
            "No plants are available in stock."
        )

        return

    # =====================================================
    # SELECT CUSTOMER
    # =====================================================

    customer_options = {
        f"{row['customer_id']} - "
        f"{row['customer_name']}":
        row["customer_name"]

        for _, row in customers.iterrows()
    }

    selected_customer = st.selectbox(
        "Select Customer",
        list(
            customer_options.keys()
        )
    )

    customer_name = customer_options[
        selected_customer
    ]

    # =====================================================
    # SELECT PLANT
    # =====================================================

    plant_options = {
        f"{row['plant_id']} - "
        f"{row['plant_name']} - "
        f"₹{row['price']} - "
        f"Stock: {row['quantity']}":
        row

        for _, row in plants.iterrows()
    }

    selected_plant = st.selectbox(
        "Select Plant",
        list(
            plant_options.keys()
        )
    )

    plant = plant_options[
        selected_plant
    ]

    # =====================================================
    # QUANTITY
    # =====================================================

    quantity = st.number_input(
        "Quantity",
        min_value=1,
        max_value=int(
            plant["quantity"]
        ),
        step=1
    )

    total_amount = (
        float(plant["price"])
        * quantity
    )

    st.write(
        f"### Total Amount: ₹{total_amount}"
    )

    # =====================================================
    # GENERATE BILL
    # =====================================================

    if st.button(
        "Generate Bill"
    ):

        connection = None
        cursor = None

        try:

            connection = get_connection()

            cursor = connection.cursor()

            # Insert sale
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
                    %s
                )
                """,
                (
                    customer_name,
                    plant["plant_name"],
                    quantity,
                    total_amount,
                    date.today()
                )
            )

            # Reduce stock
            cursor.execute(
                """
                UPDATE plants
                SET quantity = quantity - %s
                WHERE plant_id = %s
                """,
                (
                    quantity,
                    plant["plant_id"]
                )
            )

            connection.commit()

            st.success(
                "Bill generated successfully!"
            )

            # =================================================
            # BILL
            # =================================================

            st.subheader(
                "🧾 Bill"
            )

            st.write(
                f"**Customer:** {customer_name}"
            )

            st.write(
                f"**Plant:** {plant['plant_name']}"
            )

            st.write(
                f"**Quantity:** {quantity}"
            )

            st.write(
                f"**Price:** ₹{plant['price']}"
            )

            st.write(
                f"**Total Amount:** ₹{total_amount}"
            )

            st.write(
                f"**Date:** {date.today()}"
            )

        except Exception as e:

            if connection:

                connection.rollback()

            st.error(
                f"Billing error: {e}"
            )

        finally:

            if cursor:
                cursor.close()

            if connection:
                connection.close()


# =========================================================
# REPORTS
# =========================================================

def reports_management():

    st.header(
        "📊 Reports"
    )

    option = st.selectbox(
        "Select Report",
        [
            "Total Sales",
            "Available Stock",
            "Low Stock",
            "Customer History"
        ]
    )

    # =====================================================
    # TOTAL SALES
    # =====================================================

    if option == "Total Sales":

        df = fetch_dataframe(
            """
            SELECT
                COUNT(*) AS total_bills,
                COALESCE(
                    SUM(total_amount),
                    0
                ) AS total_sales
            FROM sales
            """
        )

        if not df.empty:

            total_bills = int(
                df.iloc[0][
                    "total_bills"
                ]
            )

            total_sales = float(
                df.iloc[0][
                    "total_sales"
                ]
            )

            st.metric(
                "Total Bills",
                total_bills
            )

            st.metric(
                "Total Sales",
                f"₹{total_sales}"
            )

        sales_df = fetch_dataframe(
            """
            SELECT *
            FROM sales
            ORDER BY sale_id DESC
            """
        )

        if not sales_df.empty:

            st.subheader(
                "Sales Details"
            )

            st.dataframe(
                sales_df,
                use_container_width=True
            )

    # =====================================================
    # AVAILABLE STOCK
    # =====================================================

    elif option == "Available Stock":

        st.subheader(
            "📦 Available Stock"
        )

        df = fetch_dataframe(
            """
            SELECT
                plant_id,
                plant_name,
                category,
                price,
                quantity,
                supplier_name
            FROM plants
            ORDER BY plant_id
            """
        )

        if df.empty:

            st.info(
                "No stock data available."
            )

        else:

            st.dataframe(
                df,
                use_container_width=True
            )

    # =====================================================
    # LOW STOCK
    # =====================================================

    elif option == "Low Stock":

        st.subheader(
            "⚠️ Low Stock Plants"
        )

        df = fetch_dataframe(
            """
            SELECT *
            FROM plants
            WHERE quantity <= 5
            ORDER BY quantity
            """
        )

        if df.empty:

            st.success(
                "No low-stock plants."
            )

        else:

            st.warning(
                "These plants have low stock."
            )

            st.dataframe(
                df,
                use_container_width=True
            )

    # =====================================================
    # CUSTOMER HISTORY
    # =====================================================

    elif option == "Customer History":

        st.subheader(
            "👤 Customer History"
        )

        customer_name = st.text_input(
            "Customer Name"
        )

        if st.button(
            "View Customer History"
        ):

            df = fetch_dataframe(
                """
                SELECT *
                FROM sales
                WHERE customer_name = %s
                ORDER BY sale_date DESC
                """,
                (customer_name,)
            )

            if df.empty:

                st.warning(
                    "No sales found for this customer."
                )

            else:

                st.dataframe(
                    df,
                    use_container_width=True
                )


# =========================================================
# MAIN SIDEBAR
# =========================================================

st.sidebar.title(
    "🌱 Green Bloom"
)

menu = st.sidebar.selectbox(
    "Main Menu",
    [
        "Home",
        "Plant",
        "Supplier",
        "Customer",
        "Billing",
        "Reports"
    ]
)


# =========================================================
# MAIN MENU
# =========================================================

if menu == "Home":

    home_page()

elif menu == "Plant":

    plant_management()

elif menu == "Supplier":

    supplier_management()

elif menu == "Customer":

    customer_management()

elif menu == "Billing":

    billing_management()

elif menu == "Reports":

    reports_management()