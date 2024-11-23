# notification.py
import streamlit as st
from firebase_init import db
import pandas as pd
import datetime

def notification_management():
    st.title("Notification Management")

    # Branch Selection
    branches_ref = db.collection("branches").stream()
    branches = [{"Branch Name": b.to_dict()["cafe_name"], "Branch ID": b.id} for b in branches_ref]

    if not branches:
        st.warning("No branches available. Please contact admin.")
    else:
        branch_names = [branch["Branch Name"] for branch in branches]
        selected_branch_name = st.selectbox("Select Branch for Notifications", branch_names)
        selected_branch_id = next(
            branch["Branch ID"] for branch in branches if branch["Branch Name"] == selected_branch_name
        )

        # Order Ready Notification
        st.subheader(f"Order Ready Notifications for {selected_branch_name}")

        # Fetch unprepared orders for the selected branch
        orders_ref = db.collection("orders") \
            .where("branch_id", "==", selected_branch_id) \
            .where("prepared_time", "==", None) \
            .stream()

        unprepared_orders = []
        for o in orders_ref:
            order_data = o.to_dict()
            order_id = o.id
            order_time = order_data.get("order_time")
            customer = order_data.get("customer")
            items = order_data.get("items", [])
            unprepared_orders.append({
                "Order ID": order_id,
                "Order Time": order_time,
                "Customer": customer,
                "Items": items
            })

        if unprepared_orders:
            # Wrap the unprepared orders section in a container with a border
            container = st.container(border=True)
            with container:
                # Prepare data for display
                display_data = []
                for order in unprepared_orders:
                    order_id = order["Order ID"]
                    order_time = order["Order Time"]
                    customer = order["Customer"]
                    items = order["Items"]
                    # Combine items into a single string
                    items_description = ", ".join([f"{item['quantity']}x {item['coffee']}" for item in items])
                    display_data.append({
                        "Order ID": order_id,
                        "Order Time": order_time,
                        "Customer": customer,
                        "Order Details": items_description
                    })

                # Convert to DataFrame for display
                df_unprepared = pd.DataFrame(display_data)
                st.write("Unprepared Orders:")
                st.table(df_unprepared)

                # Select Order to Mark as Prepared
                selected_order_id = st.selectbox(
                    "Select Order ID to mark as Prepared", df_unprepared["Order ID"].values
                )
                if st.button("Mark as Prepared"):
                    prepared_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    db.collection("orders").document(selected_order_id).update({"prepared_time": prepared_time})
                    st.success(f"Order ID {selected_order_id} marked as Prepared at {prepared_time}.")
                    st.rerun()
        else:
            # Display the message outside the container
            st.info(f"No unprepared orders at the moment for {selected_branch_name}.")

        # Low Stock Reminder
        st.subheader(f"Low Stock Reminder for {selected_branch_name}")

        # Fetch Inventory for the Selected Branch
        branch_ref = db.collection("branches").document(selected_branch_id).get()
        branch_inventory = branch_ref.to_dict()["inventory"] if branch_ref.exists else {}

        # Define thresholds and identify low stock items
        low_stock_threshold = {
            "coffee_beans": 100,
            "cup": 50,
            "milk": 20,
            "sugar": 10
        }

        # Identify low stock items
        low_stock_items = [
            {
                "Item": item_key.replace('_', ' ').title(),
                "Stock": stock,
                "Threshold": low_stock_threshold.get(item_key, 50)
            }
            for item_key, stock in branch_inventory.items()
            if stock < low_stock_threshold.get(item_key, 50)
        ]

        if low_stock_items:
            # Wrap the low stock items section in a container with a border
            container = st.container(border=True)
            with container:
                st.warning(f"The following items are running low for {selected_branch_name}:")
                st.table(pd.DataFrame(low_stock_items))
        else:
            # Display the message outside the container
            st.success(f"All inventory items are adequately stocked for {selected_branch_name}.")
