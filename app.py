from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import sqlite3
import bcrypt
import smtplib
import random
from email.mime.text import MIMEText

app = Flask(__name__, static_folder='.')
CORS(app)

reset_codes = {}

# =====================
# DATABASE
# =====================
def get_db():
    conn = sqlite3.connect("/tmp/users.db")  # 🔥 مهم
    conn.row_factory = sqlite3.Row
    return conn

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

create_table()

# =====================
# HOME
# =====================
@app.route("/")
def home():
    return send_from_directory(".", "index.html")

# =====================
# STATIC FILES
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

        hashed_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
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
        return jsonify({"success": False, "message": str(e)})

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
            if bcrypt.checkpw(password.encode(), bytes(user["password"])):
                return jsonify({"success": True})

        return jsonify({"success": False, "message": "Wrong email or password ❌"})

    except Exception as e:
        print("LOGIN ERROR:", e)
        return jsonify({"success": False, "message": str(e)})

# =====================
# SEND CODE
# =====================
@app.route("/send-code", methods=["POST"])
def send_code():
    try:
        data = request.get_json()
        email = data.get("email")

        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
        user = cursor.fetchone()
        conn.close()

        if not user:
            return jsonify({"success": False, "message": "Email not found ❌"})

        code = str(random.randint(100000, 999999))
        reset_codes[email] = code

        sender = "your_email@gmail.com"
        password = "your_app_password"

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
        return jsonify({"success": False, "message": str(e)})

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

        if email not in reset_codes:
            return jsonify({"success": False, "message": "Send code first ❌"})

        if reset_codes[email] != code:
            return jsonify({"success": False, "message": "Wrong code ❌"})

        hashed_password = bcrypt.hashpw(new_password.encode(), bcrypt.gensalt())
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
        return jsonify({"success": False, "message": str(e)})

# =====================
# RUN
# =====================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
