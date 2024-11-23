# promotions.py
import streamlit as st
import datetime
from firebase_init import db
from menu import menu

def promotions_management():
    st.title("Promotions & Discounts Management")

    # Fetch current promotions and filter out expired ones
    today = datetime.date.today()
    promotions_ref = db.collection("promotions").stream()
    promotions = []
    for p in promotions_ref:
        promo_data = p.to_dict()
        expiration_date = datetime.datetime.strptime(promo_data["expiration_date"], "%Y-%m-%d").date()
        if expiration_date >= today:
            promotions.append({"id": p.id, **promo_data})
        else:
            # Optionally, delete expired promotions from the database
            db.collection("promotions").document(p.id).delete()

    # Display Current Promotions and Coupons
    st.subheader("Current Promotions and Coupons")
    if promotions:
        for promo in promotions:
            # Wrap each promotion or coupon in a container
            container = st.container(border=True)
            with container:
                promo_type = promo.get('type', 'Promotion')  # Default to 'Promotion' if 'type' is not set
                if promo_type == 'Promotion':
                    st.write(f"**Promotion Name:** {promo['name']}")
                else:
                    st.write(f"**Coupon Code:** {promo['coupon_code']}")
                st.write(f"**Type:** {promo_type}")
                st.write(f"**Included Coffees:** {', '.join(promo['included_coffees'])}")
                st.write(f"**Discount (%):** {promo['discount']}")
                st.write(f"**Expiration Date:** {promo['expiration_date']}")

                terminate_key = f"terminate_{promo['id']}"
                display_name = promo.get('name') or promo.get('coupon_code')
                if st.button(f"Terminate '{display_name}'", key=terminate_key):
                    # Delete the promotion immediately without confirmation
                    db.collection("promotions").document(promo["id"]).delete()
                    st.success(f"{promo_type} '{display_name}' has been terminated.")
                    st.rerun()
    else:
        st.info("No active promotions or coupons available.")

    # Handle success message for creating a promotion
    if "promotion_success" not in st.session_state:
        st.session_state["promotion_success"] = None

    # Display success message if it exists
    if st.session_state["promotion_success"]:
        st.success(st.session_state["promotion_success"])
        st.session_state["promotion_success"] = None  # Clear after displaying

    # Add New Promotion or Coupon
    st.subheader("Create New Promotion or Coupon")
    with st.container(border=True):
        st.write("Use the form below to create a new promotion or coupon.")
        promo_type = st.selectbox("Select Type", ["Promotion", "Coupon"])
        if promo_type == "Promotion":
            promo_name = st.text_input("Promotion Name")
            coupon_code = ""
        else:
            promo_name = ""
            coupon_code = st.text_input("Coupon Code")

        included_coffees = st.multiselect("Select Coffees", list(menu.keys()))
        discount = st.number_input("Discount Percentage (1-100%)", min_value=1, max_value=100, step=1)
        expiration_date = st.date_input("Expiration Date", min_value=today)

        if st.button("Create"):
            if ((promo_type == "Promotion" and promo_name) or (promo_type == "Coupon" and coupon_code)) and included_coffees and 1 <= discount <= 100 and expiration_date:
                if expiration_date >= today:
                    new_promo = {
                        "type": promo_type,
                        "name": promo_name,
                        "coupon_code": coupon_code,
                        "included_coffees": included_coffees,
                        "discount": discount,
                        "expiration_date": expiration_date.strftime("%Y-%m-%d"),
                    }
                    db.collection("promotions").add(new_promo)

                    # Store success message in session state
                    display_name = promo_name if promo_type == "Promotion" else coupon_code
                    st.session_state["promotion_success"] = f"{promo_type} '{display_name}' created successfully!"
                    st.rerun()
                else:
                    st.error("Expiration date must be today or in the future.")
            else:
                st.error("Please fill in all fields and ensure the discount is between 1% and 100%.")
