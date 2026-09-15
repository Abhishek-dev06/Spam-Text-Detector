from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import joblib
import os

app = Flask(
    __name__,
    static_folder="/frontend",
    static_url_path=""
)
CORS(app)

MODEL_PATH = os.path.join(os.path.dirname(__file__), "backend/spam_model.joblib")

if not os.path.exists(MODEL_PATH):
    raise FileNotFoundError(
        "Model not found. First run: python train_model.py"
    )

model = joblib.load(MODEL_PATH)


@app.route("/")
def home():
    return send_from_directory("/frontend", "index.html")


@app.route("/metrics")
def metrics_page():
    return send_from_directory("/frontend", "metrics.html")


@app.route("/predict", methods=["POST"])
def predict():
    data = request.get_json()

    if not data or "text" not in data:
        return jsonify({"error": "Please send text in JSON body."}), 400

    text = data["text"].strip()

    if not text:
        return jsonify({"error": "Text cannot be empty."}), 400

    prediction = model.predict([text])[0]
    probabilities = model.predict_proba([text])[0]

    classes = list(model.classes_)
    predicted_index = classes.index(prediction)
    confidence = float(probabilities[predicted_index]) * 100

    label = "Spam" if prediction == "spam" else "Genuine"

    return jsonify({
        "label": label,
        "confidence": round(confidence, 2)
    })



@app.route("/api/metrics")
def get_metrics():
    import json
    metrics_path = os.path.join(os.path.dirname(__file__), "backend/metrics.json")

    if not os.path.exists(metrics_path):
        return jsonify({"error": "Metrics not found."}), 404

    with open(metrics_path, "r") as file:
        return jsonify(json.load(file))


if __name__ == "__main__":
    app.run(debug=True)
