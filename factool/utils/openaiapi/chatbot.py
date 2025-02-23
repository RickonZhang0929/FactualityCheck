import os
from openai import OpenAI
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

client = OpenAI(api_key='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')


@app.route("/chat", methods=["POST"])
def chat():
    user_message = request.json.get("message")
    if not user_message:
        return jsonify({"error": "No message provided"}), 400

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": user_message}]
        )
        print(response)
        bot_reply = response.choices[0].message.content
        return jsonify({"reply": bot_reply})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(port=5000, debug=True)