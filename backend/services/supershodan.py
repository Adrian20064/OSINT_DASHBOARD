import subprocess
import json
import os
from flask import Blueprint, request, jsonify
from datetime import datetime
from databases.models import SuperShodanScan
from databases.db import db

supershodan_bp = Blueprint('supershodan_bp', __name__)

def run_command(cmd, timeout=60):
    """Ejecuta un comando y devuelve el output"""
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            check=True,
            timeout=timeout,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        return result.stdout
    except subprocess.TimeoutExpired:
        return "Error: Tiempo de espera agotado"
    except subprocess.CalledProcessError as e:
        return f"Error: {e.stderr}"
    except Exception as e:
        return f"Error: {str(e)}"
    
    
def run_theharvester(domain):
    """Ejecuta TheHarvester (OSINT para emails y subdominios)"""
    try:
        # Ruta al ejecutable theHarvester.py en tu proyecto
        theharvester_path = os.path.join(os.path.dirname(__file__), '..', 'theHarvester', 'theHarvester.py')
        
        # Usar ruta temporal de Windows
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_file = os.path.join(os.environ['TEMP'], f"theharvester_{timestamp}.json")
        
        # Comando para Windows
        cmd = f'python "{theharvester_path}" -d {domain} -b anubis,baidu,bevigil,crtsh -f "{output_file}" --json'
        
        # Ejecutar el comando
        output = run_command(cmd, timeout=120)
        
        # Verificar y leer el archivo de resultados
        if os.path.exists(output_file):
            with open(output_file, 'r', encoding='utf-8') as f:
                return json.load(f)
            # Opcional: eliminar el archivo temporal después de leerlo
            # os.remove(output_file)
        return {"error": "No se generó el archivo de resultados"}
        
    except json.JSONDecodeError:
        return {"error": "Error al decodificar JSON"}
    except Exception as e:
        return {"error": str(e)}
    
    
    
def run_nmap(target):
    """Escaneo básico con Nmap (puertos comunes)"""
    try:
        cmd = ["nmap", "-T4", "-Pn", "-sV", "--open", "-p", "21,22,80,443,8080", target]
        return run_command(cmd)
    except Exception as e:
        return {"error": str(e)}

def run_whois(target):
    """Consulta WHOIS tradicional"""
    try:
        if os.name == 'nt':  # Windows
            cmd = f"whois {target}"
        else:  # Linux/Mac
            cmd = ["whois", target]
        return run_command(cmd)
    except Exception as e:
        return {"error": str(e)}

def run_dns_enum(target):
    """Enumeración DNS con herramientas nativas"""
    try:
        tools = {}
        if os.system("which host") == 0:
            tools['host'] = f"host {target}"
        if os.system("which dig") == 0:
            tools['dig'] = f"dig {target} ANY +short"
        if os.system("which dnsrecon") == 0:
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
    
    # Validación básica
    if not target:
        return jsonify({"error": "Se requiere un objetivo (IP/dominio/email)"}), 400
    if not tools:
        return jsonify({"error": "Selecciona al menos una herramienta"}), 400

    # Crear registro en la base de datos
    scan_record = SuperShodanScan(target=target)
    try:
        if hasattr(request, 'user') and hasattr(request.user, 'is_authenticated') and request.user.is_authenticated:
            scan_record.user_id = request.user.id
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

        # Guardar resultados en la base de datos
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