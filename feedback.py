# feedback.py
import streamlit as st
from firebase_init import db
import datetime

def feedback():
    st.title("Feedback")
    st.write("Provide feedback for your recent orders.")

    # Fetch customer's orders
    orders_ref = db.collection("orders").where("customer", "==", st.session_state["authenticated_user"]).stream()
    customer_orders = [
        {"id": o.id, **o.to_dict()}
        for o in orders_ref
    ]

    if customer_orders:
        # Allow customer to select an order by ID
        order_ids = [order["id"] for order in customer_orders]
        selected_order_id = st.selectbox("Select an Order ID", order_ids)

        # Show items corresponding to the selected order
        selected_order = next(order for order in customer_orders if order["id"] == selected_order_id)

        # Fetch branch name using branch_id
        branch_id = selected_order.get('branch_id', 'N/A')
        if branch_id != 'N/A':
            branch_doc = db.collection('branches').document(branch_id).get()
            if branch_doc.exists:
                branch_name = branch_doc.to_dict().get('cafe_name', 'Unknown Branch')
            else:
                branch_name = 'Unknown Branch'
        else:
            branch_name = 'N/A'

        # Display order details in a container with a border
        with st.container(border=True):
            st.subheader(f"Order Details for Order ID: {selected_order_id}")
            # Display all items in the order
            st.write("**Items:**")
            for item in selected_order['items']:
                coffee_name = item['coffee']
                quantity = item['quantity']
                st.write(f"{quantity}x {coffee_name}")
            st.write(f"**Branch:** {branch_name}")
            st.write(f"**Order Placed At:** {selected_order['order_time']}")

        # Allow customer to select an item from the order to provide feedback
        item_descriptions = [
            f"{item['quantity']}x {item['coffee']}" for item in selected_order["items"]
        ]
        selected_item_description = st.selectbox("Select an Item to Provide Feedback", item_descriptions)
        selected_item = next(
            item for item in selected_order["items"]
            if f"{item['quantity']}x {item['coffee']}" == selected_item_description
        )

        # Feedback inputs within a container
        with st.container(border=True):
            st.subheader("Rate your experience")
            coffee_rating = st.slider("Rate the coffee", min_value=1, max_value=5, step=1)
            service_rating = st.slider("Rate the service", min_value=1, max_value=5, step=1)
            review = st.text_area("Write your review (optional)")

            if st.button("Submit Feedback"):
                # Save feedback to the Firestore database
                feedback_data = {
                    "order_id": selected_order_id,
                    "coffee": selected_item["coffee"],
                    "customer": st.session_state["authenticated_user"],
                    "branch_id": branch_id,  # Store branch_id instead of branch name
                    "coffee_rating": coffee_rating,
                    "service_rating": service_rating,
                    "review": review,
                    "submitted_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                }
                db.collection("feedbacks").add(feedback_data)
                st.success("Thank you for your feedback!")
    else:
        st.warning("You have no orders to provide feedback for.")
