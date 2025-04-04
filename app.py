from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from sentence_transformers import SentenceTransformer, util
from blreward_data import blreward_data
import torch

app = Flask(__name__)
CORS(app)

# Load the model (this may take time on first run)
model = SentenceTransformer('all-MiniLM-L6-v2')

# Precompute embeddings
prompts = [item["prompt"] for item in blreward_data]
prompt_embeddings = model.encode(prompts, convert_to_tensor=True)

def get_legal_response(user_input):
    user_embedding = model.encode(user_input, convert_to_tensor=True)
    scores = util.cos_sim(user_embedding, prompt_embeddings)[0]
    best_score = float(scores.max())
    best_idx = int(scores.argmax())

    confidence_threshold = 0.7
    item = blreward_data[best_idx]
    response = item[f"response_{item['preferred']}"]

    if best_score >= confidence_threshold:
        return response
    else:
        return (
            "⚠️ I have not yet been trained on this exact question, "
            "but based on my knowledge I am responding:\n\n" + response
        )

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    user_msg = request.json.get("message", "")
    reply = get_legal_response(user_msg)
    return jsonify({"response": reply})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
