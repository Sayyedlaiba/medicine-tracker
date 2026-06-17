import datetime
import streamlit as st
import pandas as pd

# Set up page configuration
st.set_page_config(page_title="Medicine Inventory Tracker", layout="wide")

st.title("💊 Medicine Inventory Tracker")
st.write("Keep track of your medicines, expiration dates, and stock levels effortlessly.")

# --- Session State Initialization ---
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
st.sidebar.header("Actions Panel")

if not st.session_state.inventory.empty:
    all_meds = st.session_state.inventory["Name"].tolist()
    available_meds = st.session_state.inventory[
        st.session_state.inventory["Quantity"] > 0
    ]["Name"].tolist()

    # --- 1. Log Consumed Medicine ---
    st.sidebar.subheader("Log Consumed Medicine")
    if available_meds:
        selected_med = st.sidebar.selectbox(
            "Which medicine did you take?", available_meds, key="consume_select"
        )
        take_quantity = st.sidebar.number_input(
            "Quantity taken", min_value=1, value=1, step=1, key="consume_qty"
        )

        if st.sidebar.button("Update Inventory", key="consume_btn"):
            idx = st.session_state.inventory[
                st.session_state.inventory["Name"] == selected_med
            ].index[0]
            current_qty = st.session_state.inventory.at[idx, "Quantity"]

            new_qty = max(0, current_qty - take_quantity)
            st.session_state.inventory.at[idx, "Quantity"] = new_qty

            st.sidebar.success(f"Updated! Took {take_quantity} of {selected_med}.")
            st.rerun()
    else:
        st.sidebar.info("No active medicine stock available to consume.")

    st.sidebar.markdown("---")

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
