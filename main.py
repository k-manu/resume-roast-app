import streamlit as st
import google.generativeai as genai
import pandas as pd
import os
import PyPDF2
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure Gemini API using environment variable
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))

def roast_resume(resume_text):
    prompt = f"""Roast my resume in a fun, sarcastic, and brutally honest way. 
            Pretend I'm your friend, and feel free to be a bit dark and mature with the humor. 
            Keep it cringe-worthy, casual, and add in some dad jokes if they fit. 
            Don't hold back—make it simple, sharp, and to the point, with a total word count under 150. 
            My Resume:
            {resume_text}"""
    model = genai.GenerativeModel("gemini-2.0-pro-exp-02-05")
    response = model.generate_content(prompt)
    return response.text if response else "No response from AI."

def load_users():
    try:
        return pd.read_csv("users.csv")
    except FileNotFoundError:
        return pd.DataFrame(columns=["username", "password"])

def save_user(username, password):
    users = load_users()
    if username not in users["username"].values:
        new_user = pd.DataFrame({"username": [username], "password": [password]})
        users = pd.concat([users, new_user], ignore_index=True)
        users.to_csv("users.csv", index=False)

def authenticate(username, password):
    users = load_users()
    return ((users["username"] == username) & (users["password"] == password)).any()

st.title("Resume Roast - AI Edition")
st.sidebar.header("Login / Signup")

username = st.sidebar.text_input("Username")
password = st.sidebar.text_input("Password", type="password")

if st.sidebar.button("Login"):
    if authenticate(username, password):
        st.sidebar.success(f"Welcome {username}!")
        st.session_state["authenticated"] = True
    else:
        st.sidebar.error("Invalid username or password")

if st.sidebar.button("Signup"):
    save_user(username, password)
    st.sidebar.success("Signup successful. Please login.")

if "authenticated" in st.session_state and st.session_state["authenticated"]:
    st.write("Upload your resume and let AI roast it!")
    uploaded_file = st.file_uploader("Upload your resume (PDF or TXT)", type=["pdf", "txt"])
    
    if uploaded_file:
        if uploaded_file.type == "application/pdf":
            try:
                pdf_reader = PyPDF2.PdfReader(uploaded_file)
                resume_text = []
                for page in pdf_reader.pages:
                    text = page.extract_text()
                    # Clean up the text: normalize spaces and add line breaks
                    text = ' '.join(text.split())  # Normalize multiple spaces into single spaces
                    resume_text.append(text)
                resume_text = '\n\n'.join(resume_text)  # Add double line breaks between pages
            except Exception as e:
                st.error(f"Error reading PDF: {str(e)}")
                resume_text = ""
        else:  # For txt files
            resume_text = uploaded_file.read().decode("utf-8")
        print(resume_text)
        if resume_text:  # Only proceed if we have text content
            if st.button("Roast my resume"):
                with st.spinner("Roasting in progress..."):
                    roast_result = roast_resume(resume_text)
                    st.subheader("🔥 AI's Roast of Your Resume 🔥")
                    st.write(roast_result)

    if st.sidebar.button("Logout"):
        st.session_state.pop("authenticated")
        st.rerun()