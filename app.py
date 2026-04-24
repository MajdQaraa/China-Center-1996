from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import sqlite3
import bcrypt
import random
import os
import requests

app = Flask(__name__, static_folder='.')
CORS(app, resources={r"/*": {"origins": "*"}})

# 🔥 تخزين الأكواد مؤقت
reset_codes = {}

# =====================
# DB
# =====================
def get_db():
    db_path = os.path.join(os.getcwd(), "users.db")
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def create_database():
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
    print("Database ready ✅")


create_database()

# =====================
# HOME
# =====================
@app.route("/")
def home():
    return send_from_directory(".", "index.html")


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

        hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
        hashed = sqlite3.Binary(hashed)

        conn = get_db()
        cursor = conn.cursor()

        cursor.execute(
            "INSERT INTO users (email, password) VALUES (?, ?)",
            (email, hashed)
        )

        conn.commit()
        conn.close()

        return jsonify({"success": True})

    except sqlite3.IntegrityError:
        return jsonify({"success": False, "message": "Email already exists ❌"})

    except Exception as e:
        print("SIGNUP ERROR:", e)
        return jsonify({"success": False})


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

        if user and bcrypt.checkpw(password.encode(), user["password"]):
            return jsonify({"success": True})

        return jsonify({"success": False, "message": "Wrong email or password ❌"})

    except Exception as e:
        print("LOGIN ERROR:", e)
        return jsonify({"success": False})


# =====================
# SEND CODE
# =====================
@app.route("/send-code", methods=["POST"])
def send_code():
    try:
        data = request.get_json()
        email = data.get("email")

        if not email:
            return jsonify({"success": False, "message": "Email required ❌"})

        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
        user = cursor.fetchone()
        conn.close()

        if not user:
            return jsonify({"success": False, "message": "Email not found ❌"})

        code = str(random.randint(100000, 999999))
        reset_codes[email] = code

        url = "https://api.brevo.com/v3/smtp/email"

        payload = {
            "sender": {
                "name": "China Center",
                "email": "majdahmadqaraa@gmail.com"
            },
            "to": [{"email": email}],
            "subject": "Password Reset",
            "htmlContent": f"<h3>Your code is: {code}</h3>"
        }

        headers = {
            "accept": "application/json",
            "api-key": os.environ.get("BREVO_API_KEY"),
            "content-type": "application/json"
        }

        response = requests.post(url, json=payload, headers=headers)

        # 🔥 Debug كامل
        print("STATUS CODE:", response.status_code)
        print("RESPONSE:", response.text)

        # 🔥 تحليل النتيجة الحقيقي
        if response.status_code == 201:
            return jsonify({"success": True})
        else:
            return jsonify({
                "success": False,
                "message": "Brevo failed to send email ❌",
                "status_code": response.status_code,
                "debug": response.text
            })

    except Exception as e:
        print("BREVO ERROR:", e)
        return jsonify({
            "success": False,
            "message": "Server error ❌",
            "error": str(e)
        })


# =====================
# RESET PASSWORD
# =====================
@app.route("/reset-password", methods=["POST"])
def reset_password():
    try:
        print("RESET ENDPOINT HIT")

        # 🔥 قراءة JSON بشكل آمن
        data = request.get_json(silent=True)

        # 🔥 fallback لو ما وصل JSON
        if not data:
            return jsonify({
                "success": False,
                "message": "No data received ❌"
            })

        email = data.get("email")
        code = data.get("code")
        new_password = data.get("new_password")

        # 🔥 تحقق من البيانات
        if not email or not code or not new_password:
            return jsonify({
                "success": False,
                "message": "Missing fields ❌"
            })

        # 🔥 تحقق الكود
        stored_code = reset_codes.get(email)

        if stored_code is None:
            return jsonify({
                "success": False,
                "message": "Code not found or expired ❌"
            })

        if stored_code != code:
            return jsonify({
                "success": False,
                "message": "Wrong code ❌"
            })

        # 🔐 تحديث الباسورد
        hashed = bcrypt.hashpw(new_password.encode(), bcrypt.gensalt())
        hashed = sqlite3.Binary(hashed)

        conn = get_db()
        cursor = conn.cursor()

        cursor.execute(
            "UPDATE users SET password = ? WHERE email = ?",
            (hashed, email)
        )

        conn.commit()
        conn.close()

        # 🧹 حذف الكود بعد النجاح
        reset_codes.pop(email, None)

        return jsonify({
            "success": True,
            "message": "Password updated successfully ✅"
        })

    except Exception as e:
        import traceback
        print("RESET ERROR:", e)
        print(traceback.format_exc())

        return jsonify({
            "success": False,
            "message": "Server error ❌",
            "error": str(e)
        })


# =====================
# RUN
# =====================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)