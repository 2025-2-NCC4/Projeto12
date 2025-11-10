from functools import wraps
from flask import jsonify
from flask_login import current_user

def role_required(*allowed_roles):
    def _decorator(f):
        @wraps(f)
        def _wrapper(*args, **kwargs):
            if not current_user.is_authenticated:
                return jsonify({"ok": False, "error": "unauthorized"}), 401
            perfil = getattr(current_user.perfil, "tipo", None)
            if perfil not in allowed_roles:
                return jsonify({"ok": False, "error": "forbidden"}), 403
            return f(*args, **kwargs)
        return _wrapper
    return _decorator
