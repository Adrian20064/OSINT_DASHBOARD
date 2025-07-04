from flask import Flask,send_from_directory
from dotenv import load_dotenv
from databases.models import FileAnalysis
import os
from databases.db import db
from databases import models # importa los modelos para registrarlos
from services.email_powned import email_bp
from services.file_analisis import file_bp
from services.hash_service import hash_bp
from services.censys_service import censys_bp
from services.nmap_whois import localscan_bp
from flask_migrate import Migrate
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
migrate = Migrate(app,db)

# Registrar blueprint
app.register_blueprint(email_bp)
app.register_blueprint(file_bp)
app.register_blueprint(hash_bp)
app.register_blueprint(censys_bp) #Se debe cambiar con referencia a los cambios en el censys_service.py, con una nueva herramienta diferente y totalmente gratis a shodan 
app.register_blueprint(localscan_bp)
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
    path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../frontend'))
    print("Sirviendo desde:", path)
    return send_from_directory(path, 'index.html')

@app.route('/fix-null-values')
def fix_null_values():
    with app.app_context():
        records = FileAnalysis.query.filter(
            (FileAnalysis.content == None) | (FileAnalysis.malicious == None)
        ).all()
        for record in records:
            if record.content is None:
                record.content = ""
            if record.malicious is None:
                record.malicious = False
        db.session.commit()
    return "Valores NULL actualizados"

if __name__ == '__main__':
    app.run(debug=True)