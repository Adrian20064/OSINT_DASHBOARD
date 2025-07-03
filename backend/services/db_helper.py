
from databases.db import db

def save_to_db(model_instance):
    try:
        db.session.add(model_instance)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        raise e