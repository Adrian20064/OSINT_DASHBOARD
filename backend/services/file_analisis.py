from flask import Blueprint, request, jsonify
from databases.models import FileAnalysis
from services.db_helper import save_to_db
import base64

file_bp = Blueprint('file', __name__)

@file_bp.route('/api/file-analyze', methods=['POST'])
def analyze_file():
    data = request.get_json()
    base64_content = data.get('content', '')
    filename = data.get('filename', '')

    print(f"Archivo recibido: {filename}, longitud base64: {len(base64_content)}")

    try:
        decoded_bytes = base64.b64decode(base64_content)
        clean_text = decoded_bytes.decode('utf-8', errors='ignore')
        content_text = clean_text.replace('\x00', '')  # Eliminar caracteres NUL
    except Exception as e:
        print(f"Error decodificando base64: {e}")
        return jsonify({"error": "Error al decodificar el contenido: " + str(e)}), 400

    print(f"Contenido texto limpio (primeros 200 chars): {content_text[:200]}")

    content_length = len(decoded_bytes)
    line_count = content_text.count('\n') + 1
    malicious = is_malicious(content_text)

    try:
        record = FileAnalysis(
            content=content_text,
            content_length=content_length,
            line_count=line_count,
            malicious=malicious
        )
        save_to_db(record)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    return jsonify({
        "filename": filename,
        "content_length": content_length,
        "line_count": line_count,
        "malicious": malicious,
        "message": "Guardado correctamente"
    })

def is_malicious(content):
    keywords = ["malware", "trojan", "backdoor", "virus"]
    return any(word in content.lower() for word in keywords)