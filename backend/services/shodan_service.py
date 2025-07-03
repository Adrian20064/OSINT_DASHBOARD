from flask import Blueprint, request, jsonify
from databases.db import db
from databases.models import ShodanLookup
import requests

shodan_bp = Blueprint('shodan_bp', __name__)

@shodan_bp.route('/api/shodan', methods=['POST'])
def shodan_lookup():
    data = request.get_json()
    ip = data.get('ip', '').strip()
    if not ip:
        return jsonify({"error": "IP requerida"}), 400

    # Aquí pondrías la llamada real a la API Shodan, ejemplo simulado:
    shodan_data = {"ip": ip, "open_ports": [80, 443], "vulnerabilities": ["CVE-2020-1234"]}

    try:
        record = ShodanLookup(ip=ip, data=str(shodan_data))
        db.session.add(record)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

    return jsonify(shodan_data)