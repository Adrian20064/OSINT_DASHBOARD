#SCRIPT PARA LA COMPROBACION DEL EMAAIL
#LA API CUESTA ENTONCES ESTO SE VA A ALAGRAR 

#TEST
from flask import Blueprint, request, jsonify
from services.db_helper import save_to_db
from databases.models import EmailCheck

email_bp = Blueprint('email_bp', __name__)

#mail
@email_bp.route('/api/email-check', methods=['POST'])
def check_email():
    data = request.json
    email = data.get("email", "")
    is_pwned = "@" in email and email.endswith(".com")

    # Guardar en DB usando la función centralizada
    record = EmailCheck(email=email, pwned=is_pwned)
    save_to_db(record)

    return jsonify({
        "email": email,
        "pwned": is_pwned,
        "message": "Comprometido" if is_pwned else "No encontrado en brechas"
    })