#!/bin/bash

echo "📦 Updating system and installing dependencies..."
sudo apt update -y
sudo apt install -y python3 python3-pip python3-venv mysql-server libxml2-dev libxslt1-dev

echo "🔐 Starting and securing MySQL..."
sudo systemctl start mysql

echo "🧪 Creating virtual environment..."
python3 -m venv venv
source venv/bin/activate

echo "📄 Installing Python packages..."
pip install --upgrade pip
pip install -r requirements.txt

echo "💾 Creating MySQL database and tables..."
# Modify this block if you want to use a specific password or user later
mysql -u root <<EOF
CREATE DATABASE IF NOT EXISTS MyShop;

USE MyShop;

CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    email VARCHAR(255) NOT NULL,
    password VARCHAR(255) NOT NULL,
    role VARCHAR(50) DEFAULT 'user'
);

CREATE TABLE IF NOT EXISTS otp_flows (
    flow_id VARCHAR(64) PRIMARY KEY,
    email VARCHAR(255) NOT NULL,
    otp VARCHAR(10) NOT NULL,
    valid_until DATETIME NOT NULL
);
EOF

echo "🛠️ Creating default config.py..."
cat <<EOL > config.py
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "",  
    "database": "MyShop"
}

EMAIL_ADDRESS = "your-email@gmail.com"        # <-- Replace with your email
EMAIL_PASSWORD = "your-app-password-here"     # <-- Replace with app password
EOL

echo "📦 Creating default products.xml..."
cat <<EOL > products.xml
<?xml version="1.0" encoding="UTF-8"?>
<catalog>
</catalog>
EOL

echo "🚀 Running Flask app (ctrl+c to stop)"
export FLASK_APP=app.py
flask run --host=0.0.0.0 --port=5000
