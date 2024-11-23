# order.py
import streamlit as st
import stripe

from firebase_init import db
from menu import menu
from utils import validate_branch_inventory, save_order_to_firestore, create_checkout_session
import datetime
import os
from PIL import Image
import webbrowser

def customer_order():
    st.title("Order")

    # Fetch branch data from Firestore
    branches_ref = db.collection("branches").stream()
    branches = [{"Branch Name": b.to_dict()["cafe_name"], "Branch ID": b.id} for b in branches_ref]

    if not branches:
        st.warning("No branches available. Please contact admin.")
    else:
        # Branch selection
        with st.container(border=True):
            st.subheader("Select Branch")
            branch_names = [branch["Branch Name"] for branch in branches]
            selected_branch_name = st.selectbox("Select Branch to Order From", branch_names)
            selected_branch = next(branch for branch in branches if branch["Branch Name"] == selected_branch_name)
            selected_branch_id = selected_branch["Branch ID"]

        # Initialize session state for quantity reset
        if "reset_quantity" not in st.session_state:
            st.session_state["reset_quantity"] = False

        # Display menu
        st.subheader(f"Menu at {selected_branch_name}")
        menu_items = list(menu.items())  # Convert menu dictionary to a list of tuples
        num_items = len(menu_items)
        cols_per_row = 2  # Adjust the number of columns per row as needed

        for i in range(0, num_items, cols_per_row):
            cols = st.columns(cols_per_row)
            for idx, (coffee, details) in enumerate(menu_items[i:i + cols_per_row]):
                with cols[idx]:
                    # Display coffee image
                    if os.path.exists(details["image_path"]):
                        image = Image.open(details["image_path"])
                        resized_image = image.resize((300, 200))  # Resize to a consistent size
                        st.image(resized_image, use_container_width=True)
                    else:
                        st.error(f"Image not found for {coffee}. Please check the file path.")

                    # Display coffee details
                    st.markdown(f"### {coffee}")
                    st.markdown(f"**Price:** RM{details['price']:.2f}")
                    st.write(details["description"])

                    # Quantity input and "Add to Cart" button
                    quantity = st.number_input(
                        f"Quantity of {coffee}",
                        min_value=0,
                        step=1,
                        key=f"qty_{coffee}",
                        value=0 if st.session_state["reset_quantity"] else None,
                    )
                    if st.button(f"Add {coffee} to Cart", key=f"add_{coffee}"):
                        if quantity > 0:
                            if "cart" not in st.session_state:
                                st.session_state["cart"] = []
                            # Update cart to combine items with the same coffee and branch
                            existing_item = next(
                                (item for item in st.session_state["cart"]
                                 if item["coffee"] == coffee and item["branch_id"] == selected_branch_id),
                                None
                            )
                            if existing_item:
                                existing_item["quantity"] += quantity
                            else:
                                st.session_state["cart"].append(
                                    {"coffee": coffee, "quantity": quantity, "branch_id": selected_branch_id}
                                )
                            # Clear checkout message when a new item is added
                            st.session_state["checkout_message"] = None
                            st.session_state["reset_quantity"] = False
                            st.success(f"Added {quantity}x {coffee} to cart from {selected_branch_name}.", icon="✅")
                        else:
                            st.error("Please select a quantity greater than 0.")

        # Display the checkout success message if it exists
        if "checkout_message" in st.session_state and st.session_state["checkout_message"]:
            st.success(st.session_state["checkout_message"], icon="🎉")

        # Display cart
        if "cart" in st.session_state and st.session_state["cart"]:
            with st.container(border=True):
                st.subheader("Cart")
                cart_items = st.session_state["cart"]
                for idx, item in enumerate(cart_items):
                    branch = next(branch for branch in branches if branch["Branch ID"] == item["branch_id"])
                    st.write(f"{item['quantity']}x {item['coffee']} (Branch: {branch['Branch Name']})")
                    if st.button(f"Remove", key=f"remove_{idx}"):
                        st.session_state["cart"].pop(idx)
                        st.rerun()

            # Apply coupon code
            with st.container(border=True):
                st.subheader("Apply Coupon or Voucher")
                coupon_code = st.text_input("Enter Coupon Code")
                if st.button("Validate Coupon"):
                    promo_docs = db.collection("promotions").where("type", "==", "Coupon").stream()
                    matching_coupon = next(
                        (doc.to_dict() for doc in promo_docs if doc.to_dict().get("coupon_code") == coupon_code), None
                    )
                    if matching_coupon:
                        expiration_date = datetime.datetime.strptime(matching_coupon["expiration_date"], "%Y-%m-%d").date()
                        if expiration_date >= datetime.date.today():
                            st.session_state["applied_coupon"] = matching_coupon
                            st.success(f"Coupon '{coupon_code}' applied successfully!")
                        else:
                            st.error(f"Coupon '{coupon_code}' has expired.")
                    else:
                        st.error("Invalid coupon code.")

            # Fetch applicable promotions
            cart_coffees = [item["coffee"] for item in st.session_state["cart"]]
            promotions_ref = db.collection("promotions").where("type", "==", "Promotion").stream()

            # Convert Firestore documents to dictionaries
            applicable_promotions = [
                promo.to_dict() for promo in promotions_ref
                if any(coffee in promo.to_dict().get("included_coffees", []) for coffee in cart_coffees)
            ]

            # Display applicable promotions
            if applicable_promotions:
                with st.container(border=True):
                    st.subheader("Available Vouchers")
                    for promo in applicable_promotions:
                        st.write(f"**{promo['name']}**: {promo['discount']}% off for "
                                 f"{', '.join(promo['included_coffees'])} (Expires: {promo['expiration_date']})")
                        if st.button(f"Apply '{promo['name']}'", key=promo['name']):
                            st.session_state["applied_promotion"] = promo
                            st.success(f"Voucher '{promo['name']}' applied!")

            # Final price and checkout
            with st.container(border=True):
                st.subheader("Final Price and Checkout")
                total_price = sum(
                    menu[item["coffee"]]["price"] * item["quantity"] for item in st.session_state["cart"]
                )
                applied_discount = 0

                # Apply promotion discount
                if "applied_promotion" in st.session_state and st.session_state["applied_promotion"]:
                    promo = st.session_state["applied_promotion"]
                    if "included_coffees" in promo:  # Ensure promo is valid
                        for item in st.session_state["cart"]:
                            if item["coffee"] in promo["included_coffees"]:
                                applied_discount += (
                                    menu[item["coffee"]]["price"] * item["quantity"] * promo["discount"] / 100
                                )

                # Apply coupon discount
                if "applied_coupon" in st.session_state and st.session_state["applied_coupon"]:
                    coupon = st.session_state["applied_coupon"]
                    if "included_coffees" in coupon:  # Ensure coupon is valid
                        for item in st.session_state["cart"]:
                            if item["coffee"] in coupon["included_coffees"]:
                                applied_discount += (
                                    menu[item["coffee"]]["price"] * item["quantity"] * coupon["discount"] / 100
                                )

                total_price -= applied_discount
                total_price = max(total_price, 0)  # Ensure total is not negative
                st.write(f"**Total Price (after discount): RM{total_price:.2f}**")

                if st.button("Checkout"):
                    cart = st.session_state.get("cart", [])
                    if cart:
                        if validate_branch_inventory(cart, selected_branch_id):
                            # Save order to Firestore and get the order ID
                            order_ref = db.collection("orders").add({
                                "branch_id": selected_branch_id,
                                "customer": st.session_state.get("authenticated_user", "guest"),
                                "items": cart,
                                "total_cost": total_price,
                                "order_time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                "prepared_time": None,
                            })
                            order_id = order_ref[1].id  # Get the generated order ID from Firestore
                            st.session_state["checkout_message"] = (
                                f"Order placed successfully from {selected_branch_name} with Order ID: {order_id}!"
                            )
                            st.success(st.session_state["checkout_message"], icon="🎉")

                            try:
                                # Create Stripe price object
                                stripe_price = stripe.Price.create(
                                    currency="myr",
                                    unit_amount=int(total_price * 100),  # Convert to cents
                                    product_data={"name": "Coffee Order"},
                                )

                                # Create Stripe checkout session
                                session = stripe.checkout.Session.create(
                                    line_items=[
                                        {"price": stripe_price['id'], "quantity": 1}
                                    ],
                                    mode="payment",
                                    success_url="https://example.com/success",
                                    cancel_url="https://example.com/cancel",
                                )

                                # Open the checkout session URL
                                webbrowser.open(session.url, new=0)

                                # Retrieve the session and display payment status
                                st.write("Redirecting to payment gateway...")
                                payment_session = stripe.checkout.Session.retrieve(session.id)
                                st.write(f"Payment Status: {payment_session.payment_status}")
                            except Exception as e:
                                st.error(f"Stripe checkout session failed: {str(e)}")

                            # Clear cart and set reset_quantity flag
                            st.session_state["cart"] = []
                            st.session_state["applied_promotion"] = None
                            st.session_state["applied_coupon"] = None
                            st.session_state["reset_quantity"] = True
                            st.rerun()
                        else:
                            st.error("Insufficient inventory at the selected branch to fulfill the order.")
                    else:
                        st.error("Your cart is empty. Add items to proceed with checkout.")
