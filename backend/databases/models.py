#LAS CLASES DE MODELOS DE LA BASE DE DATOS (CREAN TABLAS EN LA DB)
from databases.db import db

class EmailCheck(db.Model):
    __tablename__ = 'email_checks'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), nullable=False)
    pwned = db.Column(db.Boolean, nullable=False)
    

class FileAnalysis(db.Model):
    __tablename__ = 'file_analysis'
    id = db.Column(db.Integer, primary_key=True)
    content_length = db.Column(db.Integer, nullable=False)
    line_count = db.Column(db.Integer, nullable=False)
    # Puedes agregar más campos si quieres guardar más info

class HashRecord(db.Model):
    __tablename__ = 'hash_records'
    id = db.Column(db.Integer, primary_key=True)
    original_text = db.Column(db.Text, nullable=False)
    sha256_hash = db.Column(db.String(64), nullable=False)  # 64 chars para SHA-256 hex

class ShodanLookup(db.Model):
    __tablename__ = 'shodan_lookups'
    id = db.Column(db.Integer, primary_key=True)
    ip_address = db.Column(db.String(45), nullable=False)  # IPv6 compatible
    open_ports = db.Column(db.Text)  # Podrías almacenar JSON como string
    vulnerabilities = db.Column(db.Text)  # Igual JSON como string

class WhoisRecord(db.Model):
    __tablename__ = 'whois_records'
    id = db.Column(db.Integer, primary_key=True)
    domain = db.Column(db.String(255), nullable=False, unique=True)
    registrar = db.Column(db.String(255))
    creation_date = db.Column(db.String(50))
    expiration_date = db.Column(db.String(50))