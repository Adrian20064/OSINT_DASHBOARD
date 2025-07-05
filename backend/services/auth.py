from flask import Blueprint, request, jsonify, session
from databases.models import User
from databases.db import db
from flask_login import LoginManager, login_user, logout_user, login_required, current_user

auth_bp = Blueprint('auth_bp', __name__)
login_manager = LoginManager()

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@auth_bp.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    user = User.query.filter_by(username=username).first()
    if user and user.check_password(password):
        login_user(user)
        return jsonify({"message": "Login exitoso", "username": user.username})
    return jsonify({"error": "Credenciales inválidas"}), 401

@auth_bp.route('/api/logout')
@login_required
def logout():
    logout_user()
    return jsonify({"message": "Sesión cerrada"})
