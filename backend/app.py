from dotenv import load_dotenv
load_dotenv()

from flask import Flask, jsonify, request
from flask_cors import CORS

from routes.predict import predict_plant
from routes.chatbot import chatbot_bp
from db import get_use_from_db, store_use_to_db
from gemini_fetch import get_use_from_gemini

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

# Register routes
app.register_blueprint(predict_plant)
app.register_blueprint(chatbot_bp)


@app.route("/", methods=["GET"])
def home():
    return jsonify({"status": "Backend running"})


# Optional route: separate use fetch
@app.route("/api/get-plant-uses", methods=["POST"])
def fetch_uses():
    data = request.json
    sci = data.get("scientific_name")

    if not sci:
        return jsonify({"error": "scientific_name required"}), 400

    uses = get_use_from_db(sci)
    if uses:
        return jsonify({
            "source": "database",
            "scientific_name": sci,
            "uses": uses
        })

    # Call Gemini
    uses = get_use_from_gemini(sci)
    if not uses:
        return jsonify({"error": "Gemini failed"}), 500

    store_use_to_db(sci, uses)

    return jsonify({
        "source": "gemini",
        "scientific_name": sci,
        "uses": uses
    })


if __name__ == "__main__":
    app.run(debug=True)
