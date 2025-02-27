# Resume Roast - AI Edition 🔥

A fun web application that uses Google's Gemini AI to roast your resume in a humorous, sarcastic way. Upload your resume and get ready for some brutal honesty wrapped in comedy!

## Features 🌟

- User authentication with secure password hashing
- Support for PDF and TXT resume uploads
- AI-powered resume roasting using Google's Gemini model
- Simple and intuitive web interface
- Secure storage of user credentials

## Prerequisites 📋

- Python 3.8 or higher
- A Google API key for Gemini AI
- Internet connection

## Setup Instructions 🚀

1. **Clone the repository**
   ```bash
   git clone https://github.com/hariPrasadCoder/resume-roast-app.git
   cd resume-roast-app
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   ```

3. **Activate the virtual environment**
   - On Windows:
     ```bash
     venv\Scripts\activate
     ```
   - On macOS/Linux:
     ```bash
     source venv/bin/activate
     ```

4. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

5. **Get your Google API Key**
   - Visit the [Google AI Studio](https://aistudio.google.com/apikey)
   - Sign in with your Google account
   - Create a new API key
   - Copy the API key

6. **Set up environment variables**
   - Create a `.env` file in the project root
   - Add your API key:
     ```
     GEMINI_API_KEY=your_api_key_here
     ```

## Running the Application 🏃‍♂️

1. **Ensure your virtual environment is activated**

2. **Start the Streamlit server**
   ```bash
   python -m streamlit run main.py
   ```

3. **Access the application**
   - Open your web browser
   - Navigate to `http://localhost:8501`

## Usage Guide 📖

1. **First-time users**
   - Click the "Signup" button in the sidebar
   - Create your username and password
   - Login with your credentials

2. **Returning users**
   - Enter your username and password
   - Click "Login"

3. **Getting your resume roasted**
   - Upload your resume (PDF or TXT format)
   - Click "Roast my resume"
   - Wait for the AI to generate its humorous critique
   - Enjoy the roast! 🔥

## Security Notes 🔒

- Passwords are securely hashed using SHA-256
- Never share your API key
- Keep your `.env` file private

## Troubleshooting 🔧

- If you get API errors, verify your API key in the `.env` file
- Make sure all dependencies are installed correctly
- Check if your resume file is in PDF or TXT format
- Ensure you have a stable internet connection

## Contributing 🤝

Feel free to fork this repository and submit pull requests. For major changes, please open an issue first to discuss what you would like to change.

## License 📄

[MIT License](LICENSE)

## Acknowledgments 👏

- Google Gemini AI for the roasting capabilities
- Streamlit for the awesome web framework
- All contributors and users of this project
