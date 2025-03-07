# Resume Roast - AI Edition 🔥

A fun web application that uses Google's Gemini AI to roast your resume in a humorous, sarcastic way. Upload your resume and get ready for some brutal honesty wrapped in comedy!

## Features 🌟

- User authentication with secure password hashing
- Support for PDF and TXT resume uploads
- AI-powered resume roasting using Google's Gemini model
- Simple and intuitive web interface
- Secure storage of user credentials in AWS S3

## Prerequisites 📋

- Python 3.8 or higher
- A Google API key for Gemini AI
- AWS account with S3 access
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

6. **Set up AWS S3**
   - Create an S3 bucket in your AWS account
   - Create an IAM user with S3 access
   - Note down the AWS access key ID and secret access key

7. **Set up environment variables**
   - Create a `.env` file in the project root
   - Add your API keys and configuration:
     ```
     GEMINI_API_KEY=your_gemini_api_key_here
     AWS_ACCESS_KEY_ID=your_aws_access_key_id
     AWS_SECRET_ACCESS_KEY=your_aws_secret_access_key
     AWS_REGION=your_aws_region
     S3_BUCKET_NAME=your_s3_bucket_name
     ```

## AWS EC2 Setup Guide 🚀

### 1. Launch EC2 Instance
1. Log into AWS Console
2. Go to EC2 Dashboard
3. Click "Launch Instance"
4. Choose Ubuntu Server (20.04 LTS or newer)
5. Select t2.micro (free tier eligible)
6. Configure Security Group:
   - Allow SSH (Port 22)
   - Allow HTTP (Port 80)
   - Allow HTTPS (Port 443)
   - Allow Custom TCP (Port 8501) for Streamlit
7. Launch instance and save your key pair (.pem file)
8. Create Elastic IP and associate it with your instance

### 2. Install Required Software
```bash
# Update package list
sudo apt update

# Install Python and pip
sudo apt install -y python3-pip

# Install virtual environment
sudo apt install -y python3-venv

# Install git
sudo apt install -y git
```

### 3. Clone and Setup Project
```bash
# Clone the repository
git clone https://github.com/hariPrasadCoder/resume-roast-app.git
cd resume-roast-app

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 4. Create and Configure .env File

```bash
# Create .env file with content in one command
echo "GEMINI_API_KEY=your_gemini_api_key_here
AWS_ACCESS_KEY_ID=your_aws_access_key_id
AWS_SECRET_ACCESS_KEY=your_aws_secret_access_key
AWS_REGION=your_aws_region
S3_BUCKET_NAME=your_s3_bucket_name" > .env

# Set proper permissions
chmod 600 .env
```

### 5. Run the Application with Custom Domain 🌐

#### A. Set Up Nginx as Reverse Proxy
```bash
# Install Nginx
sudo apt install nginx

# Create Nginx configuration file
sudo nano /etc/nginx/sites-available/resume-roast
```

Add the following configuration:
```nginx
server {
    server_name mrpdemo.com www.mrpdemo.com;

    location / {
        proxy_pass http://localhost:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }
}
```

```bash
# Create symbolic link
sudo ln -s /etc/nginx/sites-available/resume-roast /etc/nginx/sites-enabled/

# Test Nginx configuration
sudo nginx -t

# Restart Nginx
sudo systemctl restart nginx
```

#### B. Configure DNS on your domain registrar
1. Log into your control panel
2. Go to DNS Zone Editor
3. Add an A record:
   - Type: A
   - Name: @
   - Points to: Your EC2 instance IP
   - TTL: 14400
4. Add another A record:
   - Type: A
   - Name: www
   - Points to: Your EC2 instance IP
   - TTL: 14400

#### C. Set Up SSL (Optional but Recommended)
```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx

# Obtain SSL certificate
sudo certbot --nginx -d mrpdemo.com -d www.mrpdemo.com

# Certbot will automatically configure Nginx for HTTPS
```

#### D. Run the Application as a Service
```bash
# Create a systemd service file
sudo nano /etc/systemd/system/resume-roast.service
```

Add the following content:
```ini
[Unit]
Description=Resume Roast Streamlit App
After=network.target

[Service]
User=ubuntu
WorkingDirectory=/home/ubuntu/resume-roast-app
Environment="PATH=/home/ubuntu/resume-roast-app/venv/bin"
ExecStart=/home/ubuntu/resume-roast-app/venv/bin/streamlit run main.py --server.address=0.0.0.0

[Install]
WantedBy=multi-user.target
```

```bash
# Start and enable the service
sudo systemctl start resume-roast
sudo systemctl enable resume-roast

# Check status
sudo systemctl status resume-roast
```

Your application should now be accessible at https://mrpdemo.com


## Running the Application Locally

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
