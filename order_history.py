# order_history.py
import streamlit as st
from firebase_init import db
from menu import menu  # Import the menu to access coffee prices


def order_history():
    st.title("Order History")

    # Fetch customer's orders
    orders_ref = db.collection("orders").where("customer", "==", st.session_state["authenticated_user"]).stream()
    customer_orders = [
        {"Order ID": o.id, **o.to_dict()}
        for o in orders_ref
    ]

    # Sort orders by order_time in descending order
    # Added: Sorting customer_orders based on 'order_time'
    customer_orders.sort(key=lambda x: x.get("order_time", ""), reverse=True)

    if customer_orders:
        st.subheader("Your Order History")
        branch_cache = {}  # Cache to store branch names to avoid multiple database calls

        for order in customer_orders:
            # Create a container with a border for each order
            with st.container(border=True):
                st.write(f"**Order ID:** {order['Order ID']}")

                # Get the branch ID from the order
                branch_id = order.get("branch_id", "N/A")
                if branch_id != "N/A":
                    # Check if the branch name is already in the cache
                    if branch_id in branch_cache:
                        branch_name = branch_cache[branch_id]
                    else:
                        # Fetch the branch document from Firestore
                        branch_doc = db.collection("branches").document(branch_id).get()
                        if branch_doc.exists:
                            branch_name = branch_doc.to_dict().get("cafe_name", "Unknown Branch")
                            # Store the branch name in the cache
                            branch_cache[branch_id] = branch_name
                        else:
                            branch_name = "Unknown Branch"
                else:
                    branch_name = "N/A"

                st.write(f"**Branch:** {branch_name}")

                # Display all items in the order
                st.write("**Items:**")
                for item in order["items"]:
                    coffee_name = item["coffee"]
                    quantity = item["quantity"]
                    # Calculate the price per item
                    price_per_item = menu[coffee_name]["price"]
                    total_item_price = price_per_item * quantity
                    st.write(f"{quantity}x {coffee_name} - RM{total_item_price:.2f}")

                # Display total price of the order
                st.write(f"**Total Quantity:** {order.get('total_quantity', 0)}")
                st.write(f"**Total Price:** RM{order.get('total_price', 0.00):.2f}")
                st.write(f"**Order Placed At:** {order['order_time']}")

                # No need for a separator line as the container provides visual separation
    else:
        st.warning("You have no previous orders.")
