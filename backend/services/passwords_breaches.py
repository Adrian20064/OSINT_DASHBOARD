import hashlib
import requests
from flask import Blueprint, request, jsonify
from databases.models import PasswordBreachQuery
from services.db_helper import save_to_db

passwords_bp = Blueprint('passwords_breaches', __name__)

@passwords_bp.route('/api/check-password-leak', methods=['POST'])
def check_password_leak():
    data = request.get_json()
    password = data.get('password', '')
    if not password:
        return jsonify({'error': 'No password provided'}), 400

    sha1_password = hashlib.sha1(password.encode('utf-8')).hexdigest().upper()
    prefix = sha1_password[:5]
    suffix = sha1_password[5:]

    url = f'https://api.pwnedpasswords.com/range/{prefix}'
    try:
        res = requests.get(url, timeout=5)
        if res.status_code != 200:
            return jsonify({'error': 'Error contacting HaveIBeenPwned API'}), 500

        hashes = (line.split(':') for line in res.text.splitlines())
        for h, count in hashes:
            if h == suffix:
                record = PasswordBreachQuery(
                    sha1_hash=sha1_password,
                    leaked=True,
                    count=int(count)
                )
                save_to_db(record)
                return jsonify({
                    'sha1': sha1_password,
                    'leaked': True,
                    'count': int(count),
                    'message': f'La contraseña ha sido filtrada {count} veces.'
                })

        # No encontrada
        record = PasswordBreachQuery(
            sha1_hash=sha1_password,
            leaked=False,
            count=0
        )
        save_to_db(record)

        return jsonify({
            'sha1': sha1_password,
            'leaked': False,
            'count': 0,
            'message': 'La contraseña no fue encontrada en bases de datos públicas.'
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500
