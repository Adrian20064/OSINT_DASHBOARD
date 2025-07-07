from flask import Blueprint, request, jsonify
from databases.models import HashRecord
from services.db_helper import save_to_db
import hashlib

hash_bp = Blueprint("hash_bp", __name__)

@hash_bp.route("/api/hash", methods=["POST"])
def hash_text():
    data = request.get_json()
    text = data.get("text", "")
    algorithm = data.get("algorithm", "sha256").lower()

    try:
        hash_func = getattr(hashlib, algorithm)
    except AttributeError:
        return jsonify({"error": f"Algoritmo no soportado: {algorithm}"}), 400

    hashed = hash_func(text.encode()).hexdigest()

    try:
        record = HashRecord(
            original_text=text,
            texto_hasheado=hashed,
            algoritmo=algorithm.upper()
        )
        save_to_db(record)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    return jsonify({
        "original": text,
        "hash": hashed,
        "algoritmo": algorithm.upper()
    })
