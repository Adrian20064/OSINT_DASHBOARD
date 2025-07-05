from flask import Flask, send_from_directory, request, render_template, redirect, url_for, flash,jsonify
from dotenv import load_dotenv
from databases.models import FileAnalysis, LocalScan
import os
from databases.db import db
from databases import models
from services.email_powned import email_bp
from services.file_analisis import file_bp
from services.hash_service import hash_bp
from services.supershodan import supershodan_bp
from flask_login import LoginManager, login_user, login_required, logout_user, current_user, UserMixin
from flask_migrate import Migrate

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "supersecretkey")

# Config DB
DB_USER = os.getenv('DB_USER')
DB_PASS = os.getenv('DB_PASS')
DB_HOST = os.getenv('DB_HOST')
DB_PORT = os.getenv('DB_PORT')
DB_NAME = os.getenv('DB_NAME')

app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
migrate = Migrate(app, db)


# Registrar blueprints
app.register_blueprint(email_bp)
app.register_blueprint(file_bp)
app.register_blueprint(hash_bp)
app.register_blueprint(supershodan_bp)



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
