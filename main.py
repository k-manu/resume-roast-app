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

# ======================
# Configuration Settings
# ======================

# Load environment variables from .env file
load_dotenv()

# Configure Google's Generative AI (Gemini) with API key
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))

# Configure AWS S3
s3_client = boto3.client(
    's3',
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
    region_name=os.getenv('AWS_REGION'),
    verify=True,  # Enable SSL verification
    use_ssl=True,  # Use SSL/TLS for connections
    config=boto3.session.Config(
        signature_version='s3v4',
        retries={'max_attempts': 3},
    )
)
S3_BUCKET = os.getenv('S3_BUCKET_NAME')
S3_USERS_KEY = 'users/credentials.json'

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
# S3 Utility Functions
# ======================

def get_users_from_s3() -> dict:
    """
    Load user credentials from S3.
    
    Returns:
        dict: Dictionary containing username-password pairs
    """
    try:
        response = s3_client.get_object(Bucket=S3_BUCKET, Key=S3_USERS_KEY)
        users_data = json.loads(response['Body'].read().decode('utf-8'))
        return users_data
    except s3_client.exceptions.NoSuchKey:
        # If file doesn't exist, return empty dict
        return {}
    except Exception as e:
        st.error(f"Error accessing S3: {str(e)}")
        return {}

def save_users_to_s3(users_data: dict) -> bool:
    """
    Save user credentials to S3.
    
    Args:
        users_data (dict): Dictionary containing username-password pairs
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        users_json = json.dumps(users_data)
        s3_client.put_object(
            Bucket=S3_BUCKET,
            Key=S3_USERS_KEY,
            Body=users_json
        )
        return True
    except Exception as e:
        st.error(f"Error saving to S3: {str(e)}")
        return False

# ======================
# User Management Functions
# ======================

def save_user(username: str, password: str) -> bool:
    """
    Save a new user with a hashed password to S3.

    Args:
        username (str): The user's chosen username
        password (str): The user's plain text password (will be hashed before saving)
        
    Returns:
        bool: True if successful, False otherwise
    """
    users = get_users_from_s3()
    if username not in users:
        users[username] = hash_password(password)
        return save_users_to_s3(users)
    return False

def authenticate(username: str, password: str) -> bool:
    """
    Verify user credentials against S3 stored credentials.

    Args:
        username (str): The username to verify
        password (str): The plain text password to verify

    Returns:
        bool: True if credentials are valid, False otherwise
    """
    users = get_users_from_s3()
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
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Login")
            login_username = st.text_input("Username", key="login_username")
            login_password = st.text_input("Password", type="password", key="login_password")
            
            if st.button("Login"):
                if authenticate(login_username, login_password):
                    st.session_state["authenticated"] = True
                    st.session_state["username"] = login_username
                    st.rerun()
                else:
                    st.error("Invalid username or password")
        
        with col2:
            st.subheader("Sign Up")
            signup_username = st.text_input("Choose Username", key="signup_username")
            signup_password = st.text_input("Choose Password", type="password", key="signup_password")
            
            if st.button("Sign Up"):
                if signup_username and signup_password:  # Basic validation
                    save_user(signup_username, signup_password)
                    st.success("Signup successful! Please login.")
                else:
                    st.error("Please provide both username and password")

        # Add "Continue as Guest" option
        st.markdown("---")  # Separator for better UI
        if st.button("Continue as Guest"):
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