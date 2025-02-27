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

# Third-party imports
import streamlit as st
import google.generativeai as genai
import pandas as pd
import PyPDF2
from dotenv import load_dotenv

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
# User Management Functions
# ======================

def load_users() -> pd.DataFrame:
    """
    Load the user database from CSV file or create a new one if it doesn't exist.

    Returns:
        pd.DataFrame: DataFrame containing username and hashed password columns
    """
    try:
        return pd.read_csv("users.csv")
    except FileNotFoundError:
        return pd.DataFrame(columns=["username", "password"])

def save_user(username: str, password: str) -> None:
    """
    Save a new user to the database with a hashed password.

    Args:
        username (str): The user's chosen username
        password (str): The user's plain text password (will be hashed before saving)
    """
    users = load_users()
    if username not in users["username"].values:
        hashed_password = hash_password(password)
        new_user = pd.DataFrame({
            "username": [username], 
            "password": [hashed_password]
        })
        users = pd.concat([users, new_user], ignore_index=True)
        users.to_csv("users.csv", index=False)

def authenticate(username: str, password: str) -> bool:
    """
    Verify user credentials against the stored database.

    Args:
        username (str): The username to verify
        password (str): The plain text password to verify

    Returns:
        bool: True if credentials are valid, False otherwise
    """
    users = load_users()
    hashed_password = hash_password(password)
    return ((users["username"] == username) & 
            (users["password"] == hashed_password)).any()

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
    
    # Sidebar authentication
    st.sidebar.header("Login / Signup")
    username = st.sidebar.text_input("Username")
    password = st.sidebar.text_input("Password", type="password")

    # Handle login
    if st.sidebar.button("Login"):
        if authenticate(username, password):
            st.sidebar.success(f"Welcome {username}!")
            st.session_state["authenticated"] = True
        else:
            st.sidebar.error("Invalid username or password")

    # Handle signup
    if st.sidebar.button("Signup"):
        if username and password:  # Basic validation
            save_user(username, password)
            st.sidebar.success("Signup successful. Please login.")
        else:
            st.sidebar.error("Please provide both username and password")

    # Main application area (only shown to authenticated users)
    if "authenticated" in st.session_state and st.session_state["authenticated"]:
        st.write("Upload your resume and let AI roast it!")
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

        # Logout button
        if st.sidebar.button("Logout"):
            st.session_state.pop("authenticated")
            st.rerun()

# ======================
# Application Entry Point
# ======================

if __name__ == "__main__":
    main()