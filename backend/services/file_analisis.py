from flask import Blueprint, request, jsonify
from databases.db import db
from databases.models import FileAnalysis

file_bp = Blueprint('file', __name__)

@file_bp.route('/api/file-analyze', methods=['POST'])
def analyze_file():
    data = request.get_json()
    content = data.get('content', '')

    content_length = len(content)
    line_count = content.count('\n') + 1

    # Guardar en base
    try:
        record = FileAnalysis(content_length=content_length, line_count=line_count)
        db.session.add(record)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

    return jsonify({
        "content_length": content_length,
        "line_count": line_count,
        "message": "Guardado en DB"
    })