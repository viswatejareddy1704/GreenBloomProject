import streamlit as st
import pandas as pd
from pathlib import Path
from PIL import Image, UnidentifiedImageError
import uuid

from db_connection import get_connection


# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent

IMAGE_DIR = BASE_DIR / "plant_Images"
IMAGE_DIR.mkdir(parents=True, exist_ok=True)


# ============================================================
# DEFAULT PLANT IMAGE MAPPING
# ============================================================

PLANT_IMAGES = {
    "tulsi": "Tulsi.jpg",
    "tulasi": "Tulsi.jpg",

    "aloe vera": "Aloe vera.jpg",
    "alovera": "Aloe vera.jpg",

    "money plant": "Money plant.jpg",
    "moneyplant": "Money plant.jpg",

    "jasmine": "Jasmine.jpg",

    "rose": "rose.jpg",

    "tulips": "Tulips.jpg",
}


# ============================================================
# IMAGE PATH
# ============================================================

def get_plant_image_path(plant_name, image_file=None):

    # First priority: uploaded/database image
    if image_file:

        image_file = str(image_file).strip()

        if image_file and image_file.lower() != "nan":

            db_image = IMAGE_DIR / image_file

            if db_image.exists():
                return db_image

    # Second priority: default image
    if plant_name:

        key = str(plant_name).strip().lower()

        if key in PLANT_IMAGES:

            default_image = IMAGE_DIR / PLANT_IMAGES[key]

            if default_image.exists():
                return default_image

    return None


# ============================================================
# DISPLAY IMAGE
# ============================================================

def display_plant_image(plant_name, image_file=None, width="full"):

    image_path = get_plant_image_path(
        plant_name,
        image_file
    )

    if image_path and image_path.exists():

        try:

            image = Image.open(image_path)

            st.image(
                image,
                use_container_width=True
            )

        except UnidentifiedImageError:

            st.warning("Invalid image file.")

        except Exception as e:

            st.warning(
                f"Unable to display image: {e}"
            )

    else:

        st.info("🌱 No image available")


# ============================================================
# DATABASE FETCH
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
# DATABASE EXECUTE
# ============================================================

def execute_query(query, params=None):

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


# ============================================================
# SAVE UPLOADED IMAGE
# ============================================================

def save_uploaded_image(
    uploaded_image,
    plant_name
):

    if uploaded_image is None:
        return None

    original_name = uploaded_image.name

    extension = Path(
        original_name
    ).suffix.lower()

    allowed_extensions = [
        ".jpg",
        ".jpeg",
        ".png"
    ]

    if extension not in allowed_extensions:

        st.error(
            "Only JPG, JPEG and PNG images are allowed."
        )

        return None

    clean_name = "".join(
        character
        for character in plant_name
        if character.isalnum()
        or character in (" ", "_", "-")
    ).strip()

    clean_name = clean_name.replace(
        " ",
        "_"
    )

    if not clean_name:

        clean_name = "plant"

    unique_id = uuid.uuid4().hex[:8]

    filename = (
        f"{clean_name}_{unique_id}{extension}"
    )

    file_path = IMAGE_DIR / filename

    try:

        image = Image.open(
            uploaded_image
        )

        # Convert unusual image modes to RGB
        if image.mode in ("RGBA", "P"):
            image = image.convert("RGB")

        image.save(
            file_path
        )

        return filename

    except Exception as e:

        st.error(
            f"Unable to save image: {e}"
        )

        return None


# ============================================================
# DELETE IMAGE
# ============================================================

def delete_image_file(image_file):

    if not image_file:
        return

    try:

        image_path = IMAGE_DIR / str(
            image_file
        )

        if image_path.exists():

            image_path.unlink()

    except Exception:

        pass


# ============================================================
# PLANT STATISTICS
# ============================================================

def get_plant_statistics(df):

    if df.empty:

        return 0, 0, 0, 0

    total_types = len(df)

    total_stock = int(
        pd.to_numeric(
            df["quantity"],
            errors="coerce"
        ).fillna(0).sum()
    )

    stock_value = (
        pd.to_numeric(
            df["price"],
            errors="coerce"
        ).fillna(0)
        *
        pd.to_numeric(
            df["quantity"],
            errors="coerce"
        ).fillna(0)
    ).sum()

    low_stock = len(
        df[
            pd.to_numeric(
                df["quantity"],
                errors="coerce"
            ).fillna(0) <= 10
        ]
    )

    return (
        total_types,
        total_stock,
        float(stock_value),
        low_stock
    )


