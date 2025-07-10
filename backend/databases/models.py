from databases.db import db
from datetime import datetime
import json
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
    theharvester_results = db.Column(db.JSON)
    nmap_results = db.Column(db.JSON)
    whois_results = db.Column(db.JSON)
    dns_results = db.Column(db.JSON)
    is_complete = db.Column(db.Boolean, default=False)
    error = db.Column(db.Text)

    def __init__(self, target):
        self.target = target
        self.is_complete = False
        
    def save_results(self, results):
        try:
            self.theharvester_results = results.get('theharvester')

            # Convertir a JSON string si no es None
            nmap_res = results.get('nmap')
            self.nmap_results = json.dumps(nmap_res) if nmap_res is not None else None

            whois_res = results.get('whois')
            self.whois_results = json.dumps(whois_res) if whois_res is not None else None

            self.dns_results = results.get('dns')
            self.is_complete = True
            db.session.commit()
        except Exception as e:
            self.error = str(e)
            db.session.rollback()

    def to_dict(self):
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
        return cls.query.order_by(cls.scan_date.desc()).limit(limit).all()


#Se usa solo sha1 porque:  la API de Have I Been Pwned (HIBP) Passwords, solo se usa SHA-1 para la comprobación de contraseñas filtradas.
class PasswordBreachQuery(db.Model):
    __tablename__ = 'password_breach_queries'

    id = db.Column(db.Integer, primary_key=True)
    sha1_hash = db.Column(db.String(40), nullable=False)
    leaked = db.Column(db.Boolean, nullable=False)
    count = db.Column(db.Integer, default=0)
    query_date = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<PasswordBreachQuery {self.sha1_hash} leaked={self.leaked} count={self.count}>'

    def to_dict(self):
        return {
            'id': self.id,
            'sha1_hash': self.sha1_hash,
            'leaked': self.leaked,
            'count': self.count,
            'query_date': self.query_date.isoformat()
        }

