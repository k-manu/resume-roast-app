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