# ============================================================
# PLANT CARD
# ============================================================

def display_plant_card(plant):

    with st.container(border=True):

        st.markdown(
            f"### 🌱 {plant['plant_name']}"
        )

        display_plant_image(
            plant["plant_name"],
            plant["image_file"]
        )

        st.write(
            f"**Category:** "
            f"{plant['category'] or 'Not specified'}"
        )

        price = float(
            plant["price"] or 0
        )

        quantity = int(
            plant["quantity"] or 0
        )

        st.write(
            f"**Price:** ₹{price:,.2f}"
        )

        if quantity <= 10:

            st.warning(
                f"⚠️ Low Stock: {quantity}"
            )

        else:

            st.success(
                f"📦 Stock: {quantity}"
            )

        supplier = (
            plant["supplier_name"]
            or "Not specified"
        )

        st.write(
            f"**Supplier:** {supplier}"
        )


# ============================================================
# PLANT MANAGEMENT
# ============================================================

def plant_management():

    # --------------------------------------------------------
    # PAGE HEADER
    # --------------------------------------------------------

    st.title("🌿 Plant Management")

    st.write(
        "Manage plants, stock, prices and plant images."
    )

    st.divider()


    # --------------------------------------------------------
    # LOAD PLANTS
    # --------------------------------------------------------

    all_plants = fetch_dataframe(
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


    # --------------------------------------------------------
    # STATISTICS
    # --------------------------------------------------------

    (
        total_types,
        total_stock,
        stock_value,
        low_stock
    ) = get_plant_statistics(
        all_plants
    )

    col1, col2, col3, col4 = st.columns(4)

    with col1:

        st.metric(
            "🌱 Plant Types",
            total_types
        )

    with col2:

        st.metric(
            "📦 Total Stock",
            total_stock
        )

    with col3:

        st.metric(
            "💰 Stock Value",
            f"₹{stock_value:,.2f}"
        )

    with col4:

        st.metric(
            "⚠️ Low Stock",
            low_stock
        )


    st.divider()


    # --------------------------------------------------------
    # ACTION MENU
    # --------------------------------------------------------

    option = st.selectbox(
        "Choose an action",
        [
            "View Plants",
            "Add Plant",
            "Update Plant",
            "Delete Plant",
            "Search Plant"
        ]
    )


    # ========================================================
    # VIEW PLANTS
    # ========================================================

    if option == "View Plants":

        st.subheader(
            "🌱 Plant Gallery"
        )

        if all_plants.empty:

            st.info(
                "No plants found. Add your first plant."
            )

            return


        # ----------------------------------------------------
        # GALLERY
        # ----------------------------------------------------

        for start in range(
            0,
            len(all_plants),
            3
        ):

            columns = st.columns(3)

            row = all_plants.iloc[
                start:start + 3
            ]

            for column, (_, plant) in zip(
                columns,
                row.iterrows()
            ):

                with column:

                    display_plant_card(
                        plant
                    )


        st.divider()


        # ----------------------------------------------------
        # INVENTORY TABLE
        # ----------------------------------------------------

        st.subheader(
            "📋 Plant Inventory"
        )

        display_df = all_plants.drop(
            columns=["image_file"],
            errors="ignore"
        ).copy()

        if "price" in display_df.columns:

            display_df["price"] = (
                display_df["price"]
                .apply(
                    lambda value:
                    f"₹{float(value):,.2f}"
                )
            )

        st.dataframe(
            display_df,
            use_container_width=True,
            hide_index=True
        )


    # ========================================================
    # ADD PLANT
    # ========================================================

    elif option == "Add Plant":

        st.subheader(
            "➕ Add New Plant"
        )

        st.caption(
            "Enter plant details and optionally upload "
            "a plant image."
        )


        with st.form(
            "add_plant_form",
            clear_on_submit=True
        ):

            col1, col2 = st.columns(2)

            with col1:

                plant_name = st.text_input(
                    "Plant Name",
                    placeholder="Example: Rose"
                )

                category = st.selectbox(
                    "Category",
                    [
                        "Medicinal",
                        "Flowering",
                        "Indoor",
                        "Outdoor",
                        "Herbal",
                        "Fruit",
                        "Vegetable",
                        "Other"
                    ]
                )

                price = st.number_input(
                    "Price (₹)",
                    min_value=0.0,
                    step=10.0
                )

            with col2:

                quantity = st.number_input(
                    "Quantity",
                    min_value=0,
                    step=1
                )

                supplier = st.text_input(
                    "Supplier Name",
                    placeholder="Example: Green Nursery"
                )

                uploaded_image = st.file_uploader(
                    "Plant Image",
                    type=[
                        "jpg",
                        "jpeg",
                        "png"
                    ]
                )


            st.divider()

            submitted = st.form_submit_button(
                "➕ Add Plant",
                type="primary",
                use_container_width=True
            )


        if submitted:

            if not plant_name.strip():

                st.error(
                    "Please enter a plant name."
                )

                return


            if price <= 0:

                st.error(
                    "Price must be greater than 0."
                )

                return


            image_filename = None


            # Save uploaded image
            if uploaded_image:

                image_filename = save_uploaded_image(
                    uploaded_image,
                    plant_name
                )

                if image_filename is None:

                    return


            success = execute_query(
                """
                INSERT INTO plants
                (
                    plant_name,
                    category,
                    price,
                    quantity,
                    supplier_name,
                    image_file
                )
                VALUES
                (%s, %s, %s, %s, %s, %s)
                """,
                (
                    plant_name.strip(),
                    category,
                    price,
                    int(quantity),
                    supplier.strip(),
                    image_filename
                )
            )


            if success:

                st.success(
                    f"🌱 {plant_name} added successfully!"
                )

                st.rerun()


    # ========================================================
    # UPDATE PLANT
    # ========================================================

    elif option == "Update Plant":

        st.subheader(
            "✏️ Update Plant"
        )

        if all_plants.empty:

            st.info(
                "No plants available to update."
            )

            return


        plant_options = {}

        for _, plant in all_plants.iterrows():

            label = (
                f"{plant['plant_name']} "
                f"(ID: {plant['plant_id']})"
            )

            plant_options[label] = plant


        selected_label = st.selectbox(
            "Select Plant",
            list(plant_options.keys())
        )

        selected_plant = plant_options[
            selected_label
        ]


        # ----------------------------------------------------
        # CURRENT IMAGE
        # ----------------------------------------------------

        st.write(
            "**Current Plant Image**"
        )

        display_plant_image(
            selected_plant["plant_name"],
            selected_plant["image_file"]
        )


        st.divider()


        with st.form(
            "update_plant_form"
        ):

            col1, col2 = st.columns(2)

            with col1:

                new_name = st.text_input(
                    "Plant Name",
                    value=str(
                        selected_plant["plant_name"]
                    )
                )

                new_category = st.text_input(
                    "Category",
                    value=str(
                        selected_plant["category"]
                        or ""
                    )
                )

                new_price = st.number_input(
                    "Price (₹)",
                    min_value=0.0,
                    value=float(
                        selected_plant["price"]
                    ),
                    step=10.0
                )

            with col2:

                new_quantity = st.number_input(
                    "Quantity",
                    min_value=0,
                    value=int(
                        selected_plant["quantity"]
                    ),
                    step=1
                )

                new_supplier = st.text_input(
                    "Supplier Name",
                    value=str(
                        selected_plant["supplier_name"]
                        or ""
                    )
                )

                new_image = st.file_uploader(
                    "Replace Image (optional)",
                    type=[
                        "jpg",
                        "jpeg",
                        "png"
                    ]
                )


            st.divider()

            update_button = st.form_submit_button(
                "💾 Update Plant",
                type="primary",
                use_container_width=True
            )


        if update_button:

            if not new_name.strip():

                st.error(
                    "Plant name cannot be empty."
                )

                return


            old_image = selected_plant[
                "image_file"
            ]

            new_image_filename = old_image


            if new_image:

                new_image_filename = save_uploaded_image(
                    new_image,
                    new_name
                )

                if new_image_filename is None:

                    return


            success = execute_query(
                """
                UPDATE plants
                SET
                    plant_name = %s,
                    category = %s,
                    price = %s,
                    quantity = %s,
                    supplier_name = %s,
                    image_file = %s
                WHERE plant_id = %s
                """,
                (
                    new_name.strip(),
                    new_category.strip(),
                    new_price,
                    int(new_quantity),
                    new_supplier.strip(),
                    new_image_filename,
                    int(
                        selected_plant["plant_id"]
                    )
                )
            )


            if success:

                # Delete old uploaded image
                if (
                    new_image
                    and old_image
                    and str(old_image)
                    != str(new_image_filename)
                ):

                    delete_image_file(
                        old_image
                    )

                st.success(
                    f"🌱 {new_name} updated successfully!"
                )

                st.rerun()


    # ========================================================
    # DELETE PLANT
    # ========================================================

    elif option == "Delete Plant":

        st.subheader(
            "🗑️ Delete Plant"
        )

        if all_plants.empty:

            st.info(
                "No plants available to delete."
            )

            return


        plant_options = {}

        for _, plant in all_plants.iterrows():

            label = (
                f"{plant['plant_name']} "
                f"(ID: {plant['plant_id']})"
            )

            plant_options[label] = plant


        selected_label = st.selectbox(
            "Select Plant to Delete",
            list(plant_options.keys())
        )

        selected_plant = plant_options[
            selected_label
        ]


        col1, col2 = st.columns(2)


        with col1:

            display_plant_image(
                selected_plant["plant_name"],
                selected_plant["image_file"]
            )


        with col2:

            st.warning(
                f"You are about to delete "
                f"**{selected_plant['plant_name']}**."
            )

            st.write(
                f"**Category:** "
                f"{selected_plant['category']}"
            )

            st.write(
                f"**Price:** "
                f"₹{float(selected_plant['price']):,.2f}"
            )

            st.write(
                f"**Stock:** "
                f"{selected_plant['quantity']}"
            )

            st.write(
                f"**Supplier:** "
                f"{selected_plant['supplier_name']}"
            )


        st.divider()


        confirm = st.checkbox(
            "I understand that this plant will be permanently deleted."
        )


        if st.button(
            "🗑️ Delete Plant",
            type="primary",
            use_container_width=True
        ):

            if not confirm:

                st.error(
                    "Please confirm the deletion first."
                )

                return


            plant_id = int(
                selected_plant["plant_id"]
            )

            image_file = selected_plant[
                "image_file"
            ]


            success = execute_query(
                """
                DELETE FROM plants
                WHERE plant_id = %s
                """,
                (plant_id,)
            )


            if success:

                if image_file:

                    delete_image_file(
                        image_file
                    )

                st.success(
                    f"🌱 {selected_plant['plant_name']} "
                    "deleted successfully!"
                )

                st.rerun()


    # ========================================================
    # SEARCH PLANT
    # ========================================================

    elif option == "Search Plant":

        st.subheader(
            "🔎 Search Plants"
        )

        search_text = st.text_input(
            "Search by plant name",
            placeholder="Example: Rose"
        )


        if search_text.strip():

            df = fetch_dataframe(
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
                WHERE plant_name LIKE %s
                ORDER BY plant_name
                """,
                (
                    f"%{search_text.strip()}%",
                )
            )


            if df.empty:

                st.warning(
                    "No matching plants found."
                )

                return


            st.success(
                f"{len(df)} plant(s) found."
            )


            # ------------------------------------------------
            # SEARCH CARDS
            # ------------------------------------------------

            for start in range(
                0,
                len(df),
                3
            ):

                columns = st.columns(3)

                row = df.iloc[
                    start:start + 3
                ]

                for column, (_, plant) in zip(
                    columns,
                    row.iterrows()
                ):

                    with column:

                        display_plant_card(
                            plant
                        )


            st.divider()


            # ------------------------------------------------
            # SEARCH TABLE
            # ------------------------------------------------

            st.subheader(
                "📋 Search Results"
            )

            display_df = df.drop(
                columns=["image_file"],
                errors="ignore"
            ).copy()

            if "price" in display_df.columns:

                display_df["price"] = (
                    display_df["price"]
                    .apply(
                        lambda value:
                        f"₹{float(value):,.2f}"
                    )
                )

            st.dataframe(
                display_df,
                use_container_width=True,
                hide_index=True
            )