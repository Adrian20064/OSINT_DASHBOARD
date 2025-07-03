from flask import Blueprint, request, jsonify
from databases.db import db
from databases.models import WhoisRecord
import socket
import logging

def simple_whois_query(domain):
    try:
        server = "whois.verisign-grs.com"  # Para dominios .com, .net, etc.
        port = 43
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(10)
        s.connect((server, port))
        s.send((domain + "\r\n").encode())
        response = b""
        while True:
            data = s.recv(4096)
            if not data:
                break
            response += data
        s.close()
        return response.decode(errors="ignore")
    except Exception as e:
        logging.error(f"Error en consulta WHOIS: {e}")
        return {"error": "No se pudo obtener la información WHOIS"}

# Flask route example (en email_powned.py o donde definas API)
from flask import Blueprint, request, jsonify

whois_bp = Blueprint("whois_bp", __name__)

@whois_bp.route("/api/whois", methods=["POST"])
def whois_lookup():
    data = request.get_json()
    domain = data.get("domain")
    if not domain:
        return jsonify({"error": "Falta dominio"}), 400

    result = simple_whois_query(domain)
    return jsonify({"whois_data": result})