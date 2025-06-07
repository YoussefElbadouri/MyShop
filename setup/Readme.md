#  MyShop

**MyShop** is a simple e-commerce web application developed with **Flask**.

---

##  Installation on ec2 ubuntu 24.04

### 1. Clone the repository

```bash
git clone https://github.com/sec-dojo-com/MyShop
cd MyShop/setup
```

### 2. Make the script executable and run it

```bash
chmod +x setup_MyShop.sh
./setup_MyShop.sh
```

This script will:
Install system dependencies (Python, pip, MySQL, etc.)
Create a virtual environmentInstall Python packages (requirements.txt)
Create the MyShop database with the users and otp_flows tables and the admin account
Create the myshop.service systemd service and launch the application


## Access the application

Open your browser and access to the port 5000 :

```
http://<your-ip>:5000
```
