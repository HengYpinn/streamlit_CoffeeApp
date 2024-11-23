# utils.py
import streamlit as st
from firebase_init import db
from menu import menu
import datetime
import stripe

# Securely set your Stripe secret key using st.secrets
stripe.api_key = st.secrets["stripe"]["stripe_secret_key"]  # Ensure you have added your key to .streamlit/secrets.toml

def validate_branch_inventory(cart, branch_id):
    # Fetch branch-specific inventory
    branch_ref = db.collection("branches").document(branch_id).get()
    branch_data = branch_ref.to_dict()

    if not branch_data:
        st.error("Branch not found. Please contact admin.")
        return False

    inventory = branch_data.get("inventory", {})

    # Check each item in the cart
    for item in cart:
        coffee = item["coffee"]
        quantity = item["quantity"]
        requirements = menu[coffee]["requirements"]

        # Check if inventory is sufficient for all requirements
        for required_item, required_quantity in requirements.items():
            if inventory.get(required_item, 0) < required_quantity * quantity:
                st.error(
                    f"Insufficient stock for {required_item} to fulfill {quantity}x {coffee}. "
                    f"Available: {inventory.get(required_item, 0)}, Needed: {required_quantity * quantity}"
                )
                return False  # Return False if any inventory item is insufficient

    return True  # Return True if all inventory requirements are met

def save_order_to_firestore(cart, customer, branch_id):
    try:
        order_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        total_price = sum(
            menu[item["coffee"]]["price"] * item["quantity"] for item in cart
        )
        total_cost = sum(
            menu[item["coffee"]]["cost"] * item["quantity"] for item in cart
        )
        total_quantity = sum(item["quantity"] for item in cart)

        order_data = {
            "customer": customer,
            "branch_id": branch_id,
            "items": cart,  # Save all items in the cart under 'items'
            "total_quantity": total_quantity,
            "total_price": total_price,
            "total_cost": total_cost,
            "order_time": order_time,
            "prepared_time": None,  # To be updated when the order is prepared
        }
        # Add the order data as a single document
        db.collection("orders").add(order_data)

        # Update the branch inventory based on the order
        update_branch_inventory(cart, branch_id)
    except Exception as e:
        st.error(f"Error saving order: {str(e)}")

def update_branch_inventory(cart, branch_id):
    try:
        # Fetch the branch's inventory
        branch_ref = db.collection("branches").document(branch_id)
        branch_doc = branch_ref.get()

        if branch_doc.exists:
            branch_data = branch_doc.to_dict()
            inventory = branch_data.get("inventory", {})

            # Deduct items from the inventory based on the order
            for item in cart:
                coffee = item["coffee"]
                quantity = item["quantity"]
                requirements = menu[coffee]["requirements"]

                for ingredient, required_quantity in requirements.items():
                    if ingredient in inventory:
                        inventory[ingredient] = max(
                            inventory[ingredient] - (required_quantity * quantity), 0
                        )  # Ensure stock doesn't go below 0
                    else:
                        # Ingredient not in inventory
                        st.error(f"Ingredient '{ingredient}' not found in inventory for branch '{branch_id}'.")
                        return

            # Update the inventory in Firestore
            branch_ref.update({"inventory": inventory})
        else:
            st.error(f"Branch with ID '{branch_id}' not found.")
    except Exception as e:
        st.error(f"Error updating inventory: {str(e)}")

def create_checkout_session(cart, total_price, YOUR_DOMAIN):
    # Build line items for Stripe Checkout
    line_items = []
    for item in cart:
        line_items.append({
            "price_data": {
                "currency": "myr",
                "product_data": {"name": item["coffee"]},
                "unit_amount": int(menu[item["coffee"]]["price"] * 100),  # Amount in cents
            },
            "quantity": item["quantity"],
        })
    session = stripe.checkout.Session.create(
        payment_method_types=["card"],
        line_items=line_items,
        mode="payment",
        success_url=YOUR_DOMAIN + '?session_id={CHECKOUT_SESSION_ID}',
        cancel_url=YOUR_DOMAIN + '?canceled=true',
    )
    return session
