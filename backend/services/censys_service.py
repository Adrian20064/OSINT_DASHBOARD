from flask import Blueprint, request, jsonify
from databases.db import db
from databases.models import ShodanLookup
from censys.search import CensysHosts
from censys.common.exceptions import CensysNotFoundException, CensysUnauthorizedException
import os
import json

censys_bp = Blueprint('censys_bp', __name__)

# Usa variables de entorno para mayor seguridad, o pon tus claves aquí directamente
CENSYS_API_ID = os.getenv("CENSYS_API_ID", "tu_api_id")
CENSYS_API_SECRET = os.getenv("CENSYS_API_SECRET", "tu_api_secret")

@censys_bp.route('/api/censys', methods=['POST'])
def censys_lookup():
    data = request.get_json()
    ip = data.get('ip', '').strip()
    if not ip:
        return jsonify({"error": "IP requerida"}), 400

    try:
        c = CensysHosts(api_id=CENSYS_API_ID, api_secret=CENSYS_API_SECRET)
        result = c.view(ip)

        open_ports = [svc["port"] for svc in result.get("services", [])]
        vulnerabilities = result.get("vulnerabilities", [])

        censys_data = {
            "ip": ip,
            "open_ports": open_ports,
            "vulnerabilities": vulnerabilities
        }

        # Guardar como string JSON en la base de datos
        record = ShodanLookup(
            ip_address=ip,
            open_ports=json.dumps(open_ports),
            vulnerabilities=json.dumps(vulnerabilities)
        )
        db.session.add(record)
        db.session.commit()

        return jsonify(censys_data)

    except CensysNotFoundException:
        return jsonify({"error": "IP no encontrada en Censys"}), 404
    except CensysUnauthorizedException:
        return jsonify({"error": "Credenciales inválidas"}), 401
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500
