from flask import Blueprint, request, jsonify
from databases.models import LocalScan
from databases.db import db
import subprocess
import platform
import os
import traceback

localscan_bp = Blueprint('localscan_bp', __name__)

def run_nmap(ip, params):
    param_list = params.split()
    cmd = ['nmap'] + param_list + [ip]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
    return result.stdout

def run_whois(ip_or_domain):
    if platform.system() == 'Windows':
        whois_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'whois64.exe'))
        result = subprocess.run([whois_path, ip_or_domain], capture_output=True, text=True, timeout=30)
    else:
        result = subprocess.run(['whois', ip_or_domain], capture_output=True, text=True, timeout=30)
    return result.stdout

@localscan_bp.route('/api/scan', methods=['POST'])
def scan():
    data = request.get_json()
    ip = data.get('ip', '').strip()
    run_nmap_flag = data.get('runNmap', False)
    run_whois_flag = data.get('runWhois', False)
    nmap_params = data.get('nmapParams', '-sV -p 80,443').strip()

    if not ip:
        return jsonify({"error": "IP o dominio requerido"}), 400
    if not run_nmap_flag and not run_whois_flag:
        return jsonify({"error": "Selecciona al menos Nmap o Whois para ejecutar"}), 400

    try:
        nmap_output = ""
        whois_output = ""

        if run_nmap_flag:
            nmap_output = run_nmap(ip, nmap_params)
        if run_whois_flag:
            whois_output = run_whois(ip)

        record = LocalScan(
            ip_address=ip,
            nmap_result=nmap_output if run_nmap_flag else None,
            whois_result=whois_output if run_whois_flag else None
        )
        db.session.add(record)
        db.session.commit()

        return jsonify({
            "ip": ip,
            "nmap_result": nmap_output,
            "whois_result": whois_output
        })

    except subprocess.TimeoutExpired as e:
        db.session.rollback()
        return jsonify({"error": f"Tiempo de espera agotado: {str(e)}"}), 500
    except Exception as e:
        db.session.rollback()
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500