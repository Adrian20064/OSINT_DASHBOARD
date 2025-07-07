#SCRIPT PARA LA COMPROBACION DEL EMAAIL
#LA API CUESTA ENTONCES ESTO SE VA A ALAGRAR 

#TEST
from flask import Blueprint, request, jsonify,current_app
import logging
import traceback
from services.db_helper import save_to_db
from databases.models import EmailCheck

email_bp = Blueprint('email_bp', __name__)

#mail
@email_bp.route('/api/email-check', methods=['POST'])
def check_email():
    try:
        data = request.get_json(force=True)
        if not data or 'email' not in data:
            return jsonify({"error": "Falta campo email"}), 400

        email = data.get("email", "")
        is_pwned = "@" in email and email.endswith(".com")

        record = EmailCheck(email=email, pwned=is_pwned)
        save_to_db(record)

        return jsonify({
            "email": email,
            "pwned": is_pwned,
            "message": "Comprometido" if is_pwned else "No encontrado en brechas"
        })

    except Exception as e:
        current_app.logger.error(f"Error en /api/email-check: {e}")
        current_app.logger.error(traceback.format_exc())
        return jsonify({
            "error": str(e),
            "trace": traceback.format_exc()
        }), 500