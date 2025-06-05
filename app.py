from flask import Flask, render_template, request, redirect, url_for, session, flash
from datetime import datetime, timedelta
import mysql.connector
import secrets
import time
from uuid import uuid4
import smtplib
from email.message import EmailMessage
from config import DB_CONFIG, EMAIL_ADDRESS, EMAIL_PASSWORD
from datetime import timezone
import socket
import xml.etree.ElementTree as ET
from config import DB_CONFIG
from lxml import etree
app = Flask(__name__)
app.secret_key = 'supersecretkey'


def send_otp_email(to_email, otp_code):
    msg = EmailMessage()
    msg['Subject'] = 'Your OTP Code'
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = to_email
    msg.set_content(f"Here is your OTP code: {otp_code}\nIt is valid for 5 minutes.")

    try:
        socket.setdefaulttimeout(3)
        with smtplib.SMTP_SSL('smtp.gmail.com', 465, timeout=3) as smtp:
            smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            smtp.send_message(msg)
        print(f"[MAIL SENT] OTP {otp_code} sent to {to_email}")
    except Exception as e:
        print(f"[MAIL ERROR] Could not send to {to_email}: {e}")
    finally:
        
        socket.setdefaulttimeout(None)

@app.route("/")
def home():
    import xml.etree.ElementTree as ET

    products = []

    try:
        tree = ET.parse("products.xml")  
        root = tree.getroot()

        for product in root.findall("product"):
            name = product.find("name").text
            price = product.find("price").text
            description = product.find("description").text
            

            products.append({
                "name": name,
                "price": price,
                "description": description,
                
            })

    except Exception as e:
        products = [{"name": "Error loading products", "price": "N/A", "description": str(e)}]

    return render_template("index.html", products=products)



@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        role = "user"

        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO users (email, password, role) VALUES (%s, %s, %s)", (email, password, role))
            conn.commit()
            flash("Account created!", "success")
            return redirect(url_for("login"))
        except mysql.connector.Error as err:
            flash(f"Error: {err}", "danger")
        finally:
            cursor.close()
            conn.close()

    return render_template("signup.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE email = %s AND password = %s", (email, password))
        user = cursor.fetchone()
        cursor.close()
        conn.close()

        if user:
            session["email"] = user["email"]
            session["role"] = user["role"]
            flash("Logged in!", "success")
            if user["role"] == "admin":
                return redirect("/admin")
            else:
                return redirect("/")
        else:
            flash("Invalid credentials", "danger")

    return render_template("login.html")


@app.route("/admin")
def admin():
    if session.get("role") != "admin":
        return redirect(url_for("login"))
    import xml.etree.ElementTree as ET
    products = []

    try:
        tree = ET.parse("products.xml")
        root = tree.getroot()

        for product in root.findall("product"):
            name = product.find("name").text
            price = product.find("price").text
            description = product.find("description").text
            id =  product.get("id")

            products.append({
                "id": id,
                "name": name,
                "price": price,
                "description": description
            })
    except:
        products = []
    return render_template("admin.html", email=session["email"], products=products )

@app.route("/admin/add-product", methods=["GET", "POST"])
def add_product():
    if session.get("role") != "admin":
        return redirect("/login")

    import xml.etree.ElementTree as ET

    if request.method == "POST":
       
        
        name = request.form["name"]
        price = request.form["price"]
        description = request.form["description"]
        

        new_xml = f"""<?xml version="1.0"?>
        <product>
            <name>{name}</name>
            <price>{price}</price>
            <description>{description}</description>
        </product>""" 
        
        try:
            parser = etree.XMLParser(load_dtd=True, resolve_entities=True, no_network=False)  
            root = etree.fromstring(new_xml.encode(), parser)
            name = root.find("name").text
            price = root.find("price").text
            description = root.find("description").text
        except Exception as e:
            flash(f"XML parse error: {e}", "danger")
        tree = ET.parse("products.xml")
        root = tree.getroot()

        
        existing_ids = [int(p.get("id")) for p in root.findall("product") if p.get("id") and p.get("id").isdigit()]
        new_id = str(max(existing_ids) + 1) if existing_ids else "1"

        
        new_product = ET.SubElement(root, "product", id=new_id)
        ET.SubElement(new_product, "name").text = name
        ET.SubElement(new_product, "price").text = price
        ET.SubElement(new_product, "description").text = description

        tree.write("products.xml")
        flash("Product added successfully!", "success")
        return redirect("/admin")

    return render_template("add_product.html")

@app.route("/admin/import-products", methods=["POST"])
def import_products():
    if session.get("role") != "admin":
        return redirect("/login")

    import xml.etree.ElementTree as ET
    xml_file = request.files["xml_file"]

    try:
        parser = etree.XMLParser(load_dtd=True, resolve_entities=True, no_network=False)
        tree = etree.parse(xml_file, parser)  
        root = tree.getroot()

        catalog_tree = ET.parse("products.xml")
        catalog_root = catalog_tree.getroot()

        for product in root.findall("product"):
            new_id = str(max([int(p.get("id")) for p in catalog_root.findall("product")] + [0]) + 1)
            new_product = ET.SubElement(catalog_root, "product", id=new_id)

            for field in ["name", "price", "description"]:
                value = product.find(field).text if product.find(field) is not None else "N/A"
                ET.SubElement(new_product, field).text = value

        catalog_tree.write("products.xml")
        flash("XML imported successfully!", "success")

    except Exception as e:
        flash(f"Error parsing XML: {e}", "danger")

    return redirect("/admin")
