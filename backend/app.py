from flask import Flask, send_from_directory, request, render_template, redirect, url_for, flash, jsonify
from dotenv import load_dotenv
from databases.models import FileAnalysis
import os
import logging
from databases.models import SuperShodanScan
from databases.db import db,init_db
from databases import models
from services.email_powned import email_bp
from services.file_analisis import file_bp
from services.hash_service import hash_bp
from services.supershodan import supershodan_bp 
from flask_migrate import Migrate
from services.passwords_breaches import passwords_bp
from flask_cors import CORS
from pathlib import Path

#cargar .env
env_path = Path(__file__).resolve().parent / '.env'
print("DATABASE_URL =", os.getenv("DATABASE_URL"))
load_dotenv(dotenv_path=env_path)
print("DATABASE_URL =", os.getenv("DATABASE_URL"))


# Configurar la aplicación Flask
app = Flask(__name__)
# Configurar la URI de la DB antes de inicializarla
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DATABASE_URL")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Inicializar la base de datos
init_db(app)

#logger para el debug
if app.debug:
    app.logger.setLevel(logging.DEBUG)
    handler = logging.StreamHandler()
    handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter('[%(asctime)s] %(levelname)s in %(module)s: %(message)s')
    handler.setFormatter(formatter)
    app.logger.addHandler(handler)
    
#cargar base de datos supabase, nuevo puerto
with app.app_context():
    db.create_all()
#inicialize app and migrations to databse
migrate = Migrate(app, db)

# Registrar blueprints
app.register_blueprint(email_bp)
app.register_blueprint(file_bp)
app.register_blueprint(hash_bp)
app.register_blueprint(passwords_bp)
app.register_blueprint(supershodan_bp)

#cors (for deployment)
CORS(app, supports_credentials=True, origins=[
    "https://osint-dashboard.onrender.com",
    "http://127.0.0.1:5000",
    "http://localhost:5000"
])
# Crear DB
@app.route('/create-db')
def create_db():
    with app.app_context():
        db.create_all()
    return "Base de datos creada"

# Servir frontend
@app.route('/assets/<path:path>')
def send_assets(path):
    return send_from_directory('../frontend/assets', path)

@app.route('/')
def serve_index():
    path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../frontend'))
    return send_from_directory(path, 'index.html')

@app.route('/api/supershodan/recent')
def supershodan_recent():
    scans = SuperShodanScan.get_recent_scans()
    return jsonify([scan.to_dict() for scan in scans])

@app.route('/fix-null-values')
def fix_null_values():
    with app.app_context():
        records = FileAnalysis.query.filter(
            (FileAnalysis.content == None) | (FileAnalysis.malicious == None)
        ).all()
        for record in records:
            record.content = record.content or ""
            record.malicious = record.malicious if record.malicious is not None else False
        db.session.commit()
    return "Valores NULL actualizados"

if __name__ == '__main__':
    app.run(debug=True)
