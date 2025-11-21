from flask import jsonify, get_flashed_messages, Blueprint

bp = Blueprint("flash", __name__)  

@bp.route("/get_flash_messages")
def get_flash_messages():
    """
    Gibt die aktuellen Flash-Messages als JSON zurück.
    """
    messages = get_flashed_messages(with_categories=True)
    return jsonify({"messages": [{"category": cat, "text": msg} for cat, msg in messages]})