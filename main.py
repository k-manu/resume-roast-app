"""
Resume Roast - AI Edition
-------------------------
A Streamlit web application that uses Gemini AI to humorously critique resumes.
The app includes user authentication and supports PDF/TXT resume uploads.

Main Features:
- User registration and authentication with secure password hashing
- PDF and TXT file upload and processing
- AI-powered resume roasting using Google's Gemini model
- Simple and intuitive web interface using Streamlit

Author: [Your Name]
Date: [Current Date]
"""

# Standard library imports
import os
import hashlib
import json
import io

# Third-party imports
import streamlit as st
import google.generativeai as genai
import pandas as pd
import PyPDF2
from dotenv import load_dotenv
import boto3

# Add csv import
import csv
import os.path

# ======================
# Configuration Settings
# ======================

# Load environment variables from .env file
load_dotenv()

# Configure Google's Generative AI (Gemini) with API key
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))

# ======================
# Security Functions
# ======================

def hash_password(password: str) -> str:
    """
    Convert a plain text password into a hashed version using SHA-256.

    Args:
        password (str): The plain text password to hash

    Returns:
        str: The hexadecimal representation of the hashed password
    """
    return hashlib.sha256(password.encode()).hexdigest()

# ======================
# CSV Utility Functions
# ======================

def get_users_from_csv() -> dict:
    """
    Load user credentials from CSV file.
    
    Returns:
        dict: Dictionary containing username-password pairs
    """
    users_data = {}
    csv_file = 'user_credentials.csv'
    
    # Create file if it doesn't exist
    if not os.path.exists(csv_file):
        with open(csv_file, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['username', 'password'])  # Write header
        return users_data
        
    try:
        with open(csv_file, 'r', newline='') as f:
            reader = csv.DictReader(f)
            for row in reader:
                users_data[row['username']] = row['password']
        return users_data
    except Exception as e:
        st.error(f"Error reading CSV: {str(e)}")
        return {}

def save_users_to_csv(users_data: dict) -> bool:
    """
    Save user credentials to CSV file.
    
    Args:
        users_data (dict): Dictionary containing username-password pairs
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        with open('user_credentials.csv', 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['username', 'password'])  # Write header
            for username, password in users_data.items():
                writer.writerow([username, password])
        return True
    except Exception as e:
        st.error(f"Error saving to CSV: {str(e)}")
        return False

# ======================
# User Management Functions
# ======================

def save_user(username: str, password: str) -> bool:
    """
    Save a new user with a hashed password to CSV.
    """
    users = get_users_from_csv()
    if username not in users:
        users[username] = hash_password(password)
        return save_users_to_csv(users)
    return False

def authenticate(username: str, password: str) -> bool:
    """
    Verify user credentials against CSV stored credentials.
    """
    users = get_users_from_csv()
    hashed_password = hash_password(password)
    return username in users and users[username] == hashed_password

# ======================
# AI Processing Functions
# ======================

def roast_resume(resume_text: str) -> str:
    """
    Process resume text through Gemini AI for a humorous critique.

    Args:
        resume_text (str): The text content of the resume to analyze

    Returns:
        str: AI-generated humorous critique of the resume
    """
    prompt = f"""Roast my resume in a fun, sarcastic, and brutally honest way. 
            Pretend I'm your friend, and feel free to be a bit dark and mature with the humor. 
            Keep it cringe-worthy, casual, and add in some dad jokes if they fit. 
            Don't hold back—make it simple, sharp, and to the point, with a total word count under 150. 
            My Resume:
            {resume_text}"""
    
    # Initialize and use the Gemini AI model
    model = genai.GenerativeModel("gemini-2.0-pro-exp-02-05")
    response = model.generate_content(prompt)
    return response.text if response else "No response from AI."

# ======================
# Main Application UI
# ======================

def main():
    """Main function that sets up the Streamlit UI and handles user interaction."""
    
    st.title("Resume Roast - AI Edition")
    
    # Initialize session state for tracking the current view
    if "view" not in st.session_state:
        st.session_state.view = "login"  # Default view is login
    
    # Show authentication page if not logged in
    if "authenticated" not in st.session_state or not st.session_state["authenticated"]:
        # Create tabs for Login and Sign Up
        login_tab, signup_tab = st.tabs(["Login", "Sign Up"])
        
        with login_tab:
            st.subheader("Login")
            login_username = st.text_input("Username", key="login_username")
            login_password = st.text_input("Password", type="password", key="login_password")
            
            if st.button("Login", use_container_width=True):
                if authenticate(login_username, login_password):
                    st.session_state["authenticated"] = True
                    st.session_state["username"] = login_username
                    st.rerun()
                else:
                    st.error("Invalid username or password")
        
        with signup_tab:
            st.subheader("Sign Up")
            signup_username = st.text_input("Choose Username", key="signup_username")
            signup_password = st.text_input("Choose Password", type="password", key="signup_password")
            
            if st.button("Sign Up", use_container_width=True):
                if signup_username and signup_password:  # Basic validation
                    if save_user(signup_username, signup_password):
                        st.success("Signup successful! Please go to the Login tab.")
                    else:
                        st.error("Username already exists. Please choose another.")
                else:
                    st.error("Please provide both username and password")

        # Add "Continue as Guest" option
        st.markdown("---")  # Separator for better UI
        if st.button("Continue as Guest", use_container_width=True):
            st.session_state["authenticated"] = True
            st.session_state["username"] = "Guest"
            st.rerun()
    
    # Show main application only after authentication
    else:
        # Show welcome message and logout button in a horizontal layout
        col1, col2 = st.columns([3, 1])
        with col1:
            st.write(f"Welcome, {st.session_state.get('username', '')}! 👋")
        with col2:
            if st.button("Logout"):
                st.session_state.clear()
                st.rerun()
        
        st.write("---")  # Divider
        
        # Main application content
        st.write("Upload your resume and let AI roast it! 🔥")
        uploaded_file = st.file_uploader("Upload your resume (PDF or TXT)", 
                                       type=["pdf", "txt"])
        
        if uploaded_file:
            resume_text = ""
            
            # Handle PDF files
            if uploaded_file.type == "application/pdf":
                try:
                    pdf_reader = PyPDF2.PdfReader(uploaded_file)
                    resume_text = []
                    for page in pdf_reader.pages:
                        text = page.extract_text()
                        # Clean up the text: normalize spaces
                        text = ' '.join(text.split())
                        resume_text.append(text)
                    resume_text = '\n\n'.join(resume_text)
                except Exception as e:
                    st.error(f"Error reading PDF: {str(e)}")
            
            # Handle TXT files
            else:
                resume_text = uploaded_file.read().decode("utf-8")

            # Process the resume if we have content
            if resume_text:
                if st.button("Roast my resume"):
                    with st.spinner("Roasting in progress..."):
                        roast_result = roast_resume(resume_text)
                        st.subheader("🔥 AI's Roast of Your Resume 🔥")
                        st.write(roast_result)

# ======================
# Application Entry Point
# ======================

if __name__ == "__main__":
    main()