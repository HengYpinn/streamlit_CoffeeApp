# main.py
import streamlit as st
from firebase_init import db  # Firebase setup
from auth import authenticate_user, initialize_session_state, login_signup
from menu import menu
from inventory import inventory_management
from sales_reporting import sales_reporting
from analytics import analytics_dashboard
from promotions import promotions_management
from order import customer_order
from order_history import order_history
from pickup_notification import pickup_notification
from feedback import feedback
from notification import notification_management
from utils import validate_branch_inventory

# Initialize session state
initialize_session_state()

# Login and Signup Page
if not st.session_state["authenticated_user"]:
    login_signup()
else:
    if st.session_state["role"] == "admin":
        nav = st.sidebar.radio(
            "Admin Navigation",
            [
                "Inventory Management",
                "Sales Reporting",
                "Analytics Dashboard",
                "Promotions & Discounts",
                "Notification",
            ],
        )
    else:
        nav = st.sidebar.radio(
            "Customer Navigation",
            ["Order", "Order History", "Pickup Notification", "Feedback"],
        )

    # Logout button
    if st.sidebar.button("Log out"):
        st.session_state["authenticated_user"] = None
        st.session_state["role"] = None
        st.rerun()

    # Navigation
    if st.session_state["role"] == "admin":
        if nav == "Inventory Management":
            inventory_management()
        elif nav == "Sales Reporting":
            sales_reporting()
        elif nav == "Analytics Dashboard":
            analytics_dashboard()
        elif nav == "Promotions & Discounts":
            promotions_management()
        elif nav == "Notification":
            notification_management()
    else:
        if nav == "Order":
            customer_order()
        elif nav == "Order History":
            order_history()
        elif nav == "Pickup Notification":
            pickup_notification()
        elif nav == "Feedback":
            feedback()