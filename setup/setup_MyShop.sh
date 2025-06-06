#!/bin/bash

echo "📦 Updating system and installing dependencies..."
sudo apt update -y
sudo apt install -y python3 python3-pip python3-venv mysql-server libxml2-dev libxslt1-dev

echo "🔐 Starting MySQL service..."
sudo systemctl start mysql

echo "🧪 Creating virtual environment..."
python3 -m venv venv
source venv/bin/activate

echo "📄 Installing Python packages..."
pip install --upgrade pip
pip install -r requirements.txt

echo "💾 Creating MySQL database and tables..."
sudo mysql <<EOF
CREATE DATABASE IF NOT EXISTS MyShop;
CREATE USER IF NOT EXISTS 'ysf'@'localhost' IDENTIFIED BY 'YsFp@s5!';
GRANT ALL PRIVILEGES ON MyShop.* TO 'ysf'@'localhost';
FLUSH PRIVILEGES;
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
INSERT INTO users (email, password, role)
VALUES 
('admin@secdojo.me', 'Adm1NN_D0j0__', 'admin');
EOF

echo "🛠️ Creating systemd service myshop.service..."
APP_DIR=$(pwd)
USER_NAME=$(whoami)

sudo bash -c "cat > /etc/systemd/system/myshop.service" <<EOF
[Unit]
Description=Flask MyShop Application
After=network.target mysql.service

[Service]
User=${USER_NAME}
WorkingDirectory=${APP_DIR}
Environment=\"PATH=${APP_DIR}/venv/bin\"
Environment=FLASK_APP=app.py

ExecStart=${APP_DIR}/venv/bin/flask run --host=0.0.0.0 --port=5000
Restart=always

[Install]
WantedBy=multi-user.target
EOF

echo "🔄 Reloading and starting systemd service..."
sudo systemctl daemon-reexec
sudo systemctl daemon-reload
sudo systemctl enable myshop.service
sudo systemctl start myshop.service

echo "✅ MyShop is running at: http://<your-ip>:5000"