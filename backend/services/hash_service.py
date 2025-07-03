from flask import Blueprint, request, jsonify
from databases.db import db
from databases.models import HashRecord
import hashlib

hash_bp = Blueprint('hash_bp', __name__)

@hash_bp.route('/api/hash', methods=['POST'])
def hash_text():
    data = request.get_json()
    text = data.get('text', '')
    if not text:
        return jsonify({"error": "Texto requerido"}), 400

    hashed = hashlib.sha256(text.encode('utf-8')).hexdigest()

    try:
        record = HashRecord(original=text, hashed=hashed)
        db.session.add(record)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

    return jsonify({"original": text, "hashed": hashed})