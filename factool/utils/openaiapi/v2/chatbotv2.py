import os
import sqlite3
from openai import OpenAI
from flask import Flask, request, jsonify, g
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import jwt
import datetime

app = Flask(__name__)
CORS(app)

JWT_SECRET = '123'  # JWT secret key
client = OpenAI(api_key='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')


def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect('chatbot.db')
        g.db.row_factory = sqlite3.Row
    return g.db


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, 'db', None)
    if db is not None:
        db.close()


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if "Authorization" in request.headers:
            auth_header = request.headers["Authorization"]
            parts = auth_header.split()
            if len(parts) == 2 and parts[0] == "Bearer":
                token = parts[1]
        if not token:
            return jsonify({"error": "Token is missing!"}), 401
        try:
            data = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
            user_id = data["user_id"]
            db = get_db()
            cursor = db.cursor()
            cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
            user = cursor.fetchone()
            cursor.close()
            if not user:
                return jsonify({"error": "User not found!"}), 401
            g.user = user
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token has expired!"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"error": "Invalid token!"}), 401
        return f(*args, **kwargs)

    return decorated


@app.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")
    if not username or not password:
        return jsonify({"error": "Username and password are required."}), 400
    db = get_db()
    cursor = db.cursor()
    password_hash = generate_password_hash(password)
    try:
        cursor.execute("INSERT INTO users (username, password_hash) VALUES (?, ?)", (username, password_hash))
        db.commit()
        cursor.close()
        return jsonify({"message": "User registered successfully."}), 201
    except sqlite3.IntegrityError:
        cursor.close()
        return jsonify({"error": "Username already exists."}), 400


@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
    user = cursor.fetchone()
    cursor.close()
    if user and check_password_hash(user["password_hash"], password):
        token = jwt.encode({
            "user_id": user["id"],
            "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=1)
        }, JWT_SECRET, algorithm="HS256")
        return jsonify({"token": token})
    else:
        return jsonify({"error": "Invalid username or password."}), 401


@app.route("/themes", methods=["GET", "POST"])
@token_required
def themes():
    db = get_db()
    cursor = db.cursor()
    user_id = g.user["id"]
    if request.method == "POST":
        data = request.get_json()
        theme_name = data.get("theme_name")
        if not theme_name:
            return jsonify({"error": "Theme name is required."}), 400
        cursor.execute("INSERT INTO themes (user_id, theme_name) VALUES (?, ?)", (user_id, theme_name))
        db.commit()
        cursor.close()
        return jsonify({"message": "Theme created successfully."}), 201
    elif request.method == "GET":
        cursor.execute("SELECT * FROM themes WHERE user_id = ?", (user_id,))
        themes = cursor.fetchall()
        cursor.close()
        theme_list = [{
            "id": theme["id"],
            "theme_name": theme["theme_name"]
        } for theme in themes]
        return jsonify({"themes": theme_list})


@app.route("/themes/<int:theme_id>", methods=["DELETE"])
@token_required
def delete_theme(theme_id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("DELETE FROM themes WHERE id = ? AND user_id = ?", (theme_id, g.user["id"]))
    db.commit()
    cursor.close()
    return jsonify({"message": "Theme deleted successfully."})


@app.route("/themes/<int:theme_id>/records", methods=["GET"])
@token_required
def get_theme_records(theme_id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM chat_records WHERE user_id = ? AND theme = ?", (g.user["id"], theme_id))
    records = cursor.fetchall()
    cursor.close()
    record_list = [{
        "user_message": record["user_message"],
        "bot_reply": record["bot_reply"]
    } for record in records]
    return jsonify({"records": record_list})


@app.route("/chat", methods=["POST"])
@token_required
def chat():
    user_message = request.json.get("message")
    theme = request.json.get("theme")
    if not user_message:
        return jsonify({"error": "No message provided"}), 400

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": user_message}]
        )
        bot_reply = response.choices[0].message.content

        db = get_db()
        cursor = db.cursor()
        cursor.execute("INSERT INTO chat_records (user_id, theme, user_message, bot_reply) VALUES (?, ?, ?, ?)",
                       (g.user["id"], theme, user_message, bot_reply))
        db.commit()
        cursor.close()

        return jsonify({"reply": bot_reply})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(port=5000, debug=True)