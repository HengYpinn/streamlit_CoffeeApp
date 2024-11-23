# auth.py
import streamlit as st
from firebase_init import db

def initialize_session_state():
    if "authenticated_user" not in st.session_state:
        st.session_state["authenticated_user"] = None
    if "role" not in st.session_state:
        st.session_state["role"] = None
    if "cart" not in st.session_state:
        st.session_state["cart"] = []
    if "signup_mode" not in st.session_state:
        st.session_state["signup_mode"] = False

def authenticate_user(username, password, role):
    users_ref = db.collection("users").where("username", "==", username).where("role", "==", role.lower()).stream()
    for user_doc in users_ref:
        user = user_doc.to_dict()
        if user.get("password") == password:
            return user
    return None

def login_signup():
    st.title("Login" if not st.session_state["signup_mode"] else "Sign Up")

    if not st.session_state["signup_mode"]:
        # Login Interface
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        role = st.radio("Login as", ["Admin", "Customer"])
        if st.button("Login"):
            user = authenticate_user(username, password, role)
            if user:
                st.session_state["authenticated_user"] = username
                st.session_state["role"] = role.lower()
                st.success(f"Logged in as {role}.")
                st.rerun()
            else:
                st.error("Invalid username or password.")
        if role == "Customer" and st.button("Create an Account"):
            st.session_state["signup_mode"] = True
            st.rerun()
    else:
        # Signup Interface
        new_username = st.text_input("New Username")
        new_password = st.text_input("New Password", type="password")
        if st.button("Create Account"):
            db.collection("users").add({"username": new_username, "password": new_password, "role": "customer"})
            st.success("Account created successfully! Please log in.")
            st.session_state["signup_mode"] = False
            st.rerun()
