#LAS CLASES DE MODELOS DE LA BASE DE DATOS (CREAN TABLAS EN LA DB)
from databases.db import db
from datetime import datetime

class EmailCheck(db.Model):
    __tablename__ = 'email_checks'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), nullable=False)
    pwned = db.Column(db.Boolean, nullable=False)
    
class FileAnalysis(db.Model):
    __tablename__ = 'file_analysis'
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)  # Aquí guardamos base64 (string)
    content_length = db.Column(db.Integer, nullable=False)
    line_count = db.Column(db.Integer)
    malicious = db.Column(db.Boolean, default=False)

class HashRecord(db.Model):
    __tablename__ = 'hash_records'
    id = db.Column(db.Integer, primary_key=True)
    original_text = db.Column(db.Text, nullable=False)
    texto_hasheado = db.Column(db.Text, nullable=False)
    algoritmo = db.Column(db.String(20), nullable=False)


class SuperShodanScan(db.Model):
    __tablename__ = 'supershodan_scans'
    
    id = db.Column(db.Integer, primary_key=True)
    target = db.Column(db.String(255), nullable=False)
    scan_date = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))  # Si tienes autenticación
    theharvester_results = db.Column(db.JSON)  # Para almacenar resultados JSON
    nmap_results = db.Column(db.Text)
    whois_results = db.Column(db.Text)
    dns_results = db.Column(db.JSON)
    is_complete = db.Column(db.Boolean, default=False)
    error = db.Column(db.Text)

    # Relación con usuario si usas Flask-Login
    user = db.relationship('User', backref='supershodan_scans')

    def __init__(self, target, user_id=None):
        self.target = target
        self.user_id = user_id
        self.is_complete = False

    def save_results(self, results):
        """Guarda los resultados en la base de datos"""
        try:
            self.theharvester_results = results.get('theharvester')
            self.nmap_results = results.get('nmap')
            self.whois_results = results.get('whois')
            self.dns_results = results.get('dns')
            self.is_complete = True
            db.session.commit()
        except Exception as e:
            self.error = str(e)
            db.session.rollback()

    def to_dict(self):
        """Convierte el objeto a diccionario para JSON"""
        return {
            'id': self.id,
            'target': self.target,
            'scan_date': self.scan_date.isoformat() if self.scan_date else None,
            'theharvester': self.theharvester_results,
            'nmap': self.nmap_results,
            'whois': self.whois_results,
            'dns': self.dns_results,
            'is_complete': self.is_complete,
            'error': self.error
        }

    @classmethod
    def get_recent_scans(cls, limit=10):
        """Obtiene los escaneos más recientes"""
        return cls.query.order_by(cls.scan_date.desc()).limit(limit).all()