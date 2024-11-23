import firebase_admin
from firebase_admin import credentials, firestore
import streamlit as st
# Load Firebase credentials from Streamlit secrets
firebase_creds = st.secrets["firebase"]

# Convert AttrDict to a plain dictionary
firebase_creds_dict = dict(firebase_creds)

# Initialize Firebase App
cred = credentials.Certificate(firebase_creds_dict)  # Pass the plain dictionary
firebase_admin.initialize_app(cred)

# Connect to Firestore Database
db = firestore.client()
