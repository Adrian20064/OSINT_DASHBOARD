import subprocess
import json
import os
import shutil
from flask import Blueprint, request, jsonify
from databases.models import SuperShodanScan
from databases.db import db

supershodan_bp = Blueprint('supershodan_bp', __name__)

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
    
    
def run_theharvester(domain):
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    theharvester_path = os.path.join(BASE_DIR, "theHarvester", "theHarvester.py")

    output_file = os.path.join(os.getenv('TEMP', '/tmp'), f'theharvester_{domain}.txt')
    cmd = f'python "{theharvester_path}" -d {domain} -b anubis,baidu,bevigil,crtsh -f "{output_file}"'

    output = run_command(cmd, timeout=120)
    print(f"Ejecutando: {cmd}")
    print(f"Output comando:\n{output}")
    print(f"Archivo generado existe? {os.path.exists(output_file)}")

    if os.path.exists(output_file):
        with open(output_file, 'r', encoding='utf-8') as f:
            data = f.read()
        print("Datos cargados")
        return {"raw_output": data}

    print("No se generó el archivo de resultados")
    return {"error": "No se generó el archivo de resultados"}

def run_nmap(target):
    try:
        cmd = ["nmap", "-T4", "-Pn", "-sV", "--open", "-p", "21,22,80,443,8080", target]
        return run_command(cmd)
    except Exception as e:
        return {"error": str(e)}

def run_whois(target):
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    whois_exe = os.path.join(BASE_DIR, "whois64.exe")

    if not os.path.exists(whois_exe):
        return {"error": "whois64.exe no encontrado en backend/"}

    try:
        cmd = [whois_exe, target]
        return run_command(cmd)
    except Exception as e:
        return {"error": str(e)}

def run_dns_enum(target):
    try:
        tools = {}
        if shutil.which("host"):
            tools['host'] = f"host {target}"
        if shutil.which("dig"):
            tools['dig'] = f"dig {target} ANY +short"
        if shutil.which("dnsrecon"):
            tools['dnsrecon'] = f"dnsrecon -d {target}"

        results = {}
        for tool, cmd in tools.items():
            results[tool] = run_command(cmd)

        return results if results else {"error": "No se encontraron herramientas DNS disponibles"}
    except Exception as e:
        return {"error": str(e)}

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
        db.session.add(scan_record)
        db.session.commit()
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

        try:
            scan_record.theharvester_results = results.get('theharvester')
            scan_record.nmap_results = results.get('nmap')
            scan_record.whois_results = results.get('whois')
            scan_record.dns_results = results.get('dns')
            scan_record.is_complete = True
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            scan_record.error = f"Error al guardar resultados: {str(e)}"
            db.session.commit()

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
