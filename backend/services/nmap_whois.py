from flask import Blueprint, request, jsonify
from databases.db import db
from databases.models import LocalScan
import subprocess

localscan_bp = Blueprint('localscan_bp', __name__)

def run_nmap(ip):
    result = subprocess.run(['nmap', '-sV', '-p-', ip], capture_output=True, text=True)
    return result.stdout

def run_whois(ip_or_domain):
    result = subprocess.run(['whois', ip_or_domain], capture_output=True, text=True)
    return result.stdout

@localscan_bp.route('/api/scan', methods=['POST'])
def scan():
    data = request.get_json()
    ip = data.get('ip', '').strip()
    if not ip:
        return jsonify({"error": "IP o dominio requerido"}), 400

    try:
        nmap_output = run_nmap(ip)
        whois_output = run_whois(ip)

        record = LocalScan(
            ip_address=ip,
            nmap_result=nmap_output,
            whois_result=whois_output
        )
        db.session.add(record)
        db.session.commit()

        return jsonify({
            "ip": ip,
            "nmap_result": nmap_output,
            "whois_result": whois_output
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500
