from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import sqlite3
import bcrypt
import smtplib
import random
from email.mime.text import MIMEText

app = Flask(__name__, static_folder='.')
CORS(app)

# 🔥 تخزين الأكواد مؤقت
reset_codes = {}

# =====================
# DB
# =====================
def get_db():
    conn = sqlite3.connect("users.db")
    conn.row_factory = sqlite3.Row
    return conn

# 🔥 إنشاء الجدول تلقائي
def create_table():
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT UNIQUE,
        password BLOB
    )
    """)

    conn.commit()
    conn.close()

# 🔥 تشغيل إنشاء الجدول أول ما السيرفر يشتغل
create_table()

# =====================
# HOME PAGE
# =====================
@app.route("/")
def home():
    return send_from_directory(".", "index.html")  # غيّر الاسم إذا صفحتك مختلفة

# =====================
# SERVE FILES
# =====================
@app.route("/<path:path>")
def static_files(path):
    return send_from_directory(".", path)

# =====================
# SIGNUP
# =====================
@app.route("/signup", methods=["POST"])
def signup():
    try:
        data = request.get_json()

        email = data.get("email")
        password = data.get("password")

        if not email or not password:
            return jsonify({"success": False, "message": "Missing data ❌"})

        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        hashed_password = sqlite3.Binary(hashed_password)

        conn = get_db()
        cursor = conn.cursor()

        cursor.execute(
            "INSERT INTO users (email, password) VALUES (?, ?)",
            (email, hashed_password)
        )

        conn.commit()
        conn.close()

        return jsonify({"success": True})

    except sqlite3.IntegrityError:
        return jsonify({"success": False, "message": "Email already exists ❌"})

    except Exception as e:
        print("SIGNUP ERROR:", e)
        return jsonify({"success": False, "message": "Server error ❌"})

# =====================
# LOGIN
# =====================
@app.route("/login", methods=["POST"])
def login():
    try:
        data = request.get_json()

        email = data.get("email")
        password = data.get("password")

        conn = get_db()
        cursor = conn.cursor()

        cursor.execute("SELECT password FROM users WHERE email = ?", (email,))
        user = cursor.fetchone()

        conn.close()

        if user:
            stored_password = bytes(user["password"])

            if bcrypt.checkpw(password.encode('utf-8'), stored_password):
                return jsonify({"success": True})

        return jsonify({"success": False, "message": "Wrong email or password ❌"})

    except Exception as e:
        print("LOGIN ERROR:", e)
        return jsonify({"success": False, "message": "Server error ❌"})

# =====================
# SEND CODE
# =====================
@app.route("/send-code", methods=["POST"])
def send_code():
    try:
        data = request.get_json()
        email = data.get("email")

        if not email:
            return jsonify({"success": False})

        conn = get_db()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
        user = cursor.fetchone()
        conn.close()

        if not user:
            return jsonify({"success": False, "message": "Email not found ❌"})

        code = str(random.randint(100000, 999999))
        reset_codes[email] = code

        sender = "majdahmadqaraa@gmail.com"
        password = "ofyf nskl tcse brne"

        msg = MIMEText(f"Your reset code is: {code}")
        msg["Subject"] = "Password Reset"
        msg["From"] = sender
        msg["To"] = email

        server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
        server.login(sender, password)
        server.send_message(msg)
        server.quit()

        return jsonify({"success": True})

    except Exception as e:
        print("EMAIL ERROR:", e)
        return jsonify({"success": False})

# =====================
# RESET PASSWORD
# =====================
@app.route("/reset-password", methods=["POST"])
def reset_password():
    try:
        data = request.get_json()

        email = data.get("email")
        code = data.get("code")
        new_password = data.get("new_password")

        if not email or not code or not new_password:
            return jsonify({"success": False, "message": "Missing data ❌"})

        if email not in reset_codes:
            return jsonify({"success": False, "message": "Send code first ❌"})

        if reset_codes[email] != code:
            return jsonify({"success": False, "message": "Wrong code ❌"})

        hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())
        hashed_password = sqlite3.Binary(hashed_password)

        conn = get_db()
        cursor = conn.cursor()

        cursor.execute(
            "UPDATE users SET password = ? WHERE email = ?",
            (hashed_password, email)
        )

        conn.commit()
        conn.close()

        reset_codes.pop(email)

        return jsonify({"success": True})

    except Exception as e:
        print("RESET ERROR:", e)
        return jsonify({"success": False, "message": "Server error ❌"})

# =====================
# RUN
# =====================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
