import streamlit as st
import hashlib
from utils.db import get_user_by_email, create_user

def make_hash(password):
    """Create a secure SHA-256 hash of the password"""
    return hashlib.sha256(str.encode(password)).hexdigest()

def check_hashes(password, hashed_text):
    """Verify a password against its hash"""
    return make_hash(password) == hashed_text

def login_ui():
    """Renders the Login/Signup Sidebar"""
    st.sidebar.markdown("## 🔐 Member Access")
    
    # Toggle between Login and Signup
    auth_mode = st.sidebar.radio("I want to:", ["Log In", "Sign Up"])

    if auth_mode == "Log In":
        email = st.sidebar.text_input("Email", key="login_email")
        password = st.sidebar.text_input("Password", type="password", key="login_pw")
        
        if st.sidebar.button("Log In"):
            user = get_user_by_email(email)
            if user:
                # Verify Password
                if check_hashes(password, user['password_hash']):
                    st.session_state.authenticated = True
                    st.session_state.user = user
                    st.rerun()
                else:
                    st.sidebar.error("Wrong password")
            else:
                st.sidebar.error("User not found")

    else: # Sign Up
        new_email = st.sidebar.text_input("New Email", key="su_email")
        new_user = st.sidebar.text_input("Username", key="su_user")
        new_pass = st.sidebar.text_input("New Password", type="password", key="su_pass")
        
        if st.sidebar.button("Create Account"):
            if not new_email or not new_user or not new_pass:
                st.sidebar.error("Please fill in all fields")
            else:
                # Create secure hash before saving to DB
                secure_pw = make_hash(new_pass)
                if create_user(new_email, new_user, secure_pw):
                    st.sidebar.success("Account created! Please Log In.")
                else:
                    st.sidebar.error("Email already exists")

    return st.session_state.get('authenticated', False)