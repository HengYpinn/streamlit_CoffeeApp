# pickup_notification.py
import streamlit as st
from firebase_init import db
import datetime

def pickup_notification():
    st.title("Pickup Notification")

    # Get today's date
    today = datetime.datetime.now().date()

    # Fetch customer's orders placed today
    orders_ref = db.collection("orders") \
        .where("customer", "==", st.session_state["authenticated_user"]) \
        .stream()
    customer_orders = [
        {"id": o.id, **o.to_dict()}
        for o in orders_ref
        if datetime.datetime.strptime(o.to_dict()["order_time"], "%Y-%m-%d %H:%M:%S").date() == today
    ]

    if customer_orders:
        st.subheader("Your orders today 😋:")
        branch_cache = {}  # Cache to store branch names
        for order in customer_orders:
            # Parse order time
            order_time = datetime.datetime.strptime(order["order_time"], "%Y-%m-%d %H:%M:%S")
            prepared_time = order.get("prepared_time")

            # Get branch name
            branch_id = order.get('branch_id', 'N/A')
            if branch_id != 'N/A':
                if branch_id in branch_cache:
                    branch_name = branch_cache[branch_id]
                else:
                    branch_doc = db.collection('branches').document(branch_id).get()
                    if branch_doc.exists:
                        branch_name = branch_doc.to_dict().get('cafe_name', 'Unknown Branch')
                        branch_cache[branch_id] = branch_name
                    else:
                        branch_name = 'Unknown Branch'
            else:
                branch_name = 'N/A'

            # Display order details within a container with a border
            container = st.container(border=True)
            with container:
                st.write(f"**Order ID:** {order['id']}")
                st.write(f"**Branch:** {branch_name}")
                st.write(f"**Order Placed At:** {order_time.strftime('%Y-%m-%d %H:%M:%S')}")

                # Display items in the order
                st.write("**Order Details:**")
                for item in order['items']:
                    coffee_name = item['coffee']
                    quantity = item['quantity']
                    st.write(f"{quantity}x {coffee_name}")

                # Display preparation status
                if prepared_time:
                    st.success(f"**Status:** Ready for pickup since {prepared_time}.")
                else:
                    st.info("**Status:** Being prepared. Please wait for a notification.")
    else:
        st.warning("You have no orders awaiting pickup today.")
