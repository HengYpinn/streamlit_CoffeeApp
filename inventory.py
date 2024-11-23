# inventory.py

import streamlit as st
from firebase_init import db
import pandas as pd
from constants import ITEM_DISPLAY_NAMES, DISPLAY_NAME_TO_ITEM  # Import mappings from constants.py

def inventory_management():
    st.title("Inventory Management")

    # Initialize a session state variable to store success messages
    if "restock_message" not in st.session_state:
        st.session_state["restock_message"] = None

    # Fetch the list of branches
    branches_ref = db.collection("branches").stream()
    branches = [{"id": branch.id, **branch.to_dict()} for branch in branches_ref]

    if branches:
        # Wrap branch selection in a container
        with st.container(border=True):
            # Select a branch
            st.subheader("Select a Branch")
            branch_names = [branch["cafe_name"] for branch in branches]
            selected_branch_name = st.selectbox("Select Branch", branch_names)
            selected_branch = next(branch for branch in branches if branch["cafe_name"] == selected_branch_name)

        # Wrap inventory display in a container
        with st.container(border=True):
            # Display the current inventory for the selected branch
            st.subheader(f"Inventory for {selected_branch['cafe_name']}")
            inventory = selected_branch["inventory"]
            low_stock_thresholds = {
                'coffee_beans': 100,
                'cup': 50,
                'milk': 20,
                'sugar': 10
            }

            # Check for low stock items
            low_stock_items = []
            for item_key, stock in inventory.items():
                display_name = ITEM_DISPLAY_NAMES.get(item_key, item_key.replace('_', ' ').title())
                threshold = low_stock_thresholds.get(item_key, 50)
                if stock < threshold:
                    low_stock_items.append({"Item": display_name, "Stock": stock, "Threshold": threshold})

            if low_stock_items:
                st.warning("The following items are low on stock:")
                st.table(pd.DataFrame(low_stock_items))
            else:
                st.success("All inventory items are adequately stocked.")

            # Display inventory items with display names
            st.write("**Current Inventory Levels:**")
            for item_key, stock in inventory.items():
                display_name = ITEM_DISPLAY_NAMES.get(item_key, item_key.replace('_', ' ').title())
                st.write(f"{display_name}: {stock} units")

        # Display the success message if it exists
        if st.session_state["restock_message"]:
            st.success(st.session_state["restock_message"])
            st.session_state["restock_message"] = None  # Clear the message after displaying it

        # Wrap restocking functionality in a container
        with st.container(border=True):
            st.subheader("Restock Inventory")
            restock_items = [
                ITEM_DISPLAY_NAMES.get(item_key, item_key.replace('_', ' ').title())
                for item_key in inventory.keys()
            ]
            restock_item_display = st.selectbox("Select Item to Restock", restock_items)

            # Map the selected display name back to the database key
            restock_item_key = DISPLAY_NAME_TO_ITEM.get(restock_item_display)

            restock_qty = st.number_input("Restock Quantity", min_value=1, step=1)

            if st.button("Restock"):
                # Update the inventory for the selected branch
                new_stock = inventory[restock_item_key] + restock_qty
                db.collection("branches").document(selected_branch["id"]).update({
                    f"inventory.{restock_item_key}": new_stock
                })

                # Store the success message in session state
                st.session_state["restock_message"] = (
                    f"Restocked {restock_qty} units of {restock_item_display} in {selected_branch['cafe_name']}."
                )

                # Refresh the page to show updated inventory and show the success message
                st.rerun()
    else:
        st.warning("No branches available. Please add branches to manage inventory.")
