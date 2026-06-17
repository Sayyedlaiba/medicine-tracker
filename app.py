import datetime
import streamlit as st
import pandas as pd

# Set up page configuration
st.set_page_config(page_title="Medicine Inventory Tracker", layout="wide")

st.title("💊 Medicine Inventory Tracker")
st.write("Keep track of your medicines, expiration dates, and stock levels effortlessly.")

# --- Session State Initialization ---
# This ensures our data persists while the user interacts with the app
if "inventory" not in st.session_state:
    # Starting with some sample data
    st.session_state.inventory = pd.DataFrame(
        [
            {
                "Name": "Paracetamol",
                "Uses": "Fever and Pain relief",
                "Expiry Date": datetime.date(2026, 8, 20),
                "Quantity": 15,
            },
            {
                "Name": "Vitamin C",
                "Uses": "Immunity booster",
                "Expiry Date": datetime.date(2025, 12, 1),
                "Quantity": 2,
            },
        ]
    )

# --- Expiry & Depletion Alerts ---
today = datetime.date.today()
expired_medicines = []
finished_medicines = []

for idx, row in st.session_state.inventory.iterrows():
    # Check for expired medicine
    if row["Expiry Date"] <= today:
        expired_medicines.append(row["Name"])
    # Check for finished medicine
    if row["Quantity"] <= 0:
        finished_medicines.append(row["Name"])

# Display Alert Popups/Boxes at the very top
if expired_medicines:
    for med in expired_medicines:
        st.error(f"🚨 **Alert:** `{med}` has expired! Please dispose of it safely.")

if finished_medicines:
    for med in finished_medicines:
        st.warning(
            f"⚠️ **Restock Warning:** `{med}` is finished. You should restock soon!"
        )


# --- Layout: Sidebar and Main Content ---
# Sidebar for logging medicine consumption
st.sidebar.header("Log Consumed Medicine")

if not st.session_state.inventory.empty:
    # Filter out already empty medicines so user doesn't log negative quantities
    available_meds = st.session_state.inventory[
        st.session_state.inventory["Quantity"] > 0
    ]["Name"].tolist()

    if available_meds:
        selected_med = st.sidebar.selectbox(
            "Which medicine did you take?", available_meds
        )
        take_quantity = st.sidebar.number_input(
            "Quantity taken", min_value=1, value=1, step=1
        )

        if st.sidebar.button("Update Inventory"):
            # Find the row index and deduct the quantity
            idx = st.session_state.inventory[
                st.session_state.inventory["Name"] == selected_med
            ].index[0]
            current_qty = st.session_state.inventory.at[idx, "Quantity"]

            # Ensure we don't drop below 0 unexpectedly
            new_qty = max(0, current_qty - take_quantity)
            st.session_state.inventory.at[idx, "Quantity"] = new_qty

            st.sidebar.success(f"Updated! Took {take_quantity} of {selected_med}.")
            st.rerun()
    else:
        st.sidebar.info("No active medicine stock available to consume.")
else:
    st.sidebar.info("Add medicines to the inventory first.")
    # --- 2. Delete Medicine Record ---
    st.sidebar.subheader("🗑️ Delete Medicine Record")
    delete_med = st.sidebar.selectbox(
        "Select medicine to remove completely:", all_meds, key="delete_select"
    )

    if st.sidebar.button("Delete from Inventory", type="primary", key="delete_btn"):
        # Filter out the selected medicine row
        st.session_state.inventory = st.session_state.inventory[
            st.session_state.inventory["Name"] != delete_med
        ].reset_index(drop=True)

        st.sidebar.success(f"Removed `{delete_med}` from records.")
        st.rerun()
    else:
    st.sidebar.info("Add medicines to the inventory first.")


# --- Main Content: Add New Medicine Form ---
with st.expander("➕ Add New Medicine to Inventory", expanded=True):
    with st.form("medicine_form", clear_on_submit=True):
        col1, col2 = st.columns(2)

        with col1:
            med_name = st.text_input("Medicine Name").strip()
            med_uses = st.text_input("Uses / Purpose")

        with col2:
            med_expiry = st.date_input("Expiry Date", min_value=today)
            med_qty = st.number_input(
                "Quantity (Strips/Tablets)", min_value=1, step=1, value=10
            )

        submit_btn = st.form_submit_button("Add Medicine")

        if submit_btn:
            if med_name:
                # Check if medicine already exists to avoid duplicates
                if (
                    med_name.lower()
                    in st.session_state.inventory["Name"].str.lower().values
                ):
                    st.error(
                        f"'{med_name}' already exists in the table. Update it or use a different name."
                    )
                else:
                    # Append new data row
                    new_row = pd.DataFrame(
                        [
                            {
                                "Name": med_name,
                                "Uses": med_uses,
                                "Expiry Date": med_expiry,
                                "Quantity": med_qty,
                            }
                        ]
                    )
                    st.session_state.inventory = pd.concat(
                        [st.session_state.inventory, new_row], ignore_index=True
                    )
                    st.success(f"Successfully added {med_name}!")
                    st.rerun()
            else:
                st.error("Please enter a valid medicine name.")


# --- Main Content: Display Current Inventory ---
st.subheader("📋 Current Medicine Stock")

if not st.session_state.inventory.empty:
    # Formatting the display table nicely
    display_df = st.session_state.inventory.copy()
    display_df["Expiry Date"] = display_df["Expiry Date"].apply(
        lambda x: x.strftime("%Y-%m-%d")
    )

    # Display using Streamlit's native interactive data frame
    st.dataframe(display_df, use_container_width=True, hide_index=True)
else:
    st.info("Your inventory is currently empty.")
