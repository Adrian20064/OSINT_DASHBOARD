import subprocess
import json
import os
import shutil
import requests
import whois
import dns.resolver
from services.db_helper import save_to_db
from flask import Blueprint, request, jsonify
from databases.models import SuperShodanScan
from databases.db import db

supershodan_bp = Blueprint('supershodan_bp', __name__)

# ========================
# Procesamiento de comandos
# ========================
def run_command(cmd, timeout=60):
    try:
        result = subprocess.run(
            cmd,
            shell=isinstance(cmd, str),
            check=True,
            timeout=timeout,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        print("STDOUT:", result.stdout)
        print("STDERR:", result.stderr)
        return result.stdout
    except subprocess.TimeoutExpired:
        print("Timeout expired")
        return "Error: Tiempo de espera agotado"
    except subprocess.CalledProcessError as e:
        print("CalledProcessError STDOUT:", e.stdout)
        print("CalledProcessError STDERR:", e.stderr)
        return f"Error: {e.stderr}"
    except Exception as e:
        print("Exception:", str(e))
        return f"Error: {str(e)}"

# ========================
# Remplazo de: TheHarvester a  crt.sh
# ========================
def run_theharvester(domain):
    try:
        url = f"https://crt.sh/?q=%25.{domain}&output=json"
        response = requests.get(url, timeout=30)
        if response.status_code != 200:
            return {"error": f"Error consultando crt.sh: {response.status_code}"}

        data = response.json()
        emails = set()
        domains = set()

        for entry in data:
            name_value = entry.get("name_value", "")
            for val in name_value.split("\n"):
                if "@" in val:
                    emails.add(val.strip())
                elif domain in val:
                    domains.add(val.strip())

        return {
            "emails_found": list(emails),
            "domains_found": list(domains),
            "raw_count": len(data)
        }

    except Exception as e:
        return {"error": f"Error al consultar certificados: {str(e)}"}

# ========================
# Remplazo: Nmap (no disponible) a  IP-API 
# ========================
def run_nmap(target):
    error_message = "Nmap no está disponible para estos casos. Usando IP-API."
    try:
        ip_info = requests.get(f"http://ip-api.com/json/{target}", timeout=10)
        if ip_info.status_code == 200:
            data = ip_info.json()
            return {
                "nmap": {
                    "nmap_error": error_message,
                    "ip_api_info": {
                        "ip": data.get("query"),
                        "isp": data.get("isp"),
                        "org": data.get("org"),
                        "country": data.get("country"),
                        "city": data.get("city"),
                        "region": data.get("regionName"),
                        "timezone": data.get("timezone"),
                        "lat": data.get("lat"),
                        "lon": data.get("lon"),
                        "as": data.get("as"),
                        "reverse": data.get("reverse"),
                        "status": data.get("status")
                    }
                }
            }
        else:
            return {
                "nmap": {
                    "nmap_error": error_message,
                    "ip_api_error": f"ip-api.com respondió con estado: {ip_info.status_code}"
                }
            }
    except Exception as e:
        return {
            "nmap": {
                "nmap_error": error_message,
                "ip_api_error": f"Excepción al consultar ip-api.com: {str(e)}"
            }
        }

# ========================
# Whois (con librería)
# ========================
def run_whois(target):
    try:
        w = whois.whois(target)
        result = {k: str(v) for k, v in w.items() if v}
        return result
    except Exception as e:
        return {"error": f"Error en whois: {str(e)}"}

# ========================
# DNS Lookup (con dnspython)
# ========================
def run_dns_enum(domain):
    try:
        records = {}
        for record_type in ["A", "AAAA", "MX", "NS", "TXT", "CNAME"]:
            try:
                answers = dns.resolver.resolve(domain, record_type)
                records[record_type] = [r.to_text() for r in answers]
            except dns.resolver.NoAnswer:
                records[record_type] = []
            except dns.resolver.NXDOMAIN:
                records[record_type] = ["Dominio no encontrado"]
        return records
    except Exception as e:
        return {"error": f"Error DNS: {str(e)}"}

# ========================
# Ruta principal del escaneo
# ========================
@supershodan_bp.route('/api/super-osint', methods=['POST'])
def super_osint():
    data = request.get_json()
    target = data.get('target', '').strip()
    tools = data.get('tools', [])

    if not target:
        return jsonify({"error": "Se requiere un objetivo (IP/dominio/email)"}), 400
    if not tools:
        return jsonify({"error": "Selecciona al menos una herramienta"}), 400

    scan_record = SuperShodanScan(target=target)

    try:
        save_to_db(scan_record)
    except Exception as e:
        return jsonify({"error": f"Error al crear registro: {str(e)}"}), 500

    results = {}

    try:
        if 'theharvester' in tools and ('@' in target or '.' in target):
            domain = target.split('@')[-1] if '@' in target else target
            results['theharvester'] = run_theharvester(domain)

        if 'nmap' in tools and ('.' in target or ':' in target):
            results['nmap'] = run_nmap(target)

        if 'whois' in tools:
            results['whois'] = run_whois(target)

        if 'dns' in tools and ('.' in target or ':' in target):
            results['dns'] = run_dns_enum(target)

        # Guardar resultados en la base de datos
        scan_record.save_results(results)

        return jsonify({
            'scan_id': scan_record.id,
            'results': results,
            'status': 'completed'
        })

    except Exception as e:
        db.session.rollback()
        scan_record.error = str(e)
        db.session.commit()
        return jsonify({
            'scan_id': scan_record.id,
            'error': f"Error interno: {str(e)}",
            'status': 'failed'
        }), 500
