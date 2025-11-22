from flask import Blueprint, request, jsonify
import os
import requests

from db import get_use_from_db, store_use_to_db
from gemini_fetch import get_use_from_gemini

predict_plant = Blueprint("predict_plant", __name__)

# Load PlantNet Key
PLANTNET_API_KEY = os.getenv("PLANTNET_API_KEY")
PLANTNET_URL = f"https://my-api.plantnet.org/v2/identify/all?api-key={PLANTNET_API_KEY}"


@predict_plant.route("/predict", methods=["POST"])
def predict():
    if "image" not in request.files:
        return jsonify({"error": "No image uploaded"}), 400

    file = request.files["image"]

    # Send image to PlantNet
    files = {
        "images": (file.filename, file.stream, file.content_type)
    }
    data = {"organs": ["leaf"]}

    try:
        response = requests.post(PLANTNET_URL, files=files, data=data)
        result = response.json()
    except Exception as e:
        return jsonify({"error": f"PlantNet request failed: {str(e)}"}), 500

    # Validate PlantNet response
    if "results" not in result or not result["results"]:
        return jsonify({"error": "No plant identified"}), 400

    top_result = result["results"][0]
    species = top_result["species"]

    scientific_name = species["scientificName"]
    common_name = species["commonNames"][0] if species["commonNames"] else "Unknown"

    # Check DB for uses
    uses = get_use_from_db(scientific_name)

    # If not in DB → get from Gemini & store
    if not uses:
        uses = get_use_from_gemini(scientific_name)
        if uses:
            store_use_to_db(scientific_name, uses)

    return jsonify({
        "scientific_name": scientific_name,
        "common_name": common_name,
        "uses": uses or "Not available"
    })
