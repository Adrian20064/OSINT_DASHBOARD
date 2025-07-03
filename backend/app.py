from flask import Flask,send_from_directory
from dotenv import load_dotenv
import os
from databases.db import db
from databases import models  # importa los modelos para registrarlos
from services.email_powned import email_bp
from services.file_analisis import file_bp
from services.hash_service import hash_bp
from services.shodan_service import shodan_bp
from services.whois_services import whois_bp
load_dotenv()

app = Flask(__name__)

# Configurar base de datos desde .env
DB_USER = os.getenv('DB_USER')
DB_PASS = os.getenv('DB_PASS')
DB_HOST = os.getenv('DB_HOST')
DB_PORT = os.getenv('DB_PORT')
DB_NAME = os.getenv('DB_NAME')
app.config['SQLALCHEMY_DATABASE_URI'] = (
    f'postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}'
)

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Inicializar SQLAlchemy
db.init_app(app)

# Registrar blueprint
app.register_blueprint(email_bp)
app.register_blueprint(file_bp)
app.register_blueprint(hash_bp)
app.register_blueprint(shodan_bp)
app.register_blueprint(whois_bp)
# Ruta para crear la base de datos
@app.route('/create-db')
def create_db():
    with app.app_context():
        db.create_all()
    return "Base de datos creada"
# Servir archivos estáticos dentro de assets
@app.route('/assets/<path:path>')
def send_assets(path):
    return send_from_directory('../frontend/assets', path)

# Servir index.html en la raíz
@app.route('/')
def serve_index():
    return send_from_directory('../frontend', 'index.html')


if __name__ == '__main__':
    app.run(debug=True)