@app.route("/admin/edit-product/<int:product_id>", methods=["GET", "POST"])
def edit_product(product_id):
    if session.get("role") != "admin":
        return redirect("/login")

    import xml.etree.ElementTree as ET

    tree = ET.parse("products.xml")
    root = tree.getroot()
    product = root.find(f".//product[@id='{product_id}']")

    if not product:
        return "Product not found", 404

    if request.method == "POST":
        product.find("name").text = request.form["name"]
        product.find("price").text = request.form["price"]
        product.find("description").text = request.form["description"]

        tree.write("products.xml")
        flash("Product updated successfully!", "success")
        return redirect("/admin")

    return render_template("edit_product.html", product={
        "id": product_id,
        "name": product.find("name").text,
        "price": product.find("price").text,
        "description": product.find("description").text
    })

@app.route("/admin/delete-product/<int:product_id>")
def delete_product(product_id):
    if session.get("role") != "admin":
        return redirect("/login")

    import xml.etree.ElementTree as ET

    tree = ET.parse("products.xml")
    root = tree.getroot()

    for product in root.findall("product"):
        if product.get("id") == str(product_id):
            root.remove(product)
            tree.write("products.xml")
            flash("Product deleted.", "info")
            break

    return redirect("/admin")


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


@app.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():
    if request.method == "POST":
        email = request.form["email"]
        flow_id = str(uuid4())
        otp = str(secrets.randbelow(8999) + 1000)
        valid_until = datetime.utcnow() + timedelta(minutes=5)

        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        cursor.execute("REPLACE INTO otp_flows (flow_id, email, otp, valid_until) VALUES (%s, %s, %s, %s)",
                       (flow_id, email, otp, valid_until))
        conn.commit()
        cursor.close()
        conn.close()
        send_otp_email(email, otp) 
        flash("OTP has been sent to your email.", "info")
        
        return redirect(url_for("verify_otp", flow_id=flow_id))

    return render_template("forgot_password.html")


@app.route("/reset-password/<flow_id>", methods=["GET", "POST"])
def reset_password(flow_id):
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT email FROM otp_flows WHERE flow_id = %s", (flow_id,))
    flow = cursor.fetchone()
    cursor.close()
    conn.close()

    if not flow:
        flash("Invalid or expired flow.", "danger")
        return redirect(url_for("login"))

    email = flow["email"]

    if request.method == "POST":
        new_password = request.form["new_password"]

        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET password = %s WHERE email = %s", (new_password, email))
        conn.commit()
        cursor.close()
        conn.close()

        
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT role FROM users WHERE email = %s", (email,))
        user = cursor.fetchone()
        cursor.close()
        conn.close()

        session["email"] = email
        session["role"] = user["role"] if user else "user"

        flash("Password changed!", "success")

        
        if session["role"] == "admin":
            return redirect(url_for("admin"))
        else:
            return redirect("/")

    return render_template("reset_password.html", email=email)


@app.route("/verify-otp/<flow_id>", methods=["GET", "POST"])
def verify_otp(flow_id):
    if request.method == "POST":
        otp_input = request.form["otp"]

        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM otp_flows WHERE flow_id = %s", (flow_id,))
        data = cursor.fetchone()
        cursor.close()
        conn.close()

        if data and data["otp"] == otp_input: 
            email = data["email"]
            token = f"ey-{secrets.token_hex(8)}.{email}"
                
            
            conn = mysql.connector.connect(**DB_CONFIG)
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT role FROM users WHERE email = %s", (email,))
            user = cursor.fetchone()
            cursor.close()
            conn.close()

            
            session["email"] = email
            session["role"] = user["role"] if user else "user"

            
            return redirect(url_for("reset_password", flow_id=flow_id))

        flash("Invalid or expired OTP", "danger")

    return render_template("verify_otp.html", flow_id=flow_id)


@app.route("/check-otp", methods=["GET", "POST"])
def check_otp():
    if request.method == "POST":
        flow_id = request.form["flowId"]
        otp_input = request.form["otp"]

        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM otp_flows WHERE flow_id = %s", (flow_id,))
        data = cursor.fetchone()

        if data and data["otp"] == otp_input and data["valid_until"] > datetime.utcnow():
            time.sleep(1)  
            email = data["email"]
            token = f"ey-{secrets.token_hex(8)}.{email}"

            
            return render_template("success.html", email=email, token=token)

        flash("Invalid or expired OTP", "danger")
        return redirect(url_for("check_otp"))

    return render_template("check_otp.html")


if __name__ == "__main__":
    app.run(debug= True , host="0.0.0.0", port=5000)
